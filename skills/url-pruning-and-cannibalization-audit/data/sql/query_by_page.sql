-- Search Console bulk export: query x page totals for the window.
-- Replace {table} with `<project>.<dataset>.searchdata_url_impression` and set the dates.
-- position is 1-based: sum_position is zero-based, so add 1 after dividing.
-- Anonymized queries are excluded here; page-level totals (page_search_totals.sql) include them.
WITH b AS (
  SELECT REGEXP_REPLACE(REGEXP_REPLACE(url, r'[#?].*$', ''), r'/$', '') AS page,
         LOWER(TRIM(query)) AS query,
         SUM(clicks) AS c, SUM(impressions) AS i, SUM(sum_position) AS sp
  FROM {table}
  WHERE (search_type = 'WEB' OR search_type IS NULL)
    AND NOT is_anonymized_query AND query IS NOT NULL
    AND data_date BETWEEN '{start}' AND '{end}'
  GROUP BY 1, 2)
SELECT query, page, c AS clicks, i AS impressions, ROUND(sp / i + 1, 2) AS position
FROM b
WHERE i >= 10 AND sp / i + 1 <= 30
ORDER BY query, i DESC
