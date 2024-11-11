
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import chromedriver_autoinstaller
import os

app = Flask(__name__)

# Function to fetch Group UID and Name using Selenium
def fetch_group_data(email, password):
    # Automatically installs the correct version of ChromeDriver
    chromedriver_autoinstaller.install()

    # Set the path for Chrome binary
    chrome_path = os.environ.get("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome-stable")
    
    # Set Chrome options for headless mode
    chrome_options = Options()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode
    chrome_options.add_argument('--no-sandbox')  # Needed for server environments
    chrome_options.add_argument('--disable-dev-shm-usage')  # For low memory environments

    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get("https://www.facebook.com")
    
    # Facebook par login karein
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.ID, "pass").send_keys(Keys.RETURN)

    time.sleep(5)

    # Facebook Messenger par jaayein
    driver.get("https://www.facebook.com/messages/t/")
    time.sleep(5)

    # Group chat UID aur naam extract karein
    chats = driver.find_elements(By.XPATH, "//a[contains(@href, '/messages/t/')]")
    group_data = []
    
    for chat in chats:
        chat_url = chat.get_attribute("href")
        thread_id = chat_url.split("/")[-1]
        group_name = chat.text  # Group name link ke text me hota hai
        
        group_data.append({"thread_id": thread_id, "group_name": group_name})

    driver.quit()

    return group_data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch_data():
    email = request.form['email']
    password = request.form['password']

    # Group data fetch karein
    group_data = fetch_group_data(email, password)
    
    # Template render karein
    return render_template('index.html', group_data=group_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
