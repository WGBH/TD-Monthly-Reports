
USE td_analytics
# resource page views - all US visits
SELECT 'resource_view_top100', 'us', 'all', x.month, SUBSTRING_INDEX(SUBSTRING_INDEX(url_path, '/', -2), '/', 1) code, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type IN ('building_block', 'learning_object', 'lesson_plan', 'student_activity', 'teacher_activity')
GROUP BY x.month, code;

# resource page views - all US visits by state
SELECT 'resource_view_top100', 'us', geo_region, x.month, SUBSTRING_INDEX(SUBSTRING_INDEX(url_path, '/', -2), '/', 1) code, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type IN ('building_block', 'learning_object', 'lesson_plan', 'student_activity', 'teacher_activity')
GROUP BY x.month, code, m.geo_region;

# asset page views - all US visits
SELECT 'asset_view_top100', 'us', 'all', x.month, SUBSTRING_INDEX(SUBSTRING_INDEX(url_path, '/', -2), '/', 1) code, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type IN ('asset_view', 'user_media_view')
GROUP BY x.month, code;

# asset page views - all US visits by state
SELECT 'asset_view_top100', 'us', geo_region, x.month, SUBSTRING_INDEX(SUBSTRING_INDEX(url_path, '/', -2), '/', 1) code, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type IN ('asset_view', 'user_media_view')
GROUP BY x.month, code, m.geo_region;

# 
# downloads - all US visits
SELECT 'download_top100', 'us', 'all', x.month, SUBSTRING_INDEX(SUBSTRING_INDEX(url_path, '/', -2), '/', 1) code, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type = 'asset_download_complete'
GROUP BY x.month, code;

# downloads - all US visits by state
SELECT 'download_top100', 'us', geo_region, x.month, SUBSTRING_INDEX(SUBSTRING_INDEX(url_path, '/', -2), '/', 1) code, COUNT(m.id) n
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type = 'asset_download_complete'
GROUP BY x.month, code, m.geo_region;

# 
