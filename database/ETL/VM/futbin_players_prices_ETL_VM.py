## Use this to automatically pull all CSV's from thr RAW s3
## File and load into the price history table

import os
import pandas as pd
import psycopg2
import shutil
import glob
import boto3

RAW_FOLDER = "/Users/alexwade/Documents/WADE_BOT/RAW/"
PROCESSED_FOLDER = "/Users/alexwade/Documents/WADE_BOT/Processed/"
S3_BUCKET = 'wade-bot-scraper-dumps'
S3_RAW_FOLDER = 'Raw/'  # Folder in S3 where raw files are stored
S3_PROCESSED_FOLDER = 'Processed/'  # Folder in S3 for processed files

# Initialize the S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id='AKIA5MSUBXIYQH6JNS4X',
    aws_secret_access_key='Klv6xshqnXf5w5Hg8KHGcjtx7IdNSnuvUdOyxWnR'
)

def connect_db():
    conn = psycopg2.connect(
        dbname="postgres",  # Database name from your JDBC URL
        host="localhost",  # From your JDBC URL
        port="5432"  # Default PostgreSQL port
    )
    return conn

def transform_price(price_str):
    """
    Transforms price strings like '50K', '1.1M', '1.22M', '45.25K' into corresponding numeric values.
    :param price_str: The price string to transform.
    :return: The numeric value of the price.
    """
    # Ensure the string is uppercase to handle lowercase 'k' or 'm'
    price_str = price_str.upper()

    # Handle millions (M)
    if 'M' in price_str:
        price_str = price_str.replace('M', '')
        return float(price_str) * 1_000_000

    # Handle thousands (K)
    elif 'K' in price_str:
        price_str = price_str.replace('K', '')
        return float(price_str) * 1_000

    # Handle cases where it's a regular number
    else:
        return float(price_str)

def insert_player_prices(cursor, player):
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
    if os.stat(file_path).st_size == 0:
        print(f"Skipping empty file: {file_path}")
        return

    try:
        df = pd.read_csv(file_path)

        if df.empty:
            print(f"No data in file: {file_path}")
            return

        # Transform the 'price' column using the transform_price function
        if 'price' in df.columns:
            df['price'] = df['price'].apply(transform_price)

        conn = connect_db()
        cursor = conn.cursor()

        # Iterate over the DataFrame rows and insert each player's price data
        for _, row in df.iterrows():
            insert_player_prices(cursor, row)

        conn.commit()
        cursor.close()
        conn.close()

    except pd.errors.EmptyDataError as e:
        print(f"Error reading file {file_path}: {e}")
        return

def move_file(file_path, processed_folder):
    shutil.move(file_path, processed_folder)

def download_files_from_s3():
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_RAW_FOLDER)

        if 'Contents' not in response:
            print(f"No files found in the folder '{S3_RAW_FOLDER}'")
            return []

        file_paths = []

        for obj in response['Contents']:
            key = obj['Key']
            # Only process files that start with 'futbin_player_prices' and end with '.csv'
            if key.startswith(f"{S3_RAW_FOLDER}futbin_players_prices") and key.endswith('.csv'):
                file_name = key.split('/')[-1]
                local_path = os.path.join(RAW_FOLDER, file_name)

                print(f"Downloading {file_name} from S3 bucket {S3_BUCKET}...")
                s3.download_file(S3_BUCKET, key, local_path)
                file_paths.append(local_path)

        return file_paths

    except Exception as e:
        print(f"Error downloading files from S3: {str(e)}")
        return []


def upload_processed_files_to_s3():
    """
    Uploads all files from the local 'Processed' folder to the 'Processed' folder in the S3 bucket.
    """
    try:
        # Find all CSV files in the PROCESSED_FOLDER
        files_to_upload = glob.glob(os.path.join(PROCESSED_FOLDER, "*.csv"))

        if not files_to_upload:
            print(f"No files found in the processed folder '{PROCESSED_FOLDER}'")
            return

        # Upload each file to the S3 bucket
        for file_path in files_to_upload:
            file_name = os.path.basename(file_path)  # Extract the file name
            s3_key = os.path.join(S3_PROCESSED_FOLDER, file_name)  # S3 path for the processed file

            print(f"Uploading {file_name} to S3 bucket {S3_BUCKET} in folder '{S3_PROCESSED_FOLDER}'...")

            try:
                # Perform the file upload
                s3.upload_file(file_path, S3_BUCKET, s3_key)
                print(f"Uploaded {file_name} successfully.")

                # Optionally delete the local file after upload
                # os.remove(file_path)
                # print(f"Deleted local file: {file_path}")

            except Exception as e:
                print(f"Error uploading {file_name}: {str(e)}")

    except Exception as e:
        print(f"Error uploading files to S3: {str(e)}")


def delete_file_from_s3(file_name, folder_type):
    """
    Deletes the specified file from the S3 folder (raw or processed).

    :param file_name: The name of the file to delete.
    :param folder_type: The folder type from which to delete the file ('raw' or 'processed').
    """
    # Define folder paths based on folder type
    if folder_type == 'Raw':
        s3_folder = 'Raw/'
    elif folder_type == 'processed':
        s3_folder = 'processed/'
    else:
        print(f"Invalid folder type specified: {folder_type}. Must be 'raw' or 'processed'.")
        return

    # Construct the full S3 key (path) for the file
    s3_key = f"{s3_folder}{file_name}"  # Ensure correct S3 path formatting

    try:
        # Debug print to check if the correct key is being used
        print(f"Attempting to delete file with S3 key: {s3_key} from bucket {S3_BUCKET}")

        # Perform the deletion from S3
        s3.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        print(f"Successfully deleted {s3_key} from S3 bucket {S3_BUCKET}.")
    except Exception as e:
        print(f"Error deleting file {s3_key} from S3: {str(e)}")

def main():
    # Step 1: Download all CSV files from the S3 bucket folder to RAW_FOLDER
    files_to_process = download_files_from_s3()

    # Check if any files were downloaded
    if not files_to_process:
        print("No files downloaded from S3. Exiting process.")
        return

    # Step 2: Process each file
    for file_path in files_to_process:
        print(f"Processing file: {file_path}")
        process_file(file_path)

        file_name = os.path.basename(file_path)

        # Step 3: After processing, move the file to the PROCESSED_FOLDER
        move_file(file_path, os.path.join(PROCESSED_FOLDER, file_name))
        print(f"Moved file to: {PROCESSED_FOLDER}")

    # Step 4: Upload processed files to S3
    upload_processed_files_to_s3()

    # Step 5: Delete the file from the S3 'Raw' folder, only if files were processed
    if file_name:  # Ensure file_name is defined before trying to delete
        delete_file_from_s3(file_name, 'Raw')
    else:
        print("No file was processed, skipping deletion from S3.")

if __name__ == "__main__":
    main()