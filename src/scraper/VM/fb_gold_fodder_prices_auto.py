# /path/to/scraper.py
## this is the script that pulls 10 windows at a time
import asyncio
from pyppeteer import launch
import re
import pandas as pd
from datetime import datetime
import nest_asyncio
import boto3
from io import StringIO
from botocore.exceptions import ClientError
import json

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

# Function to load webpage content
async def load_webpage(url):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    try:
        await page.goto(url, {'timeout': 60000, 'waitUntil': 'domcontentloaded'})
        await asyncio.sleep(3)  # Sleep to allow page to fully load
        html_content = await page.content()
        await browser.close()
        return html_content
    except Exception as e:
        print(f"Error loading page {url}: {e}")
        await browser.close()
        return None
    finally:
        await browser.close()

# Function to extract player names
def find_player_names(html_content):
    pattern = r'/25/player/\d+/([^">]+)">'
    matches = re.findall(pattern, html_content)
    return matches

# Function to extract player price
def find_player_price(html_content):
    price_pattern = r'<td class="table-price no-wrap platform-ps-only">\s*<div class="price bold  centered small-row align-center">(\d+(?:\.\d+)?[kKmM]?)<img alt="Coin"'
    prices = re.findall(price_pattern, html_content)
    return prices

# Function to extract player rating
def find_player_rating(html_content):
    rating_pattern = r'<div class="player-rating-card-text font-standard bold">(\d+)</div>'
    ratings = re.findall(rating_pattern, html_content)
    return ratings

# Function to extract pace
def find_player_pace(html_content):
    pace_pattern = r'<td class="table-pace">.*?<div class="table-key-stats[^>]+">(\d+)</div>'
    pace_stats = re.findall(pace_pattern, html_content, re.DOTALL)
    return pace_stats

# Function to extract shooting
def find_player_shooting(html_content):
    shooting_pattern = r'<td class="table-shooting">.*?<div class="table-key-stats[^>]+">(\d+)</div>'
    shooting_stats = re.findall(shooting_pattern, html_content, re.DOTALL)
    return shooting_stats

# Function to extract passing
def find_player_passing(html_content):
    passing_pattern = r'<td class="table-passing">.*?<div class="table-key-stats[^>]+">(\d+)</div>'
    passing_stats = re.findall(passing_pattern, html_content, re.DOTALL)
    return passing_stats

# Function to extract dribbling
def find_player_dribbling(html_content):
    dribbling_pattern = r'<td class="table-dribbling">.*?<div class="table-key-stats[^>]+">(\d+)</div>'
    dribbling_stats = re.findall(dribbling_pattern, html_content, re.DOTALL)
    return dribbling_stats

# Function to extract defending
def find_player_defending(html_content):
    defending_pattern = r'<td class="table-defending">.*?<div class="table-key-stats[^>]+">(\d+)</div>'
    defending_stats = re.findall(defending_pattern, html_content, re.DOTALL)
    return defending_stats

# Function to extract physicality
def find_player_physicality(html_content):
    physicality_pattern = r'<td class="table-physicality">.*?<div class="table-key-stats[^>]+">(\d+)</div>'
    physicality_stats = re.findall(physicality_pattern, html_content, re.DOTALL)
    return physicality_stats

# Validation function to ensure all lists have the same length
def validate_data_lengths(*data_lists):
    lengths = [len(lst) for lst in data_lists]
    if len(set(lengths)) != 1:
        print(f"Data length mismatch: {lengths}")
        return False
    return True

# Function to scrape a single page
async def scrape_page(url):
    html_content = await load_webpage(url)

    if html_content:
        player_names = find_player_names(html_content)
        player_ratings = find_player_rating(html_content)
        player_prices = find_player_price(html_content)
        player_pace = find_player_pace(html_content)
        player_shooting = find_player_shooting(html_content)
        player_passing = find_player_passing(html_content)
        player_dribbling = find_player_dribbling(html_content)
        player_defending = find_player_defending(html_content)
        player_physicality = find_player_physicality(html_content)
        current_timestamp = [datetime.now()] * len(player_names)  # Timestamp for price scraping

        # Validate that all lists are of equal length
        if validate_data_lengths(player_names, player_ratings, player_prices, player_pace, player_shooting,
                                 player_passing, player_dribbling, player_defending, player_physicality):
            player_data = []
            for name, rating, price, pace, shooting, passing, dribbling, defending, physicality, dttm in zip(
                    player_names, player_ratings, player_prices, player_pace, player_shooting, player_passing,
                    player_dribbling, player_defending, player_physicality, current_timestamp):
                player_data.append({
                    'name': name,
                    'rating': rating,
                    'price': price,
                    'pace': pace,
                    'shooting': shooting,
                    'passing': passing,
                    'dribbling': dribbling,
                    'defending': defending,
                    'physicality': physicality,
                    'dttm_price': dttm  # Added timestamp column
                })

            df = pd.DataFrame(player_data)
            return df
        else:
            print("Data mismatch detected!")
            return pd.DataFrame()
    else:
        return pd.DataFrame()


# Function to upload the DataFrame to S3
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
    # s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucket_name,
        Key=f"{s3_folder}/futbin_players_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        Body=csv_buffer.getvalue()
    )

# Main function to scrape all URLs concurrently
async def main():
    urls = [
        'https://www.futbin.com/players?page=1&player_rating=83-83&sort=ps_price&order=asc',
        'https://www.futbin.com/players?page=1&player_rating=84-84&sort=ps_price&order=asc',
        'https://www.futbin.com/players?page=1&player_rating=85-85&sort=ps_price&order=asc',
        'https://www.futbin.com/players?page=1&player_rating=86-86&sort=ps_price&order=asc',
        'https://www.futbin.com/players?page=1&player_rating=87-87&sort=ps_price&order=asc',
        'https://www.futbin.com/players?page=1&player_rating=88-88&sort=ps_price&order=asc',
        'https://www.futbin.com/players?page=1&player_rating=89-89&sort=ps_price&order=asc',
        'https://www.futbin.com/players?page=1&player_rating=90-90&sort=ps_price&order=asc',
        'https://www.futbin.com/players?page=1&player_rating=91-91&sort=ps_price&order=asc'
    ]

    all_dataframes = []

    # Scrape all pages concurrently
    tasks = [scrape_page(url) for url in urls]
    dataframes = await asyncio.gather(*tasks)

    # Append the results to the final DataFrame
    all_dataframes.extend(dataframes)

    # Concatenate all dataframes into a single DataFrame
    final_df = pd.concat(all_dataframes, ignore_index=True)

    # Print the final DataFrame
    print(final_df.to_string())

    # Optionally, save the final DataFrame to a CSV file
    # final_df.to_csv(f'/Users/alexwade/Documents/WADE_BOT/RAW/futbin_players_prices_{datetime.now()}.csv', index=False)
    upload_df_to_s3(final_df, 'wade-bot-scraper-dumps', 'Raw')

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())