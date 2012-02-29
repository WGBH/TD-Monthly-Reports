USE td_now
SELECT 'reg', 'us',
	DATE_FORMAT(u.date_created, '%Y-%m') month,
	'us_td',
	IF(FIND_IN_SET(t.code, 'teacher,student'), t.code, 'other') user_type,
	COUNT(u.id) n
FROM tduser u, org o, tduser_user_type t
WHERE u.org_id = o.id
AND o.country_code = 'us'
AND u.org_id NOT IN (126510, 126511)
AND u.user_type_id = t.id
GROUP BY month, user_type
ORDER BY month;

