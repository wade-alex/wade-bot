-- this table creates the average price and index
-- at each time for the 5 cheapest players at each rating
-- where the price is > 0

-- make more indexes by joining the player type
-- table and making that an additional filter

-- Drop the final reporting table if it exists
DROP TABLE IF EXISTS reporting.reg_fodder;

-- Step 1: Rank the players by price and rating
DROP TABLE IF EXISTS price_rank;
SELECT
    FPP.p_oid,
    FPP.rating,
    FPP.price,
    FPP.dttm_price,
    to_timestamp(
        floor(EXTRACT(epoch FROM FPP.dttm_price) / EXTRACT(epoch FROM interval '5 minutes')) * EXTRACT(epoch FROM interval '5 minutes')
    ) AS rounded_date,
    ROW_NUMBER() OVER (PARTITION BY FPP.rating, FPP.dttm_price ORDER BY FPP.price) AS price_rank
into price_rank
FROM
    players.futbin_players_prices FPP
WHERE
    FPP.price <> 0 AND
    extract(minute FROM
        to_timestamp(
            floor(EXTRACT(epoch FROM FPP.dttm_price) / EXTRACT(epoch FROM interval '5 minutes')) * EXTRACT(epoch FROM interval '5 minutes')
        )
    ) IN (0, 15, 30, 45);

-- Step 2: Calculate the index start based on a specific date
DROP TABLE IF EXISTS index_start;
SELECT
    PR.rating,
    AVG(PR.price) AS index_start
INTO temp index_start
FROM price_rank PR
LEFT JOIN players.futbin_players_type T
    on T.p_oid = PR.p_oid
WHERE
    PR.dttm_price::DATE = '2024-09-27'
    AND PR.price_rank < 5
--     and T.type = 'Normal'
GROUP BY PR.rating;

-- Step 3: Create the final reg_fodder table with calculated index
CREATE TABLE reporting.reg_fodder AS
SELECT
    PR.rounded_date,
    PR.rating,
    (AVG(PR.price) / MAX(I.index_start)) * 100 AS index,
    AVG(PR.price) AS avg_price
FROM price_rank PR
JOIN index_start I
    ON I.rating = PR.rating
WHERE PR.price_rank < 5
GROUP BY PR.rounded_date, PR.rating;
