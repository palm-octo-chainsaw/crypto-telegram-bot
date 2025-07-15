from typing import Dict, Tuple
from utils.helpers import load_json, setup_logging
from data.prices import fetch_prices
from telegram_bot import Bot
from summary import Summary
from data.balance import Balance


logger = setup_logging('debug')


class Portfolio:
    def __init__(self):
        self.bot: Bot = Bot()
        self.summary: Summary = Summary()
        self.targets: dict = load_json("config/targets.json")
        self.portfolio: dict = Balance().get_spot_balance()
        self.send_rebalance: bool = False

    def get_targets(self) -> Dict[str, int]:
        """Return the target allocations."""
        return self.targets

    def set_target(self, symbol: str, percent: int) -> Dict[str, int]:
        """Set the target allocation for a specific symbol."""
        self.targets[symbol] = percent
        logger.debug("Target for %s set to %d%%", symbol, percent)
        return self.targets

    def update_portfolio(self) -> None:
        self.portfolio: dict = Balance().get_spot_balance()
        logger.debug("Portfolio updated: %s", self.portfolio)

    def fetch_live_data(self) -> Tuple[dict, dict, float]:
        prices = fetch_prices([symbol for symbol in self.portfolio])
        values = {
            symbol: amount * prices[symbol]
            for symbol, amount in self.portfolio.items()
        }
        total_value = sum(values.values())
        logger.debug("Total: %s", total_value)
        return prices, values, total_value

    def update_telegram(self, message: str) -> None:
        self.bot.send_message(message)

    def evaluate_symbol(self, values: dict, total_value) -> None:
        for symbol, value in values.items():
            current_pct = (value / total_value) * 100
            target_pct = int(self.targets[symbol])
            diff = current_pct - target_pct

            msg = f"${symbol}: {current_pct:.2f}% (Target: {target_pct}%) {'🔺' if diff > 0 else '🔻'} {diff:.2f}%"
            logger.debug(msg)
            self.summary.add_summary(msg)

            if abs(diff) > 3:
                msg = f"⚠️ *Rebalance Needed*: ${symbol} is off by {diff:+.2f}% " \
                      f"(Current: {current_pct:.2f}%; Target: {target_pct}%)"
                self.summary.add_rebalance(msg)

                logger.debug(
                    "⚠️ ${} is off by more than 5% from the target allocation! Current: {:.2f}%, Target: {}%".format(
                        symbol, current_pct, target_pct
                    )
                )
                logger.debug("⚠️ Consider rebalancing %s!", symbol)
                self.send_rebalance = True

    def calculate_rebalance(self, prices: dict, values: dict, total_value) -> Dict[str, float]:
        rebalance = {}

        for symbol in self.portfolio:
            current_value = values[symbol]
            target_value = (self.targets[symbol] / 100) * total_value
            value_diff = target_value - current_value
            unit_diff = value_diff / prices[symbol]
            rebalance[symbol] = round(unit_diff, 8)

        self.summary.add_rebalance("\n🧮 *Rebalance Plan*\n")

        for symbol, amount in rebalance.items():
            if abs(amount) < 1e-6:
                continue

            action = "Buy" if amount > 0 else "Sell"
            self.summary.add_rebalance(
                f"{action} [{abs(amount):.8f}] ${symbol} | "
                f"{'-' if action == 'Sell' else ''}${abs(amount*prices[symbol]):.2f} USD"
            )

        return rebalance

    def listener(self) -> str:
        self.send_rebalance = False
        self.update_portfolio()
        prices, values, total_value = self.fetch_live_data()
        self.evaluate_symbol(values, total_value)
        self.calculate_rebalance(prices, values, total_value) if self.send_rebalance else None
        return self.summary.flush_summary()

    def process(self) -> None:
        self.send_rebalance = False
        self.update_portfolio()
        prices, values, total_value = self.fetch_live_data()
        self.evaluate_symbol(values, total_value)
        self.calculate_rebalance(prices, values, total_value) if self.send_rebalance else None
        self.update_telegram(self.summary.flush_summary())
