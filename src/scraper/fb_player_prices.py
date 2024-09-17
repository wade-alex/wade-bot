import asyncio
from pyppeteer import launch
import re
import pandas as pd
from datetime import datetime

# Function to load webpage content
async def load_webpage(url):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    try:
        await page.goto(url, {'timeout': 60000, 'waitUntil': 'domcontentloaded'})
        await asyncio.sleep(3)
        html_content = await page.content()
        await browser.close()
        return html_content
    except Exception as e:
        print(f"Error loading page: {e}")
        await browser.close()
        return None
    finally:
        await browser.close()  # Ensure the browser is closed even if there's an error

# Function to extract player names
def find_player_names(html_content):
    pattern = r'/25/player/\d+/([^">]+)">'
    matches = re.findall(pattern, html_content)
    return matches


# Function to extract player price
def find_player_price(html_content):
    price_pattern = r'<td class="table-price no-wrap platform-ps-only">\s*<div class="price bold  centered small-row align-center">(\d+)<img alt="Coin"'
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


async def main():
    max_page_number = 10  # You can change this to the desired max page number
    pages_per_chunk = 5
    all_dataframes = []

    # Loop over pages in chunks of 5
    for start_page in range(1, max_page_number + 1, pages_per_chunk):
        end_page = min(start_page + pages_per_chunk - 1, max_page_number)

        # Create URLs for the current chunk
        urls = [f'https://www.futbin.com/players?page={page}' for page in range(start_page, end_page + 1)]

        # Scrape the pages concurrently
        tasks = [scrape_page(url) for url in urls]
        dataframes = await asyncio.gather(*tasks)

        # Append the results to the final DataFrame
        all_dataframes.extend(dataframes)

        # Print progress
        print(f"Scraped pages {start_page} to {end_page}")

    # Concatenate all dataframes into a single DataFrame
    final_df = pd.concat(all_dataframes, ignore_index=True)

    # Print the final DataFrame
    print(final_df.to_string())

    # Optionally, save the final DataFrame to a CSV file
    # final_df.to_csv('/Users/alexwade/Documents/WADE_BOT/futbin_players.csv', index=False)


if __name__ == "__main__":
    asyncio.run(main())