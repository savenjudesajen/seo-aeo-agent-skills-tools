# Common errors and the fix for each

| What goes wrong | Fix |
|---|---|
| One sheet mixes 200 and non-200 pages, and the action column suits the wrong audience | Three sheets: live pages with an action each, redirects and errors flagged for CMS removal, parameter URLs with researched handling |
| Decisions drafted by script or regex are wrong both ways | Write every row by hand with a reason. Scripts only transcribe |
| Claims about the CMS come from the crawl alone | Verify against the CMS API before the sheet goes out |
| The crawl misses live pages | Diff the CMS list against the crawl and crawl the gap in List mode |
| A list crawl runs with Search Console and GA4 disconnected | Check the API tab before every crawl, Connect, Request API Data, count non-empty cells |
| Blank similarity is read as "below threshold" | The score fills only when a neighbour passes the threshold and only for pages with vectors. Count vectors, compute the rest from text, validate |
| A high embedding score is taken as duplication while the cleaned page text barely overlaps | Full-page embeddings include shared chrome. Confirm with cleaned page text and the live pages |
| A line-by-line "unique content" check flags every page | Page text is hard-wrapped. Compare H2/H3 sections and their bodies |
| Pages in a template family are called near-duplicates because one pair scores high | Label by the group's mean pairwise similarity |
| Redirect reasons cite a similarity the sheet does not show | Every number in a Reason must come from the row or a stated check. The QA auditor compares them |
| Same-task variants (one task written per platform, city or integration) are ungrouped, and some redirect while others stay | Group by task name, apply one rule, document it |
| A source with far more sessions than its target is redirected without mention | Quote both session counts in the Reason |
| Menus will not open in background mode, the first click on a dialog fails, clipboard write is denied | Request full control up front, click the dialog title first, type the path into the file picker |
| An export tool ignores an unknown parameter and returns results inline | Use the wrapper's documented parameter names and a relative path; check the file exists |
| A redirect target points at an unpublished template | Check the target on the live sheet or in the CMS |
| Per-URL backlinks are unavailable | State it, mark no rule safe, send the human to a backlink tool's per-page export |
| Field and path slips in hand-authored TSVs | Validate field count, allowed values and keys against master addresses |
| The builder checks its own work | A sub-agent that did not build the workbook audits it against live pages |
| Sheets grow beyond the ask | Three sheets plus Method |

## Process habits

- Sub-agents for row batches and for the final QA; validate their TSVs and findings in the main thread.
- Save intermediate TSVs per batch and rebuild the workbook from files.
- Short status messages during long waits. A long silent wait is a failure.
- Never touch a crawl the user started. Read progress only.
- Send nothing unconfirmed. Confirm claims with Google, the live pages or a scraper spot check.
