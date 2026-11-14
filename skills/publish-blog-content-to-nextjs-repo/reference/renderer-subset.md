# Determining the renderer's subset, and converting to it

## Why this is the whole game

Marketing sites built on Next.js very often ship a hand-rolled Markdown-ish parser rather than a
library. It typically splits the body on blank lines and handles a handful of block forms. Anything
else renders as literal text in a paragraph, in production, on the client's site.

So: **read the renderer and write down its grammar before authoring a single line of content.**

## Reading the grammar off the code

Look for the function that receives the post body. Typical tells: `body.split('\n\n')`, a chain of
`startsWith(...)` checks, a regex for `**...**` or `[...](...)`, and a final `return <p>...</p>`
fallback. Write the grammar as a table, block forms first, then inline forms:

| Input (one block = text between blank lines) | Output |
|---|---|
| line starts `## ` | h2 |
| line starts `### ` | h3 |
| every non-empty line starts `- ` | ul |
| first line starts `\|` | table |
| anything else | p |

That table is an illustration, not a default; yours comes from the code. Variants worth checking for:

- a block that is a single bold-only line promoted to a heading (common, and the reason the .docx bold
  trap in SKILL.md matters);
- ordered lists supported or not;
- inline forms beyond `**bold**` and `[text](url)` (italics, inline code) supported or not;
- whether links starting `/` are rendered as internal links and absolute ones as external.

Write down what is missing too: typically no ordered lists, no blockquotes, no HTML, no images, no code
fences, no headings above h2 or below h3. Then set `SUPPORTED` and `LEAKS` in `data/verify_publish.py`
to exactly this grammar.

## Conversion rules

Write a converter; don't hand-edit. For each unsupported construct decide between converting down and
dropping, and **disclose every drop in the PR body**.

- **HTML tags**: with no HTML path, tags render as visible text. Strip them and re-express the content
  in a supported form.
- **Video / iframe embeds**: drop the element entirely. Never leave a bare URL where an embed was.
- **Ordered lists**: either render as `- **1.** ...` bullets, or offer a renderer patch as a separate
  PR. Don't ship `1. ` into a paragraph parser.
- **Blockquotes**: downgrade to a plain paragraph, preserving the text.
- **Tables**: pipe syntax only, with the first line starting `|`.
- **Internal links**: rewrite absolute links to the client's own site as root-relative paths so the
  renderer treats them as internal.
- **Headings outside the supported levels**: map H1 in the body to nothing (the page template owns the
  title) and H4+ to the lowest supported level, and check the counts afterwards.

## Template-literal safety

When the body lands inside a JS/TS template literal, the content must contain no backtick, no `${` and
no backslash. Assert this in the converter and again in the apply script. A single stray backtick
silently ends the literal and breaks the build in a way whose error message points somewhere else
entirely.

Also assert the file's backtick count stays even after the edit.

## Prove it before shipping

`data/verify_publish.py renderer` simulates the parser against your converted content and reports any
block that would fall through to a paragraph carrying literal Markdown. The ratio of supported blocks
must be 1.0. Not "looks right": measured. Keep its counts (`--json`) for the live comparison.
