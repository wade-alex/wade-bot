import boto3
import pandas as pd
import psycopg2
from botocore.exceptions import ClientError
import json

S3_BUCKET = 'wade-bot-scraper-dumps'
S3_RAW_FOLDER = 'Raw/'  # Folder in S3 where raw files are stored
S3_PROCESSED_FOLDER = 'Processed/'  # Folder in S3 for processed files

# Function to get AWS credentials from Secrets Manager
def get_secret():
    secret_name = "wade-bot-s3"  # Your secret name
    region_name = "us-east-2"  # Your AWS region

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        # Retrieve the secret value
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        # Parse the secret string and return it as a dictionary
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)

    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        raise e


# Retrieve the secrets from AWS Secrets Manager
secrets = get_secret()
aws_access_key_id = secrets['aws_access_key_id']
aws_secret_access_key = secrets['aws_secret_access_key']

# Initialize the S3 client using the credentials from Secrets Manager
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name="us-east-2"  # Ensure the region matches your S3 bucket
)


def connect_db():
    """Establishes and returns a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname="postgres",
        host="localhost",
        port="5432"
    )
    return conn

def insert_or_update_sbc(cursor, sbc):
    """Inserts or updates SBC data in the database."""
    sql = """
    INSERT INTO sbc.sbc (sbc_name, rating, description, total_challenges, expires_in, price, sbc_link, type, dttm_scraped, dttm_created, dttm_updated)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ON CONFLICT (sbc_name, rating, type)
    DO UPDATE SET
        description = EXCLUDED.description,
        total_challenges = EXCLUDED.total_challenges,
        expires_in = EXCLUDED.expires_in,
        price = EXCLUDED.price,
        sbc_link = EXCLUDED.sbc_link,
        dttm_scraped = EXCLUDED.dttm_scraped,
        dttm_updated = CURRENT_TIMESTAMP
    """
    cursor.execute(sql, (
        sbc['Player Name'], sbc['Rating'], sbc['Description'], sbc['Total Challenges'],
        sbc['Expires In'], sbc['Price'], sbc['SBC Link'], sbc['Type'], sbc['dttm_scraped']
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
            insert_or_update_sbc(cursor, row)

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
            return

        print(f"Total files found: {len(response['Contents'])}")

        for obj in response['Contents']:
            key = obj['Key']
            print(f"Checking file: {key}")
            if key.startswith(f"{S3_RAW_FOLDER}fut_gg_sbc_") and key.endswith('.csv'):
                print(f"Found matching file: {key}")
                process_s3_file(key)
                # Move the file to Processed after processing
                move_file_to_processed(key)
            else:
                print(f"File does not match criteria: {key}")

        print("Finished processing all files.")
    except Exception as e:
        print(f"Error downloading files from S3: {e}")


def main():
    try:
        print("Starting main function...")
        download_files_from_s3()
        print("Main function completed.")
    except Exception as e:
        print(f"An unexpected error occurred in main: {e}")

if __name__ == "__main__":
    main()