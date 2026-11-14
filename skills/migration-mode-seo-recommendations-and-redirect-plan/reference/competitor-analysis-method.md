# Competitor analysis: the full method, end to end

Contents: 1. Build the list: two sets, two jobs, never merged · 2. Pull the data: TWO exports per domain · 3. Parse by header name, not position · 3a. The AI-citation columns · 4. STOP: the two exports answer different questions · 5. Classify: brand vs non-brand · 6. Filter to an evidenced target list · 7. Compute the Pareto · 8. Classify page type · 9. Look for the exception, and for the transferable tactic · 10. What this phase outputs

Everything from "who are the competitors" to "the tab is in the workbook and the number is on the
slide". Written for a fresh session with no context. Run it in order.

This phase produces the content argument. It is also where the most tempting wrong claim lives
("the market is small"), so §4 is not optional.

Placeholders used below: CompetitorD, CompetitorB, CompetitorF; all domains are `*.example`.

---
## 1. Build the list: two sets, two jobs, never merged

Start from the client's own list. Clients often supply **direct and indirect** competitors on purpose,
so the indirect set can be mined for category strategy. Ask which is which if they haven't said, and
**never prune the "irrelevant" ones**.

| Set | Who | The question it answers |
|---|---|---|
| **Direct** | same buyer, same problem | "where do we lose today?": head-to-head, keyword gap, share of voice |
| **Direct+ / adjacent** | same buyer, neighbouring problem | "what does this buyer already see?" |
| **Indirect** | different problem, same industry, **has a content engine** | "what does winning look like in this category?": the playbook sample |

Add your own where the client's list has a hole. The indirect set often carries most of the content
argument, so don't treat it as filler.

Record the set label on every row from here on; every downstream table is grouped by it.

---
## 2. Pull the data: TWO exports per domain

You need, for every comparator, a **top pages** export and an **organic rankings (positions)** export.
Semrush calls them Organic Research → Pages and Positions; Ahrefs calls them Top pages and Organic
keywords. Through an API, a connector, or the web UI:

```
Semrush Pages      https://www.semrush.com/analytics/organic/pages/?db=us&q=<domain>&searchType=domain
Semrush Positions  https://www.semrush.com/analytics/organic/positions/?db=us&q=<domain>&searchType=domain
```

Swap the market code for the client's market. Do **both** reports for **every** comparator (§4 says
why).

### When the API is out of units, the UI still works
Drive the web UI with a browser automation tool: navigate to the report, read the table as page text,
and click only when you must.

- The **export button can swallow the first click** (the dropdown doesn't open, and a second click
  closes it again). Hover, wait about a second, click, then pick the format.
- **Downloads may never reach a folder you can read** (a save-as dialog the browser tool can't
  operate). Don't burn turns debugging. Either read the report as page text (it returns the full
  on-screen table, which is enough for Pareto work) or **ask the user to collect the files and hand
  them back**. Ask; don't guess.
- Exports are **row-capped** by plan. That's fine for analysis; just don't imply you have every page of
  a very large estate, and state the cap as your denominator.

### Capture headline numbers as you go
Before leaving each domain, note from the report header: **organic traffic · organic pages · homepage
% of traffic · homepage top keyword**. These let you build the Summary tab even for a domain whose
export never arrives.

---
## 3. Parse by header name, not position

Export layouts change between versions and between tools, so look columns up by header text. The
aliases below cover common Semrush and Ahrefs headers; check them against your file's header row and
extend the lists if a column comes back empty.

| Logical field | Header aliases (first match wins) | Use |
|---|---|---|
| `url` | URL, Page, Address | key; join field between the two exports |
| `traffic` | Traffic, Organic traffic | sort key for the Pareto, weight for non-brand share |
| `traffic_pct` | Traffic (%), Traffic share | per-page share |
| `keywords` | Number of Keywords, Keywords | **depth signal: how many queries one page wins** |
| `top_kw` | Top Keyword, Top keyword | the query that best characterises the page |
| `intent` | Primary Intent, Keyword Intents, Intent | informational / commercial / navigational / transactional |
| `answer_engines` | Answer Engines, AI engines | **§3a: per-page AI citations** |
| `llm_prompts` | LLM Prompts, AI prompts | **§3a** |
| `kw` | Keyword | brand vs non-brand classification |
| `pos` | Position, Current position | "they rank #K for X" |
| `vol` | Search Volume, Volume | the demand number |
| `kd` | Keyword Difficulty, KD | feasibility: a low-to-mid difficulty win is reproducible |
| `cpc` | CPC | commercial value proxy |

