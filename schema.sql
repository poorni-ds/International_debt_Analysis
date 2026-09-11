create Database if not exists International_debt;
USE international_debt;

--COUNTRY TABLE--

Create Table countries (
    Country_Code CHAR(3) Primary Key,
    Country_Name VARCHAR(150) NOT NULL,
    Region VARCHAR(100),
    Income_group VARCHAR(100)
);

--INDICATORS TABLE--
Create Table indicators (
    Series_Code VARCHAR(30) Primary Key,
    Series_Name VARCHAR(255) NOT NULL,
    Topic VARCHAR(150),
    aggregation_Method VARCHAR(100)
);

Create Table debt_data(
    ID BIGINT AUTO_INCREMENT Primary KEY,
    Country_Code CHAR(3) NOT NULL,
    Series_Code VARCHAR(30),
    year INT NOT NULL,
    Value DOUBLE,
    CONSTRAINT fk_debt_country
        FOREIGN KEY(Country_Code) References countries(Country_Code),
    CONSTRAINT fk_debt_series
        FOREIGN Key(Series_Code) References indicators(Series_Code),
-- prevents duplicate (country, indicator, year) combinations
    CONSTRAINT uq_debt_record UNIQUE (country_code, series_code, year)
);

-- Speeds up the most common query patterns (filter/group by country or indicator)

CREATE INDEX idx_debt_country ON debt_data(country_code);
CREATE INDEX idx_debt_series ON debt_data(series_code);
CREATE INDEX idx_debt_year ON debt_data(year);
 
--1.Distinct Country--
Select distinct Country_Name
from countries;

--2.Country Count--
select Count(distinct Country_Name) as Country_count
from countries;

--3.Indicators Count--
select Count(distinct Series_Name) as Indicators_count
from indicators; 

--4.10 records of the dataset--
select * from Countries
LIMIT 10;
Select *from debt_data
Limit 10;
select * from indicators
Limit 10;

--5.calculate the total debt--
select sum(Value)
 as Total_globaldebt
 from debt_data;

--6.list all unique indicators name--
select distinct(Series_Name) as Indicators
from indicators;

--7.Number of records for each country--
SELECT C.Country_Name,
       COUNT(*) AS Record_Count
FROM Countries C
JOIN debt_data D
    ON C.Country_Code = D.Country_Code
GROUP BY C.Country_Name
ORDER BY Record_Count DESC;

--8.records where debt is greater than 1 billion USD.--
select * from debt_data
where Value > 1000000000;

--9.min,max,avg of debt value
select min(Value) as Minimum_debtvalue, 
max(Value) as Maximum_debtvalue,
Avg(Value) as Average_debtvalue
from debt_data;

--10.Count total number of records in the dataset--
select count(*) from debt_data;


-----------------------------------------------------------------------------------------------------------------------------------------------------

--INTERMEDIATE LEVEL--

--1.Total debt for each country--
select C.Country_Name,
sum(D.Value) as Total_debt
from countries C
JOIN debt_data D
ON C.Country_Code = D.country_Code
group by Country_Name;

--2.Top 10 Countries with highest total debt--
select C.Country_Name,
sum(D.Value) as Total_debt
from countries C
JOIN debt_data D
ON C.Country_Code = D.country_Code
group by Country_Name 
order by Total_debt desc
limit 10;

--3. average debt value per country --
SELECT c.Country_Name, AVG(d.value) AS Average_Debt
FROM countries c
JOIN debt_data d ON c.Country_Code = d.Country_Code
GROUP BY c.Country_Name;

-- 4.Total debt for each Indicator--
select I.Series_Name as Indicators,sum(D.Value) as Total_Debt
from indicators I
JOIN debt_data D 
on I.Series_Code = D.Series_Code
group by Series_Name;

--5.Indicator contributing to the highest debt--
Select I.Series_Name as Indicators, sum(D.Value) as Total_Debt
from indicators I
JOIN debt_data D 
on I.Series_Code = D.Series_Code
group by Series_Name
ORDER BY Total_Debt DESC
LIMIT 1;

--6.Country with lowestdebt---

Select C.Country_Name,sum(D.Value) as Total_debt
from Countries C
JOIN debt_data D
on C. Country_Code = D.Country_Code
group by C.Country_Name
order by Total_debt ASC
LIMIT 1;

--7.Debt for each Country and Indicator Combinations--
select C.Country_Name,I.Series_Name as Indicator,sum(D.Value) as Total_debt
from debt_data D
JOIN Countries C
on D.Country_Code = C.Country_Code
Join indicators I
on D.Series_Code = I.Series_Code
group by C.Country_Name, I.Series_Name;

--8.number od Indicators each countries has--

select distinct(Country_Name),Count(I.Series_Name) as Indicators
from indicators I
Join debt_data D
on I.Series_Code = D.Series_Code
Join countries C
on D.Country_Code = C.Country_Code
group by Country_Name;


--9.Debt value above the global average--
SELECT C.Country_Name,
       SUM(D.Value) AS Total_debt
FROM countries C
JOIN debt_data D
    ON C.Country_Code = D.Country_Code
