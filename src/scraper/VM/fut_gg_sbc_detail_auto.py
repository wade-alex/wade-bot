import boto3
import pandas as pd
from botocore.exceptions import ClientError
import json
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
from io import StringIO

S3_BUCKET = 'wade-bot-scraper-dumps'
S3_KEY = 'SBC/sbc_links.csv'
S3_RAW_FOLDER = "Raw"

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

def download_sbc_links():
    """Downloads the sbc_links.csv file from S3 and returns it as a pandas DataFrame."""
    try:
        print(f"Attempting to download file from S3: s3://{S3_BUCKET}/{S3_KEY}")
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        df = pd.read_csv(response['Body'])
        print(f"Successfully downloaded sbc_links.csv. Found {len(df)} SBC links.")
        return df
    except Exception as e:
        print(f"Error downloading sbc_links.csv: {e}")
        return None


def scrape_sbc_details(url):
    """
    Scrapes relevant information from the SBC webpage, focusing on the challenges and general SBC information.

    Args:
        url (str): The URL of the SBC webpage.

    Returns:
        list of dict: Scraped SBC data for each challenge and general SBC information.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        sbc_data = []

        # SBC Information section
        sbc_info_section = soup.find('div', class_='bg-dark-gray rounded grid grid-rows-[auto_1fr] items-center')
        if sbc_info_section:
            sbc_info_data = {
                'sbc_link': url,
                'scrape_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'segment_name': 'SBC Information',
                'reward': None,
                'requirements': []
            }

            # SBC Information details
            cost_div = sbc_info_section.find('div', class_='bg-gray rounded font-bold text-sm px-2 py-1 flex items-center')
            sbc_info_data['segment_cost'] = cost_div.text.strip() if cost_div else None

            # Reward in SBC Information
            reward_div = sbc_info_section.find('div', class_='bg-darker-gray rounded px-2 py-1')
            reward_text = reward_div.find('p', class_='text-xs text-white') if reward_div else None
            sbc_info_data['reward'] = reward_text.text.strip() if reward_text else None

            sbc_data.append(sbc_info_data)

        # Find the challenges section using a more flexible approach
        challenges_section = soup.find('section', {'id': 'challenges'}) or soup.find('div', id='challenges')
        if not challenges_section:
            print(f"No challenges section found for {url}")
            return sbc_data

        # Update class search to be more general
        challenges = challenges_section.find_all('div', class_='bg-dark-gray')
        if not challenges:
            print(f"No challenges found in the challenges section for {url}")
            return sbc_data

        for challenge in challenges:
            challenge_data = {
                'sbc_link': url,
                'scrape_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Challenge name
            challenge_name = challenge.find('h2')
            challenge_data['segment_name'] = challenge_name.text.strip() if challenge_name else None

            # Challenge reward
            reward_div = challenge.find('div', class_='bg-darker-gray rounded px-2 py-1')
            reward_text = reward_div.find('p', class_='text-xs text-white') if reward_div else None
            challenge_data['reward'] = reward_text.text.strip() if reward_text else None

            # Challenge requirements
            requirements_div = challenge.find('div', class_='mt-2')
            if requirements_div:
                requirements = requirements_div.find_all('p', class_='text-sm')
                challenge_data['requirements'] = [req.text.strip() for req in requirements if req.text.strip()]
            else:
                challenge_data['requirements'] = []

            sbc_data.append(challenge_data)

        return sbc_data
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return []


def process_all_sbc_links(urls):
    all_sbc_data = []
    for url in urls:
        print(f"Scraping: {url}")
        sbc_segments = scrape_sbc_details(url)
        all_sbc_data.extend(sbc_segments)

    return pd.DataFrame(all_sbc_data)


def upload_df_to_s3(dataframe, bucket_name, s3_folder):
    """
    Uploads a pandas DataFrame to an S3 bucket folder as a CSV file.

    Parameters:
    - dataframe: pandas DataFrame object to be uploaded
    - bucket_name: the name of the S3 bucket
    - s3_folder: the S3 folder path where the file will be stored
    """
    # Convert DataFrame to CSV in-memory
    csv_buffer = StringIO()
    dataframe.to_csv(csv_buffer, index=False)

    # Create an S3 client and upload
    s3.put_object(
        Bucket=bucket_name,
        Key=f"{s3_folder}/fut_gg_sbc_detail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        Body=csv_buffer.getvalue()
    )


def main():
    # Download SBC links
    df = download_sbc_links()

    if df is not None and 'SBC Link' in df.columns:
        urls = df['SBC Link'].tolist()

        all_sbc_data = []

        # Scrape all SBC links
        for url in urls:
            print(f"Scraping: {url}")
            sbc_segments = scrape_sbc_details(url)
            all_sbc_data.extend(sbc_segments)

        # Convert the scraped data to a DataFrame
        sbc_df = pd.DataFrame(all_sbc_data)

        # Print summary of scraped data
        print("\nScraped SBC Data Summary:")
        print(f"Total segments scraped: {len(sbc_df)}")

        # Upload the DataFrame to S3
        try:
            upload_df_to_s3(sbc_df, S3_BUCKET, S3_RAW_FOLDER)
            print(f"Successfully uploaded scraped data to S3 bucket: {S3_BUCKET}")
        except Exception as e:
            print(f"Error uploading to S3: {e}")
    else:
        print("Failed to process SBC links.")


if __name__ == "__main__":
    main()

