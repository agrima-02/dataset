import logging
import os


def setup_logger():

    os.makedirs(
        "../logs",
        exist_ok=True
    )

    logger = logging.getLogger(
        "buddhist_pipeline"
    )

    if logger.handlers:
        return logger

    logger.setLevel(
        logging.INFO
    )

    formatter = logging.Formatter(

        "[%(asctime)s] "

        "%(levelname)s "

        "%(message)s",

        datefmt="%m/%d/%y %H:%M:%S"
    )


    # TERMINAL OUTPUT

    stream_handler = logging.StreamHandler()

    stream_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        stream_handler
    )


    # FILE OUTPUT

    file_handler = logging.FileHandler(

        "../logs/pipeline.log",

        encoding="utf-8"
    )

    file_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )


    return logger