from os import getenv
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")
CHAT_ID = getenv("CHAT_ID")
BTC_ADDRESS = getenv("BTC_ADDRESS")
SOL_ADDRESS = getenv("SOL_ADDRESS")
SUI_ADDRESS = getenv("SUI_ADDRESS")
USDC_ADDRESS = getenv("USDC_ADDRESS")
TELEGRAM_API = "https://api.telegram.org/bot{}".format(BOT_TOKEN)
CRYPTO_PRICES_URL = "https://cryptoprices.cc/"
