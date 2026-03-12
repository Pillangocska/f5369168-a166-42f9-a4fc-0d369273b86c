-- =============================================================================
-- Task 2 - The Most Expensive Puppy
-- (I choose PostgreSQL)
-- =============================================================================


-- -------------------------------------------------------------------------
-- 1. DDL: Create the table (just for testing)
-- -------------------------------------------------------------------------

DROP TABLE IF EXISTS my_puppies;

CREATE TABLE my_puppies (
    name           VARCHAR(100)  NOT NULL,
    date_of_birth  DATE          NOT NULL,
    breed          VARCHAR(100)  NOT NULL,
    year           INT           NOT NULL,
    month          VARCHAR(20)   NOT NULL,
    cost           NUMERIC(10,2) NOT NULL
);

ALTER TABLE my_puppies
    ADD CONSTRAINT uq_puppy_month UNIQUE (name, date_of_birth, year, month);


-- -------------------------------------------------------------------------
-- 2. Test data: 5 puppies x 24 months
-- -------------------------------------------------------------------------

INSERT INTO my_puppies (name, date_of_birth, breed, year, month, cost)
VALUES
    ('Pancakes',  '2015-04-12', 'Boston Terrier',        2018, 'January',  17),
    ('Pancakes',  '2015-04-12', 'Boston Terrier',        2018, 'February', 20),
    ('Biscuit',   '2013-08-30', 'King Charles Cavalier', 2018, 'January',  22),
    ('Biscuit',   '2013-08-30', 'King Charles Cavalier', 2018, 'February', 25),
    ('Waffles',   '2018-01-01', 'French Bulldog',        2018, 'January',  32),
    ('Waffles',   '2018-01-01', 'French Bulldog',        2018, 'February', 35),
    ('Muffin',    '2016-06-15', 'Golden Retriever',      2018, 'January',  20),
    ('Muffin',    '2016-06-15', 'Golden Retriever',      2018, 'February', 23),
    ('Sprinkles', '2017-11-03', 'Beagle',                2018, 'January',  15),
    ('Sprinkles', '2017-11-03', 'Beagle',                2018, 'February', 18);


-- =========================================================================
-- QUERIES
-- =========================================================================


-- -------------------------------------------------------------------------
-- Q1: Dog with the highest total spend relative to its age
--     Formula: SUM(cost) / age_in_years
--     Age is calculated at the end of the data period (2019-12-31).
-- -------------------------------------------------------------------------

WITH puppy_totals AS (
    SELECT
        name,
        date_of_birth,
        breed,
        SUM(cost)                                              AS total_cost,
        EXTRACT(YEAR FROM AGE(DATE '2019-12-31', date_of_birth)) AS age_years
    FROM my_puppies
    GROUP BY name, date_of_birth, breed
)
SELECT
    name,
    date_of_birth,
    breed,
    total_cost,
    age_years,
    ROUND(total_cost / NULLIF(age_years, 0), 2) AS cost_per_year_of_age
FROM puppy_totals
ORDER BY cost_per_year_of_age DESC
LIMIT 1;


-- -------------------------------------------------------------------------
-- Q2: Descriptive statistics useful for the veterinarian
-- -------------------------------------------------------------------------

-- 2a) Overall cost statistics per puppy (lifetime view)
SELECT
    name,
    breed,
    COUNT(*)                           AS visit_months,
    SUM(cost)                          AS total_cost,
    ROUND(AVG(cost), 2)                AS avg_monthly_cost,
    MIN(cost)                          AS min_monthly_cost,
    MAX(cost)                          AS max_monthly_cost,
    ROUND(STDDEV_SAMP(cost), 2)        AS stddev_monthly_cost,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY cost)   AS median_monthly_cost
FROM my_puppies
GROUP BY name, date_of_birth, breed
ORDER BY total_cost DESC;


-- 2b) Cost statistics per breed (helps identify expensive breeds)
SELECT
    breed,
    COUNT(DISTINCT name)               AS puppy_count,
    SUM(cost)                          AS total_cost,
    ROUND(AVG(cost), 2)                AS avg_monthly_cost,
    MIN(cost)                          AS min_monthly_cost,
    MAX(cost)                          AS max_monthly_cost,
    ROUND(STDDEV_SAMP(cost), 2)        AS stddev_monthly_cost,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY cost)   AS median_monthly_cost
FROM my_puppies
GROUP BY breed
ORDER BY avg_monthly_cost DESC;


-- 2c) Cost statistics per year (trend over time)
SELECT
    year,
    COUNT(DISTINCT name)               AS puppies_treated,
    SUM(cost)                          AS total_cost,
    ROUND(AVG(cost), 2)                AS avg_monthly_cost,
    MIN(cost)                          AS min_monthly_cost,
    MAX(cost)                          AS max_monthly_cost,
    ROUND(STDDEV_SAMP(cost), 2)        AS stddev_monthly_cost,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY cost)   AS median_monthly_cost
FROM my_puppies
GROUP BY year
ORDER BY year;


-- 2d) Monthly seasonality (which months tend to be most expensive?)
SELECT
    month,
    SUM(cost)                          AS total_cost,
    ROUND(AVG(cost), 2)                AS avg_cost,
    MIN(cost)                          AS min_cost,
    MAX(cost)                          AS max_cost
FROM my_puppies
GROUP BY month
ORDER BY avg_cost DESC;


-- -------------------------------------------------------------------------
-- Q3: Breed of the puppy with the highest total spend in 2018
-- -------------------------------------------------------------------------

SELECT
    name,
    breed,
    SUM(cost) AS total_cost_2018
FROM my_puppies
WHERE year = 2018
GROUP BY name, date_of_birth, breed
ORDER BY total_cost_2018 DESC
LIMIT 1;
