-- No need to include in Airflow
-- daily

create schema reporting;

CREATE TABLE reporting.calendar_daily (
    date DATE PRIMARY KEY,
    day_of_week TEXT,
    week_of_year INT,
    day_of_year INT,
    is_weekend BOOLEAN
);

-- Insert daily data into the calendar table (starting from 2024 for example)
INSERT INTO reporting.calendar_daily (date, day_of_week, week_of_year, day_of_year, is_weekend)
SELECT 
    date_series AS date,
    to_char(date_series, 'Day') AS day_of_week,
    EXTRACT(WEEK FROM date_series) AS week_of_year,
    EXTRACT(DOY FROM date_series) AS day_of_year,
    CASE WHEN EXTRACT(ISODOW FROM date_series) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
FROM 
    generate_series('2024-01-01'::DATE, '2030-12-31'::DATE, '1 day') AS date_series;


-- 15 mins
CREATE TABLE reporting.calendar_15min (
    timestamp TIMESTAMP PRIMARY KEY,
    day_of_week TEXT,
    week_of_year INT,
    is_weekend BOOLEAN
);

-- Insert 15-minute interval data into the calendar table (starting from 2024)
INSERT INTO reporting.calendar_15min (timestamp, day_of_week, week_of_year, is_weekend)
SELECT 
    timestamp_series AS timestamp,
    to_char(timestamp_series, 'Day') AS day_of_week,
    EXTRACT(WEEK FROM timestamp_series) AS week_of_year,
    CASE WHEN EXTRACT(ISODOW FROM timestamp_series) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
FROM 
    generate_series('2024-01-01 00:00'::TIMESTAMP, '2030-12-31 23:59'::TIMESTAMP, '15 minutes') AS timestamp_series;
