import logging
import requests
from requests import RequestException
from constants import CRYPTO_PRICES_URL


logger = logging.getLogger(__name__)


def fetch_prices(symbols: list) -> dict:
    price_dict = {}

    for sym in symbols:
        try:
            response = requests.get(f"{CRYPTO_PRICES_URL}/{sym}")
            response.raise_for_status()
            price_dict[sym] = response.json()

        except RequestException as error:
            logger.error(f"Error fetching price for {sym}: {error}")
            price_dict[sym] = None

    logger.debug(f"Fetched prices: {price_dict}")

    return price_dict
