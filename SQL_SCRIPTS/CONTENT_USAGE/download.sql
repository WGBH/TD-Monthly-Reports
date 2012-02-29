USE td_analytics
SELECT 'download', 'us', 'all', x.month, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type = 'asset_download_complete'
AND x.month = '2012-01'
GROUP BY x.month;

SELECT 'download', 'us', geo_region, x.month, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type = 'asset_download_complete'
AND x.month = '2012-01'
GROUP BY x.month, m.geo_region;

