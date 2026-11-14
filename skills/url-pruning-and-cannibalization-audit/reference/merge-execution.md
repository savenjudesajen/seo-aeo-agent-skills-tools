# Executing a merge (after the candidates list is approved)

## 1. Intent read decides, the score only nominates

Read both pages side by side: H2 list, word count, images, videos, tables. A crawl similarity of 0.90 or
higher on a site with shared menus often means a shared topic, not the same job. A score in the Review
band usually turns out to be two pages that do different work on one subject, such as a quick answer and
a step-by-step walkthrough, or a buyer's checklist and a troubleshooting page, so expect the read to keep
many of them apart. Rows that pass the full Merge test usually hold up. Record one outcome per row:
Stays separate (name the job each page does), On hold (name what blocks it) or Done.

## 2. Build the merged survivor body

- Carry whole sections from the merged page, placed before a named survivor H2 where they fit the
  reading order.
- Carry every image, video and table the merged page holds. Drop only an asset the survivor already shows
  (same video ID or same chart). Check by listing asset IDs on both sides: nothing from the merged page
  may be missing in the survivor.
- Rename carried H2s that duplicate or clash with survivor H2s, and strip step numbering that no longer
  fits.
- Rewrite every link that points to a merged slug so it points to its survivor, as an absolute URL.
  Unwrap links that now point to the page itself. Fix sentences that referred to the merged page by name.
- Remove duplicated paragraphs and repeated charts inside the merged result.
- Add a link from the survivor to any sibling page kept separate on the same topic.
- Set the refresh date to the merge date.

## 3. Write, verify, publish

- Back up the survivor fields before writing.
- Take the item ID from the fetched item for that slug and print slug and ID together before every write.
  Never reuse an ID from a list typed earlier.
- After the write, compare the stored body with the intended file (whitespace-normalised). Fix any
  mismatch before publishing.
- Before publishing a survivor, check for unpublished staged edits by someone else. If present, hold the
  merge and flag it to the owner.
- Repoint every hub or collection reference that points to a merged item, including links inside FAQ or
  rich-text fields, and publish the hubs.

## 4. Redirects and retirement

- Redirect file: repoint existing rules whose target is a merged slug to the survivor, add one rule per
  merged page, and check for loops and new chains.
- The owner imports the file and publishes. Confirm each merged URL now 301s to its survivor and each
  survivor shows the carried sections and assets live.
- Only then unpublish and archive the merged items.

## 5. Candidates sheet format

Sheet name Merge candidates, header in row 1, one row per pair: Page, Survivor, Decision, Live since,
Age, Similarity, Shared queries (top 3 with impressions and both positions), Query overlap %,
Cannibalization, the page's clicks, impressions, position and inlinks, the survivor's same four numbers
side by side, Reason, Source, then Outcome and Outcome note once the intent read and merge are done
(Outcome: Stays separate, On hold or Done). The side-by-side survivor numbers are what make the sheet
quick to review and sign off.

The workbook's second sheet is Cannibalization pairs: one row per pair with its Resolution. Pairs that
are not merge candidates live there too (Re-target, Split anchors, Wait). Layout: `sheet-columns.md`.
Query evidence and Method are the only other sheets.
