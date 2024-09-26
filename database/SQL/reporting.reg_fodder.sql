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
    ROW_NUMBER() OVER (PARTITION BY FPP.rating, FPP.dttm_price ORDER BY FPP.price) AS price_rank
INTO price_rank
FROM players.futbin_players_prices FPP
WHERE FPP.price <> 0;

-- Step 2: Calculate the index start based on a specific date
DROP TABLE IF EXISTS index_start;
SELECT
    rating,
    AVG(price) AS index_start
INTO temp index_start
FROM price_rank
WHERE
    dttm_price::DATE = '2024-09-20'
    AND price_rank < 5
GROUP BY rating;

-- Step 3: Create the final reg_fodder table with calculated index
CREATE TABLE reporting.reg_fodder AS
SELECT
    PR.dttm_price,
    PR.rating,
    (AVG(PR.price) / MAX(I.index_start)) * 100 AS index,
    AVG(PR.price) AS avg_price
FROM price_rank PR
JOIN index_start I
    ON I.rating = PR.rating
WHERE PR.price_rank < 5
GROUP BY PR.dttm_price, PR.rating;