import logging


def setup_custom_logger(name: str, level: int) -> logging.log:
    """
    Sets the logging format, level and name of the logger.
    :param name: Name of the logger.
    :param level: Initial logging level.
    :return: Returns a log.
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    logger.addHandler(handler)
    return logger
