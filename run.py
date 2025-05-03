from telegram.ext import ApplicationBuilder, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

from constants import BOT_TOKEN
from portfolio import Portfolio
from utils.command_handlers import (
    post_init, check, set_target,
    get_targets, get_total, get_balance
)


if __name__ == "__main__":
    portfolio = Portfolio()
    portfolio.process()

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("balance", get_balance))
    app.add_handler(CommandHandler("total", get_total))
    app.add_handler(CommandHandler("set_target", set_target))
    app.add_handler(CommandHandler("get_targets", get_targets))

    scheduler = BackgroundScheduler({"apscheduler.timezone": "Europe/Sofia"})
    scheduler.add_job(portfolio.process, trigger="cron", hour=10, minute=0, )
    scheduler.start()

    app.run_polling()
