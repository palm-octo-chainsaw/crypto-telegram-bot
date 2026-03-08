import requests
import krakenex
from web3 import Web3
from binance.client import Client


from constants import (
    BTC_ADDRESS, SOL_ADDRESS,
    SUI_ADDRESS, META_MASK,
    ETH_ADDRESS, DOGE_ADDRESS,
    XRP_ADDRESS,
    BINANCE_API_KEY, BINANCE_API_SECRET,
    KRAKEN_API_KEY, KRAKEN_API_SECRET,
)


class Balance:
    def __init__(self):
        self.ERC20_ABI = [{"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf",
                          "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
                          {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "",
                                                                                            "type": "uint8"}],
                          "type": "function"},
                          {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "",
                                                                                          "type": "string"}],
                          "type": "function"}]
        self.binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        self.kraken_client = krakenex.API(key=KRAKEN_API_KEY, secret=KRAKEN_API_SECRET)

    def get_spot_balance(self) -> dict:
        kraken_map = {
            "BTC":  "XXBT",
            "ETH":  "XETH",
            "SOL":  "SOL",
            "XRP":  "XXRP",
            "DOGE": "XDG",
            "USDC": "USDC",
            "LINK": "LINK",
            "PAXG": "PAXG",
        }

        kraken_raw = self.get_raw_kraken_balance()

        def kraken(symbol: str) -> float:
            return float(kraken_raw.get(kraken_map.get(symbol, ""), 0.0))

        return {
            "BTC":  self.get_btc_balance() + kraken("BTC"),
            "PAXG": kraken("PAXG"),
            "SOL":  self.get_sol_balance() + kraken("SOL"),
            "SUI":  self.get_sui_balance(),
            "USDC": self.get_usdc_balance() + kraken("USDC"),
            "ETH":  self.get_eth_balance() + kraken("ETH"),
            "DOGE": self.get_dodge_balance() + kraken("DOGE"),
            "XRP":  self.get_xrp_balance() + kraken("XRP"),
            "LINK": self.get_binance_balance("LINK") + kraken("LINK"),
            "HYPE": self.get_hype_balance(),
            "BNB":  self.get_binance_balance("BNB"),
        }

    def get_leverage_balace(self) -> dict:
        return {
            "BTCBULL2X": self.get_btcbull2x(),
            "BTCBULL4X": self.get_btcbull4x(),
            "ETHBULL4X": self.get_ethbull4x()
        }

    def get_btc_balance(self) -> float:
        """
        Returns the balance of Bitcoin in the wallet.
        """
        url = 'https://blockchain.info/q/addressbalance/'
        address = BTC_ADDRESS

        balance = requests.get(f"{url}/{address}").json()
        return (balance / 1e8) + self.get_binance_balance("BTC")

    def get_sol_balance(self) -> float:
        url = "https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [SOL_ADDRESS]
        }

        res = requests.post(url, json=data, headers=headers).json()
        lamports = res["result"]["value"]

        return (lamports / 1e9) + self.get_binance_balance("SOL")

    def get_sui_balance(self) -> float:
        url = "https://fullnode.mainnet.sui.io:443"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "suix_getAllBalances",
            "params": [SUI_ADDRESS]
        }

        response: dict = requests.post(url, json=payload).json()
        balances = response.get("result", [])

        for b in balances:
            if b["coinType"] == "0x2::sui::SUI":
                return (int(b["totalBalance"]) / 1e9) + self.get_binance_balance("SUI")

        return 0.0

    def get_usdc_balance(self) -> float:
        ARBITRUM_RPC = "https://arbitrum-one-rpc.publicnode.com"
        USDC_CONTRACT_ADDRESS = Web3.to_checksum_address("0xaf88d065e77c8cC2239327C5EDb3A432268e5831")

        web3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC))
        contract = web3.eth.contract(address=USDC_CONTRACT_ADDRESS, abi=self.ERC20_ABI)
        decimals = contract.functions.decimals().call()
        raw_balance = contract.functions.balanceOf(Web3.to_checksum_address(META_MASK)).call()

        return (raw_balance / (10 ** decimals)) + self.get_binance_balance("USDC")

    def get_eth_balance(self) -> float:
        """
        Returns ETH balance (in ETH) for the given wallet address using the provided RPC URL.
        """
        wallet = ETH_ADDRESS
        ARBITRUM_RPC = "https://arbitrum-one-rpc.publicnode.com"
        try:
            w3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC))
            if not w3.is_connected():
                raise ConnectionError("Failed to connect to the Ethereum node.")

            balance_wei = w3.eth.get_balance(Web3.to_checksum_address(wallet))
            return float(w3.from_wei(balance_wei, 'ether')) + self.get_binance_balance("ETH")

        except Exception as e:
            print(f"Error fetching ETH balance: {e}")
            return 0.0

    def get_dodge_balance(self) -> float:
        url = f"https://api.blockcypher.com/v1/doge/main/addrs/{DOGE_ADDRESS}"
        response: dict = requests.get(url).json()

        return (response.get('final_balance', 0) / 1e8) + self.get_binance_balance("DOGE")

    def get_btcbull2x(self) -> float:
        wallet = META_MASK
        token_contract = "0xe3254397f5D9C0B69917EBb49B49e103367B406f"
        infra_url = "https://arbitrum-one-rpc.publicnode.com"

        w3 = Web3(Web3.HTTPProvider(infra_url))

        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(token_contract), abi=self.ERC20_ABI)
            balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet)).call()
            decimals = contract.functions.decimals().call()

            return balance / (10 ** decimals)

        except Exception as e:
            print(f"Error fetching token balance: {e}")
            return 0.0

    def get_btcbull4x(self) -> float:
        wallet = META_MASK
        token_contract = "0xd49d22f2a2f05B2088fD42503409E430a8a7D827"
        infra_url = "https://arbitrum-one-rpc.publicnode.com"

        w3 = Web3(Web3.HTTPProvider(infra_url))

        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(token_contract), abi=self.ERC20_ABI)
            balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet)).call()
            decimals = contract.functions.decimals().call()

            return balance / (10 ** decimals)

        except Exception as e:
            print(f"Error fetching token balance: {e}")
            return 0.0

    def get_ethbull4x(self) -> float:
        wallet = META_MASK
        token_contract = "0xBf4aB4224B2AC26667Cd4b8A0E5134D55cB0B293"
        infra_url = "https://arbitrum-one-rpc.publicnode.com"

        w3 = Web3(Web3.HTTPProvider(infra_url))

        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(token_contract), abi=self.ERC20_ABI)
            balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet)).call()
            decimals = contract.functions.decimals().call()

            return balance / (10 ** decimals)

        except Exception as e:
            print(f"Error fetching token balance: {e}")
            return 0.0

    def get_xrp_balance(self) -> float:
        address = XRP_ADDRESS
        url = "https://s1.ripple.com:51234/"
        payload = {
            "method": "account_info",
            "params": [
                {
                    "account": address,
                    "ledger_index": "validated",
                    "strict": True
                }
            ]
        }

        try:
            response = requests.post(url, json=payload)
            data = response.json()
            balance_drops = int(data["result"]["account_data"]["Balance"])

            return (balance_drops / 1_000_000) + self.get_binance_balance("XRP")

        except Exception as e:
            print(f"XRP Balance Fetch Error: {e}")
            return 0.0

    def get_binance_balance(self, symbol: str) -> float:
        binance_data = self.binance_client.get_asset_balance(symbol)

        if binance_data:
            return float(binance_data['free']) + float(binance_data['locked'])
        return 0.0

    def get_hype_balance(self) -> float:
        return 0.0

    def get_raw_kraken_balance(self) -> dict:
        try:
            result = self.kraken_client.query_private("Balance")
            if result.get("error"):
                print(f"Kraken API error: {result['error']}")
                return {}
            return result["result"]
        except Exception as e:
            print(f"Kraken balance fetch error: {e}")
            return {}
