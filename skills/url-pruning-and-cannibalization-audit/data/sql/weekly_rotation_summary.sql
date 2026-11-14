-- One row per contested query: how often our top URL changed week to week.
-- Use this when the weekly query x page rows are too large to download (console limit 10 MB).
WITH r AS (
  SELECT data_date, REGEXP_REPLACE(REGEXP_REPLACE(url, r'[#?].*$', ''), r'/$', '') AS page,
         LOWER(TRIM(query)) AS query, impressions, sum_position
  FROM {table}
  WHERE (search_type = 'WEB' OR search_type IS NULL) AND NOT is_anonymized_query
    AND query IS NOT NULL AND data_date BETWEEN '{start}' AND '{end}'),
b AS (SELECT query, page FROM r GROUP BY 1, 2
      HAVING SUM(impressions) >= 10 AND SUM(sum_position) / SUM(impressions) + 1 <= 30),
c AS (SELECT query FROM b GROUP BY 1 HAVING COUNT(*) >= 2),
w AS (SELECT DATE_TRUNC(r.data_date, WEEK(MONDAY)) AS wk, r.query, r.page,
             SUM(r.sum_position) / SUM(r.impressions) + 1 AS pos
      FROM r JOIN b USING (query, page) JOIN c USING (query) GROUP BY 1, 2, 3),
t AS (SELECT query, wk, ARRAY_AGG(page ORDER BY pos LIMIT 1)[OFFSET(0)] AS top,
             COUNTIF(pos <= 10) AS n10 FROM w GROUP BY 1, 2),
s AS (SELECT query, wk, top, n10, LAG(top) OVER (PARTITION BY query ORDER BY wk) AS prev FROM t)
SELECT query, COUNT(*) AS weeks, COUNTIF(prev IS NOT NULL AND prev != top) AS rotations,
       COUNTIF(n10 >= 2) AS double_weeks, STRING_AGG(DISTINCT top, ' | ') AS tops
FROM s GROUP BY 1
