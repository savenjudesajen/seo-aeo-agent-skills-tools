-- Long-tail population split, run inside BigQuery on the full Search Console bulk export (no row cap).
-- Same labels as data/longtail_split.py. Before running, replace:
--   your-project.searchconsole  the project and dataset your bulk export writes to
--   brandname                   the client's brand regex from Step 0 (lower case, alternatives joined with |)
--   vendor_a|vendor_b|vendor_c  the category's vendor names, for the STACK label (three or more in one string)
--   the TEMPLATE noun list      add the category's own head nouns after the generic ones, and any template shape
--                               you found in the samples as a further alternative (same as --template-pattern)
-- REPEAT here = 10+ words, 3+ impressions a day on the days the phrasing appeared, on 14+ days. The bulk export has
-- one row per day, so the rate is measured per active day rather than over the whole window.
-- The period column splits the last 90 days from everything before, so a population that grew recently shows.
WITH b AS (
  SELECT LOWER(query) q, data_date d, impressions i
  FROM `your-project.searchconsole.searchdata_url_impression`
  WHERE query IS NOT NULL AND is_anonymized_query = FALSE AND ARRAY_LENGTH(SPLIT(query, ' ')) >= 6),
a AS (
  SELECT q, IF(d >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY), 'recent90', 'prior') per,
         SUM(i) imp, COUNT(DISTINCT d) days
  FROM b GROUP BY 1, 2),
c AS (
  SELECT *, CASE
    WHEN REGEXP_CONTAINS(q, r'^[+%]') THEN 'PREFIX'
    WHEN REGEXP_CONTAINS(q, r'\b(site|inurl|intitle):|^(list|crawl|scan) every |^watch \S+ for ') THEN 'AGENT'
    WHEN w > 40 OR REGEXP_CONTAINS(q, r"(forced ranking|(?:rank|order)(?:ed)?(?: them)? from best to worst|you must (?:provide|rank|list|give|answer)|^\s*you are an? |search the web for|do not invent|^\s*<[a-z_ ]+>|^i am an? .{80,}|^i'm an? .{80,})") THEN 'TRACKER'
    WHEN REGEXP_CONTAINS(q, r"^(i'm|i am|as) an? [a-z ,-]{3,60}[.,] ") THEN 'PERSONA_SHORT'
    WHEN ARRAY_LENGTH(REGEXP_EXTRACT_ALL(q, r'\b(vendor_a|vendor_b|vendor_c)\b')) >= 3 THEN 'STACK'
    WHEN REGEXP_CONTAINS(q, r'^(evaluate the |best (tools?|platforms?|software|solutions?|services?|agenc(y|ies)|compan(y|ies)|providers?|apps?|vendors?)\b|top (tools?|platforms?|software|solutions?|services?|agenc(y|ies)|compan(y|ies)|providers?|apps?|vendors?)\b|tools? (to|for) |(leading|highest.rated|most reliable|most affordable) )') THEN 'TEMPLATE'
    WHEN REGEXP_CONTAINS(q, r'^(what|how|which|who|why|is|are|can|do|does|should|will|where|when)\b')
      THEN IF(ARRAY_LENGTH(SPLIT(q, ' ')) >= 10 AND imp / GREATEST(days, 1) >= 3 AND days >= 14, 'REPEAT', 'HUMAN')
    ELSE 'other' END pop
  FROM (SELECT *, ARRAY_LENGTH(SPLIT(q, ' ')) w FROM a))
SELECT per, pop, COUNT(*) n, SUM(imp) imp, ROUND(AVG(w), 1) w,
  APPROX_QUANTILES(imp, 2)[OFFSET(1)] med_imp,
  -- shape shares per population: a "for <qualifier>" tail, compound asks, provider nouns, the client's own name
  ROUND(COUNTIF(REGEXP_CONTAINS(q, r'\bfor [a-z]+')) / COUNT(*), 3) fortail,
  ROUND(COUNTIF(REGEXP_CONTAINS(q, r' and | or |,')) / COUNT(*), 3) compound,
  ROUND(COUNTIF(REGEXP_CONTAINS(q, r'\b(agenc(y|ies)|consultan[a-z]*|services?|partner|vendors?)\b')) / COUNT(*), 3) provider,
  ROUND(COUNTIF(REGEXP_CONTAINS(q, r'\b(brandname)\b')) / COUNT(*), 3) own
FROM c GROUP BY 1, 2 ORDER BY 1, 2

-- To read the phrasings themselves, by population, for the last 90 days, swap the final SELECT for:
--   SELECT q, pop, imp FROM c WHERE per = 'recent90' QUALIFY ROW_NUMBER() OVER (PARTITION BY pop ORDER BY imp DESC) <= 70
-- Read the samples before trusting any share: a template the patterns have not seen lands in "other".
-- REPEAT-SET (slot-swapped templates) and OWN-TRACK (match to the tracked-prompt export) are not computed here:
-- export the phrasings and run data/longtail_split.py with --tracked for those two.
