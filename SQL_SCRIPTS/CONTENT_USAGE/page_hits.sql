USE td_analytics
SELECT 'page_hits', 'us', 'all', x.month, COUNT(m.id)
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND x.month = '2012-01'
GROUP BY x.month;

SELECT 'page_hits', 'us', geo_region, x.month, COUNT(m.id)
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND x.month = '2012-01'
GROUP BY x.month, m.geo_region;

