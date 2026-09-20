-- 1. Quelles villes auront les températures les plus élevées ?
SELECT city, date, temp_max
FROM weather_forecast
JOIN cities ON weather_forecast.city_id = cities.city_id
ORDER BY temp_max DESC
LIMIT 5;

-- 2. Quelles villes auront les plus fortes précipitations ?
SELECT city, date, precip
FROM weather_forecast
JOIN cities ON weather_forecast.city_id = cities.city_id
ORDER BY precip DESC
LIMIT 5;

-- 3. Quelles villes présentent le risque moyen le plus élevé ?
SELECT city, ROUND(AVG(risk_score), 2) AS moyenne_risque
FROM weather_forecast
JOIN cities ON weather_forecast.city_id = cities.city_id
GROUP BY city
ORDER BY moyenne_risque DESC
LIMIT 5;

-- 4. Quelles périodes présentent le risque maximal ?
SELECT date, ROUND(AVG(risk_score), 2) AS moyenne_risque, MAX(risk_score) AS max_risque
FROM weather_forecast
GROUP BY date
ORDER BY max_risque DESC, moyenne_risque DESC;

-- 5. Pour chaque ville, quelle période présente le plus grand risque ?
SELECT city, date, risk_score
FROM (
    SELECT c.city, wf.date, wf.risk_score,
           ROW_NUMBER() OVER (PARTITION BY c.city ORDER BY wf.risk_score DESC, wf.date ASC) as rn
    FROM weather_forecast wf
    JOIN cities c ON wf.city_id = c.city_id
) ranked
WHERE rn = 1
ORDER BY risk_score DESC;