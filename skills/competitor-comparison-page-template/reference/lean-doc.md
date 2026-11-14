# Lean doc: page-order table, then screenshots in the same order (the default deliverable)

Two sections, nothing else:

1. **Page order**: one table. One row per section of the page, in page order: number, section, status (Keep,
   Rework, Add, Remove) and one short action.
2. **Screenshots in page order**: the same rows in the same order. Under each row, one or two screenshots with a
   short caption under each. Mix the company's own live sections (tagged in the accent colour) with competitor and
   best-in-class patterns (tagged blue).

Keep it short. The reader should see the order, what to do with each part, and an example of each part. Target 5 to
9 pages and about 900 to 1,300 words. Anything that is not the table or a captioned screenshot is cut. URL and title rules,
criteria by product line, hub changes, alternatives pages, rollout and CMS fields are not in this doc. Offer them as
a follow-up only if the user asks.

## 1. The row set

The same 12 rows every time, in this order. Each row draws on blocks of the benchmark model
(`reference/section-model.md`, block numbers below). Look the best examples up in `reference/site-index.md` to find
the page and its notes before capturing.

| # | Row | Blocks | Best examples to borrow patterns from |
|---|---|---|---|
| 1 | Hero | 1 H1 and the difference, 4 button | Semrush, Ahrefs, Airtable (H1). Shopify, Ahrefs, Airtable (button) |
| 2 | Short answer | 2 byline, 6 takeaways, 7 choose-if | monday.com (byline). monday.com, Shopify, HubSpot (takeaways). monday.com (choose-if) |
| 3 | Side-by-side table | 9 | monday.com, Webflow, Zendesk |
| 4 | Where {Company} leads | 10 | monday.com, Ahrefs |
| 5 | Sections by buying question | 12, plus 10 for concessions | monday.com, Zendesk |
| 6 | Pricing and how it is bought | 14 | Zendesk, Shopify, monday.com |
| 7 | Moving over or using both | 13, 18 | Intercom, HubSpot, Shopify. Airtable, Shopify, Notion |
| 8 | Proof | 5 proof strip, 17 | Ahrefs, Shopify, monday.com |
| 9 | FAQ | 19 | Airtable, Intercom, Webflow |
| 10 | Related comparisons | 24 | monday.com, ClickUp, Zendesk |
| 11 | Closing CTA | 26, label from 4 | Ahrefs, Shopify, Webflow |
| 12 | How the page was checked | 3 disclosure, 20 method, 21 sources | Ahrefs, Semrush, HubSpot (sources). No vendor page in the set shows a disclosure line, a method or a change log: describe them, or capture an independent review page in a neutral category |
| Cut | Only when the live page has a block to remove | none | Name the block as the page calls it |

Left out of the default doc (block numbers): jump links 8, what both do 11, security and data handling 15, company
context 16, product in action 22, take-away PDF 23, ask an AI assistant 25. Add a row only when the user asks.

**Statuses**, measured against the company's live pages audited in this run:
- **Keep**: on the live page and works. Say what to keep and what to add, if anything.
- **Rework**: on the live page and needs a change. Say the change.
- **Add**: not on the live page.
- **Remove**: on the live page and should go. Used only by the Cut row.
- When the company has no comparison pages yet, every row is Add, there are no company captures, and the basis line
  says so.

**The What to do cell**: one or two sentences, 30 words at most, plain words. Every statement about the company's
pages was read on the live page. Name the page when pages differ. Use <Rival> as the placeholder. Give no price
its owner does not publish.

**Page 1** holds the title, one basis line (Based on the live pages and best-in-class examples, captured Month
Year), a one-sentence intro and the table. Section 2 starts on a new page.

## 2. The screenshots

- One band per table row, with the number, name and status in the same words and colours as the table.
- Under it, one figure row: two screenshots side by side (3.2 in each), or one wider image (4.2 to 5.8 in) when the
  section needs width. Two crops can stack in one cell when one pattern needs both (for example the tabs and the
  section they open).
