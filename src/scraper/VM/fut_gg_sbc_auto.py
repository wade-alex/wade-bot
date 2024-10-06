import asyncio
from pyppeteer import launch
import pandas as pd
from datetime import datetime
import nest_asyncio
import boto3
from io import StringIO
from botocore.exceptions import ClientError
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# S3 Configuration
S3_BUCKET = 'wade-bot-scraper-dumps'
S3_FOLDER = 'Raw'
S3_SBC_FOLDER = 'SBC'

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

# Apply nest_asyncio for environments like Jupyter
nest_asyncio.apply()
# List of URLs to scrape
urls = [
    "https://www.fut.gg/sbc/players/",
    "https://www.fut.gg/sbc/upgrades/",
    "https://www.fut.gg/sbc/challenges/",
    "https://www.fut.gg/sbc/foundations/"
]


async def load_webpage(url):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    try:
        await page.goto(url, {'timeout': 60000, 'waitUntil': 'domcontentloaded'})
        await asyncio.sleep(3)  # Sleep to allow page to fully load
        html_content = await page.content()
        return html_content
    except Exception as e:
        print(f"Error loading page {url}: {e}")
        return None
    finally:
        await browser.close()


def extract_sbc_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = []

    # Get the current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for player_div in soup.find_all('div', class_='grid grid-cols-[1fr_2fr] items-center p-2 gap-2'):
        name = player_div.find_previous('h2', class_='text-xl font-bold').text.strip()
        description = player_div.find('p', class_='text-sm mb-3').text.strip()
        rating = player_div.find('p', class_='text-xs text-white').text.strip().split()[0]
        challenges = int(player_div.find('span', string='Challenges').find_next('span').text.strip())
        expires_in = player_div.find('span', string='Expires In').find_next('span').text.strip()

        price_div = player_div.find_previous('div',
                                             class_='bg-gray rounded font-bold text-sm px-2 py-1 flex items-center')
        price = price_div.text.strip() if price_div else 'N/A'

        # Find the link to the specific player SBC
        link = player_div.find('a', href=True)
        player_sbc_link = 'https://www.fut.gg' + link['href'] if link else 'N/A'

        # Create a single row for each player
        data.append({
            'Player Name': name,
            'Rating': rating,
            'Description': description,
            'Total Challenges': challenges,
            'Expires In': expires_in,
            'Price': price,
            'SBC Link': player_sbc_link,
            'dttm_scraped': current_time  # Add the timestamp
        })

    # Create DataFrame and remove duplicates
    df = pd.DataFrame(data).drop_duplicates()
    return df


async def scrape_and_return_df(url):
    html_content = await load_webpage(url)
    if html_content:
        # Extract SBC data
        df = extract_sbc_data(html_content)

        # Extract 'Type' from URL
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        sbc_type = path_parts[-1] if path_parts else 'unknown'

        # Add 'Type' column
        df['Type'] = sbc_type

        print(f"SBC data for {url} has been scraped")
        return df
    else:
        print(f"Failed to load webpage: {url}")
        return None

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
        Key=f"{s3_folder}/fut_gg_sbc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        Body=csv_buffer.getvalue()
    )


def upload_consolidated_sbc_data(dataframe):
    """
    Uploads the consolidated SBC data to the SBC folder in S3.
    """
    print("Uploading consolidated SBC data...")
    try:
        # Convert DataFrame to CSV in-memory
        csv_buffer = StringIO()
        dataframe.to_csv(csv_buffer, index=False)

        # Create an S3 client and upload
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=f"{S3_SBC_FOLDER}/sbc_links.csv",
            Body=csv_buffer.getvalue()
        )
        print(f"Successfully uploaded consolidated SBC data to {S3_SBC_FOLDER}/sbc_links.csv")
    except Exception as e:
        print(f"Error uploading consolidated SBC data: {e}")


async def main():
    urls = [
        "https://www.fut.gg/sbc/players/",
        "https://www.fut.gg/sbc/upgrades/",
        "https://www.fut.gg/sbc/challenges/",
        "https://www.fut.gg/sbc/foundations/"
    ]
    all_dfs = []
    for url in urls:
        df = await scrape_and_return_df(url)
        if df is not None:
            all_dfs.append(df)

    # Combine all dataframes into one
    final_df = pd.concat(all_dfs, ignore_index=True)

    # Print the final DataFrame
    print(final_df.to_string(index=False))

    # Upload the DataFrame to S3 (Raw folder)
    upload_df_to_s3(final_df, S3_BUCKET, S3_FOLDER)

    # Upload the consolidated data to the SBC folder
    upload_consolidated_sbc_data(final_df)

# Run the main function
asyncio.get_event_loop().run_until_complete(main())

