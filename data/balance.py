import requests
from web3 import Web3

from constants import BTC_ADDRESS, SOL_ADDRESS, SUI_ADDRESS, META_MASK, ETH_ADDRESS, DOGE_ADDRESS


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

    def get_spot_balance(self) -> dict:
        return {
            "BTC": self.get_btc_balance(),
            "SOL": self.get_sol_balance(),
            "SUI": self.get_sui_balance(),
            "USDC": self.get_usdc_balance(),
            "ETH": self.get_eth_balance(),
            "DOGE": self.get_dodge_balance()
        }

    def get_leverage_balace(self) -> dict:
        return {
            "BTCBULL2X": self.get_btcbull2x()
        }

    def get_btc_balance(self) -> float:
        """
        Returns the balance of Bitcoin in the wallet.
        """
        url = 'https://blockstream.info/api/address'
        address = BTC_ADDRESS

        respose = requests.get(f"{url}/{address}").json()
        sats = respose['chain_stats']['funded_txo_sum'] - respose['chain_stats']['spent_txo_sum']
        return sats / 1e8

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

        return lamports / 1e9

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
                return int(b["totalBalance"]) / 1e9

        return 0.0

    def get_usdc_balance(self) -> float:
        ARBITRUM_RPC = "https://arbitrum-one-rpc.publicnode.com"
        USDC_CONTRACT_ADDRESS = Web3.to_checksum_address("0xaf88d065e77c8cC2239327C5EDb3A432268e5831")

        web3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC))
        contract = web3.eth.contract(address=USDC_CONTRACT_ADDRESS, abi=self.ERC20_ABI)
        decimals = contract.functions.decimals().call()
        raw_balance = contract.functions.balanceOf(Web3.to_checksum_address(META_MASK)).call()

        return raw_balance / (10 ** decimals)

    def get_eth_balance(self) -> float:
        address = ETH_ADDRESS

        w3 = Web3(Web3.HTTPProvider("https://mainnet.optimism.io"))
        balance_wei = w3.eth.get_balance(address)

        return float(w3.from_wei(balance_wei, 'ether'))

    def get_dodge_balance(self) -> float:
        url = f"https://api.blockcypher.com/v1/doge/main/addrs/{DOGE_ADDRESS}"
        response = requests.get(url).json()

        return response['final_balance'] / 1e8

    def get_btcbull2x(self) -> float:
        wallet = "0x103D99E55d94b14c359e7BbC50F94335dda000B3"
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
