import logging
import colorlog


def get_logger(name):
    logger = logging.getLogger(f"codemonkey:{name}")
    return logger

class TruncatingFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        message = super().format(record)
        if len(message) > 100:
            return message[:97] + "..."
        return message


def setup_logging(debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        handler = colorlog.StreamHandler()
        handler.setFormatter(
            TruncatingFormatter(
                "%(log_color)s%(levelname)-8s %(message)s%(reset)s",
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
        get_logger("logging").debug("Debug logging enabled")
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
