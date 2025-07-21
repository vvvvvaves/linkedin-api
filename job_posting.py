from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import json
import yaml
from argparse import ArgumentParser
import selenium
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

DEFAULT_URL = ('https://www.linkedin.com/jobs/view/fake-job-posting/')
parser = ArgumentParser()
parser.add_argument('-u', '--url',
                    help='URL of the company\'s LinkedIn job posting.',
                    default=DEFAULT_URL)
parser.add_argument('--headless',
                    help='Run in headless mode',
                    default=False,
                    action='store_true')
args = parser.parse_args()

def get_driver(url):
    # Set up Selenium options
    options = Options()
    options.add_argument("--start-maximized")
    if args.headless:
        options.add_argument("--headless")  # Uncomment for headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    driver.get(url)

    return driver, wait

def click_at_coordinates(driver, x, y):
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()
    # Move the mouse back to (0,0) to avoid offset issues in future actions
    actions.move_by_offset(-x, -y).perform()

def get_job_description_structured(driver, wait):
    # Try to click at coordinates (e.g., 100, 200)
    try:
        click_at_coordinates(driver, 300, 300)
        time.sleep(5)
    except Exception as e:
        print(f"Click at coordinates failed: {e}")

    # Get the HTML content of the job description container
    content_container = driver.find_element(By.XPATH, './/div[contains(@class, "core-section-container")]')
    html_content = content_container.get_attribute('innerHTML')

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Option 1: Get as Markdown (preserves structure)
    try:
        import markdownify
    except ImportError:
        print("Please install markdownify: pip install markdownify")
        return soup.prettify()  # fallback to pretty HTML

    markdown = markdownify.markdownify(str(soup), heading_style="ATX")
    return markdown

if __name__ == "__main__":
    driver, wait = get_driver(args.url)
    job_description = get_job_description_structured(driver, wait)
    driver.quit()
    with open("job_description.md", "w", encoding="utf-8") as f:
        f.write(job_description)
    print("Job description saved to job_description.md")
