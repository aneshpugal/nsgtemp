import logging
from logging import Filter

class TriggerIdFilter(Filter):
    def __init__(self, trigger_id):
        self.trigger_id = trigger_id

    def filter(self, record):
        record.trigger_id = self.trigger_id
        return True

def configure_logging(trigger_id):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("/home/anesh-zt668/Documents/NSG_PYTHON_VS/Logs/stdout.log")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - Trigger ID: %(trigger_id)s - %(message)s')
    file_handler.setFormatter(formatter)
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(file_handler)
    logger.addFilter(TriggerIdFilter(trigger_id))

    return logger

# Initialize a default logger
logger = configure_logging("default_trigger_id")
