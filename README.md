# SIA UTY Data Extractor

This project is a Python-based application that automates the process of logging into the Universitas Teknologi Yogyakarta (UTY) Student Information System (SIA) at `https://sia.uty.ac.id/std`, solving the CAPTCHA, and extracting specific academic data. It exposes this functionality via a Flask web API.

## Features

* Automated login to SIA UTY.
* Automatic CAPTCHA solving.
* Extraction of specific data from the SIA dashboard.
* Flask API endpoint to trigger the process and retrieve data.
* Headless browser operation using Selenium and ChromeDriver.

## Prerequisites

* Python 3.x
* Google Chrome browser installed (as Selenium uses ChromeDriver)

## Setup and Installation

1.  **Clone the repository (or download the files):**
    ```bash
    # If you have it as a git repository
    # git clone https://github.com/Charles03010/login-with-sia.git
    # cd login-with-sia
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    * On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    * On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    Ensure you have `requirements.txt` in your project directory.
    ```bash
    pip install -r requirements.txt
    ```
    This will install Flask, Selenium, and webdriver-manager.

## Files

* **`app.py`**: The main Flask application file. It defines the API endpoint to receive login credentials and return extracted data.
* **`sia_actions.py`**: Contains the core logic for interacting with the SIA website using Selenium. This includes navigation, filling login forms, solving the CAPTCHA, and extracting data.
* **`driver_setup.py`**: Handles the setup and configuration of the Selenium WebDriver (Chrome). It includes options for headless Browse and waits for pages to load completely.
* **`requirements.txt`**: Lists the Python dependencies for the project.

## How it Works

1.  The Flask application (`app.py`) receives a POST request with `username` and `password`.
2.  It calls the `login_and_extract_data` function from `sia_actions.py`.
3.  `sia_actions.py` initializes a headless Chrome WebDriver using `driver_setup.py`.
4.  It navigates to the SIA login page (`https://sia.uty.ac.id/std`).
5.  The script enters the provided username and password.
6.  It reads the CAPTCHA text. It parses the numbers, calculates, and enters the solution.
7.  After submitting the login form, it waits for the dashboard page to load, indicated by the presence of a specific element ("KALENDER AKADEMIK" heading).
8.  If login is successful, it extracts text data from a predefined XPath on the page.
9.  The extracted data (or an error message if an issue occurs) is returned to the Flask app, which then sends it as a JSON response.

## Running the Application

To start the Flask development server:

```bash
python app.py
