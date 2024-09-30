
DROP TABLE IF EXISTS reporting.reg_fodder_table;
CREATE TABLE reporting.reg_fodder_table AS
SELECT
    RF.rating,
    -- Average price over the last day (1 day)
    AVG(CASE
            WHEN RF.rounded_date >= CURRENT_TIMESTAMP - INTERVAL '1 day'
            THEN RF.avg_price
        END) AS avg_price_last_day,
    -- Average price over the last 3 days
    AVG(CASE
            WHEN RF.rounded_date >= CURRENT_TIMESTAMP - INTERVAL '3 days'
            THEN RF.avg_price
        END) AS avg_price_last_3_days,
    -- Average price over the last week (7 days)
    AVG(CASE
            WHEN RF.rounded_date >= CURRENT_TIMESTAMP - INTERVAL '7 days'
            THEN RF.avg_price
        END) AS avg_price_last_week,
        -- Average price over the previous week (14 to 7 days ago)
    AVG(CASE
            WHEN RF.rounded_date >= CURRENT_TIMESTAMP - INTERVAL '14 days'
                 AND RF.rounded_date < CURRENT_TIMESTAMP - INTERVAL '7 days'
            THEN RF.avg_price
        END) AS avg_price_previous_week
FROM
    reporting.reg_fodder RF
GROUP BY
    RF.rating
ORDER BY
    RF.rating ASC;