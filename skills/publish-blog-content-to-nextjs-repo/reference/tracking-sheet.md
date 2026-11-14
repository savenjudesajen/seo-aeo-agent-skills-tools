# Updating the client's content tracking sheet

Shipping is not done when the page is live. It is done when the tracker says so. Most content
engagements run off a workbook whose Status column is how the client sees progress. If you leave it
stale, the client's view of the work is wrong.

## Rules

- **Only mark a row Live after the live-URL gate passes.** Not after merge, not after the deploy shows
  Ready. The page has to actually serve.
- Update the row for every page you touched, refreshes and net-new.
- Don't touch rows for work you didn't do.

## Finding the right rows

These workbooks usually have at least two relevant tabs, for example a net-new tab keyed by proposed
topic and a refresh tab keyed by mapped URL. Their layouts differ: header rows are often on different
rows, and the Status column is rarely in the same place. Establish, per tab:

1. Which row the header is on, and therefore which sheet row the first data row is.
2. Which column letter holds Status.
3. Which column identifies the row (topic title, or mapped page URL).

**Trap: don't derive any of this from a text dump of the workbook.** When a cell contains an embedded
object, such as an attached .docx or .html draft in a document-link column, a CSV-style export can shift
every column after it, so complete rows read as blank and a write lands in the wrong cell. Confirm the
column mapping against the rendered sheet before writing anything.

## Writing the cells

**Preferred:** a Google Sheets connector or the Sheets API with the user's own access. Read the header
row and the identifying column by range, then write the Status cells by address. That avoids every UI
trap below.

**Without API access, drive the Google Sheets UI.** The sheet is canvas-rendered, so DOM scraping
returns nothing useful, and a `fetch` of the CSV export endpoint is blocked by CORS from inside the
Sheets page. Instead:

- **Navigate:** set the value of the Name Box (`#t-name-box` at the time of writing) to the cell address
  and dispatch an Enter keydown. Clicking the Name Box and typing is unreliable; it often doesn't take
  focus.
- **Read a cell:** after navigating, read the formula bar (`#t-formula-bar-input`).
- **Write a run of cells:** navigate to the first one, then type the value followed by a newline once
  per cell. Enter commits and moves down, so one `Live` plus a newline per row fills a run of
  consecutive rows in one action.

Google changes these element ids from time to time; if one finds nothing, inspect the page for the Name
Box and formula bar and use their current ids.

## Verify before reporting done

1. Re-read each cell you wrote.
2. Re-read the identifying column for those same rows and confirm the topic or URL is the one you meant.
3. Read the cell one row past your last write and confirm it is unchanged, which proves nothing spilled
   past the boundary.

An .xlsx opened in Google Sheets saves back to the same Drive file, so no export or re-upload step is
needed.
