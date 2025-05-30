from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

def get_webdriver():
    """Initializes and returns a Chrome WebDriver instance."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    try:
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None

def wait_for_document_ready(driver_instance, timeout=10):
    """Waits for the document.readyState to be 'complete'."""
    try:
        WebDriverWait(driver_instance, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("Page is fully loaded and ready.")
    except TimeoutException:
        print(f"Page did not reach 'complete' state within {timeout} seconds.")