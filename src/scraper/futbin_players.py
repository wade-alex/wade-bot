# futbin_players.py
import asyncio
from pyppeteer import launch
import pyperclip
import re
import pandas as pd

async def load_webpage(url):
    # Launch the browser
    browser = await launch(headless=True)  # Set to False to visually debug
    page = await browser.newPage()

    # Set user agent to mimic a real browser
    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    # Navigate to the page and wait for the content to load
    try:
        await page.goto(url, {'timeout': 60000, 'waitUntil': 'domcontentloaded'})  # Reduced to 'domcontentloaded'
        await asyncio.sleep(3)  # Wait for 3 seconds to ensure content is loaded

        # Get the page content
        html_content = await page.content()
        await browser.close()
        return html_content
    except Exception as e:
        print(f"Error loading page: {e}")
        await browser.close()
        return None

# Function to extract player names
def find_player_names(html_content):
    pattern = r'/25/player/\d+/([^">]+)">'
    matches = re.findall(pattern, html_content)
    return matches

# Function to extract strong foot
def find_strong_foot(html_content):
    foot_pattern = r'<td class="table-foot"><img alt="Strong Foot" src="/design2/img/static/filters/foot-(left|right).svg"'
    strong_foot = re.findall(foot_pattern, html_content)
    return strong_foot

# Function to extract weak foot
def find_weak_foot(html_content):
    weak_foot_pattern = r'<td class="table-weak-foot">(\d+)<i'
    weak_foot_stats = re.findall(weak_foot_pattern, html_content)
    return weak_foot_stats

# Function to extract skill stars
def find_skill_stars(html_content):
    skill_stars_pattern = r'<td class="table-skills">(\d+)<i'
    skill_stars = re.findall(skill_stars_pattern, html_content)
    return skill_stars

# Function to extract card type
def find_card_type(html_content):
    card_type_pattern = r'<div class="table-player-revision">([^<]+)</div>'
    card_types = re.findall(card_type_pattern, html_content)
    return card_types

# Function to extract player position
def find_player_position(html_content):
    position_pattern = r'<td class="table-pos">\s*<div class="bold">([^<]+)</div>'
    positions = re.findall(position_pattern, html_content)
    return positions

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

async def main():
    url = 'https://www.futbin.com/players'
    html_content = await load_webpage(url)

    if html_content:
        # Find player names
        player_names = find_player_names(html_content)

        # Find stats for strong foot, weak foot, skill stars, card type, position
        strong_foot = find_strong_foot(html_content)
        weak_foot = find_weak_foot(html_content)
        skill_stars = find_skill_stars(html_content)
        card_type = find_card_type(html_content)
        position = find_player_position(html_content)

        # Find stats for pace, shooting, passing, dribbling, defending, physicality
        player_pace = find_player_pace(html_content)
        player_shooting = find_player_shooting(html_content)
        player_passing = find_player_passing(html_content)
        player_dribbling = find_player_dribbling(html_content)
        player_defending = find_player_defending(html_content)
        player_physicality = find_player_physicality(html_content)

        # Validate that all data points have the same length
        if not validate_data_lengths(player_names, strong_foot, weak_foot, skill_stars, card_type, position, player_pace, player_shooting, player_passing, player_dribbling, player_defending, player_physicality):
            print("Data length mismatch. Aborting...")
            return

        # Create a list of dictionaries containing the player data
        player_data = []
        for name, foot, weak, skill, card, pos, pace, shooting, passing, dribbling, defending, physicality in zip(
            player_names, strong_foot, weak_foot, skill_stars, card_type, position, player_pace,
            player_shooting, player_passing, player_dribbling, player_defending, player_physicality):
            player_data.append({
                'name': name,
                'strong_foot': foot,
                'weak_foot': weak,
                'skill_stars': skill,
                'card_type': card,
                'position': pos,
                'pace': pace,
                'shooting': shooting,
                'passing': passing,
                'dribbling': dribbling,
                'defending': defending,
                'physicality': physicality
            })

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(player_data)

        # Print the DataFrame
        print(df.to_string())

        # Optionally, you can save the dataframe to a CSV file
        # df.to_csv('futbin_players.csv', index=False)
    else:
        print("Failed to load page content.")

if __name__ == "__main__":
    asyncio.run(main())