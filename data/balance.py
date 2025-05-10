import requests
from web3 import Web3

from constants import BTC_ADDRESS, SOL_ADDRESS, SUI_ADDRESS, USDC_ADDRESS, ETH_ADDRESS


class Balance:
    def get_balance(self) -> dict:
        return {
            "BTC": self.get_btc_balance(),
            "SOL": self.get_sol_balance(),
            "SUI": self.get_sui_balance(),
            "USDC": self.get_usdc_balance(),
            "ETH": self.get_eth_balance()
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
        ERC20_ABI = ('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf",'
                     '"outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]')

        web3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC))
        contract = web3.eth.contract(address=USDC_CONTRACT_ADDRESS, abi=ERC20_ABI)
        raw_balance = contract.functions.balanceOf(Web3.to_checksum_address(USDC_ADDRESS)).call()

        return raw_balance / 1e6

    def get_eth_balance(self) -> float:
        address = ETH_ADDRESS

        w3 = Web3(Web3.HTTPProvider("https://mainnet.optimism.io"))
        balance_wei = w3.eth.get_balance(address)

        return float(w3.from_wei(balance_wei, 'ether'))
