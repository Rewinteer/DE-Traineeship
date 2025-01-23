--Вывести количество фильмов в каждой категории, отсортировать по убыванию.

SELECT
	c.name,
	COUNT(fc.film_id) AS film_count
FROM
	film_category fc
JOIN category c ON c.category_id = fc.category_id
GROUP BY c.name
ORDER BY film_count DESC;


--Вывести 10 актеров, чьи фильмы большего всего арендовали, отсортировать по убыванию.

	-- 10 актеров из наиболее арендуемых фильмов:

		SELECT
			COUNT(*) AS film_rent_count,
			CONCAT(a.first_name, ' ', a.last_name) AS actor_name
		FROM
			rental r
		JOIN inventory i ON i.inventory_id = r.inventory_id
		JOIN film_actor fa ON fa.film_id = i.film_id
		JOIN actor a ON fa.actor_id = a.actor_id
		GROUP BY i.film_id, actor_name
		ORDER BY film_rent_count DESC, actor_name ASC
		LIMIT 10;

--Вывести категорию фильмов, на которую потратили больше всего денег.

SELECT
	c.name,
	sum(p.amount) as spent_money
FROM
	payment p
JOIN rental r ON p.rental_id = r.rental_id
JOIN inventory i ON i.inventory_id = r.inventory_id
JOIN film f ON i.film_id = f.film_id
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
GROUP BY c.name
ORDER BY spent_money DESC
LIMIT 1;


--Вывести названия фильмов, которых нет в inventory. Написать запрос без использования оператора IN.

SELECT
	f.title
FROM
	film f
LEFT JOIN inventory i ON f.film_id = i.film_id
WHERE i.film_id IS null;

--Вывести топ 3 актеров, которые больше всего появлялись в фильмах в категории “Children”. Если у нескольких актеров одинаковое кол-во фильмов, вывести всех.

WITH top_values AS (
	SELECT
		DISTINCT COUNT(*) AS cnt
	FROM
		actor a
	JOIN film_actor fa ON a.actor_id = fa.actor_id
	JOIN film_category fc ON fa.film_id = fc.film_id
	JOIN category c ON fc.category_id = c.category_id
	WHERE c."name" = 'Children'
	GROUP BY c."name", a.first_name, a.last_name
	ORDER BY cnt DESC LIMIT 3
) SELECT
	CONCAT(a.first_name, ' ', a.last_name) AS name,
	c."name" AS film_category,
	COUNT(*) AS appeared_times
FROM
	actor a
JOIN film_actor fa ON a.actor_id = fa.actor_id
JOIN film_category fc ON fa.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
WHERE c."name" = 'Children'
GROUP BY c."name", a.first_name, a.last_name
HAVING COUNT(*) in (SELECT cnt FROM top_values)
ORDER BY appeared_times DESC;



--Вывести города с количеством активных и неактивных клиентов (активный — customer.active = 1). Отсортировать по количеству неактивных клиентов по убыванию.

SELECT
	ct.city,
	COUNT(CASE c.active  WHEN 1 THEN 1 ELSE NULL END) as active,
  	COUNT(CASE c.active WHEN 0 THEN 1 ELSE NULL END) as unactive
FROM
	customer c
LEFT JOIN address a ON c.address_id = a.address_id
JOIN city ct ON a.city_id = ct.city_id
GROUP BY ct.city
ORDER BY unactive DESC, ct.city;



--Вывести категорию фильмов, у которой самое большое кол-во часов суммарной аренды в городах (customer.address_id в этом city),
--и которые начинаются на букву “a”. То же самое сделать для городов в которых есть символ “-”. Написать все в одном запросе.

WITH category_ranks_per_city AS (
	SELECT
		ct.city AS city,
		c.name AS category,
		SUM (r.return_date - r.rental_date) AS total_rental_time,
		ROW_NUMBER() OVER (PARTITION BY ct.city ORDER BY SUM (r.return_date - r.rental_date) DESC) AS rank
	FROM
		category c
	JOIN film_category fc ON c.category_id = fc.category_id
	JOIN inventory i ON i.film_id = fc.film_id
	JOIN rental r ON i.inventory_id = r.inventory_id
	JOIN customer cr ON r.customer_id = cr.customer_id
	JOIN address a ON cr.address_id = a.address_id
	JOIN city ct ON a.city_id = ct.city_id
	WHERE ct.city LIKE 'A%' OR ct.city LIKE '%-%'
	GROUP BY ct.city, c.name
	ORDER BY ct.city, total_rental_time DESC
)
SELECT
	city,
	category
FROM
	category_ranks_per_city
WHERE
	category_ranks_per_city."rank" = 1
ORDER BY city;
