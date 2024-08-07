import logging
import colorlog


class LogFilter(logging.Filter):
    def __init__(self, prefix):
        super().__init__()
        self.prefix = prefix

    def filter(self, record):
        if record.levelno == logging.DEBUG:
            return record.name.startswith(self.prefix)
        return True

def get_logger(name):
    logger = logging.getLogger(f"codemonkey:{name}")
    return logger


MAX_LENGTH = 200
# MAX_LENGTH = 0


class TruncatingFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        message = super().format(record)
        if record.levelno == logging.DEBUG and MAX_LENGTH > 0 and len(message) > MAX_LENGTH:
            return message[: MAX_LENGTH - 3] + "...\033[0m"
        return message


def setup_logging(debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        handler = colorlog.StreamHandler()
        handler.setFormatter(
            TruncatingFormatter(
                "%(log_color)s%(levelname)-8s %(name)s %(message)s%(reset)s",
                log_colors={
                    "DEBUG": "light_black",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
        )
        root_logger = logging.getLogger()

        # Remove any existing handlers and add our new handler
        root_logger.handlers = []
        root_logger.addHandler(handler)

        # Add the custom filter
        name_filter = LogFilter("codemonkey:")
        root_logger.addFilter(name_filter)

        get_logger("logging").debug("Debug logging enabled")
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
