LinkedIn Scraper

Overview

This project is a LinkedIn scraping tool built with Python, Selenium, and Flask. It allows users to automate the extraction of employee data from LinkedIn based on company name and optional filters for description and location. The scraped data is saved in an Excel file and can be downloaded via a web interface.

Features

Automated Scraping: Logs into LinkedIn and navigates to the desired company's employee list.
Search and Filter: Search employees by company name and filter results by job description and location.
Data Export: Saves scraped data in an Excel file.
Web Interface: Provides a user-friendly web interface for entering LinkedIn credentials and search criteria.
Requirements
Python 3.x: Ensure you have Python 3.x installed.
Selenium: Install with pip install selenium.
Flask: Install with pip install flask.
OpenPyXL: Install with pip install openpyxl.
Unidecode: Install with pip install unidecode.
ChromeDriver: Download the appropriate version for your Chrome browser from ChromeDriver and update the path in the script.

Setup

Clone the Repository

bash
git clone https://github.com/yourusername/linkedin-scraper.git

cd linkedin-scraper

Install Dependencies

bash
pip install -r requirements.txt

Configure WebDriver

Download and place chromedriver.exe in C:\Windows\chromedriver-win64\ (or update the path in the script to match your setup).

Usage
Start the Flask Server

bash
python app.py
Open the Web Interface

Navigate to http://127.0.0.1:5000 in your web browser.

Enter Credentials and Search Criteria

Provide your LinkedIn email and password.
Enter the company name.
Optionally filter by description and location.
Start Scraping

Click the "Start Scraping" button. The script will log in, perform the search, and scrape employee data.

Download the Results

Once scraping is complete, download the Excel file containing the data from the provided download link.

API Endpoints
POST /scrape: Initiates the scraping process. Requires JSON payload with email, password, company, description, and location.
GET /download/<filename>: Allows downloading the generated Excel file.
Troubleshooting
Login Issues: Ensure your LinkedIn credentials are correct and that you have enabled access for less secure apps.
Element Not Found: LinkedIn may have updated its page structure. Check the XPaths and CSS selectors in the script and update them if necessary.
WebDriver Compatibility: Ensure your ChromeDriver version matches your installed Chrome browser version.
Contributing
Feel free to fork the repository and submit pull requests with improvements or bug fixes. For major changes, please open an issue to discuss the proposed changes before submitting a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

