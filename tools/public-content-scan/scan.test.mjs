// Tests for scan.mjs, against a synthetic source repository: the real pinned matcher with a test list and a test key.
//
//   PUBLIC_SCAN_MATCHER=<dir>/client-names.mjs node --test tools/public-content-scan/scan.test.mjs
//
// CI writes the matcher with `scan.mjs export-matcher <dir>`. Without it the tests fail; they never skip.
// The test words below are made up. Flagged wording is assembled at run time, so this published file doesn't carry it.

import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { randomBytes } from "node:crypto";
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { after, before, describe, test } from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const MATCHER = process.env.PUBLIC_SCAN_MATCHER;
const LISTED = "Zorblax Quantics"; // one listed kind
const LISTED_TOO = "Vexmoor"; // the other kind
const WORDING = [..."seman tneilc fo debburcs"].reverse().join(""); // reversed, so this file carries no flagged wording
const KEY = randomBytes(32).toString("hex");
const GIT_ENV = {
  GIT_CONFIG_GLOBAL: "/dev/null",
  GIT_CONFIG_NOSYSTEM: "1",
  GIT_AUTHOR_NAME: "Test",
  GIT_AUTHOR_EMAIL: "test@example.com",
  GIT_COMMITTER_NAME: "Test",
  GIT_COMMITTER_EMAIL: "test@example.com",
};

let root, source, remote, work, run, baseEnv;

const git = (cwd, ...args) => execFileSync("git", args, { cwd, encoding: "utf8", env: { ...process.env, ...GIT_ENV } }).trim();
const write = (dir, file, text) => {
  mkdirSync(path.dirname(path.join(dir, file)), { recursive: true });
  writeFileSync(path.join(dir, file), text);
};
const commit = (dir, msg, env = {}) => {
  git(dir, "add", "-A");
  execFileSync("git", ["commit", "-q", "--allow-empty", "-m", msg], { cwd: dir, env: { ...process.env, ...GIT_ENV, ...env } });
  return git(dir, "rev-parse", "HEAD");
};
const scan = (argv, opts = {}) => run(argv, { cwd: work, env: { ...baseEnv, ...opts.env }, stdin: opts.stdin });
const ZERO = "0".repeat(40);
/** The output may name a place and a rule, never a listed word or which kind of word it is. */
function assertQuiet(lines) {
  const all = lines.join("\n");
  for (const word of ["Zorblax", "Quantics", "Vexmoor", "employer", "client"]) assert.ok(!all.includes(word), `output says "${word}"`);
  for (const l of lines) assert.match(l, /^public-content: [^\n\r]*$/);
}

before(async () => {
  assert.ok(MATCHER, "set PUBLIC_SCAN_MATCHER to the pinned matcher (scan.mjs export-matcher <dir>)");
  root = mkdtempSync(path.join(tmpdir(), "public-scan-test-"));
  const m = await import(pathToFileURL(MATCHER).href);
  // The source: the matcher and a list built with the test key, served over file:// with partial clone allowed.
  source = path.join(root, "source");
  mkdirSync(source);
  git(source, "init", "-q", "-b", "main");
  git(source, "config", "uploadpack.allowFilter", "true");
  git(source, "config", "uploadpack.allowAnySHA1InWant", "true");
  write(source, "scripts/privacy/client-names.mjs", readFileSync(MATCHER, "utf8"));
  const list = m.buildHashFile([LISTED, { name: LISTED_TOO, kind: m.KINDS[1] }], Buffer.from(KEY, "hex"));
  write(source, "scripts/privacy/client-names.hmac", list.text);
  const pinned = commit(source, "matcher");
  // A copy of the driver whose pin names that commit.
  const driver = path.join(root, "driver");
  mkdirSync(driver);
  copyFileSync(path.join(HERE, "scan.mjs"), path.join(driver, "scan.mjs"));
  writeFileSync(path.join(driver, "exceptions.json"), "[]\n");
  writeFileSync(path.join(driver, "pin.json"), JSON.stringify({ source: "test/source", commit: pinned }));
  ({ run } = await import(pathToFileURL(path.join(driver, "scan.mjs")).href));
  baseEnv = { ...process.env, ...GIT_ENV, PUBLIC_SCAN_KEY: KEY, PUBLIC_SCAN_SOURCE_URL: `file://${source}` };
  delete baseEnv.CI;
  // The published repository and a clone that pushes to it.
  remote = path.join(root, "remote.git");
  git(root, "init", "-q", "--bare", "-b", "main", remote);
  work = path.join(root, "work");
  mkdirSync(work);
  git(work, "init", "-q", "-b", "main");
  git(work, "remote", "add", "origin", remote);
  write(work, "README.md", "# Skills\n\nPlain text about keyword research.\n");
  write(work, "skills/a/SKILL.md", "---\nname: a\n---\nSteps.\n");
  write(work, "tools/x.py", "print('hello')\n");
  write(work, "LICENSE", "Apache License\n");
  commit(work, "first");
  git(work, "push", "-q", "origin", "main");
});

