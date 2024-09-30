import os
import pandas as pd
import psycopg2
import shutil
import glob

RAW_FOLDER = "/Users/alexwade/Documents/WADE_BOT/RAW/"
PROCESSED_FOLDER = "/Users/alexwade/Documents/WADE_BOT/Processed/"


def connect_db():
    # Connect to PostgreSQL using peer authentication (no username or password required)
    conn = psycopg2.connect(
        dbname="postgres",  # Database name from your JDBC URL
        host="localhost",  # From your JDBC URL
        port="5432"  # Default PostgreSQL port
    )
    return conn


def insert_player_prices(cursor, player):
    # Generate p_oid by concatenating name and all player stats
    p_oid = f"{player['name']}-{player['pace']}-{player['shooting']}-{player['passing']}-{player['dribbling']}-{player['defending']}-{player['physicality']}-{player['rating']}"

    sql = """
    INSERT INTO players.futbin_players_prices (
        p_oid, name, rating, price, pace, shooting, passing, dribbling, defending, physicality, dttm_price
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        p_oid, player['name'], player['rating'], player['price'], player['pace'], player['shooting'],
        player['passing'], player['dribbling'], player['defending'], player['physicality'], player['dttm_price']
    ))


def process_file(file_path):
    # Check if the file is empty
    if os.stat(file_path).st_size == 0:
        print(f"Skipping empty file: {file_path}")
        return

    try:
        # Try reading the CSV file
        df = pd.read_csv(file_path)

        # If the file is not empty, connect to PostgreSQL
        if df.empty:
            print(f"No data in file: {file_path}")
            return

        conn = connect_db()
        cursor = conn.cursor()

        # Iterate over the DataFrame rows and insert each player's price data
        for _, row in df.iterrows():
            insert_player_prices(cursor, row)

        # Commit changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()

    except pd.errors.EmptyDataError as e:
        print(f"Error reading file {file_path}: {e}")
        return


def move_file(file_path, processed_folder):
    # Move the processed file to the processed folder
    shutil.move(file_path, processed_folder)


def main():
    # Get all CSV files in RAW_FOLDER that contain "futbin_players_prices" in the filename
    file_pattern = os.path.join(RAW_FOLDER, "*futbin_players_prices*.csv")
    files_to_process = glob.glob(file_pattern)

    # Process each file
    for file_path in files_to_process:
        print(f"Processing file: {file_path}")
        process_file(file_path)
        # After processing, move the file to the PROCESSED_FOLDER
        move_file(file_path, os.path.join(PROCESSED_FOLDER, os.path.basename(file_path)))
        print(f"Moved file to: {PROCESSED_FOLDER}")


if __name__ == "__main__":
    main()