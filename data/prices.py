import logging
from typing import Dict
import requests
from requests import RequestException, Response
# from bs4 import BeautifulSoup

from constants import CRYPTO_PRICES_URL


logger = logging.getLogger(__name__)


def fetch_prices(symbols: list) -> Dict:
    try:
        params = {
            "symbols": ", ".join(map(str, symbols)),
            "vs_currencies": "usd"
        }
        response: Response = requests.get(CRYPTO_PRICES_URL, params=params)
        response.raise_for_status()

        logger.info("Prices fetched successfully: %s", response)
        response: dict = response.json()

        key: str
        value: list
        prices: dict = {}

        for key, value in response.items():
            if 'usd' not in value:
                logger.warning("Price for %s not found", key)
                continue

            prices[key.upper()] = value['usd']

        return prices

    except RequestException as error:
        logger.error("Error fetching prices: %s", error)
        return {}


# def get_leverage_prices() -> Dict:
#     site = "https://toros.finance/vault/0xd49d22f2a2f05b2088fd42503409e430a8a7d827"

#     responce: Response = requests.get(site)

#     print(responce.text)


# get_leverage_prices()
