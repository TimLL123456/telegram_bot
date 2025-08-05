import logging
import functools

def logger_setup(
    logger_name:str,
    logger_filename:str,
    log_console_format:str = '%(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    log_file_format:str = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
):
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_console_format)
    console_handler.setFormatter(console_formatter)

    # Create rotating file handler
    file_handler = logging.FileHandler(logger_filename)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_file_format)
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def log_function(logger:logging):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Entering function '{func.__name__}' with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.debug(f"Exiting function '{func.__name__}' with result={result}")
            return result
        return wrapper
    return decorator