import logging

from app.settings import settings

logger = logging.getLogger("deribit_price_tracker")
logger.setLevel(settings.LOG_LEVEL)
logger.propagate = False

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
