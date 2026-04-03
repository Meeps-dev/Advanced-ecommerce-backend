import logging
import os
import sys
from pythonjsonlogger import jsonlogger


class DefaultFieldsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        defaults = {
            "request_id": "-",
            "method": "-",
            "path": "-",
            "status_code": 0,
            "latency_ms": 0,
            "event": "-",
            "entity": "-",
            "entity_id": "-",
            "user_id": "-",
        }

        for key, value in defaults.items():
            if not hasattr(record, key):
                setattr(record, key, value)
        return True


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",      # cyan
        "INFO": "\033[32m",       # green
        "WARNING": "\033[33m",    # yellow
        "ERROR": "\033[31m",      # red
        "CRITICAL": "\033[1;31m", # bold red
    }
    RESET = "\033[0m"
    SERVICE_COLORS = {
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "yellow": "\033[33m",
        "green": "\033[32m",
        "red": "\033[31m",
    }

    def format(self, record: logging.LogRecord) -> str:
        service_name = os.getenv("LOG_SERVICE", "app").upper()
        service_color = self.SERVICE_COLORS.get(
            os.getenv("LOG_SERVICE_COLOR", "blue").lower(),
            "\033[34m",
        )
        record.service = f"{service_color}[{service_name}]{self.RESET}"

        base = super().format(record)
        level = record.levelname
        color = self.COLORS.get(level, "")
        if not color:
            return base
        return f"{color}{base}{self.RESET}"


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    json_formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(event)s %(entity)s %(entity_id)s %(user_id)s %(request_id)s %(method)s %(path)s %(status_code)s %(latency_ms)s"
    )
    pretty_formatter = ColorFormatter(
        "%(asctime)s | %(service)s %(levelname)-8s | %(name)s | %(message)s"
    )
    default_fields_filter = DefaultFieldsFilter()
    log_format = os.getenv("LOG_FORMAT", "json").lower()

    stream_handler = logging.StreamHandler(sys.stdout)
    if log_format in {"pretty", "text", "color"}:
        stream_handler.setFormatter(pretty_formatter)
    else:
        stream_handler.setFormatter(json_formatter)
    stream_handler.addFilter(default_fields_filter)
    root_logger.addHandler(stream_handler)

    # Optional file logging for local debugging only
    if os.getenv("LOG_TO_FILE", "false").lower() == "true":
        file_handler = logging.FileHandler("app_errors.log")
        file_handler.setFormatter(json_formatter)
        file_handler.addFilter(default_fields_filter)
        root_logger.addHandler(file_handler)

    return logging.getLogger("ecommerce_app")


logger = setup_logging()