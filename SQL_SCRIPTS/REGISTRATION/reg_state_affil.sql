USE td_now
SELECT 'reg', o.state_region state,
	DATE_FORMAT(u.date_created, '%Y-%m') month, a.code affiliate,
	IF(FIND_IN_SET(t.code, 'teacher,student'), t.code, 'other') user_type,
	COUNT(u.id) n
FROM tduser u, org o, affiliate a, tduser_user_type t
WHERE u.org_id = o.id
AND o.country_code = 'us'
AND u.org_id NOT IN (126510, 126511)
AND u.affiliate_id = a.id
AND u.user_type_id = t.id
GROUP BY month, o.state_region, affiliate, user_type
ORDER BY month;

