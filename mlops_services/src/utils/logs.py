import os
from pathlib import Path
import logging
import inspect

# Setup logging with a custom save path
def setup_logger(name, log_folder="mlops_services/logs", level=logging.INFO,start_over=True):
    """Setup logger to log to console and a custom file path."""
    log_file_path = Path(log_folder)/f"{name}.log"
    os.makedirs(Path(log_folder), exist_ok=True)
    if os.path.exists(log_file_path) & start_over:
        os.remove(log_file_path)
        
    old_logger = logging.getLogger(name)
    # Remove existing handlers if any
    for handler in old_logger.handlers[:]:
        old_logger.removeHandler(handler)
        handler.close()    
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formatter)

    handler_file = logging.FileHandler(log_file_path)
    handler_file.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Clear existing handlers to avoid duplicate logs in some cases
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler_console)
    logger.addHandler(handler_file)

    return logger

# Setup logging with a custom save path
def initiate_logger(name, log_folder="mlops_services/logs", level=logging.INFO,start_over=True):
    """Setup logger to log to console and a custom file path."""
    log_file_path = Path(log_folder)/f"{name}.log"
    os.makedirs(Path(log_folder), exist_ok=True)
    
    if os.path.exists(log_file_path) & start_over:
        os.remove(log_file_path)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )

def get_logger():
    logger = logging.getLogger()  
    return logger


def validate_logger(logger):
    if logger is not None:
        return logger
    else:
        alt_logger = logging.getLogger()
        alt_logger.setLevel(logging.INFO)
        return alt_logger
    
def get_parent_logger():
    # Get the frame object of the caller's caller (parent of current function)
    parent_frame = inspect.stack()[2]
    # Get the module object of the parent frame
    parent_module = inspect.getmodule(parent_frame[0])
    # Derive the module name, default to '__main__' for the top-level script
    parent_module_name = parent_module.__name__ if parent_module else '__main__'
    
    # Get and return the logger instance for the parent module
    return logging.getLogger(parent_module_name)
    