after(() => rmSync(root, { recursive: true, force: true }));

/** Pre-push stdin for pushing HEAD to a new branch. */
const newBranch = (name) => `refs/heads/${name} ${git(work, "rev-parse", "HEAD")} refs/heads/${name} ${ZERO}\n`;

describe("tree", () => {
  test("a clean tree passes, every file type included", async () => {
    const { exitCode, lines } = await scan(["tree", "HEAD"]);
    assert.equal(exitCode, 0, lines.join("\n"));
    assert.match(lines.at(-1), /passed/);
  });

  test("a listed word in a file fails, and the output names neither the word nor its kind", async () => {
    write(work, "skills/a/notes.md", `We tried ${LISTED} and ${LISTED_TOO.toUpperCase()} here.\n`);
    commit(work, "notes");
    const { exitCode, lines } = await scan(["tree", "HEAD"]);
    assert.equal(exitCode, 1);
    assertQuiet(lines);
    assert.ok(lines.some((l) => l.includes("skills/a/notes.md:1:")), lines.join("\n"));
    assert.equal(lines.filter((l) => l.includes("a listed word")).length, 2);
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });

  test("a listed word in a file name is masked in the output", async () => {
    write(work, `docs/${LISTED.replace(" ", "-")}.md`, "plain\n");
    commit(work, "named");
    const { exitCode, lines } = await scan(["tree", "HEAD"]);
    assert.equal(exitCode, 1);
    assertQuiet(lines);
    assert.ok(lines.some((l) => l.includes("docs/[listed].md (file name)")), lines.join("\n"));
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });

  for (const [what, file, bytes] of [
    ["a binary file", "data.bin", Buffer.from([1, 0, 2])],
    ["an image", "pic.png", Buffer.from("not really")],
    ["invalid UTF-8", "bad.txt", Buffer.from([0xc3, 0x28])],
    ["a Git LFS pointer", "big.csv", Buffer.from("version https://git-lfs.github.com/spec/v1\noid sha256:00\nsize 1\n")],
  ]) {
    test(`${what} stops the check (exit 2), never passes`, async () => {
      write(work, file, bytes);
      commit(work, what);
      const { exitCode, lines } = await scan(["tree", "HEAD"]);
      assert.equal(exitCode, 2, lines.join("\n"));
      git(work, "reset", "-q", "--hard", "HEAD~1");
    });
  }

  test("control characters and workflow commands in a path can't reach the log as commands", async () => {
    write(work, `odd\n::error::x ##[add-mask]${LISTED_TOO}.md`, "plain\n");
    commit(work, "odd");
    const { exitCode, lines } = await scan(["tree", "HEAD"]);
    assert.equal(exitCode, 1);
    assertQuiet(lines);
    for (const l of lines) assert.ok(!l.includes("::") && !l.includes("##["), l);
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });

  test("a listed word written with escapes in a file name is withheld from the output, not printed encoded", async () => {
    const encoded = [...LISTED_TOO].map((c) => `&#${c.charCodeAt(0)};`).join("");
    write(work, `docs/${encoded}.md`, "plain\n");
    commit(work, "encoded");
    const { exitCode, lines } = await scan(["tree", "HEAD"]);
    assert.equal(exitCode, 1, lines.join("\n"));
    assert.ok(!lines.join("\n").includes(encoded), lines.join("\n"));
    assert.ok(lines.some((l) => l.includes("[withheld")), lines.join("\n"));
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });
});

