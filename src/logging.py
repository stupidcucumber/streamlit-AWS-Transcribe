import logging
import sys


logging.basicConfig(
    format="[%(levelname)s] - [%(name)s] - %(message)s",
    level="INFO",
    stream=sys.stdout,
    force=True
)


def getLogger(name: str) -> logging.Logger:
    return logging.getLogger(name)