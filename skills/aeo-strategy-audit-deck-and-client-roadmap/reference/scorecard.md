# The AEO readiness index (out of 100)

The executive summary leads with one index out of 100, built from five dimensions scored 0-20. Each
dimension is the **average of its measured ratios x 20**. Nothing on the scorecard is a judgement call,
and raw counts ("N of M pages") belong in tables, not in score tiles.

If the client or a reference deck already uses a scoring frame, keep its frame and map the measures below
onto it; the rule that every score is a counted ratio with a written source still applies.

## The Scorecard sheet (strategy workbook)

One row per measure, with live formulas:

| Column | Content |
|---|---|
| A Dimension | one of the five below |
| B Measure | the name shown on the slide |
| C Definition | the exact definition, in one sentence |
| D Count | the counted value |
| E Base | what it is counted against |
| F Ratio | `=IF(E2=0,"",MIN(1,D2/E2))` (blank when there is no base, so it drops out of the average) |
| G Source | where D and E came from (crawl, raw-HTML scan, tracker, keyword export, review sites) |
| H Data date | when the data was pulled |

A second block computes each dimension: `=ROUND(AVERAGEIF(A:A,"<dimension>",F:F)*20,0)`, and the index is
the sum of the five dimension scores. The deck quotes the index and the dimension scores from this sheet;
when a number changes, it changes here first.

## Default measures

Use measures you can actually count for this client. Drop one you cannot count (do not guess it), or
replace it with another countable ratio and write the new definition in column C. Each dimension needs at
least two measures.

**Crawl and access**
- Indexable URLs / sitemap URLs that should be indexable.
- Internal links resolving with 200 / all internal links.
- AI crawler user-agents allowed on key paths / AI crawler user-agents checked.
- Key templates passing Core Web Vitals on field data / key templates tested.

**Page quality**
- Top-25 pages with a 40-60 word answer block / 25.
- Content pages with question-led H2s / content pages.
- Key page types with valid schema in raw HTML / key page types.
- Priority pages with a named author and a visible updated date / priority pages.

**Topic coverage**
- Keyword-gap themes with volume that have an owner page / keyword-gap themes with volume.
- Prompt clusters with a mapped owner page / prompt clusters.
- Client non-branded top-20 terms / the search leader's (capped at 1).

**Reputation and earned presence**
- Client referring domains / median direct competitor's (capped at 1).
- Review sites that matter where the client has a current, correctly categorised profile / review sites
  that matter.
- Most-retrieved third-party domains where the client appears / most-retrieved third-party domains
  checked.

**AI presence**
- Client visibility on non-branded tracked prompts / the visibility leader's (capped at 1).
- Client share of voice / the share-of-voice leader's (capped at 1).
- Factual test prompts answered correctly about the client / factual test prompts.

## On the slides

- Executive summary: the index out of 100 as the hero number, the five dimension scores out of 20 beside
  it, and the top owned priority (content first).
- Scorecard slide: each dimension with its measures as short bars (ratio as a percentage) and a one-line
  definition. Sources and data dates go in the presenter notes.
- Re-score with the same measures at each quarterly read so movement is comparable; if a measure changes,
  say so in the notes.