- Mix per row: a company capture when the company has the section (kind today, tagged with the company name and
  today, in the accent colour), plus one or two patterns picked for the fix the row action asks for (tagged Pattern,
  site and kind, in blue). When the company lacks the section, show two patterns. When it has the section on several
  pages, show the page that best illustrates the action and name the others in the caption.
- Caption: a bold tag, then 30 words at most (the lint limit is 35). Company captions say what is on the page and
  what is missing. Pattern captions say what layout is worth copying, in terms of what the crop shows. Then a 7 pt
  grey line, Source: domain/path, Month Year. Nothing else.
- A caption claims only what the crop shows. Read labels, headings and any ratings in the browser before writing
  it. Never carry a competitor's claim over as the company's. The section note says once that patterns show layout,
  not claims to copy.

## 3. Capture (a real browser)

Headless fetches and cloud shells often get blocked or see a different page, so captures come from a real browser
session driven by your browser automation tool (for example Claude in Chrome or Playwright).

1. Open a new tab, navigate, and wait about 2 seconds (sections fade in on scroll).
2. Inject this helper on every page (one line; re-inject after each navigation). `__clean(keepTop)` hides cookie
   banners, chat widgets, and fixed or sticky bars at the foot of the screen, and at the top unless `keepTop` is
   true. It only hides elements. It never clicks Accept or Reject. `__go(regex, offset)` scrolls the first visible
   heading (h1 to h4, then p, strong, li, span, a, button) that matches to `offset` px from the top and returns its
   first 70 characters.

```
(()=>{document.documentElement.style.scrollBehavior='auto';if(document.body)document.body.style.scrollBehavior='auto';window.__clean=(keepTop)=>{let n=0;document.querySelectorAll('body *').forEach(e=>{const s=getComputedStyle(e);if(s.position!=='fixed'&&s.position!=='sticky')return;const r=e.getBoundingClientRect();if(r.height<=0||r.width<=0)return;const t=(e.innerText||'').slice(0,400).toLowerCase();const sig=String(e.id+' '+e.className).toLowerCase();const overlay=/cookie|consent|gdpr|privacy choices|chat|launcher|messenger|widget/.test(t+' '+sig)&&r.height<innerHeight*0.7;const top=r.top<=8&&r.height<220;const bottom=innerHeight-r.bottom<=8&&r.height<220;if(overlay||bottom||(top&&!keepTop)){e.style.setProperty('display','none','important');n++}});return n};window.__go=(re,off)=>{const R=new RegExp(re,'i');const bad=/cookie|privacy|consent/i;for(const sel of ['h1,h2,h3,h4','p,strong,li,span,a,button']){const el=[...document.querySelectorAll(sel)].find(e=>e.offsetParent!==null&&R.test(e.innerText||'')&&!bad.test(e.innerText||''));if(el){scrollTo(0,el.getBoundingClientRect().top+scrollY-(off??120));return (el.innerText||'').slice(0,70)}}return 'no match'};return 'helpers ready'})()
```

3. For each section: `__go('heading words', 120)`, move the pointer to the left margin to clear hover states, then
   take a screenshot of the content region at full resolution (a zoomed region capture, scale 1) and save it to
   disk. A smaller scale shrinks the saved file. Copy it to `raw/<page>_<section>.png`. Use `__clean(true)` for the
   hero so the header shows, and `__clean(false)` for the rest. Batch the steps when your tool allows it.
4. Crop each raw capture to the content column with the spec crops (box in raw pixels: x0, y0, x1, y1). Aim for at
   most about 3 in tall at the placed width, legible at print size. Check each crop for lines cut in half and widen or
   lengthen the box. For pointer fill, stitching two scroll positions or blurring personal details, use
   `data/crop_map.py`.
5. Read every cropped image and note exactly what it shows before writing its caption.

