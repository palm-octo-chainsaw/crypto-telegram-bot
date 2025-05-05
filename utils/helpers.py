import json
import logging
from logging import Logger
from datetime import datetime
from typing import Dict


def load_json(file_path) -> Dict:
    with open(file_path) as file:
        return json.load(file)


def write_json(file_path, data) -> None:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def setup_logging(level) -> Logger:
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        encoding="utf-8",
        handlers=[
            logging.FileHandler(
                f"{datetime.now().strftime('%Y_%m_%d')}.log"
            ),
            logging.StreamHandler()
        ]
    )
    return logger


def format_message(message: str) -> str:
    return f"```\n{message}```"