```python
import re, openpyxl

ALIASES = {
    "url": ["url", "page", "address"],
    "traffic": ["traffic", "organic traffic"],
    "traffic_pct": ["traffic (%)", "traffic share"],
    "keywords": ["number of keywords", "keywords"],
    "top_kw": ["top keyword"],
    "intent": ["primary intent", "keyword intents", "intent"],
    "answer_engines": ["answer engines", "ai engines"],
    "llm_prompts": ["llm prompts", "ai prompts"],
    "kw": ["keyword"],
    "pos": ["position", "current position"],
    "vol": ["search volume", "volume"],
    "kd": ["keyword difficulty", "kd"],
    "cpc": ["cpc"],
}

def _index(header):
    norm = [str(h or "").strip().lower() for h in header]
    out = {}
    for field, names in ALIASES.items():
        for n in names:
            if n in norm:
                out[field] = norm.index(n)
                break
    return out

def read_export(path):
    """Any top-pages or positions export -> list of dicts keyed by logical field, traffic desc."""
    ws = openpyxl.load_workbook(path, read_only=True).active
    it = ws.iter_rows(values_only=True)
    idx = _index(next(it))
    rows = []
    for r in it:
        if not r or not any(r):
            continue
        row = {f: r[i] for f, i in idx.items() if i < len(r)}
        for num in ("traffic", "traffic_pct", "keywords", "llm_prompts", "pos", "vol", "cpc"):
            row[num] = row.get(num) or 0
        if "kw" in row:
            row["kw"] = str(row["kw"]).lower().strip()
        if row.get("url"):
            row["type"] = classify(row["url"])            # classify() is in §8
        rows.append(row)
    rows.sort(key=lambda x: -x["traffic"])
    return rows
```

Keep both lists per competitor, keyed by its set label and placeholder name. **The two exports join on
`url`**: that join lets you say "this page earns this many keywords worth this much demand", which is
the case-study slide.

## 3a. The AI-citation columns

Some suites' top-pages exports now carry **per-page AI-citation data** with no AEO tool involved:

