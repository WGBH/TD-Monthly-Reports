
USE td_analytics
# resource page views - all US visits
SELECT 'resource_visit', 'us', 'all', x.month, COUNT(m.id)
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type IN ('building_block', 'learning_object', 'lesson_plan', 'student_activity', 'teacher_activity')
AND x.month = '2012-01'
GROUP BY x.month;

# resource page views - all US visits by state
SELECT 'resource_visit', 'us', geo_region, x.month, COUNT(m.id)
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.page_type IN ('building_block', 'learning_object', 'lesson_plan', 'student_activity', 'teacher_activity')
AND x.month = '2012-01'
GROUP BY x.month, m.geo_region;

# resource page views - US logins
SELECT 'resource_login', 'us', 'all', x.month, COUNT(m.id)
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.user_id IS NOT NULL
AND m.page_type IN ('building_block', 'learning_object', 'lesson_plan', 'student_activity', 'teacher_activity')
AND x.month = '2012-01'
GROUP BY x.month;

# resource page views - US logins by state
SELECT 'resource_login', 'us', geo_region, x.month, COUNT(m.id)
FROM metrics_page_hits m, metrics_month_id_range x
WHERE m.id BETWEEN x.low AND x.high
AND m.geo_country = 'us'
AND m.user_id IS NOT NULL
AND m.page_type IN ('building_block', 'learning_object', 'lesson_plan', 'student_activity', 'teacher_activity')
AND x.month = '2012-01'
GROUP BY x.month, m.geo_region;