describe("pre-push", () => {
  test("flagged wording in a commit message is refused", async () => {
    commit(work, `Cleanup: ${WORDING}`);
    const { exitCode, lines } = await scan(["pre-push", "origin"], { stdin: newBranch("wording") });
    assert.equal(exitCode, 1, lines.join("\n"));
    assert.ok(lines.some((l) => /commit [0-9a-f]{12} message:1:\d+ .*\(rule /.test(l)), lines.join("\n"));
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });

  test("a word added in one commit and removed in the next is still refused", async () => {
    write(work, "skills/a/SKILL.md", `---\nname: a\n---\nSteps for ${LISTED}.\n`);
    commit(work, "add");
    write(work, "skills/a/SKILL.md", "---\nname: a\n---\nSteps.\n");
    commit(work, "remove");
    const { exitCode, lines } = await scan(["pre-push", "origin"], { stdin: newBranch("added-removed") });
    assert.equal(exitCode, 1, lines.join("\n"));
    assertQuiet(lines);
    assert.ok(lines.some((l) => / @ [0-9a-f]{12}:4:/.test(l)), lines.join("\n"));
    git(work, "reset", "-q", "--hard", "HEAD~2");
  });

  test("a listed word in the author is refused", async () => {
    commit(work, "authored", { GIT_AUTHOR_NAME: `Someone at ${LISTED_TOO}` });
    const { exitCode, lines } = await scan(["pre-push", "origin"], { stdin: newBranch("author") });
    assert.equal(exitCode, 1);
    assert.ok(lines.some((l) => / author:1:/.test(l)), lines.join("\n"));
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });

  test("an annotated tag's message is read", async () => {
    git(work, "tag", "-a", "v9", "-m", `Release for ${LISTED}`);
    const tag = git(work, "rev-parse", "v9");
    const { exitCode, lines } = await scan(["pre-push", "origin"], { stdin: `refs/tags/v9 ${tag} refs/tags/v9 ${ZERO}\n` });
    assert.equal(exitCode, 1);
    assert.ok(lines.some((l) => l.includes("tag message:1:")), lines.join("\n"));
    git(work, "tag", "-d", "v9");
  });

  test("a listed word in the branch name is refused", async () => {
    const { exitCode, lines } = await scan(["pre-push", "origin"], { stdin: newBranch(`fix-${LISTED_TOO.toLowerCase()}`) });
    assert.equal(exitCode, 1);
    assertQuiet(lines);
  });

  test("a clean push passes, and commits already on the remote aren't read again", async () => {
    write(work, "skills/b/SKILL.md", "---\nname: b\n---\nMore steps.\n");
    commit(work, "b");
    const { exitCode, lines } = await scan(["pre-push", "origin"], { stdin: newBranch("clean") });
    assert.equal(exitCode, 0, lines.join("\n"));
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });

  test("a delete or an up-to-date push publishes nothing; a line it can't parse stops the check", async () => {
    const del = `(delete) ${ZERO} refs/heads/old ${git(work, "rev-parse", "HEAD")}\n`;
    assert.equal((await scan(["pre-push", "origin"], { stdin: del })).exitCode, 0);
    assert.equal((await scan(["pre-push", "origin"], { stdin: "" })).exitCode, 0);
    assert.equal((await scan(["pre-push", "origin"], { stdin: "garbage\n" })).exitCode, 2);
  });

  test("a listed word glued inside one word of a commit message is refused (free text)", async () => {
    commit(work, `Notes for #team${LISTED.replace(" ", "")}launch`);
    const { exitCode, lines } = await scan(["pre-push", "origin"], { stdin: newBranch("glued") });
    assert.equal(exitCode, 1, lines.join("\n"));
    assertQuiet(lines);
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });

  test("every tag in a chain of tags is read, not only the outer one", async () => {
    git(work, "tag", "-a", "inner", "-m", `Inner note for ${LISTED}`);
    git(work, "tag", "-a", "outer", "-m", "Plain outer note", "inner");
    const tag = git(work, "rev-parse", "outer");
    const { exitCode, lines } = await scan(["pre-push", "origin"], { stdin: `refs/tags/outer ${tag} refs/tags/outer ${ZERO}\n` });
    assert.equal(exitCode, 1, lines.join("\n"));
    git(work, "tag", "-d", "outer", "inner");
  });

  test("a commit in another encoding stops the check", async () => {
    execFileSync("git", ["-c", "i18n.commitEncoding=ISO-8859-1", "commit", "-q", "--allow-empty", "-m", "Caf\u00e9"], { cwd: work, env: { ...process.env, ...GIT_ENV } });
    const { exitCode } = await scan(["pre-push", "origin"], { stdin: newBranch("latin1") });
    assert.equal(exitCode, 2);
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });
});

describe("fails closed", () => {
  test("no key, or an empty key (a fork PR's secrets), is exit 2", async () => {
    const env = { ...baseEnv };
    delete env.PUBLIC_SCAN_KEY;
    assert.equal((await run(["tree", "HEAD"], { cwd: work, env })).exitCode, 2);
    assert.equal((await scan(["tree", "HEAD"], { env: { PUBLIC_SCAN_KEY: "" } })).exitCode, 2);
  });

  test("a key the list wasn't built with is exit 2", async () => {
    assert.equal((await scan(["tree", "HEAD"], { env: { PUBLIC_SCAN_KEY: randomBytes(32).toString("hex") } })).exitCode, 2);
  });

  test("an unreachable source is exit 2", async () => {
    assert.equal((await scan(["tree", "HEAD"], { env: { PUBLIC_SCAN_SOURCE_URL: `file://${root}/nowhere` } })).exitCode, 2);
  });

  test("a matcher changed on the source's main is exit 2 until the pin moves", async () => {
    write(source, "scripts/privacy/client-names.mjs", `${readFileSync(MATCHER, "utf8")}\n// changed\n`);
    commit(source, "matcher change");
    const { exitCode, lines } = await scan(["tree", "HEAD"]);
    assert.equal(exitCode, 2);
    assert.match(lines.join("\n"), /bump/);
    git(source, "reset", "-q", "--hard", "HEAD~1");
  });

  test("a word added to the list on the source's main is enforced without a pin change", async () => {
    const m = await import(pathToFileURL(MATCHER).href);
    const list = m.buildHashFile([LISTED, { name: LISTED_TOO, kind: m.KINDS[1] }, "Keyword"], Buffer.from(KEY, "hex"));
    write(source, "scripts/privacy/client-names.hmac", list.text);
    commit(source, "list change");
    assert.equal((await scan(["tree", "HEAD"])).exitCode, 1);
    git(source, "reset", "-q", "--hard", "HEAD~1");
  });

  test("--show-style output is never produced; unknown modes are exit 2", async () => {
    assert.equal((await scan(["--show"])).exitCode, 2);
  });
});

describe("github events", () => {
  const event = (name, body) => {
    const file = path.join(root, `${name}.json`);
    writeFileSync(file, JSON.stringify(body));
    return { GITHUB_EVENT_NAME: name, GITHUB_EVENT_PATH: file };
  };

  test("a push to a new branch reads what it adds beyond the default branch", async () => {
    write(work, "skills/c/SKILL.md", `Steps for ${LISTED}.\n`);
    const after = commit(work, "c");
    git(work, "push", "-q", "origin", "HEAD:refs/heads/feature");
    const env = event("push", { ref: "refs/heads/feature", before: ZERO, after, repository: { default_branch: "main" } });
    const { exitCode, lines } = await scan(["github"], { env });
    assert.equal(exitCode, 1, lines.join("\n"));
    assertQuiet(lines);
    git(work, "push", "-q", "origin", ":refs/heads/feature");
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });

  test("a PR's commits, files, title and description are read from git objects and the event file", async () => {
    write(work, "skills/d/SKILL.md", "Plain steps.\n");
    const head = commit(work, "d");
    git(work, "push", "-q", "origin", "HEAD:refs/pull/7/head");
    const pr = (title, body) => event("pull_request", { number: 7, pull_request: { title, body, head: { sha: head, ref: "d" }, base: { ref: "main" } } });
    assert.equal((await scan(["github"], { env: pr("Add d", "Plain") })).exitCode, 0);
    const { exitCode, lines } = await scan(["github"], { env: pr("Add d", `For ${LISTED}`) });
    assert.equal(exitCode, 1);
    assertQuiet(lines);
    assert.ok(lines.some((l) => l.includes("PR description:1:")), lines.join("\n"));
    const moved = event("pull_request", { number: 7, pull_request: { title: "t", body: "", head: { sha: "2".repeat(40), ref: "d" }, base: { ref: "main" } } });
    assert.equal((await scan(["github"], { env: moved })).exitCode, 2);
    git(remote, "update-ref", "-d", "refs/pull/7/head");
    git(work, "reset", "-q", "--hard", "HEAD~1");
  });

  test("a push whose ref moved since the event stops the check", async () => {
    const env = event("push", { ref: "refs/heads/main", before: ZERO, after: "1".repeat(40), repository: { default_branch: "main" } });
    assert.equal((await scan(["github"], { env })).exitCode, 2);
  });

  test("a release's notes are read from the event file", async () => {
    const env = event("release", { release: { name: "v2", body: `Thanks to ${LISTED_TOO}`, tag_name: "v2", assets: [] } });
    const { exitCode, lines } = await scan(["github"], { env });
    assert.equal(exitCode, 1);
    assertQuiet(lines);
  });

  test("pull_request_target is refused: the secrets must never check outsiders' text", async () => {
    const env = event("pull_request_target", { number: 1 });
    assert.equal((await scan(["github"], { env })).exitCode, 2);
  });
});
