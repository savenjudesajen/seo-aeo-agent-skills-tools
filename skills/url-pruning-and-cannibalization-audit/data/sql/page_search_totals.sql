-- Page-level search totals for the window, anonymized queries included.
-- Feeds the page value check: impressions and clicks per URL.
SELECT REGEXP_REPLACE(REGEXP_REPLACE(url, r'[#?].*$', ''), r'/$', '') AS page,
       SUM(impressions) AS impressions, SUM(clicks) AS clicks
FROM {table}
WHERE data_date BETWEEN '{start}' AND '{end}'
GROUP BY 1
