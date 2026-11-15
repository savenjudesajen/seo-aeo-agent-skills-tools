#!/usr/bin/env node
// Public-content check: every file, commit, tag, branch name and PR or release text this repository publishes is
// checked against the maintainers' private word list and wording rules before it goes out. The matcher and the list
// live in a private repository; this driver reads the matcher at the commit pinned in pin.json and the list from
// that repository's main branch. Nothing of either is stored here.
//
//   node tools/public-content-scan/scan.mjs pre-push <remote> [<url>]    git runs this (.githooks/pre-push); refs on stdin
//   node tools/public-content-scan/scan.mjs github                       CI: reads the GitHub event (push, PR, release, schedule)
//   node tools/public-content-scan/scan.mjs tree [<rev>]                 every file at <rev> (default HEAD)
//   node tools/public-content-scan/scan.mjs history                      every commit, tag and file ever reachable
//   node tools/public-content-scan/scan.mjs text --label <label>         text on stdin (a PR or release note draft)
//   node tools/public-content-scan/scan.mjs bump                         move pin.json to the matcher on the source's main
//   node tools/public-content-scan/scan.mjs export-matcher <dir>         write the pinned matcher to <dir> (the tests use it)
//
// Exit 0 = nothing found · 1 = something found · 2 = the check could not run. Exit 2 is never a pass.
// Key: PUBLIC_SCAN_KEY, else the file named by `git config publicscan.keyfile` (mode 600, yours, not a symlink).
// Source access: PUBLIC_SCAN_SOURCE_URL (CI: the SSH URL with a read-only deploy key), else HTTPS with your own git
// credentials. Output never contains a listed word: every line is masked, and no message says which kind of word it is.

