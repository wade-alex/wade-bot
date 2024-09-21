# /web_scraper_template.py
# Purpose: Template for navigating a webpage, interacting with buttons, inserting data, and printing text/buttons.
# This script uses Selenium to control Chromium with an option to toggle headless mode.


# When setting up mac mini, need to follow script that I used to initially access the
# established chrome with the login so we don't have to send a code every time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_existing_browser():
    """
    Sets up Selenium to connect to an existing Chrome browser instance running in remote debugging mode.
    :return: WebDriver instance connected to the existing Chrome browser.
    """
    options = Options()

    # Connect to the Chrome instance with remote debugging enabled
    options.debugger_address = "localhost:9222"  # This should match the port you used for remote debugging

    driver = webdriver.Chrome(options=options)
    return driver

def setup_browser(headless=True):
    """
    Sets up the Chromium browser with WebDriver Manager for automatic driver management,
    and an option for headless browsing.
    :param headless: Boolean. If True, the browser runs headless (without UI).
    :return: WebDriver instance.
    """
    options = Options()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')  # For compatibility on Windows

    # Use WebDriver Manager to automatically install and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.implicitly_wait(10)

    return driver


def print_text_and_buttons(driver):
    """
    Prints all visible text and button elements currently on the webpage, including their name and class.
    :param driver: WebDriver instance controlling the browser.
    """
    # Get all text elements (could use more specific locators based on your need)
    text_elements = driver.find_elements(By.XPATH, "//*[not(self::script) and not(self::style)]")
    for elem in text_elements:
        print(elem.text)

    # Get all button elements
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print("\nAvailable buttons:")
    for button in buttons:
        button_text = button.text  # The visible text of the button
        button_name = button.get_attribute("name")  # The 'name' attribute of the button
        button_class = button.get_attribute("class")  # The 'class' attribute of the button

        print(f"Text: {button_text}")
        print(f"Name: {button_name if button_name else 'No name attribute'}")
        print(f"Class: {button_class if button_class else 'No class attribute'}\n")


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def click_button(driver, button_text=None, button_class=None):
    """
    Clicks a button based on its text or class name.
    :param driver: WebDriver instance.
    :param button_text: Optional. The text of the button to click.
    :param button_class: Optional. The class of the button to click.
    """
    try:
        if button_class:
            # Wait until the button with the specified class is clickable
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, button_class.split()[0]))  # Use the first class only
            )
            buttons = driver.find_elements(By.CLASS_NAME, button_class.split()[0])  # Search using the first class
            for button in buttons:
                if button_text is None or button.text == button_text:
                    button.click()
                    print(f"Clicked button with class '{button_class}' and text '{button.text}'")
                    return
        elif button_text:
            # Wait until the button with the specified text is clickable
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[text()='{button_text}']"))
            )
            buttons = driver.find_elements(By.XPATH, f"//button[text()='{button_text}']")
            for button in buttons:
                button.click()
                print(f"Clicked button with text '{button_text}'")
                return
        print(f"Button with class '{button_class}' or text '{button_text}' not found.")
    except Exception as e:
        print(f"Error clicking button: {str(e)}")

def click_login_if_present(driver):
    """
    Clicks the 'Login' button if it appears on the page.
    :param driver: WebDriver instance.
    """
    try:
        # Wait for up to 10 seconds for the Login button to appear (modify as needed)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
        )
        login_button.click()
        print("Clicked 'Login' button")
    except TimeoutException:
        # If the Login button doesn't appear in time, skip it
        print("Login button not found. Proceeding without login.")
    except NoSuchElementException:
        # Handle case where button isn't found by any means
        print("Login button does not exist on this page.")


def login(driver, email, password):
    """
    Fills in the login form with an email and password.
    :param driver: WebDriver instance.
    :param email: The email to input.
    :param password: The password to input (you can provide this later if there's a password field).
    """
    try:
        # Find the email input box by id and input the email
        email_field = driver.find_element(By.ID, "email")  # Use the ID 'email'
        email_field.clear()  # Clear any pre-filled text
        email_field.send_keys(email)
        print("Entered email")

        # If there's a password field, handle it similarly (replace this with actual password field locator)
        password_field = driver.find_element(By.ID, "password")  # Using the ID 'password'
        password_field.clear()  # Clear any pre-filled text
        password_field.send_keys(password)
        print("Entered password")


        # Find and click the 'Sign in' button by ID
        sign_in_button = driver.find_element(By.ID, "logInBtn")  # Using the ID 'logInBtn'
        sign_in_button.click()
        print("Clicked 'Sign in' button")

        # Submit the form or find and click the login button (adjust the locator to match the actual login button)
        # login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")  # Adjust locator for actual button
        # login_button.click()
        # print("Clicked submit button")

    except NoSuchElementException as e:
        print(f"Error finding login elements: {str(e)}")

def open_new_tab(driver):
    """
    Opens a new tab in the existing Chrome browser.
    :param driver: WebDriver instance connected to Chrome.
    """
    driver.execute_script("window.open('');")  # Opens a new blank tab
    driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
    print("New tab opened and switched.")

def navigate_and_interact():
    """
    Main function to navigate and interact with the website.
    """
    # Set up browser with headless option
    # driver = setup_browser(headless=False)  # Set to True to run in headless mode
    driver = setup_existing_browser()
    try:
        open_new_tab(driver)
        # Navigate to the webpage
        url = "https://www.ea.com/ea-sports-fc/ultimate-team/web-app/"
        driver.get(url)
        time.sleep(10)
        click_login_if_present(driver)
        login(driver, "wadecalex@gmail.com", "Aw603157!!")  # Replace with actual credentials

        # -- FUTURE INTERACTIONS HERE --
        # Step 3: Click the button with class 'ut-tab-bar-item icon-sbc' and text 'SBC'
        click_button(driver, button_text="Transfers", button_class="ut-tab-bar-item icon-transfer")
        time.sleep(10)

        print_text_and_buttons(driver)
        driver.close()
    finally:
        # Close the browser after completion
        driver.close()

if __name__ == "__main__":
    navigate_and_interact()