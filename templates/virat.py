
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

app = Flask(__name__)

# Function to fetch Group UID and Name using Selenium
def fetch_group_data(email, password):
    driver = webdriver.Chrome()  # Make sure ChromeDriver is in your PATH
    driver.get("https://www.facebook.com")
    
    # Login to Facebook
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.ID, "pass").send_keys(Keys.RETURN)

    time.sleep(5)

    # Go to Facebook Messenger
    driver.get("https://www.facebook.com/messages/t/")
    time.sleep(5)

    # Extracting the group chat UID and name
    chats = driver.find_elements(By.XPATH, "//a[contains(@href, '/messages/t/')]")
    group_data = []
    
    for chat in chats:
        chat_url = chat.get_attribute("href")
        thread_id = chat_url.split("/")[-1]
        group_name = chat.text  # Group name is in the text of the link
        
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

    # Fetch group data
    group_data = fetch_group_data(email, password)
    
    # Render the template with the fetched data
    return render_template('index.html', group_data=group_data)

if __name__ == '__main__':
    app.run(debug=True)
