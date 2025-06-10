from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
from flask import jsonify, redirect
from driver_setup import get_webdriver, wait_for_document_ready
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
import asyncio
import os
import random
import string
import glob
import time

TARGET_URL = "https://sia.uty.ac.id/std"
LOGIN_SUCCESS_INDICATOR_XPATH = "//h1[contains(text(), 'KALENDER AKADEMIK')]"
DATA_XPATH = "/html/body/div[2]/nav/div[2]/div/ul/div/center/p"


async def login_and_extract_data(username, password):
    """
    Asynchronously logs into SIA UTY, extracts specific data, and returns it.
    Returns the extracted data string or None if an error occurs.
    """
    loop = asyncio.get_event_loop()
    driver = await loop.run_in_executor(None, get_webdriver)
    if not driver:
        return jsonify({"error": "Internal Server Error Try Again"}), 500
    try:
        print(f"Attempting to navigate to {TARGET_URL}")
        await loop.run_in_executor(None, driver.get, TARGET_URL)
        await loop.run_in_executor(None, wait_for_document_ready, driver)
        print("Page loaded. Attempting login...")
        username_elem = await loop.run_in_executor(
            None,
            lambda: WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "loginNipNim"))
            ),
        )
        username_elem.send_keys(username)
        print(f"Username '{username}' entered.")
        password_elem = await loop.run_in_executor(
            None, lambda: driver.find_element(By.ID, "loginPsw")
        )
        password_elem.send_keys(password)
        print("Password entered.")
        captcha_element = await loop.run_in_executor(
            None,
            lambda: WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/section/div/div/div/div[1]/div/div[2]/div/div[2]/form/div/p",
                    )
                )
            ),
        )
        captcha_text = captcha_element.text
        print(f"CAPTCHA text found: '{captcha_text}'")
        angka_captchas = map(int, re.findall(r"\d+", captcha_text))
        angka_captcha = list(angka_captchas)
        if len(angka_captcha) < 2:
            print("Error: Could not parse two numbers from CAPTCHA.")
            return jsonify({"error": "Internal Server Error Try Again"}), 500
        captcha_solution = str(angka_captcha[0] + angka_captcha[1])
        captcha_input = await loop.run_in_executor(
            None, lambda: driver.find_element(By.NAME, "mumet")
        )
        captcha_input.send_keys(captcha_solution)
        print(f"CAPTCHA solution '{captcha_solution}' entered.")
        login_btn = await loop.run_in_executor(
            None, lambda: driver.find_element(By.ID, "BtnLogin")
        )
        login_btn.click()
        print("Login button clicked.")
        await loop.run_in_executor(None, wait_for_document_ready, driver, 20)
        try:
            await loop.run_in_executor(
                None,
                lambda: WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.XPATH, LOGIN_SUCCESS_INDICATOR_XPATH)
                    )
                ),
            )
            print("Login successful! Dashboard element found.")
        except TimeoutException:
            print("Login might have failed or the dashboard element was not found.")
            return redirect("/?error=failed")
        print(f"Attempting to extract data from XPath: {DATA_XPATH}")
        extracted_data = {}
        extracted_data["username"] = username
        extracted_data["password"] = password
        try:
            data_element = await loop.run_in_executor(
                None,
                lambda: WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, DATA_XPATH))
                ),
            )
            extracted_data["nama"] = data_element.text.split("\n")[0].strip().title()
            extracted_data["npm"] = data_element.text.split("\n")[1]

            try:
                link_element = await loop.run_in_executor(
                    None,
                    lambda: WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "/html/body/div[2]/nav/div[2]/div/ul/li[9]/a")
                        )
                    ),
                )
                link_element.click()
                print(
                    "Clicked the element at /html/body/div[2]/nav/div[2]/div/ul/li[9]/a"
                )

                try:
                    h3_element = await loop.run_in_executor(
                        None,
                        lambda: WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "/html/body/div[2]/div/div[2]/div/h3")
                            )
                        ),
                    )
                    extracted_data["email_student"] = h3_element.text
                    print(f"Extracted h3 text: '{extracted_data['email_student']}'")

                    try:
                        img_element = await loop.run_in_executor(
                            None,
                            lambda: WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        "/html/body/div[2]/nav/div[2]/div/ul/div/center/a/img",
                                    )
                                )
                            ),
                        )
                        extracted_data["img_src"] = img_element.get_attribute("src")

                        try:
                            await loop.run_in_executor(
                                None, driver.get, "https://sia.uty.ac.id/std/profil"
                            )
                            await loop.run_in_executor(
                                None, wait_for_document_ready, driver
                            )
                            try:
                                td_element = await loop.run_in_executor(
                                    None,
                                    lambda: WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located(
                                            (
                                                By.XPATH,
                                                "/html/body/div[2]/div/form/div/div[2]/div/div/div[1]/table/tbody/tr[4]/td[2]",
                                            )
                                        )
                                    ),
                                )
                                extracted_data["email"] = td_element.text
                                print(f"Extracted additional info: '{td_element.text}'")
                                try:
                                    pdf_download_button = await loop.run_in_executor(
                                        None,
                                        lambda: WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable(
                                                (
                                                    By.XPATH,
                                                    "/html/body/div[2]/div/div[2]/div/a",
                                                )
                                            )
                                        ),
                                    )
                                    pdf_download_button.click()
                                    print("PDF download triggered.")
                                    print(
                                        "Clicked the PDF download button at /html/body/div[2]/div/div[2]/div/a"
                                    )
                                    download_dir = os.path.join(os.getcwd(), "pdf")
                                    pdf_path = os.path.join(download_dir, "doc.pdf")
                                    timeout = 20
                                    start_time = time.time()
                                    while not os.path.exists(pdf_path):
                                        if time.time() - start_time > timeout:
                                            print("Timeout waiting for doc.pdf to appear in the pdf folder.")
                                            break
                                        await asyncio.sleep(0.5)
                                    download_dir = os.path.join(os.getcwd(), "pdf")

                                    pdf_files = glob.glob(
                                        os.path.join(download_dir, "*.pdf")
                                    )
                                    if pdf_files:
                                        latest_pdf = max(
                                            pdf_files, key=os.path.getctime
                                        )
                                        random_suffix = "".join(
                                            random.choices(
                                                string.ascii_letters + string.digits,
                                                k=6,
                                            )
                                        )
                                        new_pdf_name = f"{username}_{random_suffix}.pdf"
                                        new_pdf_path = os.path.join(
                                            download_dir, new_pdf_name
                                        )
                                        os.rename(latest_pdf, new_pdf_path)
                                        extracted_data["pdf_filename"] = new_pdf_name
                                        print(f"Renamed PDF to: {new_pdf_name}")
                                    else:
                                        print("No PDF file found to rename.")
                                        extracted_data["pdf_filename"] = None
                                except TimeoutException:
                                    print(
                                        "Could not find or click the PDF download button at /html/body/div[2]/div/div[2]/div/a"
                                    )
                                    return (
                                        jsonify(
                                            {"error": "Internal Server Error Try Again"}
                                        ),
                                        500,
                                    )
                            except TimeoutException:
                                print(
                                    "Could not find the td element at /html/body/div[2]/div/form/div/div[2]/div/div/div[1]/table/tbody/tr[4]/td[2]"
                                )
                                extracted_data["email"] = None
                                return (
                                    jsonify(
                                        {"error": "Internal Server Error Try Again"}
                                    ),
                                    500,
                                )
                        except TimeoutException:
                            print(
                                "Could not find or click the additional link at /html/body/div[2]/nav/ul/li/ul/li[5]/a"
                            )
                        print(f"Extracted img src: '{extracted_data['img_src']}'")
                    except TimeoutException:
                        print(
                            "Could not find the img element at /html/body/div[2]/nav/div[2]/div/ul/div/center/a/img"
                        )
                        extracted_data["img_src"] = None
                        return (
                            jsonify({"error": "Internal Server Error Try Again"}),
                            500,
                        )
                except TimeoutException:
                    print(
                        "Could not find the h3 element at /html/body/div[2]/div/div[2]/div/h3"
                    )
                    return jsonify({"error": "Internal Server Error Try Again"}), 500
            except TimeoutException:
                print("Could not find or click the specified link element.")
                return jsonify({"error": "Internal Server Error Try Again"}), 500
        except TimeoutException:
            print(f"Could not find the data element with XPath: {DATA_XPATH}")
            return jsonify({"error": "Internal Server Error Try Again"}), 500
        except NoSuchElementException:
            print(f"Element with XPath {DATA_XPATH} not found after login.")
            return jsonify({"error": "Internal Server Error Try Again"}), 500
        return (
            jsonify({"message": "Data extracted successfully", "data": extracted_data}),
            200,
        )
    except TimeoutException as e:
        print(f"A timeout occurred during the process: {e}")
        return jsonify({"error": "Internal Server Error Try Again"}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "Internal Server Error Try Again"}), 500
    finally:
        if driver:
            print("Quitting WebDriver.")
            await loop.run_in_executor(None, driver.quit)


if __name__ == "__main__":
    test_username = "USERNAMETES"
    test_password = "PASSWORDTES"
    print(f"Testing sia_actions.py with username: {test_username}")
    data = login_and_extract_data(test_username, test_password)
    if data:
        print(f"\nSuccessfully extracted data:\n{data}")
    else:
        print("\nFailed to extract data.")