- **Answer engines:** a list of the engines citing the page (Google AI features, ChatGPT search,
  Gemini and so on, in the tool's own labels).
- **LLM prompts:** the count of distinct AI prompts the page surfaces for.

On a migration engagement this is the cheapest AEO evidence there is, and it is *page-level*, which
prompt-tracking tools usually aren't. Compute per competitor: **pages cited by any engine as a % of the
pages in the export**, and **total prompts**. State the denominator: because exports are capped, on a
large estate the percentage is "of the top N pages by traffic", not of the whole site. Then look at the
outliers.

Lay it out like this (values are placeholders):

| Competitor | Pages in export | Pages cited by an engine | Total prompts |
|---|---|---|---|
| Competitor 1 | N | N (N%) | N |
| Competitor 2 | N | N (N%) | N |
| Competitor 3 | N | N (N%) | N |

**The hypothesis to test:** does page count predict citation share across the set? Sort by pages and
by citation share and compare. If the largest estates are not the most cited, you have evidence that
page volume doesn't buy AI citations and that answering real questions matters more. The evidence is a
spreadsheet the client's own SEO subscription can produce.

---
## 4. STOP: the two exports answer different questions

| Export | Tells you | Does NOT tell you |
|---|---|---|
| **Top Pages** | how traffic is **distributed** across a site | what the site **ranks for**, or whether demand exists |
| **Organic Rankings** | the **actual keywords**, volume, difficulty, intent, ranking URL | nothing this method needs |

**Never infer the size of a category's search market from a top-pages export.** Page concentration
shows how a site's traffic is spread, not how much demand exists. A set of brand-concentrated
competitors is equally consistent with "little demand" and "plenty of demand nobody has built for".
Only the rankings export separates the two, so pull it for every comparator before any slide says
demand is low.

**The lesson generalises:** before explaining *why* a market looks the way it does, check whether you
measured the thing you are explaining, or only something correlated with it.

---
## 5. Classify: brand vs non-brand

The honest answer to "is this competitor brand-dependent?" is **non-brand share of traffic**, not page
count.

Build a token map per domain. **Include misspellings and former names**: a misspelled brand is still
brand traffic, and a renamed or acquisitive competitor carries several brand vocabularies.

Sources for the tokens, in order: the domain name · the company's own "formerly known as" or about page
· its press releases about acquisitions · the export itself (sort by traffic and read the top 30
keywords; brand variants and misspellings are obvious there).

```python
BRAND = {   # key = the competitor placeholder you file its exports under
    "competitord": ["competitord", "competitor d", "compettord"],          # misspellings count
    "competitorb": ["competitorb", "competitor b", "formername"],          # former names too
    "competitorf": ["competitorf", "acquiredproduct"],                     # acquired brands too
}

def split_brand(key, rows):          # rows from read_export() on a positions export
    tot = nb_kw = 0
    tt = nbt = 0.0
    for x in rows:
        tot += 1
        tt += x["traffic"]
        if any(tok in x["kw"] for tok in BRAND[key]):
            continue
        nb_kw += 1
        nbt += x["traffic"]
    return tot, nb_kw, tt, nbt, (nbt / tt * 100 if tt else 0)
```

Weight by **traffic**, not keyword count: thousands of non-brand keywords earning a sliver of traffic is
a very different site from the same count earning a fifth of it.

| Competitor | Total keywords | Non-brand keywords | Non-brand % of traffic | Reading |
|---|---|---|---|---|
| the exception | N | N | high | has built real non-brand demand |
| typical peer | N | N | low | brand name only |
| thin peer | N | N | ~0 | brand + login only |

A banding that works: **≥15% = has built real non-brand demand · 5–15% = some · <5% = brand name
only.** Colour the cell; the client reads the colour before the number.

---
## 6. Filter to an evidenced target list

From the pooled non-brand keywords, keep those **relevant to the client's service**, above a volume
floor, excluding recruitment and account noise. Two regexes and a floor:

```python
SERVICE_TERMS = ["<service term>", "<product category>", "<problem the client solves>"]   # fill per client
QUESTION_STEMS = [r"cost of", r"how much (is|does)", r"\bbest\b", r"how to", r"is it worth",
                  r"how to choose", r"\bvs\b", r"alternatives?", r"\breview"]
REL = re.compile("|".join([re.escape(t) for t in SERVICE_TERMS] + QUESTION_STEMS), re.I)
BAD = re.compile(r"job|career|salary|login|log in|portal|sign in|stock|glassdoor|linkedin|"
                 r"phone number|address|hours", re.I)
VOL_FLOOR = 200      # lower it (e.g. ~50) in a genuinely small category; say which you used

keep = [x for x in rows                      # non-brand rows from read_export()
        if x["vol"] >= VOL_FLOOR and REL.search(x["kw"]) and not BAD.search(x["kw"])]
```

**Build `SERVICE_TERMS` from the client's own vocabulary**, not a generic list: their service and
product names · the problems they solve · the question stems a customer would use · the recurring
non-brand terms you can see in the competitors' own top keywords. Test it by eye on 50 rows before
trusting it: a regex that keeps recruitment traffic or drops the client's core service quietly poisons
the whole list. Then tag each surviving keyword with a **theme** (cost / how it works / comparison /
alternatives / use cases / quality and trust); the themes become the content plan's sections.

This list is different from ordinary keyword research: **every row is demand a competitor has already
proven it can win.** Say so on the slide.

---
## 7. Compute the Pareto

```python
rows.sort(key=lambda x: -x["traffic"])
total = sum(x["traffic"] for x in rows) or 1
def pages_to(pct):
    c = 0
    for i, x in enumerate(rows, 1):
        c += x["traffic"]
        if c / total >= pct:
            return i
    return len(rows)
p50, p80, p90 = pages_to(.5), pages_to(.8), pages_to(.9)
```

Also compute **homepage % of traffic** and **top-3 pages % of traffic**. Homepage share is the cleanest
single brand-concentration signal on the Summary tab.

**Read the Pareto together with §5.** A very low page count for 80% of traffic means one of two opposite
things:
- **concentrated on brand** (homepage and login dominate, non-brand share near zero) = no content
  engine, or
- **concentrated on a few winning assets** (a cost guide, a glossary hub) = an efficient content engine.

The brand/non-brand split tells you which. **The Pareto alone cannot.**

---
## 8. Classify page type

URL-pattern classifier, ordered, first match wins. Tune the buckets to the client's category:

```python
def classify(url):
    path = re.sub(r"^https?://[^/]+", "", str(url).lower()).rstrip("/")
    if path in ("", "/"):                                          return "Homepage"
    if any(s in path for s in ["/blog", "/insights", "/article"]):  return "Blog"
    if any(s in path for s in ["/resource", "/case-stud", "/customer", "/stories",
                               "/webinar", "/guide", "/ebook", "/video"]):  return "Resource"
    if any(s in path for s in ["/press", "/news", "/media"]):       return "Press"
    if any(s in path for s in ["/leadership", "/team", "/board", "/bio", "/people"]): return "Bio / About"
    if any(s in path for s in ["/login", "/register", "/sign", "/account", "/portal"]): return "Account / Login"
    if any(s in path for s in ["/career", "/job"]):                 return "Careers"
    if any(s in path for s in ["/about", "/contact", "/company", "/legal", "/privacy"]): return "Corporate"
    if any(s in path for s in ["/solution", "/product", "/service", "/industr", "/use-case",
                               "/platform", "/pricing", "/location"]):  return "Landing page"
    return "Other"
```

Then average **traffic per page by type**. That table justifies the content plan's build order: build
the type that earns the most per page first, not the type that is easiest to write.

Watch for **Careers and Account/Login in the top 3**. A competitor whose second page is `/careers` has
no content engine, and saying so plainly is more useful than a Pareto number.

---
## 9. Look for the exception, and for the transferable tactic

1. **The exception.** If one competitor has materially more non-brand traffic than the rest, build the
   case-study slide around it: name its pages, queries, volumes and difficulty. It converts an
   abstract recommendation into *this works in this category, for this buyer, and here are the pages
   that did it.* Go one level deeper with the keywords column: **"one article ranks for N keywords"**
   beats any traffic number for a client who thinks they need hundreds of pages. Get it from the join:
   take the case-study URLs from the positions rows, then look each one up in the top-pages rows for
   its `keywords`, `answer_engines` and `llm_prompts`.
2. **The tactic that matches the client's moment.** On a rebrand, check every competitor or peer that has
   renamed itself. If its rename announcement or "formerly" content earns organic traffic, that is
   direct evidence that publishing the rename as content works for this buyer. Flag those rows in the workbook (`is-now`, `new-name`, `rebrand`, `formerly` in the path) so
   they can't be missed.

---
## 10. What this phase outputs

Into the **Content Plan workbook** (schemas in `workbook-specs.md`): Summary · Pareto · one tab per
competitor · Keyword Opportunity · Brand vs Non-Brand · the case-study tab.

Onto **slides** (four at most):
1. **Competitor landscape:** the two sets, traffic, pages, homepage share. Group by set and label the
   sets on the slide; an ungrouped table of a dozen rows reads as noise.
2. **The Pareto:** how few pages carry 80%, and what that means read against brand share.
3. **The exception / case study:** the one competitor that solved it, with pages and queries.
4. **Where the demand actually is:** the evidenced non-brand target list, by theme.

Everything else stays in the workbook.
