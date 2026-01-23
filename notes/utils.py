import logging
import sys
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from os import PathLike

log_context: ContextVar[dict[str, str | int | None] | None] = ContextVar(
    "log_context", default=None
)


def set_log_context(**kwargs: str | int | None) -> None:
    current = log_context.get() or {}
    log_context.set({**current, **kwargs})


def clear_log_context() -> None:
    log_context.set(None)


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        ctx = log_context.get() or {}
        record.user_id = ctx.get("user_id", "-")
        record.update_id = ctx.get("update_id", "-")
        record.request_id = ctx.get("request_id", "-")
        return True


def setup_logging(
    log_file_path: str | PathLike,
) -> tuple[logging.Logger, logging.Logger, logging.Logger]:
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | uid=%(user_id)s | upd=%(update_id)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    context_filter = ContextFilter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(context_filter)

    def make_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if not logger.handlers:
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
        return logger

    tg_logger = make_logger("tg")
    notion_logger = make_logger("notion")
    global_logger = make_logger("global")

    return global_logger, tg_logger, notion_logger
