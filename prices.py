import logging
import requests
from requests import RequestException, Response
from constants import CRYPTO_PRICES_URL


logger = logging.getLogger(__name__)


def fetch_prices(symbols: list) -> dict:
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
