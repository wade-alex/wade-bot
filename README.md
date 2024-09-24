# Cathedral: Market Intelligence

Cathedral is a market intelligence application designed for EA FC Ultimate Team players. It scrapes data from relevant sources, processes the data, and provides insights to help users make informed decisions on player trading and market trends.

## Features

- **Data Scraping**: Automates data extraction from EA FC Ultimate Team market.
- **Data Processing**: Converts raw data into structured CSV files for analysis.
- **PostgreSQL Integration**: Stores data in a PostgreSQL database for easy querying.
- **Visualization**: Provides a user-friendly interface to visualize market trends and insights.

## Project Structure

- **`data/`**: Contains raw and processed data in CSV format.
- **`database/`**: SQL scripts and database management files.
- **`src/`**: Core logic for the scraper and app functionality.
- **`docs/`**: Documentation files.

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/wade-alex/cathedral.git
    cd cathedral
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up PostgreSQL:
    - Ensure PostgreSQL is installed and running.
    - Import the database schema from the `database/` directory.

4. Run the application:
    ```bash
    python src/app.py
    ```

## Usage

- The app scrapes market data and stores it in the PostgreSQL database.
- Use the UI to visualize trends or export data for further analysis.
- Customize scraper settings by modifying the configuration in `src/config.py`.
