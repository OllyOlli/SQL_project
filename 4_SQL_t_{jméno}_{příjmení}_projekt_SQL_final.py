"""
projekt_2.py: 
author: Olga H.
email: Olcah@email.cz
discord: Olly#1959


SQL
Zadání:

Od Vašeho kolegy statistika jste obdrželi následující email:

Dobrý den,

snažím se určit faktory, které ovlivňují rychlost šíření koronaviru na úrovni jednotlivých států. Chtěl bych Vás, coby datového analytika, požádat o pomoc s přípravou dat, která potom budu statisticky zpracovávat. Prosím Vás o dodání dat podle požadavků sepsaných níže.

Výsledná data budou panelová, klíče budou stát (country) a den (date). Budu vyhodnocovat model, který bude vysvětlovat denní nárůsty nakažených v jednotlivých zemích. Samotné počty nakažených mi nicméně nejsou nic platné - je potřeba vzít v úvahu také počty provedených testů a počet obyvatel daného státu. Z těchto tří proměnných je potom možné vytvořit vhodnou vysvětlovanou proměnnou. Denní počty nakažených chci vysvětlovat pomocí proměnných několika typů. Každý sloupec v tabulce bude představovat jednu proměnnou. Chceme získat následující sloupce:

1) Časové proměnné
binární proměnná pro víkend / pracovní den
roční období daného dne (zakódujte prosím jako 0 až 3)
2) Proměnné specifické pro daný stát
hustota zalidnění - ve státech s vyšší hustotou zalidnění se nákaza může šířit rychleji
HDP na obyvatele - použijeme jako indikátor ekonomické vyspělosti státu
GINI koeficient - má majetková nerovnost vliv na šíření koronaviru?
dětská úmrtnost - použijeme jako indikátor kvality zdravotnictví
medián věku obyvatel v roce 2018 - státy se starším obyvatelstvem mohou být postiženy více
podíly jednotlivých náboženství - použijeme jako proxy proměnnou pro kulturní specifika. Pro každé náboženství v daném státě bych chtěl procentní podíl jeho příslušníků na celkovém obyvatelstvu
rozdíl mezi očekávanou dobou dožití v roce 1965 a v roce 2015 - státy, ve kterých proběhl rychlý rozvoj mohou reagovat jinak než země, které jsou vyspělé už delší dobu
3) Počasí (ovlivňuje chování lidí a také schopnost šíření viru)
průměrná denní (nikoli noční!) teplota
počet hodin v daném dni, kdy byly srážky nenulové
maximální síla větru v nárazech během dne
Napadají Vás ještě nějaké další proměnné, které bychom mohli použít? Pokud vím, měl(a) byste si vystačit s daty z následujících tabulek: countries, economies, life_expectancy, religions, covid19_basic_differences, covid19_testing, weather, lookup_table.

V případě nejasností se mě určitě zeptejte.

S pozdravem, Student (a.k.a. William Gosset)

"""

-- hustota zalidnění = (rozloha * počet obyvatel) / rozloha
 
-- HDP na obyvatele - celkové HDP / počet obyvatel státu


-- gigi koeficient - majetková nerovnost


-- dětská úmrtnost


-- medián věku


-- procentualni podíl nabozenstvi na celkovém obyvatelstvu pro jednotlive zeme v roce 2020


-- očekávaná doba dožití (rozdíl 1965 a 2015)


-- FINAL TABLE
CREATE OR REPLACE TABLE t_Olly_projekt_SQL_final AS
SELECT ctr.*, cov.date, cov.confirmed, cov.tests_performed, 
rel.Christianity, rel.Islam, rel.Unaffiliated_religions, rel.Hinduism, rel.Buddhism, rel.Folk_religions,
rel.Other_religions, rel.Judaism, wet.city, wet.binary_day, wet.season_code, wet.daily_avg_temp,
wet.count_rain_hours, wet.max_day_wind
FROM
SELECT * FROM t_michal_lehuta_SQLprojekt_Countries) ctr
LEFT JOIN
SELECT * FROM t_Olly_SQLprojekt_Religions) rel
ON ctr.country = rel.country
LEFT JOIN 
SELECT * FROM t_Olly_SQLprojekt_Covid19) cov
ON ctr.country = cov.country
LEFT JOIN
SELECT * FROM t_Olly_SQLprojekt_Weather) wet 
ON cov.date = wet.date AND ctr.capital_city = wet.city


-- COUNTRIES TABLE
CREATE OR REPLACE TABLE t_Olly_SQLprojekt_Countries AS
SELECT ctr.country, ec.population, ec.GDP_per_head, ctr.population_density, ctr.median_age_2018, ec2.mortaliy_under5, 
ec3.gini, ctr.capital_city, (le.life_exp2015-le2.life_exp1965) 
AS life_exp_diff
FROM
(SELECT country, population_density, median_age_2018, capital_city FROM  countries) ctr

LEFT JOIN
SELECT country, population, ROUND (GDP/population, 2) AS GDP_per_head FROM economies WHERE GDP IS NOTNULL GROUP BY country) ec 
ON ctr.country = ec2.country