**Traps**
- A fetch or page-text summary is not evidence of what a page shows: summaries miscount ratings and mislabel
  sections. Confirm numbers, labels and headings in the browser.
- A form behind a button or in a modal is not a closing form. Describe only what is visible.
- Tool output that contains cookie or query-string text may be blocked or noisy. Filter headings for cookie, privacy
  and consent (the helper does) and print only what you need.
- If a capture times out (page busy or mid-navigation), reload the tab, wait 3 seconds, re-inject the helper and
  retry once. Do not loop. If it keeps failing, tell the user.
- A page that cannot be loaded gets no capture. Say so rather than guessing what it shows.

## 4. Build

```
python3 data/lean_doc.py spec.py --crop --render
```

Needs python-docx and Pillow; `--render` also needs LibreOffice and poppler (`pdftoppm`). Copy
`data/lean_spec_example.py` (its header comments explain each field) and replace the title, basis, sources, crops
and rows. The run prints lint warnings (action over 30 words, caption over 35, missing image, unknown status, a row
with no screenshot, a pattern with no name, text over the word budget), the forbidden-word scan (dashes, the percent
sign, banned words, plus the spec never_mention list), word, picture and row counts, the docx validation result when
a validator is configured (`DOCX_VALIDATOR`), and with `--render` the page count and free inches per page (page
images in `pdf/p-N.png`). Without `--crop` the cropped figures must already be in `img/`.

Layout: Letter, margins 0.9 in at the sides and 0.6 in top and bottom, Calibri 10. The table repeats its header row
and its rows never split. Each figure row is a borderless table whose cell holds the picture, caption and source.
Section 2 starts on a new page. Put `page_break: True` on a row whose band would otherwise sit alone at the foot of a
page. LibreOffice ignores keep-with-next across tables (Word honours it), so check the rendered pages and not only
Word. Use `chain: True` on a figure row that must stay with the next figure row in the same band. Pair figures side
by side before shrinking them. Use the company's own document template if it has one; otherwise the builder's plain
default (pass the company's accent colour in the spec).

## 5. Verify, then deliver

1. The `lean_doc.py` output is clean: no LINT lines, `forbidden hits: []`, validation passed, 5 to 9 pages, about
   900 to 1,300 words.
2. View every rendered page: whole rows, each band on the same page as its figures, nothing cut off, every image
   legible, no page more than about 3 in short except the last.
3. Re-read every caption against its image, and every statement about the company's pages against the live page
   (heading text, button labels, dates, ratings, FAQ answers, forms).
4. Copy rules: apply the user's style rules and never-mention list. A sample default set, which is what
   `lean_doc.py` scans for (edit its BANNED list to match the user's rules): no em or en dashes, percent spelled out
   not the symbol, a short list of overused words (leverage, robust, seamless, comprehensive, ensure,
   optimize, monetize, genuinely, honestly, straightforward), acronyms spelled out at first use and sentence-case
   button labels. Comma style (serial comma or not) follows the user's guide.
5. Deliver the .docx the way the user works (attach it, or commit it to the connected folder when there is one) with
   a one-line summary. Do not draft a chat or email reply unless asked, and never send one without a yes.

## Worked example (fictional)

`data/lean_spec_example.py` is a made-up run for ExampleCo, a meal-kit company with four live comparison pages
(against CompetitorA, CompetitorB, CompetitorC and CompetitorD) at example.com: 12 rows plus a Cut row. It shows the
spec format, not a real engagement. Sample rows:

- **3 Side-by-side table, Rework.** The pages use tick grids, and each page has its own rows. Action: one sentence
  per cell, one row set for every page, and a date. Pattern: Webflow's icon-plus-sentence cells.
- **9 FAQ, Keep.** The questions are fine, but the answers load only on click. Action: keep the questions and put
  the answers in the page HTML.
- **Cut, Remove.** A video that plays on load above the table.
