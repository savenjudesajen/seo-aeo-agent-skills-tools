# Benchmark method: two sets, one taxonomy, packed

The rule: do not benchmark only the client's industry. Find the pages that do this page type best in any industry,
read many of them, and pack the client's page with every section that helps a buyer or an AI answer. Navigation and
URL placement are different: menus, footers and addresses are counted on the client's own set only, because a
reader compares the client's menu with its rivals', not with a cloud provider's.

## Two sets, one taxonomy
1. **Client set**: the client's direct competitors (4 to 8, from the user first, else from search results for the
   client's head terms) plus 6 to 12 leaders in the client's category or adjacent B2B categories. Read their menus,
   footers, where industries are linked, URL patterns, the overview page if one exists, and one industry page each
   (the same industry for every company where possible).
2. **Cross-industry set**: the 12 companies in `data/benchmark.py` (cloud, enterprise software, consulting,
   IT services), already coded. Reuse their codings unless the user asks for a refresh or a page has clearly changed;
   spot-check the pages you plan to cite. Swap in companies closer to the client's buyers when that helps (for a
   consumer brand, retailers and marketplaces), and code them the same way.
3. **One taxonomy.** The 45 section types in `reference/section-types.md`, each with an id, a definition and the best
   example. Code the client set against the same ids in `CLIENT_HUBS` and `CLIENT_IND`, so every count reads
   "client set + cross-industry = all". A section none of the 45 covers gets a new id with a definition, coded on
   every page.
4. **Pack.** Every type lands somewhere: a block, part of a block, or a "Not used" line with the reason. Order the
   blocks in the reading order of `reference/section-model.md` ("Why this order"). Nothing is dropped silently.
5. **Statuses.** Keep, New, Rework, Optional, Later, set against the client's live site in `CLIENT_STATUS`
   (definitions in the section model; none is preset).

## What to record for each client-set company (`CLIENT_NAV`)
- Where industries sit in the menu: under Solutions, a top-level item, under a product menu or another parent, or
  not in the menu. Record the group label as read (Industries, By industry, Industry solutions) and the number of
  links.
- Whether the menu links an all-industries page, and whether the menu and the overview page list the same industries
  (they often differ: count it).
- Whether industries get their own footer group.
- How industries are presented: a standalone overview page linked from the menu, a section of another page (often a
  solutions page), menu links only, industry pages with no overview, an orphan overview page not linked from the
  menu, or nothing.
- What the parent address returns (the URL one level above the industry pages): live, or broken (404, an empty
  shell, a placeholder template, another page's content, a redirect to the homepage). Broken parents are common.
- The industry slugs: plain (`/industries/healthcare`) or keyword-stuffed and inconsistent.
- Which industries each company covers (feeds the launch-set table), and the regulations its industry page names.
- A menu you cannot read (bot check, script-only render) is not a count. Never solve a bot check: take the company
  out of the menu base and say so once in the appendix.

## Reading each page
- Run sub-agents in parallel, one group of companies each. Each reads every page twice: a plain fetch and a
  JavaScript-rendered text read (tabs, carousels and accordions often render only with JavaScript; fetch summaries
  can mix in mega-menu text or return an older page variant). Where only one read saw something, label it.
- Locate moved pages with a web search; record every redirect and substitution in the appendix.
- Each sub-agent returns one fixed block per page:

```
PAGE: <company> <overview|industry> page | URL as read (and where it redirected) | SITE TYPE
TITLE / H1: <as read>
DATE SHOWN: <visible page or card dates, or none; metadata dates do not count>
PEOPLE SHOWN: <roles only, e.g. "five sector leaders with title and contact route"; no names in your notes>
APPROX WORDS: <visible body copy, excluding menu, footer and cookie banner> | NUMBER OF SECTIONS
INDUSTRIES LISTED (overview only): <count and list>
SECTIONS IN ORDER: n. <section kind> | <heading as read> | <what it shows> | BUYERS: <what it gives a buyer> |
                   AI ANSWERS: <what it gives an answer engine>
STANDOUT SECTIONS: <section number> - <why it is worth copying>
SCREENSHOT HINTS: <section number> - <heading>: <approximate height in screens>
NOTES: <structured data found, site widgets (not sections), placeholders, contradictions, anything unverified>
```

- You decide set membership by hand from these blocks; scripts only count. Re-read in the browser every quote a
  caption, a "Why" cell or a "Seen on" cell rests on.
- Mark anything a read did not confirm as unverified, and never count it.

## Captures
- At least one screenshot per New or Rework block, from the best page for that block
  (`reference/exemplar-library.md`), and one for a Later block when it helps the client see what to supply.
- Captions say only what the capture shows: which element comes first, how many cards show the pattern, whether it
  is a menu or a footer column. Re-open the image before you write the caption.
- Blur personal contact details in any capture of a people block.
- Browser mechanics (window size, pointer, cookie banners, lazy sections, zooming to fit a wide table):
  `web-screenshot-to-document`.

## Counting words
- Every count names its base: "n of N overview pages", "n of N industry pages", "n of N menus in the client set".
  Overview pages, industry pages and menus are three different bases. Say which in every cell.
- "4 of the 6" only when all 6 were checked. Otherwise name the ones seen.
- Assert every named example is in the set it illustrates (`benchmark.py` checks the block models; the builder's
  `seen_hub()` / `seen_ind()` check every name the doc prints).
- Combined counts (a hero button, proof of any kind, industry figures) are derived sets decided by hand and listed
  in the appendix with what they combine.

## Choosing the launch set of industries
Score each candidate industry on three things and show the table in the doc:
1. **Competitor coverage**: how many client-set companies have a page for it.
2. **Demand**: monthly searches for "<industry> <category>" style terms in the client's market (a keyword tool or
   API). Expect near-zero demand on niche pairings and say so plainly: these pages also serve AI answers,
   account-based campaigns and buyers arriving from the menu.
3. **Client proof**: what the client already has per industry (a customer quote, a story, a partner page, a post,
   a page in draft).
Launch with four to six industries where proof exists; list the next two with what they need. Regulation copy is
limited to what the client confirms.
