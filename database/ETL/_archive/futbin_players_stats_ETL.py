# /Users/alexwade/Documents/WADE_BOT/RAW/futbin_etl.py
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


def upsert_player_stats(cursor, player):
    # Generate p_oid by concatenating name and all player stats (position removed)
    p_oid = f"{player['name']}-{player['pace']}-{player['shooting']}-{player['passing']}-{player['dribbling']}-{player['defending']}-{player['physicality']}-{player['rating']}"

    sql = """
    INSERT INTO players.futbin_players_stats (
        p_oid, name, strong_foot, weak_foot, skills, position, pace, shooting, passing, dribbling, defending, physicality, rating
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (p_oid)
    DO UPDATE SET
        name = EXCLUDED.name,
        strong_foot = EXCLUDED.strong_foot,
        weak_foot = EXCLUDED.weak_foot,
        skills = EXCLUDED.skills,
        position = EXCLUDED.position,
        pace = EXCLUDED.pace,
        shooting = EXCLUDED.shooting,
        passing = EXCLUDED.passing,
        dribbling = EXCLUDED.dribbling,
        defending = EXCLUDED.defending,
        physicality = EXCLUDED.physicality,
        rating = EXCLUDED.rating;
    """
    cursor.execute(sql, (
        p_oid, player['name'], player['strong_foot'], player['weak_foot'], player['skills'], player['position'],
        player['pace'], player['shooting'], player['passing'], player['dribbling'], player['defending'],
        player['physicality'], player['rating']
    ))


def process_file(file_path):
    # Read CSV file
    df = pd.read_csv(file_path)

    # Connect to PostgreSQL
    conn = connect_db()
    cursor = conn.cursor()

    # Iterate over the DataFrame rows and upsert each player's stats
    for _, row in df.iterrows():
        upsert_player_stats(cursor, row)

    # Commit changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()


def move_file(file_path, processed_folder):
    # Move the processed file to the processed folder
    shutil.move(file_path, processed_folder)


def main():
    # Get all CSV files in RAW_FOLDER that contain "futbin_players_stats" in the filename
    file_pattern = os.path.join(RAW_FOLDER, "*futbin_players_stats*.csv")
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