LEFT JOIN
(SELECT country, gini, MAX (year) FROM economies WHERE gini IS NOT NULL GROUP BY country) ec3
ON ctr.country = ec3.country

LEFT JOIN
SELECT country, life_expectancy AS life_exp2015 FROM life_expectancy WHERE year = 2015) le
ON ctr.country = le.country

LEFT JOIN 
(SELECT country, life_expectancy AS life_exp1965 FROM life_expectancy WHERE year = 1965) le2
ON le.country = le2.country ORDER BY ec3.gini DESC


-- RELIGION TABLE
CREATE OR REPLACE TABLE  t_Olly_SQLprojekt_Religions AS
SELECT rbase.country, rbase.population,
ROUND(rbase.Christianity/r1.total_population*100, 2) AS Christianity, ROUND(rbase.Islam/r1.total_population*100, 2) AS Islam, ROUND(rbase.Unaffiliated_religions/r1.total_population*100, 2) AS Unaffiliated_religions,
ROUND(rbase.Hinduism/r1.total_population*100, 2) AS Hinduism, ROUND(rbase.Buddhism/r1.total_population*100, 2) AS Buddhism, ROUND(rbase.Folk_religions/r1.total_population*100, 2) AS Folk_religions,
ROUND(rbase.Other_religions/r1.total_population*100, 2) AS Other_religions, ROUND(rbase.Judaism/r1.total_population*100, 2) AS Judaism
FROM

SELECT country, SUM (population) AS population,
SUM(CASE WHEN religion = 'Christianity' THEN population ELSE 0 END) AS Christianity,
SUM(CASE WHEN religion = 'Islam' THEN population ELSE 0 END) AS Islam,
SUM(CASE WHEN religion = 'Unaffiliated Religions' THEN population ELSE 0 END) AS Unaffiliated_religions, 
SUM(CASE WHEN religion = 'Hinduism' THEN population ELSE 0 END) AS Hinduism,
SUM(CASE WHEN religion = 'Buddhism' THEN population ELSE 0 END) AS Buddhism, 
SUM(CASE WHEN religion = 'Folk Religions' THEN population ELSE 0 END) AS Folk_religions,
SUM(CASE WHEN religion = 'Other Religions' THEN population ELSE 0 END) AS Other_religions,
SUM(CASE WHEN religion = 'Judaism' THEN population ELSE 0 END) AS Judaism

FROM religions AS r WHERE year = 2020 AND population != 0 GROUP BY country) rbase 
JOIN 
SELECT country, SUM (population) AS total_population FROM religions r2 WHERE year = 2020 GROUP BY country) r1 
ON rbase.country = r1.country 


-- COVID TABLE - 
CREATE OR REPLACE TABLE AS t_olly_SQLprojekt_Covid19
SELECT cbd.date, cbd.country, cbd.confirmed, ct.tests_performed FROM
(SELECT date, CASE country WHEN "Czechia" THEN "Czech Republic" ELSE country END AS country, confirmed FROM covid19_basic_differences) cbd 
JOIN
(SELECT country, date, tests_performed FROM covid19_tests ) ct
ON cbd.date = ct.date AND cbd.country = ct.country


-- WEATHER TABLE
CREATE OR REPLACE TABLE t_olly_SQLprojekt_Weather AS
SELECT w1.city, w1.date, w2.binary_day, w2.season_code, w2.daily_avg_temp, w3.count_rain_hours, w4.max_day_wind FROM
(SELECT city, date FROM weather GROUP BY city, date) w1
LEFT JOIN
(SELECT city, date,


-- binární proměnná pro víkend = 1, pracovní den = 0
CASE WHEN dayname(date) IN ('Sunday', 'Saturday') THEN 1 ELSE 0 AND AS binary_day,


-- roční období daného dne jaro = 0, léto = 1, podzim = 2, zima = 3
CASE WHEN MONTH (date) IN (12, 1, 2) THEN 3
	WHEN MONTH (date) IN (3, 4, 5) THEN 0
	WHEN MONTH (date) IN (6, 7, 8) THEN 1 ELSE 2 END AS season_code,


-- průměrná denní teplota - průměr teplot v rozmezí 6 - 18 hodinou
AVG (temp) AS daily_avg_temp FROM weather WHERE HOUR IS BETWEEN (6, 9, 12, 15, 18) GROUP BY date, city) w2
ON w1.date = w2.date AND w1.city = w2.city
LEFT JOIN


-- počet hodin v daném dni, kdy byly srážky nenulové
SELECT city, date, COUNT (rain) AS count_rain_hours FROM weather WHERE rain != 0 GROUP BY city, date) w3
ON w1.date = w3.date AND w1.city = w3.city
LEFT JOIN


-- maximální síla větru v nárazech během dne, pro daný den a město
(SELECT city, date, MAX (wind) AS max_day_wind FROM weather GROUP BY city, date) w4 
ON w2.date = w4.date AND w1.city = w4.city