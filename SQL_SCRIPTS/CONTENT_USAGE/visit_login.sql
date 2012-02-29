USE td_analytics
CREATE TEMPORARY TABLE tmp_session_3
SELECT DISTINCT m.session_id, x.month, m.geo_country, m.geo_region, m.user_id 
FROM metrics_page_hits m, metrics_month_id_range x  
WHERE m.id BETWEEN x.low AND x.high
AND x.month = '2012-01';


CREATE INDEX by_loc ON tmp_session_3(geo_country, geo_region);

SELECT 'visits', 'us', 'all', month, COUNT(month) n
FROM tmp_session_3
WHERE geo_country = 'us'
GROUP BY month;

SELECT 'logins', 'us', 'all', month, COUNT(month) n
FROM tmp_session_3
WHERE geo_country = 'us'
AND user_id IS NOT NULL
group BY month;

SELECT 'visits', 'us', geo_region state, month, COUNT(month) n
FROM tmp_session_3
WHERE geo_country = 'us'
GROUP BY month, geo_region;

SELECT 'logins', 'us', geo_region state, month, COUNT(month) n
FROM tmp_session_3
WHERE geo_country = 'us'
AND user_id IS NOT NULL
GROUP BY month, geo_region;

