# Document patterns

How to shape content onto the blocks. The patterns hold in every theme. Voice and banned phrases come from the
client's own writing guidelines or style guide, if it has one, not from here; this file owns structure, not
words.

## The top of every document
1. **Running header and footer** come from `Doc(short_title=..., client=...)`. Short title: two to four words
   ("Redirect map sign-off", "Pricing page review").
2. **Title**: what the reader will do or get, one line of about 40 to 60 characters, sentence case, no full stop.
   "Approve the redirect map before launch", not "Redirect Map Document".
3. **Meta line**: kind, client, who prepared it, date written out ("3 March 2027"). The "prepared" part comes
   from the theme (`d.t.meta_by()`):
   - work delivered under your own team or agency name: "Prepared by <team>";
   - work delivered to an agency about the agency's client: "Prepared for <agency>";
   - in-house work: leave it out.
   Never a personal email address in the meta line.
4. **Lead**: the outcome or the request in the first sentence, then the one reason it matters to this reader,
   then the date it is needed by. Two or three sentences. It is the only paragraph with a stripe.

## Short action doc (1 to 3 pages)
For a document whose reader has work to do: approving a file, a change for their web team, a setting to switch,
a choice to make. The title and lead already carry the request, so the body is about getting it done. Pick the
sections that apply and keep this order:

| Section | Block | What goes in it |
|---|---|---|
| Context | `body`, one or two short paragraphs | What changed or is about to, and what it touches on the reader's side; leave out history they already know |
| Tasks | `table` (#, Task, Owner, Check), widths `[1, 9, 3, 4]` | One task per row, starting with a verb; the owner as a role, not a person's name; a quick check the owner can run once the task is finished |
| Decision (only when the reader must choose) | `facts` (Recommendation, Alternative, Trade-off, Decide by) | The option you advise and the runner-up as labelled rows, what each one costs or risks, and the date the choice is needed |
| If something blocks you | `bullets` | The blockers you can foresee, one line each in the form "blocker: what to do about it" |
| After you finish | `numbered` | The order of events once the reader is done: what they send back, what you do next, when they hear from you |

Keep subsections out of a short action doc; one page is the target and two the limit, unless the task table
itself runs long.

## Long recommendation doc (5 to 40 pages)
For an audit, a review or a strategy write-up.
- Title, meta ("Recommendations / <Client> / Prepared for/by ... / <date>"), and a lead with the verdict
  and the number of changes ("Two of the five pages already meet the standard; the other three need one change
  each").
- **1  Summary of changes** on page 1: one sentence of strengths, then a prioritised change table (#, Change,
  Why it matters, Effort) in 9pt (`sz=18`), then, if there is one, the target wireframe as Figure 1 on its own
  page.
- **One numbered section per area reviewed**, each starting on a new page (`new_page=True`) from section 2 on.
  Order them by reading flow or by priority, and say which in the lead.
- **Subsections with status chips** for each item under an area: "3.2  Pricing table" + Rework. Under each: the
  figure (screenshot or wireframe), then a fact table ("Today" / "Change" / "Why", or "What it is" / "Verdict",
  `label_w=0.22`).
- **Recommendation tables** carry a status column (`status_col`). Counts go in their own column as "n of N".
- **Appendices** are lettered (`appendix()`): method, the pages or data reviewed, raw counts; small type
  (`sz=16` to `17`) and `bold_first=True` for the name column.
- A `minor()` heading introduces a second table inside one section ("Nice to have later").
- Close with what happens next: owners, order, and what you need from the client (mark those blocks Later).

## Choosing blocks
- A fact with a name: fact table. A sequence: numbered table. Options compared: table with a header row.
  Prose only where a table cannot carry it, and short.
- No callout boxes, coloured paragraphs or hand-made headings outside the block set. If a document seems to need
  one, it needs a fact table, a subsection or a note.
- One section per reader question, in reading order. Labels in sentence case, no full stop.
- Keep numbers, names and repeated labels in variables or a data file in the build script, so the document is
  regenerated rather than hand-edited.

## Page flow
- Shrink a figure (`max_h`) before shrinking type.
- A page under a third full before the last page usually means a table's last rows or a small figure spilled
  over: let the next short section flow on that page instead of forcing `new_page`, or put `page_break()` before
  a subsection so its figure and fact table stay together.
- A long table repeats its header row on every page; rows never split.

## Client documents in a theme
Same sections, blocks and order in every theme. Write in the client's own nouns (their product names, their
category term, their spelling) and keep the rules the theme carries (`never_mention`). A client who sends their
own template file gets that file used instead (`adopt-a-client-template.md`).

## Filenames
`<Client>_<Document_Name>.docx` with underscores, e.g. `Halden_Redirect_Map_Signoff.docx`.
