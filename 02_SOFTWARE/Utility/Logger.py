import logging


def setup_custom_logger(name: str, level: int) -> logging.log:
    """
    Sets the logging format, level and name of the logger.

    :type name: str
    :param name: Name of the logger.
    :type level: int
    :param level: Initial logging level.
    :return: Returns a log.
    """
    formatter = logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d %(filename)6s:%(lineno)s - %(levelname)s - %(module)s - %(funcName)s()] - %(message)s",
        datefmt="%H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    logger.addHandler(handler)
    return logger
