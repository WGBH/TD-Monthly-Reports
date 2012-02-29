USE td_analytics
CREATE TEMPORARY TABLE tmp_session_3
SELECT DISTINCT m.session_id, m.geo_country, m.geo_region, m.user_id 
FROM metrics_page_hits m
WHERE m.id BETWEEN 17901087 and 21000000;

CREATE INDEX by_loc ON tmp_session_3(geo_country, geo_region);

SELECT 'visits', 'us', 'all', '2012-01', COUNT(*) n
FROM tmp_session_3
WHERE geo_country = 'us';

SELECT 'logins', 'us', 'all', '2012-01', COUNT(*) n
FROM tmp_session_3
WHERE geo_country = 'us'
AND user_id IS NOT NULL;

SELECT 'visits', 'us', geo_region state, '2012-01', COUNT(*) n
FROM tmp_session_3
WHERE geo_country = 'us'
GROUP BY geo_region;

SELECT 'logins', 'us', geo_region state, '2012-01', COUNT(*) n
FROM tmp_session_3
WHERE geo_country = 'us'
AND user_id IS NOT NULL
GROUP BY geo_region;

