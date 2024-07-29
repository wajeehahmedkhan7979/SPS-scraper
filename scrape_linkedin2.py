from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
from unidecode import unidecode
import openpyxl
import os
from datetime import datetime

# Function to normalize location strings
def normalize_location(input_str):
    return unidecode(input_str).lower()

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Path to the ChromeDriver executable
path = r"C:\Windows\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

# Function to scroll up the page
def scroll_up(driver, times=3, interval=2):
    for _ in range(times):
        driver.execute_script("window.scrollBy(0, -document.body.scrollHeight / 3);")
        time.sleep(interval)

# Function to perform LinkedIn search and navigate to company's employees page
def search_company(driver, company_name):
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.search-global-typeahead__input'))
    )
    search_input.clear()
    search_input.send_keys(company_name)
    search_input.send_keys(Keys.RETURN)
    print("Search initiated for company:", company_name)

    company_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/company/") and not(contains(@href, "/jobs/"))]'))
    )
    company_link.click()
    print("Navigated to company page.")

    time.sleep(5)
    scroll_up(driver)
    print("Scrolled up on company page.")

    people_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/search/results/people/")]'))
    )
    people_link.click()
    print("Navigated to the People page.")

# Function to scroll the page incrementally
def scroll_down_incrementally(driver):
    total_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(1, total_height, 300):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(1)

def scrape_linkedin(driver, description_to_filter, location_to_filter, file_name):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['Name', 'Description', 'Location'])

    while True:
        try:
            main_content = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'main'))
            )
            print("Main content loaded.")
            
            scroll_down_incrementally(driver)
            print("Scrolled to the bottom of the page.")

            results = driver.find_elements(By.CSS_SELECTOR, 'li.reusable-search__result-container')
            print(f"Found {len(results)} results on the page.")
            for result in results:
                try:
                    name_element = result.find_element(By.CSS_SELECTOR, 'a.app-aware-link span[aria-hidden="true"]')
                    name = name_element.text
                    if name.lower() == "linkedin member":
                        name = 'N/A'
                except NoSuchElementException:
                    name = 'N/A'
                
                try:
                    location_element = result.find_element(By.CSS_SELECTOR, 'div.entity-result__secondary-subtitle')
                    location = normalize_location(location_element.text)
                except NoSuchElementException:
                    location = 'N/A'
                
                try:
                    description_element = result.find_element(By.CSS_SELECTOR, 'div.entity-result__primary-subtitle')
                    description = description_element.text
                except NoSuchElementException:
                    description = 'N/A'
                
                if (description_to_filter == 'no' or description_to_filter == 'n' or description_to_filter in description.lower()) and (location_to_filter == 'no' or location_to_filter == 'n' or location_to_filter in location):
                    sheet.append([name, description, location])
                    print(f'Name: {name}, Description: {description}, Location: {location}')
            
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.artdeco-pagination__button--next'))
                )
                next_button.click()
                print("Clicked on the next button.")
                time.sleep(5)
            except TimeoutException:
                print("Next button not found or clickable. Ending the scraping process.")
                break
        except StaleElementReferenceException:
            print("Encountered StaleElementReferenceException, retrying...")

    workbook.save(file_name)
    print(f"Data saved to '{file_name}'.")

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    description = data.get('description', 'n')
    location = data.get('location', 'n')
    company = data.get('company')

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{company.replace(' ', '_')}_{timestamp}.xlsx"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    service = Service(executable_path=path)
    driver = webdriver.Chrome(service=service)

    try:
        driver.get('https://www.linkedin.com/login')

        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        username_field.send_keys(email)

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'password'))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'global-nav-search'))
        )

        search_company(driver, company)
        scrape_linkedin(driver, description, location, file_path)

        return jsonify({"message": "Scraping completed successfully!", "filename": file_name}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        driver.quit()

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
