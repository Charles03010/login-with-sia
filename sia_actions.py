from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

from driver_setup import get_webdriver, wait_for_document_ready

TARGET_URL = "https://sia.uty.ac.id/std"
LOGIN_SUCCESS_INDICATOR_XPATH = "//h1[contains(text(), 'KALENDER AKADEMIK')]"
DATA_XPATH = "/html/body/div[2]/nav/div[2]/div/ul/div/center/p"

def login_and_extract_data(username, password):
    """
    Logs into SIA UTY, extracts specific data, and returns it.
    Returns the extracted data string or None if an error occurs.
    """
    driver = get_webdriver()
    if not driver:
        return None
    try:
        print(f"Attempting to navigate to {TARGET_URL}")
        driver.get(TARGET_URL)
        wait_for_document_ready(driver)
        print("Page loaded. Attempting login...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginNipNim"))
        ).send_keys(username)
        print(f"Username '{username}' entered.")
        driver.find_element(By.ID, "loginPsw").send_keys(password)
        print("Password entered.")
        captcha_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/section/div/div/div/div[1]/div/div[2]/div/div[2]/form/div/p",
                )
            )
        )
        captcha_text = captcha_element.text
        print(f"CAPTCHA text found: '{captcha_text}'")
        angka_captchas = map(int, re.findall(r"\d+", captcha_text))
        angka_captcha = list(angka_captchas)
        if len(angka_captcha) < 2:
            print("Error: Could not parse two numbers from CAPTCHA.")
            return None
        captcha_solution = str(angka_captcha[0] + angka_captcha[1])
        driver.find_element(By.NAME, "mumet").send_keys(captcha_solution)
        print(f"CAPTCHA solution '{captcha_solution}' entered.")
        driver.find_element(By.ID, "BtnLogin").click()
        print("Login button clicked.")
        wait_for_document_ready(driver, timeout=20)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, LOGIN_SUCCESS_INDICATOR_XPATH)
                )
            )
            print("Login successful! Dashboard element found.")
        except TimeoutException:
            print("Login might have failed or the dashboard element was not found.")
            return None
        print(f"Attempting to extract data from XPath: {DATA_XPATH}")
        try:
            data_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, DATA_XPATH))
            )
            extracted_text = data_element.text
            print(f"Data extracted: '{extracted_text}'")
            return extracted_text
        except TimeoutException:
            print(f"Could not find the data element with XPath: {DATA_XPATH}")
            return None
        except NoSuchElementException:
            print(f"Element with XPath {DATA_XPATH} not found after login.")
            return None
    except TimeoutException as e:
        print(f"A timeout occurred during the process: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        if driver:
            print("Quitting WebDriver.")
            driver.quit()

if __name__ == "__main__":
    test_username = "USERNAMETES"
    test_password = "PASSWORDTES"
    print(f"Testing sia_actions.py with username: {test_username}")
    data = login_and_extract_data(test_username, test_password)
    if data:
        print(f"\nSuccessfully extracted data:\n{data}")
    else:
        print("\nFailed to extract data.")