GROUP BY C.Country_Name
HAVING SUM(D.Value) > (
    SELECT AVG(Country_Totals.Total_debt)
    FROM (
        SELECT Country_Code,
               SUM(Value) AS Total_debt
        FROM debt_data
        GROUP BY Country_Code
    ) AS Country_Totals
)
ORDER BY Total_debt DESC;

--10.Ranking countries based on totals highest - lowest--
SELECT C.Country_Name,
       SUM(D.Value) AS Total_debt,
       RANK() OVER (ORDER BY SUM(D.Value) DESC) AS Debt_Rank
FROM Countries C
JOIN debt_data D
    ON C.Country_Code = D.Country_Code
GROUP BY C.Country_Name
ORDER BY Debt_Rank;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


--Advanced--

--1.Top 5 Indicators contributing most to the global debt--
select I.Series_Name as Indicators,
Sum(D.Value) as Total_debt
from indicators I
Join debt_data D
on I.Series_Code = D.Series_Code
group by Indicators
order by Total_debt desc
Limit 5;

--2.Percentage contribution of each country to total global debt
Select C.Country_Name,
SUM(D.Value) / (SELECT SUM(Value) FROM debt_data) *100 as Percentage_contribution
from countries C
Join debt_data D
on C.Country_Code = D.Country_Code
group by Country_Name;

--3.the top 3 countries for each indicator based on debt--
SELECT *
FROM (
    SELECT 
        C.Country_Name,
        I.Series_Name AS Indicators,
        SUM(D.Value) AS Total_debt,
        RANK() OVER (
            PARTITION BY I.Series_Name
            ORDER BY SUM(D.Value) DESC
        ) AS debt_rank
    FROM Countries C
    JOIN debt_data D
        ON C.Country_Code = D.Country_Code
    JOIN indicators I
        ON I.Series_Code = D.Series_Code
    GROUP BY C.Country_Name, I.Series_Name
) AS ranked_data
WHERE debt_rank <= 3
ORDER BY Indicators, debt_rank;

--4.difference between maximum and minimum debt for each country--
Select C.Country_Name,
(max(D.Value) - Min(D.Value)) as difference
from countries C
Join debt_data D
ON C.Country_Code = D.Country_Code
group by Country_Name;

--5. view for the top 10 countries with highest debt--
Create View Countries_with_highestdebt AS
SELECT C.Country_Name,
sum(D.Value) as Total_debt
from countries C
join debt_data D
on C.Country_Code = D.Country_Code
group by C.Country_Name
order by Total_debt desc
LIMIT 10;

--6.Categorize the countries--
SELECT 
    C.Country_Name,
    SUM(D.Value) AS Total_Debt,
    CASE
        WHEN SUM(D.Value) < 1000000000000 THEN 'Low Debt'
        WHEN SUM(D.Value) < 10000000000000 THEN 'Medium Debt'
        ELSE 'High Debt'
    END AS Debt_Category
FROM countries C
JOIN debt_data D
    ON C.Country_Code = D.Country_Code
GROUP BY C.Country_Name;

--7.Use window functions to calculate cumulative debt per country.
SELECT
    I.Series_Name AS Indicator,
    AVG(D.Value) AS Average_Debt
FROM indicators I
JOIN debt_data D
    ON I.Series_Code = D.Series_Code
GROUP BY I.Series_Name
HAVING AVG(D.Value) > (
    SELECT AVG(Value)
    FROM debt_data
)
ORDER BY Average_Debt DESC;

--8.indicators where average debt is higher than overall average debt--
SELECT 
    I.Series_Name AS Indicator,
    AVG(D.Value) AS Average_Debt
FROM indicators I
JOIN debt_data D
    ON I.Series_Code = D.Series_Code
GROUP BY I.Series_Name
HAVING AVG(D.Value) > (
    SELECT AVG(Value)
    FROM debt_data
)
ORDER BY Average_Debt DESC;

--9.countries contributing more than 5% of global debt.--
SELECT 
    C.Country_Name,
    SUM(D.Value) AS Total_Debt,
    SUM(D.Value) / (SELECT SUM(Value) FROM debt_data) * 100 AS Debt_Percentage
FROM countries C
JOIN debt_data D
    ON C.Country_Code = D.Country_Code
GROUP BY C.Country_Name
HAVING SUM(D.Value) / (SELECT SUM(Value) FROM debt_data) * 100 > 5
ORDER BY Debt_Percentage DESC;

--10.the most dominant indicator (highest contribution) for each country.--doe

SELECT *
FROM (
    SELECT
        C.Country_Name,
        I.Series_Name AS Indicator,
        SUM(D.Value) AS Total_Debt,
        RANK() OVER (
            PARTITION BY C.Country_Name
            ORDER BY SUM(D.Value) DESC
        ) AS Indicator_Rank
    FROM countries C
    JOIN debt_data D
        ON C.Country_Code = D.Country_Code
    JOIN indicators I
        ON I.Series_Code = D.Series_Code
    GROUP BY C.Country_Name, I.Series_Name
) AS Ranked_Indicators
WHERE Indicator_Rank = 1
ORDER BY Country_Name;
