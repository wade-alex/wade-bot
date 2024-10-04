# Generates 2 CSV's in the Display folder of the S3 bucket for use in creating
# the Gold Fodder page in the app
import boto3
import pandas as pd
import psycopg2
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

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

# Configuration for different CSV files, tables, and queries
config = [
    {
        'csv_file': 'reg_fodder_table.csv',
        's3_folder': 'Display/',
        'query': 'SELECT * FROM reporting.reg_fodder_table',
        'table_name': 'reporting.reg_fodder_table'
    },
    {
        'csv_file': 'reg_fodder_graph.csv',
        's3_folder': 'Display/',
        'query': "SELECT * FROM reporting.reg_fodder WHERE rounded_date >= (current_date - INTERVAL '14 days')",
        'table_name': 'players.reg_fodder'
    },
    # Add more configurations as needed
]

S3_BUCKET = 'wade-bot-scraper-dumps'

def connect_db():
    """Establish and return a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="postgres",  # Database name from your JDBC URL
            host="localhost",  # From your JDBC URL
            port="5432"  # Default PostgreSQL port
        )
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Failed to connect to database: {e}")
        return None

def check_file_last_modified(bucket, file_path):
    """Check the last modified time of the file in the S3 bucket."""
    try:
        response = s3.head_object(Bucket=bucket, Key=file_path)
        last_modified = response['LastModified']
        return last_modified
    except s3.exceptions.ClientError as e:
        logging.info(f"File not found or other S3 error: {e}")
        return None

def refresh_required(last_modified):
    """Check if the last refresh was more than 3 hours ago."""
    if last_modified:
        time_diff = datetime.now(last_modified.tzinfo) - last_modified
        if time_diff < timedelta(hours=3):
            logging.info("File was refreshed within the last 3 hours. No refresh needed.")
            return False
    return True

def fetch_data(query):
    """Fetch data from the database and return it as a Pandas DataFrame."""
    conn = connect_db()
    if conn is None:
        logging.error("Database connection failed. Aborting refresh.")
        return None
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        logging.error(f"Failed to fetch data: {e}")
        return None
    finally:
        conn.close()

def delete_old_file(bucket, file_path):
    """Delete the old file from S3."""
    try:
        s3.delete_object(Bucket=bucket, Key=file_path)
        logging.info(f"Deleted old file from S3: {file_path}")
    except Exception as e:
        logging.error(f"Failed to delete old file: {e}")

def upload_to_s3(df, bucket, file_path):
    """Upload DataFrame as CSV to the S3 bucket."""
    try:
        csv_buffer = df.to_csv(index=False)
        s3.put_object(Bucket=bucket, Key=file_path, Body=csv_buffer)
        logging.info(f"File uploaded to {file_path} in S3 bucket {bucket}")
    except Exception as e:
        logging.error(f"Failed to upload file to S3: {e}")

def process_file(config_item):
    """Process a file based on its configuration: check S3, fetch from DB, delete old file, and upload new file."""
    file_path = f"{config_item['s3_folder']}{config_item['csv_file']}"
    last_modified = check_file_last_modified(S3_BUCKET, file_path)

    if refresh_required(last_modified):
        data = fetch_data(config_item['query'])
        if data is not None:
            if last_modified:
                delete_old_file(S3_BUCKET, file_path)
            upload_to_s3(data, S3_BUCKET, file_path)
        else:
            logging.error(f"Failed to refresh data for {config_item['csv_file']}.")
    else:
        logging.info(f"No refresh needed for {config_item['csv_file']}.")

def main():
    """Process all configured files."""
    for config_item in config:
        logging.info(f"Processing {config_item['csv_file']}...")
        process_file(config_item)

if __name__ == '__main__':
    main()