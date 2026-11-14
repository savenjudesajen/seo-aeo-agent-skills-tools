# The reviewer round: a workbook comes back

Open this the moment a reviewer sends a workbook back, before a cell of it changes: what to read, what each kind of
comment means, where the answer is recorded, and what the content plan and the tracker need afterwards.

## 1. Read everything the reviewer did, then say what you found

Run `python3 data/review_round.py --returned <the returned file> --previous <the last workbook sent>`. It lists:

- **Every comment**, sorted by sheet and cell: the text of the cell it sits on, that row's page and prompt, the author,
  the time and every message of a thread. A thread can be one comment holding all its messages (a Google Sheets export
  writes the root after a line of `=` signs and each reply after a line of `-` signs), so count messages as well as cells.
  The order inside the file is not the order on the sheet.
- **Every cell edited without a comment, and every column added, dropped or moved.** Reviewers instruct by editing too:
  a value changed across a whole column, a column added, removed or reordered, a cell corrected without a note. None of
  these carries a comment, and an edit made on one sheet can leave the workbook disagreeing with itself. Carry every
  direct edit through every sheet that holds the same field (Prompt Map, Keyword Map, Page Summary, the delta and any
  tracker notes) before anything else is built.

When asked whether you can see the comments, answer yes with the count, and put the full list in the reply so the
reviewer can check it against what they left. Never answer from the first few.

## 2. What each comment means

Give every message one action before building. A message that fits none is a question for the reviewer. A comment
phrased as a question about what a page will be often carries its instruction in the next message of the same thread, so
read the whole thread before choosing the action.

| The reviewer writes | Action | What changes | What stays |
|---|---|---|---|
| new wording for the prompt | SWAP | the prompt becomes that wording, character for character | page, keywords, family; the gates rerun (the new wording is a simulated row like any other and needs its family and reason) |
| cut or change part of the wording | REWORD | the phrase goes and nothing else | keyword, page, answer type |
| the prompt belongs on another page | MOVE | the prompt text is unchanged and its keywords follow it (one keyword, one row) | a short-form twin left on the old page goes on the flags line for a yes |
| not ready to launch | HOLD | nothing loads; the tracker column, the Page Summary and the delta say HOLD | every row stays in the map and in every page total |
| take the page out | REMOVE | the page and its prompts leave the tracked set; its keywords stay on the Keyword Map as KEYWORD ONLY rows under a REMOVED page; nothing is written to the content plan or tracker | the keywords: demand does not disappear because a page was cut |
| change the page's URL slug | RENAME | the page key changes in one pass everywhere (Prompt Map, Keyword Map, Page Summary, delta, the content plan's slug cell, tracker notes); the delta says UPDATE SLUG | sibling pages sharing the word: their rows may be live and a draft built on the old slug needs regenerating, so they go on the flags line for a yes |

Two rules behind the table:
- **HOLD and REMOVE are two states.** A held page is a launch decision; a removed page is a scope decision. When a
  page cut in an earlier round comes back in a rebuild from source data, the builder forgot a decision. Keep the reviewer's decisions
  in one ledger the builder reads (a dict in the build script is enough), so a rebuild cannot resurrect a removed page.
- **A comment on one cell applies to that cell; the siblings it could reach go on the flags line for one yes.**
  Reviewer examples are patterns to generalize for wording quality, where a bad prompt is one instance of a shape. A
  page's state or slug is different: sibling pages that share the word may have live rows or drafts, so leave them as they
  are and ask in the reply. The default changes the first time the reviewer asks for a change to apply to every
  sibling; record that in the run notes so the next round starts from it.

## 3. Record the answer where the reviewer will look

- A `Reviewer decision (<date>)` column on the Prompt Map, filled on the row the comment lands on after the build (or on
  the page's rows when the page moved or went). Each cell quotes what was written and says what was done.
  `data/review_round.py` requires a cell for every message of every comment, so an unanswered comment fails the build. A
  page with no rows left carries its decision on its REMOVED rows.
- A computed `Change vs <previous> (<date>)` column (`gates.md` section 5).
- A `Launch status` on the Page Summary: LAUNCH, HOLD or REMOVED, with the reviewer and the date, and what it means for
  the tracker and the content plan.
- A column carrying the client's keywords verbatim has a header starting with `Keyword`: the market-spelling check skips
  only those columns, because a differently spelled keyword is a different string to an engine. A delta column that holds
  keyword text under any other header fails the hygiene gate on the other market's spelling; rename the header, never the
  keyword.

## 4. Rebuild without breaking the design the reviewer signed off

A workbook back from review is edited in place. A rebuild from your builder counts as in place only when the new file
carries every direct edit (`review_round.py --previous` lists them), keeps the reviewer's column order, and puts any new
column beside theirs, never inside them. Check both before building: the layout of the returned copy is theirs, and the
builder's layout gives way to it.

## 5. After the decisions: the content plan and the tracker

- Every row that changes goes in the delta with an action from the closed list in `gates.md` section 4. Route each page
  to the sheet or table of the content plan that holds its page type (service pages and blog pages are often planned in
  different tables).
- Before adding a row to the content plan, read every sheet for a row that already holds the page or its topic. A row
  from an earlier engagement is updated, not duplicated; when it is already approved or in production, change only its
  notes, query list and volume cells. When a later round keeps and folds a page an earlier delta flagged for removal, say
  in the new delta that the earlier flag is superseded.
- Pages with no plan framework yet (no template or brief format for that page type) wait, and the reply says so.
- **Ask for any new tracker container in the first reply of the round.** Creating a container changes a shared resource,
  and a request naming only a tag does not cover it: the tag can be created without asking, the container cannot. Ask
  once, with the reason (the container is the reporting grain, and reusing a similarly named one merges this work into the
  client's own set), then carry on while waiting. Meanwhile stage the launch prompts, checked against every live prompt:
  no exact duplicate, and near-twins already tracked flagged on their rows.
- Permanent deletes are the owner's click: tag the rows to retire, leave a filtered view with them selected, and say
  what is waiting. HOLD pages load nothing; REMOVED pages write nothing to the content plan or the tracker.

## 6. The reply

Answer the question asked first. Then list the comments and what was done to each, the content plan and tracker state,
and the decisions you made where a comment left room, each worded so a single word from the reviewer reverses it. Say what
the reviewer changed without a comment. Say what is waiting on someone else and what it needs from them.
