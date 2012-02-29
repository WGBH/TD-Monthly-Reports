# asset_views.sql

USE td_analytics
SELECT 'asset_visit', 'us', 'ny', STATION, x.month, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us' AND m.geo_region = 'ny'
AND m.page_type IN ('asset_view', 'user_media_view')
GROUP BY x.month;

SELECT 'asset_login', 'us', 'ny', STATION, x.month, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us' AND m.geo_region = 'ny'
AND m.user_id IS NOT NULL
AND m.page_type IN ('asset_view', 'user_media_view')
GROUP BY x.month;

# download.sql

USE td_analytics
SELECT 'download', 'us', 'ny', STATION, x.month, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us' AND m.geo_region = 'ny'
AND m.page_type = 'asset_download_complete'
GROUP BY x.month;

# page_hits.sql

USE td_analytics
SELECT 'page_hits', 'us', 'ny', STATION, x.month, COUNT(m.id)
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us' AND m.geo_region = 'ny'
GROUP BY x.month;

# resource_views.sql

USE td_analytics
SELECT 'resource_visit', 'us', 'ny', STATION, x.month, COUNT(m.id)
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us' AND m.geo_region = 'ny'
AND m.page_type IN ('building_block', 'learning_object', 'lesson_plan', 'student_activity', 'teacher_activity')
GROUP BY x.month;

# resource page views - US logins
SELECT 'resource_login', 'us', 'ny', STATION, x.month, COUNT(m.id)
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us' AND m.geo_region = 'ny'
AND m.user_id IS NOT NULL
AND m.page_type IN ('building_block', 'learning_object', 'lesson_plan', 'student_activity', 'teacher_activity')
GROUP BY x.month;

# visit_login.sql

USE td_analytics
CREATE TEMPORARY TABLE tmp_session
SELECT DISTINCT m.session_id, x.month, m.geo_country, m.geo_region, m.user_id 
FROM metrics_page_hits m, metrics_month_id_range x  
WHERE m.id BETWEEN x.low AND x.high;

CREATE INDEX by_loc ON tmp_session(geo_country, geo_region);

SELECT 'visits', 'us', 'ny', STATION, month, COUNT(month) n
FROM tmp_session
WHERE m.geo_country = 'us' AND m.geo_region = 'ny'
GROUP BY month;

SELECT 'logins', 'us', 'ny', STATION, month, COUNT(month) n
FROM tmp_session
WHERE m.geo_country = 'us' AND m.geo_region = 'ny'
AND user_id IS NOT NULL
group BY month;

