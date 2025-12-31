import logging
import sys
from logging.handlers import RotatingFileHandler
from os import PathLike


def setup_logging(
    log_file_path: str | PathLike,
) -> tuple[logging.Logger, logging.Logger, logging.Logger]:
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    def make_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if not logger.handlers:
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
        return logger

    tg_logger = make_logger("tg")  # todo: можно взять готовый из aiogram будто бы
    notion_logger = make_logger("notion")
    global_logger = make_logger("global")

    return global_logger, tg_logger, notion_logger