import { execFileSync } from "node:child_process";
import { closeSync, constants, fstatSync, mkdtempSync, openSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PIN_FILE = path.join(HERE, "pin.json");
const EXCEPTIONS_FILE = path.join(HERE, "exceptions.json");
const MATCHER_PATH = "scripts/privacy/client-names.mjs";
const LIST_PATH = "scripts/privacy/client-names.hmac";
const ZERO = /^0+$/;
const OID = /^[0-9a-f]{40}$/;
const MIN_NODE_MAJOR = 20;
/** One message for every kind of listed word, so a public log never says which kind a word is. */
const NAME_ADVICE = "a listed word: rewrite the text without it";
/** Files whose words the check can't read. Images and PDFs need their own reader; until then they don't pass. */
const UNREADABLE = new Set([".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".ico", ".bmp", ".tif", ".tiff", ".pdf", ".zip", ".gz", ".woff", ".woff2", ".ttf", ".otf", ".mp4", ".mov", ".mp3"]);
const LFS_POINTER = "version https://git-lfs.github.com/spec/v1";
/** A file bigger than this stops the check (a skill file is a few kB; the biggest today is under 100 kB). */
const MAX_FILE_BYTES = 5 * 1024 * 1024;

class CheckError extends Error {}

// ---------------------------------------------------------------------------------------------- output

/** Set once the matcher and key are loaded; from then on every line is masked before it is printed. */
let masker = null;
const lines = [];

/** Escapes control characters, so a label can't start a new log line or a terminal sequence. */
function plain(text) {
  return String(text)
    .replace(/[\u0000-\u001f\u007f-\u009f\u2028\u2029]/g, (c) => `\\u${c.charCodeAt(0).toString(16).padStart(4, "0")}`)
    .replace(/::/g, ":\\:") // a GitHub workflow command (::error::, ::add-mask::)…
    .replace(/##\[/g, "#\\#["); // …and its legacy form, wherever they sit in the line
}

/** Every output line goes through here: masked, escaped, and prefixed (so no line is a GitHub workflow command). */
function say(text) {
  lines.push(`public-content: ${plain(masker ? masker(String(text)) : String(text))}`);
}

// ---------------------------------------------------------------------------------------------- git

const debug = () => process.env.PUBLIC_SCAN_DEBUG === "1" && !process.env.CI;

/** Runs git; any failure is a CheckError with a fixed message (git's own stderr can quote paths and URLs). */
function git(args, { cwd, input, env, encoding = "utf8", what } = {}) {
  try {
    return execFileSync("git", args, {
      cwd,
      input,
      encoding: encoding === "buffer" ? undefined : encoding,
      maxBuffer: 1 << 30,
      stdio: ["pipe", "pipe", "pipe"],
      env: { ...process.env, GIT_TERMINAL_PROMPT: "0", GIT_NO_REPLACE_OBJECTS: "1", ...env },
    });
  } catch (e) {
    if (debug()) process.stderr.write(String(e.stderr ?? e.message));
    throw new CheckError(`git ${what ?? args[0]} failed${debug() ? "" : " (set PUBLIC_SCAN_DEBUG=1 locally to see why)"}`);
  }
}

/** Whether `rev` names an object in the repository at `cwd`. */
function exists(cwd, rev) {
  try {
    execFileSync("git", ["cat-file", "-e", rev], { cwd, stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

/** Reads blobs in one `git cat-file --batch`, checking every frame. Returns Map(oid → Buffer). */
function readBlobs(cwd, oids) {
  const unique = [...new Set(oids)];
  const out = new Map();
  if (unique.length === 0) return out;
  const buf = git(["cat-file", "--batch"], { cwd, input: `${unique.join("\n")}\n`, encoding: "buffer", what: "cat-file" });
  let at = 0;
  for (const oid of unique) {
    const nl = buf.indexOf(0x0a, at);
    if (nl === -1) throw new CheckError("git cat-file returned a truncated answer");
    const [got, type, size] = buf.subarray(at, nl).toString("utf8").split(" ");
    if (got !== oid) throw new CheckError("git cat-file returned objects out of order");
    if (type !== "blob") throw new CheckError(`object ${oid.slice(0, 12)} is a ${type ?? "missing object"}, not a file`);
    const n = Number(size);
    const end = nl + 1 + n;
    if (!Number.isInteger(n) || end >= buf.length + 1 || buf[end] !== 0x0a) throw new CheckError("git cat-file returned a truncated answer");
    out.set(oid, buf.subarray(nl + 1, end));
    at = end + 1;
  }
  if (at !== buf.length) throw new CheckError("git cat-file returned more than was asked");
  return out;
}

/** Splits NUL-separated git output, refusing a missing final NUL (a truncated answer). */
function nulFields(text) {
  if (text === "") return [];
  if (!text.endsWith("\0")) throw new CheckError("git returned a truncated list");
  return text.slice(0, -1).split("\0");
}

// ---------------------------------------------------------------------------------------------- matcher + key

function readPin() {
  let pin;
  try {
    pin = JSON.parse(readFileSync(PIN_FILE, "utf8"));
  } catch {
    throw new CheckError("pin.json is missing or not JSON");
  }
  if (!/^[A-Za-z0-9-]+\/[A-Za-z0-9._-]+$/.test(pin?.source ?? "") || !OID.test(pin?.commit ?? "")) {
    throw new CheckError('pin.json must be {"source": "<owner>/<repo>", "commit": "<40-hex sha>"}');
  }
  return pin;
}

/** A fresh bare repository holding the source's pinned commit and its main, blobs fetched only when read. */
function fetchSource(pin, env) {
  const dir = mkdtempSync(path.join(tmpdir(), "public-scan-"));
  const repo = path.join(dir, "source.git");
  const url = env.PUBLIC_SCAN_SOURCE_URL || `https://github.com/${pin.source}.git`;
  git(["init", "--bare", "-q", repo], { what: "init" });
  git(["remote", "add", "origin", url], { cwd: repo, what: "remote add" });
  const fetch = ["fetch", "-q", "--no-tags", "--depth=1", "--filter=blob:none", "origin"];
  git([...fetch, pin.commit], { cwd: repo, what: "fetch (pinned matcher)" });
  git([...fetch, "+refs/heads/main:refs/remotes/origin/main"], { cwd: repo, what: "fetch (source main)" });
  return { dir, repo };
}

function blobAt(repo, rev, file) {
  return git(["cat-file", "blob", `${rev}:${file}`], { cwd: repo, what: `read ${file}` });
}

/** The key as the matcher parses it: PUBLIC_SCAN_KEY, else the configured key file (one open, no symlink). */
function loadKey(matcher, env, cwd) {
  if (env.PUBLIC_SCAN_KEY !== undefined) {
    try {
      return matcher.parseKey(env.PUBLIC_SCAN_KEY);
    } catch {
      throw new CheckError("PUBLIC_SCAN_KEY is empty or malformed (a fork PR has no secrets: a maintainer runs the check)");
    }
  }
  let keyFile;
  try {
    keyFile = execFileSync("git", ["config", "--get", "publicscan.keyfile"], { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  } catch {
    throw new CheckError("no key: set PUBLIC_SCAN_KEY, or run tools/public-content-scan/install-hook.sh with the key file");
  }
  if (!path.isAbsolute(keyFile)) throw new CheckError("publicscan.keyfile must be an absolute path");
  let fd;
  try {
    fd = openSync(keyFile, constants.O_RDONLY | constants.O_NOFOLLOW);
  } catch {
    throw new CheckError("the key file named by publicscan.keyfile can't be opened (missing, or a symlink)");
  }
  try {
    const st = fstatSync(fd);
    if (!st.isFile()) throw new CheckError("the key file is not a regular file");
    if (typeof process.getuid === "function" && st.uid !== process.getuid()) throw new CheckError("the key file must be owned by you");
    if ((st.mode & 0o077) !== 0) throw new CheckError("the key file must be readable by you only (chmod 600)");
    try {
      return matcher.parseKey(readFileSync(fd, "utf8"));
    } catch {
      throw new CheckError("the key file doesn't hold a valid key");
    }
  } finally {
    closeSync(fd);
  }
}

/**
 * Loads the matcher at the pinned commit and the list from the source's main. Refuses when main's matcher differs
 * from the pin (code never moves without a reviewed pin change) and when the list doesn't match the key.
 */
async function loadPolicy(env, cwd) {
  const pin = readPin();
  const { dir, repo } = fetchSource(pin, env);
  try {
    const pinned = git(["rev-parse", `${pin.commit}:${MATCHER_PATH}`], { cwd: repo, what: "rev-parse (pinned matcher)" }).trim();
    const current = git(["rev-parse", `refs/remotes/origin/main:${MATCHER_PATH}`], { cwd: repo, what: "rev-parse (source matcher)" }).trim();
    if (pinned !== current) throw new CheckError("the matcher changed on the source's main: run `node tools/public-content-scan/scan.mjs bump` and commit pin.json");
    const listCommit = git(["rev-parse", "refs/remotes/origin/main"], { cwd: repo, what: "rev-parse (source main)" }).trim();
    const code = path.join(dir, "matcher.mjs");
    writeFileSync(code, blobAt(repo, pin.commit, MATCHER_PATH), { mode: 0o600 });
    const matcher = await import(pathToFileURL(code).href);
    const key = loadKey(matcher, env, cwd);
    let table, exceptions;
    try {
      table = matcher.parseHashFile(blobAt(repo, listCommit, LIST_PATH), key);
    } catch (e) {
      if (e instanceof CheckError) throw e;
      throw new CheckError("the private list doesn't match the key, or is malformed");
    }
    try {
      exceptions = matcher.parseExceptions(readFileSync(EXCEPTIONS_FILE, "utf8"));
    } catch {
      throw new CheckError("exceptions.json is missing or malformed");
    }
    const ctx = {
      matcher,
      key,
      table: { key, hashes: table.hashes, maxWords: table.maxWords, cache: new Map() },
      exceptions,
      phraseHashes: new Map(matcher.PHRASE_RULES.map((r) => [r.id, matcher.phraseHash(key, r.id)])),
      versions: `matcher ${pin.commit.slice(0, 8)}, list ${listCommit.slice(0, 8)}, ${matcher.PHRASE_RULES.length} wording rules`,
    };
    masker = (text) => maskText(ctx, text);
    return ctx;
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

// ---------------------------------------------------------------------------------------------- matching

/**
 * Name hits in one reading, the site's way: whole words, then glued words split (new spans only). With `embedded`
 * (free text: commit messages, PR and release text, tags, the text mode), also names glued inside one word, as the
 * site reads a social post or a draft.
 */
function nameHits(ctx, reading, { embedded = false } = {}) {
  const { tokenize, findHits } = ctx.matcher;
  const plainTokens = tokenize(reading);
  const plainHits = findHits(plainTokens, ctx.table);
  const judged = plainHits.map((h) => ({ hash: h.hash, s: plainTokens[h.index].start, e: plainTokens[h.index + h.n - 1].end }));
  const subTokens = tokenize(reading, { subwords: true });
  const subHits = (subTokens.length === plainTokens.length ? [] : findHits(subTokens, ctx.table)).filter((h) => {
    const [s, e] = [subTokens[h.index].start, subTokens[h.index + h.n - 1].end];
    return !judged.some((j) => j.hash === h.hash && j.s <= s && e <= j.e);
  });
  return [
    ...plainHits.map((hit) => ({ hit, tokens: plainTokens })),
    ...subHits.map((hit) => ({ hit, tokens: subTokens })),
    ...(embedded ? ctx.matcher.findEmbedded(plainTokens, ctx.table).map((hit) => ({ hit, tokens: plainTokens })) : []),
  ];
}

/** Wording-rule hits in one reading (whole words only), each with its keyed rule id for exceptions. */
function phraseHits(ctx, reading) {
  const tokens = ctx.matcher.tokenize(reading);
  return ctx.matcher.findPhraseHits(tokens, reading).map((p) => ({ hit: { ...p, hash: ctx.phraseHashes.get(p.rule.id) }, tokens }));
}

/**
 * The text with every listed word replaced by [listed]. When a listed word is still found in a decoded or
 * tags-blanked reading of the result (an escaped or split name), the whole text is withheld instead.
 */
function maskText(ctx, text) {
  const masked = maskSpans(ctx, text);
  const leftover = readingsOf(ctx, masked).some((r) => nameHits(ctx, r, { embedded: true }).length > 0);
  return leftover ? "[withheld: it holds a listed word]" : masked;
}

function maskSpans(ctx, text) {
  const spans = nameHits(ctx, text, { embedded: true })
    .map(({ hit, tokens }) => [tokens[hit.index].start, tokens[hit.index + hit.n - 1].end])
    .sort((a, b) => a[0] - b[0]);
  let out = "";
  let at = 0;
  for (const [s, e] of spans) {
    if (e <= at) continue;
    out += `${text.slice(at, Math.max(s, at))}[listed]`;
    at = e;
  }
  return out + text.slice(at);
}

const readingsOf = (ctx, text) => {
  const decoded = ctx.matcher.decodeEscapes(text);
  return decoded.includes("<") ? [decoded, ctx.matcher.withoutTags(decoded)] : [decoded];
};

/**
 * Checks one text. `file` (a repository path) lets a founder-approved exception apply; a text with no file is free
 * text and is also read for names glued inside a word. Labels are masked on output.
 */
function check(ctx, state, label, text, file = null) {
  state.texts++;
  const reported = new Set();
  for (const reading of readingsOf(ctx, text)) {
    for (const { hit, tokens } of [...nameHits(ctx, reading, { embedded: file === null }), ...phraseHits(ctx, reading)]) {
      const exception = file ? ctx.matcher.allowingException(tokens, hit, ctx.exceptions, ctx.key, file) : undefined;
      if (exception) {
        state.usedExceptions.add(exception.id);
        continue;
      }
      const { line, col } = tokens[hit.index];
      // A word listed under two kinds is one problem: two lines at one place would say it is listed twice.
      const id = `${line}:${col}:${hit.rule ? hit.rule.id : "name"}`;
      if (reported.has(id)) continue;
      reported.add(id);
      state.problems++;
      say(`${label}:${line}:${col}  ${hit.rule ? `${hit.rule.advice} (rule ${hit.rule.id})` : NAME_ADVICE}`);
    }
  }
}

/** Decodes a file's bytes as text, or stops: words the check can't read are never a pass. */
function textOf(file, bytes) {
  if (bytes.length > MAX_FILE_BYTES) throw new CheckError(`${file}: over ${MAX_FILE_BYTES >> 20} MB; the check doesn't read files that big, so it can't pass it`);
  const ext = path.posix.extname(file).toLowerCase();
  if (UNREADABLE.has(ext)) throw new CheckError(`${file}: the check can't read "${ext}" files, so it can't pass them (publish text instead)`);
  if (bytes.includes(0)) throw new CheckError(`${file}: a binary file; the check can't read it, so it can't pass it`);
  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    throw new CheckError(`${file}: not UTF-8 text; the check can't read it, so it can't pass it`);
  }
  if (text.startsWith(LFS_POINTER)) throw new CheckError(`${file}: a Git LFS pointer; the check can't read the stored file, so it can't pass it`);
  if (path.posix.basename(file) === ".gitattributes" && /\bfilter=lfs\b/.test(text)) {
    throw new CheckError(`${file}: Git LFS is configured; the check can't read LFS files, so it can't pass them`);
  }
  return text;
}

// ---------------------------------------------------------------------------------------------- what gets checked

const newState = () => ({ problems: 0, texts: 0, usedExceptions: new Set(), trees: new Set(), commits: new Set(), blobs: new Set() });

/** Every file at `rev`: its path, and its text (a link: its target). Submodules can't be checked. */
function checkTree(ctx, state, cwd, rev) {
  const tree = git(["rev-parse", `${rev}^{tree}`], { cwd, what: "rev-parse (tree)" }).trim();
  if (state.trees.has(tree)) return;
  state.trees.add(tree);
  const entries = nulFields(git(["ls-tree", "-r", "-z", "--full-tree", tree], { cwd, what: "ls-tree" })).map(parseTreeEntry);
  const blobs = readBlobs(cwd, entries.map((e) => e.oid));
  for (const { mode, oid, file } of entries) checkFile(ctx, state, file, mode, oid, blobs.get(oid), file);
}

function parseTreeEntry(field) {
  const tab = field.indexOf("\t");
  const [mode, type, oid] = field.slice(0, tab).split(" ");
  if (type === "commit" || mode === "160000") throw new CheckError(`${field.slice(tab + 1)}: a submodule; the check can't read it, so it can't pass it`);
  if (type !== "blob" || !OID.test(oid)) throw new CheckError("git ls-tree returned an entry the check doesn't know");
  return { mode, oid, file: field.slice(tab + 1) };
}

function checkFile(ctx, state, file, mode, oid, bytes, label) {
  // git prints a path that isn't UTF-8 with replacement characters, which would hide the bytes from the check.
  if (file.includes("\uFFFD")) throw new CheckError("a file path isn't UTF-8; the check can't read it, so it can't pass it");
  check(ctx, state, `${label} (file name)`, file);
  if (state.blobs.has(`${file}\0${oid}`)) return;
  state.blobs.add(`${file}\0${oid}`);
  if (mode === "120000") {
    check(ctx, state, `${label} (link target)`, bytes.toString("utf8"));
    return;
  }
  check(ctx, state, label, textOf(file, bytes), file);
}

/** One commit: its message, its author and committer, and every file it changes (against each parent). */
function checkCommit(ctx, state, cwd, oid) {
  if (state.commits.has(oid)) return;
  state.commits.add(oid);
  const short = oid.slice(0, 12);
  const raw = git(["cat-file", "commit", oid], { cwd, what: "cat-file (commit)" });
  const split = raw.indexOf("\n\n");
  const headers = (split === -1 ? raw : raw.slice(0, split)).split("\n");
  refuseEncoding(headers, `commit ${short}`, raw);
  for (const h of headers) {
    const m = /^(author|committer) (.*) \d+ [+-]\d{4}$/.exec(h);
    if (m) check(ctx, state, `commit ${short} ${m[1]}`, m[2]);
    // A merged signed tag's message travels in the merge commit.
    if (h.startsWith("mergetag ")) check(ctx, state, `commit ${short} merged tag`, headers.filter((x) => x.startsWith(" ") || x.startsWith("mergetag ")).join("\n"));
  }
  check(ctx, state, `commit ${short} message`, split === -1 ? "" : raw.slice(split + 2));
  const fields = nulFields(git(["diff-tree", "-r", "-m", "--root", "-z", "--no-renames", "--no-ext-diff", "--no-textconv", "--no-commit-id", "--raw", oid], { cwd, what: "diff-tree" }));
  const changed = [];
  for (let i = 0; i < fields.length; i += 2) {
    const [, newMode, , newOid] = fields[i].slice(1).split(" ");
    const file = fields[i + 1];
    if (file === undefined) throw new CheckError("git diff-tree returned a truncated list");
    if (ZERO.test(newOid)) continue; // deleted here
    if (newMode === "160000") throw new CheckError(`${file}: a submodule; the check can't read it, so it can't pass it`);
    changed.push({ mode: newMode, oid: newOid, file });
  }
  const blobs = readBlobs(cwd, changed.map((c) => c.oid));
  for (const { mode, oid: b, file } of changed) checkFile(ctx, state, file, mode, b, blobs.get(b), `${file} @ ${short}`);
}

/** A commit or tag in another encoding would be read as replacement characters; it can't pass. */
function refuseEncoding(headers, what, raw) {
  const enc = headers.find((h) => h.startsWith("encoding "))?.slice(9).trim().toLowerCase();
  if ((enc && enc !== "utf-8" && enc !== "utf8") || raw.includes("\uFFFD")) {
    throw new CheckError(`${what} isn't UTF-8 text; the check can't read it, so it can't pass it`);
  }
}

/** An annotated tag: its message and tagger. Returns the object it points at (maybe another tag). */
function checkTagObject(ctx, state, cwd, oid) {
  const raw = git(["cat-file", "tag", oid], { cwd, what: "cat-file (tag)" });
  const split = raw.indexOf("\n\n");
  const headers = (split === -1 ? raw : raw.slice(0, split)).split("\n");
  refuseEncoding(headers, "a tag", raw);
  const name = headers.find((h) => h.startsWith("tag "))?.slice(4) ?? "";
  for (const h of headers) {
    const m = /^tagger (.*) \d+ [+-]\d{4}$/.exec(h);
    if (m) check(ctx, state, "tag tagger", m[1]);
  }
  check(ctx, state, "tag name", name);
  check(ctx, state, "tag message", split === -1 ? "" : raw.slice(split + 2));
  const target = headers.find((h) => h.startsWith("object "))?.slice(7) ?? "";
  if (!OID.test(target)) throw new CheckError("a tag names no object");
  return target;
}

/** Follows tags one at a time (each one read) to the commit at the end. */
function peelTags(ctx, state, cwd, rev) {
  for (let depth = 0; depth <= 10; depth++) {
    const type = git(["cat-file", "-t", rev], { cwd, what: "cat-file (type)" }).trim();
    if (type === "commit") return rev;
    if (type !== "tag") throw new CheckError(`a ref points at a ${type}; only commits and tags can be checked`);
    rev = checkTagObject(ctx, state, cwd, rev);
  }
  throw new CheckError("a chain of more than 10 tags can't be checked");
}

/**
 * What `tip` publishes beyond what is already published: every commit not reachable from `known`, every file those
 * commits change, and the whole tree at the tip (so a newly listed word in an old file is still caught).
 * Annotated tags on the way to the tip are read too. A missing object stops the check; it never narrows it.
 */
function checkPublish(ctx, state, cwd, tip, known) {
  const rev = peelTags(ctx, state, cwd, git(["rev-parse", tip], { cwd, what: "rev-parse (tip)" }).trim());
  const commits = git(["rev-list", rev, "--not", ...known, "--"], { cwd, what: "rev-list" }).split("\n").filter(Boolean);
  for (const c of commits) checkCommit(ctx, state, cwd, c);
  checkTree(ctx, state, cwd, rev);
}

/** Every exception must still allow something when the whole tree was read, or it is stale. */
function staleExceptions(ctx, state) {
  ctx.exceptions.forEach((e, i) => {
    if (state.usedExceptions.has(e.id)) return;
    state.problems++;
    say(`exceptions.json: exception #${i + 1} (added ${e.added}) matched nothing; remove it`);
  });
}

// ---------------------------------------------------------------------------------------------- modes

function readStdin() {
  try {
    return readFileSync(0, "utf8");
  } catch {
    return "";
  }
}

/** git's pre-push: "<local ref> <local oid> <remote ref> <remote oid>" per line on stdin. */
function prePush(ctx, state, cwd, remote, stdin) {
  if (!remote) throw new CheckError("pre-push needs the remote name (git passes it)");
  const refs = stdin.split("\n").filter((l) => l.trim());
  // git runs the hook even when there is nothing to push ("Everything up-to-date"): nothing is published.
  if (refs.length === 0) return;
  // Commits on the remote's last-fetched refs are already published (and were checked when they were pushed).
  const known = [`--remotes=${remote}`];
  for (const line of refs) {
    const [localRef, localOid, remoteRef, remoteOid, extra] = line.trim().split(" ");
    if (!OID.test(localOid ?? "") || !OID.test(remoteOid ?? "") || !remoteRef || extra !== undefined) {
      throw new CheckError("pre-push got a line it doesn't understand");
    }
    if (ZERO.test(localOid)) continue; // a delete publishes nothing new
    check(ctx, state, "pushed ref name", remoteRef);
    if (localRef !== remoteRef) check(ctx, state, "local ref name", localRef);
    const exclude = !ZERO.test(remoteOid) && exists(cwd, remoteOid) ? [remoteOid, ...known] : known;
    checkPublish(ctx, state, cwd, localOid, exclude);
  }
}

/** Fetches the exact current state of origin into refs/scan/* (never stale tracking refs). */
function fetchOrigin(cwd, extra = []) {
  git(["fetch", "-q", "--no-tags", "--prune", "origin", "+refs/heads/*:refs/scan/heads/*", "+refs/tags/*:refs/scan/tags/*", ...extra], { cwd, what: "fetch (origin)" });
}

/** The commit a fetched default branch points at, or nothing when the repository has none yet. */
const branchRef = (name) => `refs/scan/heads/${name}`;

function github(ctx, state, cwd, env) {
  const name = env.GITHUB_EVENT_NAME;
  let event = {};
  try {
    event = JSON.parse(readFileSync(env.GITHUB_EVENT_PATH ?? "", "utf8"));
  } catch {
    throw new CheckError("GITHUB_EVENT_PATH is missing or not JSON");
  }
  if (git(["rev-parse", "--is-shallow-repository"], { cwd, what: "rev-parse (shallow)" }).trim() !== "false") {
    throw new CheckError("the checkout is shallow, so history can't be read (use fetch-depth: 0)");
  }
  // The text of PRs and releases is read from the event file, never from step environment variables (the runner can
  // print those in its own log before this check runs).
  if (name === "push") {
    if (event.deleted) return;
    fetchOrigin(cwd);
    const ref = String(event.ref ?? "");
    if (!/^refs\/(heads|tags)\//.test(ref)) throw new CheckError("the push event names no branch or tag");
    const mine = ref.replace(/^refs\//, "refs/scan/");
    check(ctx, state, "pushed ref name", ref);
    const at = git(["rev-parse", mine], { cwd, what: "rev-parse (pushed ref)" }).trim();
    if (!OID.test(event.after ?? "") || at !== event.after) throw new CheckError("the ref moved while it was being checked; re-run the check");
    // What this push publishes: everything after the ref's previous commit. A new ref: everything not on the default
    // branch (whose own pushes check what they publish). Other refs are never trusted to have been checked: two refs
    // pushed together would each skip the other's commits.
    const main = branchRef(String(event.repository?.default_branch ?? "main"));
    let known = [];
    if (event.before && !ZERO.test(event.before)) {
      if (!exists(cwd, event.before)) throw new CheckError("the ref's previous commit is gone (a force push); run the history check");
      known = [event.before];
    } else if (mine !== main && exists(cwd, main)) known = [main];
    checkPublish(ctx, state, cwd, mine, known);
    return;
  }
  if (name === "pull_request") {
    // A fork's PR gets no secrets, so the key is missing and the run already stopped with exit 2: a maintainer runs
    // the check on it locally. Running it with the secrets for anyone (pull_request_target) would let an outsider
    // learn which words are listed from pass and fail.
    const pr = event.pull_request ?? {};
    if (!Number.isInteger(event.number) || !OID.test(pr.head?.sha ?? "")) throw new CheckError("the PR event has no number or head");
    // The PR head is fetched as data: the check reads its objects, it doesn't run anything from it.
    fetchOrigin(cwd, [`+refs/pull/${event.number}/head:refs/scan/pr`]);
    check(ctx, state, "PR title", String(pr.title ?? ""));
    check(ctx, state, "PR description", String(pr.body ?? ""));
    check(ctx, state, "PR branch name", String(pr.head?.ref ?? ""));
    const head = git(["rev-parse", "refs/scan/pr"], { cwd, what: "rev-parse (PR head)" }).trim();
    if (pr.head.sha !== head) throw new CheckError("the PR moved while it was being checked; the newer run checks it");
    const base = branchRef(String(pr.base?.ref ?? ""));
    checkPublish(ctx, state, cwd, head, exists(cwd, base) ? [base] : []);
    return;
  }
  if (name === "release") {
    const rel = event.release ?? {};
    check(ctx, state, "release name", String(rel.name ?? ""));
    check(ctx, state, "release notes", String(rel.body ?? ""));
    check(ctx, state, "release tag name", String(rel.tag_name ?? ""));
    // Asset files are built from the checked tree (git archive); their names are text of their own.
    for (const a of rel.assets ?? []) check(ctx, state, "release asset name", String(a?.name ?? ""));
    return;
  }
  if (name === "schedule" || name === "workflow_dispatch") {
    fetchOrigin(cwd);
    if (event.inputs?.history === true || event.inputs?.history === "true") return history(ctx, state, cwd, "refs/scan");
    checkTree(ctx, state, cwd, branchRef(String(event.repository?.default_branch ?? "main")));
    staleExceptions(ctx, state);
    return;
  }
  throw new CheckError(`the check doesn't handle the "${name}" event`);
}

/** Every commit, tag and file reachable from any ref under `prefix`. */
function history(ctx, state, cwd, prefix = "refs") {
  const refs = nulFields(git(["for-each-ref", "--format=%(refname)%00%(objectname)%00%(objecttype)%00", prefix], { cwd, what: "for-each-ref" }).replace(/\n/g, ""));
  if (refs.length === 0) throw new CheckError("no refs to check");
  for (let i = 0; i + 2 < refs.length; i += 3) {
    check(ctx, state, "ref name", refs[i]);
    if (refs[i + 2] === "tag") peelTags(ctx, state, cwd, refs[i + 1]);
  }
  const commits = git(["rev-list", ...refs.filter((_, i) => i % 3 === 0), "--"], { cwd, what: "rev-list" }).split("\n").filter(Boolean);
  for (const c of commits) checkCommit(ctx, state, cwd, c);
}

async function bump(env) {
  const pin = readPin();
  const { dir, repo } = fetchSource(pin, env);
  try {
    const main = git(["rev-parse", "refs/remotes/origin/main"], { cwd: repo, what: "rev-parse (source main)" }).trim();
    writeFileSync(PIN_FILE, `${JSON.stringify({ ...pin, commit: main }, null, 2)}\n`);
    say(`pin.json now names ${main.slice(0, 12)}; commit it in its own change`);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

function exportMatcher(env, outDir) {
  if (!outDir) throw new CheckError("export-matcher needs a directory");
  const pin = readPin();
  const { dir, repo } = fetchSource(pin, env);
  try {
    writeFileSync(path.join(outDir, "client-names.mjs"), blobAt(repo, pin.commit, MATCHER_PATH), { mode: 0o600 });
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

// ---------------------------------------------------------------------------------------------- main

/** Runs the check and returns { exitCode, lines } without touching the process (the tests call it). */
export async function run(argv, { env = process.env, cwd = process.cwd(), stdin } = {}) {
  lines.length = 0;
  masker = null;
  try {
    const major = Number(process.versions.node.split(".")[0]);
    if (!(major >= MIN_NODE_MAJOR)) throw new CheckError(`node ${process.versions.node} is too old (need ${MIN_NODE_MAJOR}+)`);
    const [mode, ...rest] = argv;
    if (mode === "bump") return { exitCode: (await bump(env), 0), lines: [...lines] };
    if (mode === "export-matcher") return { exitCode: (exportMatcher(env, rest[0]), 0), lines: [...lines] };
    if (!["pre-push", "github", "tree", "history", "text"].includes(mode)) throw new CheckError("usage: scan.mjs pre-push|github|tree|history|text|bump|export-matcher (see the file's header)");
    const ctx = await loadPolicy(env, cwd);
    const state = newState();
    const input = () => stdin ?? readStdin();
    if (mode === "pre-push") prePush(ctx, state, cwd, rest[0], input());
    else if (mode === "github") github(ctx, state, cwd, env);
    else if (mode === "tree") {
      checkTree(ctx, state, cwd, rest[0] ?? "HEAD");
      staleExceptions(ctx, state);
    } else if (mode === "history") history(ctx, state, cwd);
    else {
      const li = rest.indexOf("--label");
      const label = li === -1 ? "" : rest[li + 1] ?? "";
      if (!label) throw new CheckError("text needs --label <label>");
      const text = input();
      if (!/[\p{L}\p{N}]/u.test(text)) throw new CheckError("text got nothing on stdin");
      check(ctx, state, label, text);
    }
    if (state.problems === 0) {
      say(`passed: nothing listed and no flagged wording in ${state.texts} texts (${ctx.versions})`);
      return { exitCode: 0, lines: [...lines] };
    }
    say(`FAILED: ${state.problems} problem(s) in ${state.texts} texts (${ctx.versions}). Rewrite each one before it is published.`);
    return { exitCode: 1, lines: [...lines] };
  } catch (e) {
    say(`could not run, so nothing passed: ${e instanceof CheckError ? e.message : `internal error (${e?.name ?? "unknown"})`}`);
    return { exitCode: 2, lines: [...lines] };
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const { exitCode, lines: out } = await run(process.argv.slice(2));
  for (const l of out) (exitCode === 0 ? console.log : console.error)(l);
  process.exitCode = exitCode;
}
