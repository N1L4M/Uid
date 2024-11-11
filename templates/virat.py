
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import chromedriver_autoinstaller
import os

app = Flask(__name__)

# Function to fetch Group UID and Name using Selenium
def fetch_group_data(email, password):
    try:
        # Automatically installs the correct version of ChromeDriver
        chromedriver_autoinstaller.install()

        # Set the path for Chrome binary (for environments like Render)
        chrome_path = os.environ.get("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome-stable")
        
        # Ensure ChromeDriver is available
        if not os.path.exists(chrome_path):
            raise ValueError("Google Chrome binary not found at path: " + chrome_path)

        # Set Chrome options for headless mode
        chrome_options = Options()
        chrome_options.binary_location = chrome_path
        chrome_options.add_argument('--headless')  # Run Chrome in headless mode
        chrome_options.add_argument('--no-sandbox')  # Needed for server environments
        chrome_options.add_argument('--disable-dev-shm-usage')  # For low memory environments

        # Initialize WebDriver with the correct path for ChromeDriver
        driver = webdriver.Chrome(options=chrome_options)
        
        driver.get("https://www.facebook.com")
        
        # Facebook login process
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.ID, "pass").send_keys(Keys.RETURN)

        # Wait until login is successful and the page loads
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Messenger']"))
        )

        # Navigate to Messenger page
        driver.get("https://www.facebook.com/messages/t/")
        time.sleep(5)

        # Wait for chat elements to be available
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/messages/t/')]"))
        )

        # Group chat UID and name extraction
        chats = driver.find_elements(By.XPATH, "//a[contains(@href, '/messages/t/')]")
        group_data = []
        
        for chat in chats:
            chat_url = chat.get_attribute("href")
            thread_id = chat_url.split("/")[-1]
            group_name = chat.text  # Group name is typically the text of the link
            
            group_data.append({"thread_id": thread_id, "group_name": group_name})

        driver.quit()

        return group_data
    except Exception as e:
        print(f"Error fetching group data: {e}")
        return {"error": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch_data():
    email = request.form['email']
    password = request.form['password']

    # Fetch group data
    group_data = fetch_group_data(email, password)

    # If an error occurs while fetching data, display the error
    if "error" in group_data:
        return render_template('index.html', group_data={"error": group_data["error"]})

    # Render the template with group data
    return render_template('index.html', group_data=group_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
