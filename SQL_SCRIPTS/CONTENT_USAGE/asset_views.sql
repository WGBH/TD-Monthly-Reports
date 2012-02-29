USE td_analytics
SELECT 'asset_visit', 'us', 'all', x.month, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type IN ('asset_view', 'user_media_view')
AND x.month = '2012-01'
GROUP BY x.month;

SELECT 'asset_visit', 'us', geo_region, x.month, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type IN ('asset_view', 'user_media_view')
AND x.month = '2012-01'
GROUP BY x.month, m.geo_region;

SELECT 'asset_login', 'us', 'all', x.month, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.user_id IS NOT NULL
AND m.page_type IN ('asset_view', 'user_media_view')
AND x.month = '2012-01'
GROUP BY x.month;

SELECT 'asset_login', 'us', geo_region, x.month, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.user_id IS NOT NULL
AND m.page_type IN ('asset_view', 'user_media_view')
AND x.month = '2012-01'
GROUP BY x.month, m.geo_region;

