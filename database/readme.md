# Wade-Bot Database Architecture

Welcome to the **Wade-Bot** database architecture documentation. This document outlines the structure of the PostgreSQL database used by Wade-Bot, a FIFA Ultimate Team app. The database is divided into three schemas, each containing tables that store price histories, player stats, SBC (Squad Building Challenges) requirements, chemistry styles, and an index rollup table that tracks fodder prices over time.

## Table of Contents
- [Database Overview](#database-overview)
- [Schemas](#schemas)
  - [Player Schema](#player-schema)
  - [SBC Schema](#sbc-schema)
  - [Chemistry Styles Schema](#chemistry-styles-schema)
- [Index Rollup Table](#index-rollup-table)
- [Technical Notes](#technical-notes)

## Database Overview

The Wade-Bot database is designed in PostgreSQL to handle large volumes of data related to the FIFA Ultimate Team economy. It stores historical price data, player statistics, chemistry styles, and requirements for SBCs. This structure allows for efficient querying and tracking of trends over time, enabling advanced analytics for users.

## Schemas

### 1. Player Schema

This schema manages data related to players in FIFA Ultimate Team, including static player attributes (such as stats) and dynamic data (price history). 

#### Tables:
- **`player_stats`**  
  Stores static player data including their FIFA stats, positions, card types, and other attributes.
  - `p_oid`: Unique identifier for the player.
  - `name`: Name of the player.
  - `club`: Club the player is associated with.
  - `nation`: Nationality of the player.
  - `position`: Player's default position.
  - `card_type`: Type of the player's card (e.g., Gold, Silver, Special).
  - `pace`: Player's pace rating.
  - `shooting`: Player's shooting rating.
  - `passing`: Player's passing rating.
  - `dribbling`: Player's dribbling rating.
  - `defense`: Player's defense rating.
  - `physical`: Player's physical rating.
  - `overall_rating`: Overall rating of the player.

- **`player_price_history`**  
  Tracks historical price changes for each player over time.
  - `p_oid`: Foreign key referencing the player.
  - `date`: Date of the price record.
  - `price`: Market price of the player on the given date.

### 2. SBC Schema

This schema stores data related to Squad Building Challenges (SBCs), including the requirements to complete them and historical price data for each SBC.

#### Tables:
- **`sbc_requirements`**  
  Stores the requirements for each SBC.
  - `s_oid`: Unique identifier for the SBC.
  - `name`: Name of the SBC.
  - `min_team_rating`: Minimum team rating required to complete the SBC.
  - `min_chemistry`: Minimum team chemistry required to complete the SBC.
  - `num_players`: Number of players required to complete the SBC.
  - `specific_requirements`: Additional specific requirements (e.g., players from a certain nation or league).

- **`sbc_price_history`**  
  Tracks historical price changes for completing each SBC.
  - `s_oid`: Foreign key referencing the SBC.
  - `date`: Date of the price record.
  - `price`: Total estimated cost to complete the SBC on the given date.

### 3. Chemistry Styles Schema

This schema tracks chemistry styles, which are applied to players to modify their stats, as well as the price history of these chemistry styles.

#### Tables:
- **`chem_styles`**  
  Stores data about the available chemistry styles and their effects on player attributes.
  - `cs_oid`: Unique identifier for the chemistry style.
  - `name`: Name of the chemistry style.
  - `pace_boost`: Boolean value indicating whether the chemistry style increases the player's pace stat.
  - `shooting_boost`: Boolean value indicating whether the chemistry style increases the player's shooting stat.
  - `passing_boost`: Boolean value indicating whether the chemistry style increases the player's passing stat.
  - `dribbling_boost`: Boolean value indicating whether the chemistry style increases the player's dribbling stat.
  - `defense_boost`: Boolean value indicating whether the chemistry style increases the player's defense stat.
  - `physical_boost`: Boolean value indicating whether the chemistry style increases the player's physical stat.

- **`chem_style_price_history`**  
  Tracks the historical prices for each chemistry style over time.
  - `cs_oid`: Foreign key referencing the chemistry style.
  - `date`: Date of the price record.
  - `price`: Market price of the chemistry style on the given date.

## Index Rollup Table

The index rollup table tracks the average prices of fodder players over time. Fodder players are typically used to meet SBC requirements due to their high overall rating and lower market value.

### Table:
- **`fodder_price_index`**  
  An aggregate table that tracks the average price of fodder players over time. This allows users to monitor trends in the fodder market and predict price fluctuations.
  - `date`: Date of the record.
  - `average_fodder_price`: Average market price of fodder players on the given date.

## Technical Notes

- **PostgreSQL Database**: The database is implemented using PostgreSQL, leveraging its powerful indexing, querying, and relational data capabilities.
  
- **Normalization**: The database is fully normalized to ensure that data is efficiently stored with minimal redundancy. Foreign key relationships are enforced to maintain referential integrity between tables.

- **Indexes**: Indexes should be applied to frequently queried columns such as `p_oid`, `s_oid`, `cs_oid`, and `date` to improve performance, particularly when retrieving historical price data.

- **Data Retention**: The price history tables (`player_price_history`, `sbc_price_history`, and `chem_style_price_history`) may grow large over time. A data retention or archiving policy should be considered to manage this data, especially for older, less relevant records.

## Conclusion

The Wade-Bot PostgreSQL database architecture is designed to support the complex data requirements of the FIFA Ultimate Team ecosystem. It provides efficient ways to manage and track player stats, price histories, SBC requirements, and chemistry styles, with an emphasis on scalability and performance.

For further questions or technical assistance, please contact the development team.
