-- GA4 export: sessions per landing page and default channel group, last-click.
-- Replace {ga4} with `<project>.analytics_<property_id>.events_*` and set the suffix dates (YYYYMMDD).
-- ai_src counts sessions from AI assistants by medium or source, for properties without an AI channel group.
SELECT REGEXP_REPLACE(REGEXP_REPLACE((SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_location'),
         r'[#?].*$', ''), r'/$', '') AS page,
       session_traffic_source_last_click.cross_channel_campaign.default_channel_group AS ch,
       COUNT(*) AS sessions,
       COUNTIF(session_traffic_source_last_click.cross_channel_campaign.medium = 'ai-assistant'
               OR REGEXP_CONTAINS(IFNULL(session_traffic_source_last_click.cross_channel_campaign.source, ''),
                                  r'chatgpt|openai|perplexity|claude|gemini|copilot')) AS ai_src
FROM {ga4}
WHERE event_name = 'session_start' AND _TABLE_SUFFIX BETWEEN '{start_ymd}' AND '{end_ymd}'
GROUP BY 1, 2
