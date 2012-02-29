USE td_now
SELECT 'reg', 'world',
	DATE_FORMAT(u.date_created, '%Y-%m') month,
	'WORLD_TD',
	IF(FIND_IN_SET(t.code, 'teacher,student'), t.code, 'other') user_type,
	COUNT(u.id) n
FROM tduser u, org o, tduser_user_type t
WHERE u.org_id = o.id
AND u.org_id NOT IN (126510, 126511)
AND u.user_type_id = t.id
GROUP BY month, user_type
ORDER BY month;

