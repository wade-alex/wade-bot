import boto3
import pandas as pd
import psycopg2

S3_BUCKET = 'wade-bot-scraper-dumps'
S3_RAW_FOLDER = 'Raw/'  # Folder in S3 where raw files are stored
S3_PROCESSED_FOLDER = 'Processed/'  # Folder in S3 for processed files

# Initialize the S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id='AKIA5MSUBXIYQH6JNS4X',
    aws_secret_access_key='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'
)


def connect_db():
    """Establishes and returns a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname="postgres",
        host="localhost",
        port="5432"
    )
    return conn


def transform_price(price_str):
    """Transforms price string (e.g., '50K', '1.1M') to numeric."""
    price_str = price_str.upper()

    if 'M' in price_str:
        return float(price_str.replace('M', '')) * 1_000_000
    elif 'K' in price_str:
        return float(price_str.replace('K', '')) * 1_000
    return float(price_str)


def insert_player_prices(cursor, player):
    """Inserts player price data into the database."""
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


def process_s3_file(s3_key):
    """Downloads and processes a file directly from S3 without saving locally."""
    print(f"Processing file: {s3_key}...")
    try:
        # Retrieve the CSV file directly from S3
        s3_obj = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
        file_size = s3_obj['ContentLength']
        print(f"File size: {file_size} bytes")

        # Check if the file is empty
        if file_size == 0:
            print(f"Skipping empty file: {s3_key}")
            return

        # Process CSV content
        df = pd.read_csv(s3_obj['Body'])
        print(f"CSV file loaded. Number of records: {len(df)}")

        if df.empty:
            print(f"No data in file: {s3_key}")
            return

        # Transform the 'price' column
        if 'price' in df.columns:
            df['price'] = df['price'].apply(transform_price)

        # Insert the data into the database
        conn = connect_db()
        cursor = conn.cursor()

        for _, row in df.iterrows():
            insert_player_prices(cursor, row)

        conn.commit()
        cursor.close()
        conn.close()

        print(f"Finished processing file: {s3_key}")

    except Exception as e:
        print(f"Error processing file {s3_key}: {e}")


def move_file_to_processed(s3_key):
    """Moves the processed file from 'Raw' to 'Processed' in the S3 bucket."""
    file_name = s3_key.split('/')[-1]
    processed_key = f"{S3_PROCESSED_FOLDER}{file_name}"

    try:
        # Copy the file from Raw to Processed
        print(f"Copying {s3_key} to {processed_key}...")
        s3.copy_object(
            Bucket=S3_BUCKET,
            CopySource={'Bucket': S3_BUCKET, 'Key': s3_key},
            Key=processed_key
        )
        print(f"Copied {s3_key} to {processed_key}.")

        # Delete the original file from Raw folder
        delete_file_from_s3(file_name)

    except Exception as e:
        print(f"Error moving file {s3_key} to processed: {e}")


def delete_file_from_s3(file_name):
    """Deletes the specified file from the S3 'Raw' folder."""
    try:
        s3_key = f"{S3_RAW_FOLDER}{file_name}"
        s3.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        print(f"Successfully deleted {s3_key} from S3 bucket.")
    except Exception as e:
        print(f"Error deleting file {s3_key} from S3: {e}")


def download_files_from_s3():
    """List and download all relevant files from the S3 Raw folder."""
    print("Listing files from S3...")
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_RAW_FOLDER)

        if 'Contents' not in response:
            print(f"No files found in the folder '{S3_RAW_FOLDER}'")
            return []

        for obj in response['Contents']:
            key = obj['Key']
            if key.startswith(f"{S3_RAW_FOLDER}futbin_players_prices") and key.endswith('.csv'):
                print(f"Found file: {key}")
                process_s3_file(key)

                # Move the file to Processed after processing
                move_file_to_processed(key)

    except Exception as e:
        print(f"Error downloading files from S3: {e}")


def main():
    # Download and process files directly from S3
    download_files_from_s3()


if __name__ == "__main__":
    main()