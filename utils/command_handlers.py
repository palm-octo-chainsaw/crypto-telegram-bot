from telegram import Update, BotCommand
from telegram.ext import ContextTypes, ExtBot, Application

from utils.helpers import format_message, write_json
from portfolio import Portfolio
from data.balance import Balance


portfolio = Portfolio()

targets_file_path = "config/targets.json"


async def set_bot_commands(bot: ExtBot) -> None:
    await bot.set_my_commands([
        BotCommand("check", "Check portfolio rebalance status"),
        BotCommand("balance", "Get current portfolio balance"),
        BotCommand("total", "Get total portfolio value"),
        BotCommand("set_target", "Set target % for a token (e.g. /set_target BTC 40)"),
        BotCommand("get_targets", "Show current target allocations"),
    ])


async def post_init(application: Application) -> None:
    await set_bot_commands(application.bot)


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = portfolio.listener()

    await update.message.reply_text(message, parse_mode="Markdown")


async def get_targets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "🎯 *Current Targets*\n\n"
    total = 0

    for symbol, percent in portfolio.targets.items():
        total += percent
        message += f"{symbol}: {percent}%\n"

    message += f"\nTotal: {total}%"

    await update.message.reply_text(format_message(message), parse_mode="Markdown")


async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        symbol = context.args[0].upper()
        percent = int(context.args[1])
        portfolio.targets[symbol] = percent
        write_json(portfolio.targets, targets_file_path)

        await update.message.reply_text(f"✅ Target for {symbol} set to {percent}%", parse_mode="Markdown")

    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Usage: /set_target SYMBOL PERCENT")


async def get_total(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        total: float = portfolio.fetch_live_data()[-1]
        message = f"💰 *Total Portfolio Value*:\n\n${total:,.2f} USD"

        await update.message.reply_text(format_message(message), parse_mode="Markdown")

    except Exception as error:
        await update.message.reply_text(f"⚠️ Error: {str(error)}", parse_mode="Markdown")


async def get_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        message = "💰 *Portfolio Balance*:\n\n"
        for symbol, value in Balance().get_balance().items():
            message += f"{symbol}: {value}\n"

        await update.message.reply_text(format_message(message), parse_mode="Markdown")

    except Exception as error:
        await update.message.reply_text(f"⚠️ Error: {str(error)}", parse_mode="Markdown")
