import requests
from config.settings import API_BASE_URL, API_USERNAME, API_PASSWORD
from config.logger import get_logger

logger = get_logger("auth")


def get_token():
    url = f"{API_BASE_URL}/api/auth/login/"
    payload = {
        "username": API_USERNAME,
        "password": API_PASSWORD
    }

    response = requests.post(url, json=payload)
    logger.info(f"Login status: {response.status_code}")

    data = response.json()
    token = data["token"]
    logger.info("Token received successfully")
    return token
