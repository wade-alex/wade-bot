# futbin_players.py
import asyncio
from pyppeteer import launch
import pyperclip
import re

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
        await asyncio.sleep(10)  # Wait for 10 seconds to ensure content is loaded

        # Get the page content
        html_content = await page.content()
        await browser.close()
        return html_content
    except Exception as e:
        print(f"Error loading page: {e}")
        await browser.close()
        return None

def find_player_names(html_content):
    # Regex pattern to find the player hrefs and extract names between the last / and ">
    pattern = r'/25/player/\d+/([^">]+)">'

    # Find all matches (player names) in the HTML content
    matches = re.findall(pattern, html_content)

    # Return the number of matches found and the matches themselves
    return matches

async def main():
    url = 'https://www.futbin.com/players'
    html_content = await load_webpage(url)

    if html_content:
        # Find player names
        player_names = find_player_names(html_content)

        # Print all the player names
        print(f"Found {len(player_names)} player names.")
        for name in player_names:
            print(name)

    else:
        print("Failed to load page content.")

if __name__ == "__main__":
    asyncio.run(main())