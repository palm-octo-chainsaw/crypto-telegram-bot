from os import getenv
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")
CHAT_ID = getenv("CHAT_ID")
BTC_ADDRESS = getenv("BTC_ADDRESS")
SOL_ADDRESS = getenv("SOL_ADDRESS")
SUI_ADDRESS = getenv("SUI_ADDRESS")
META_MASK = getenv("META_MASK")
ETH_ADDRESS = getenv("ETH_ADDRESS")
DOGE_ADDRESS = getenv("DOGE_ADDRESS")
XRP_ADDRESS = getenv("XRP_ADDRESS")
TELEGRAM_API = "https://api.telegram.org/bot{}".format(BOT_TOKEN)
CRYPTO_PRICES_URL = "https://api.coingecko.com/api/v3/simple/price"

BTCBULL2X_CONTRACT = "0xe3254397f5D9C0B69917EBb49B49e103367B406f"
