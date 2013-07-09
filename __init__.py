import os
import json
import logging.config

def setup_logging(config='logging.json', log_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration """
    value = os.getenv(env_key, None)
    if value:
        config = value
        
    if os.path.exists(config):
        with open(path, 'rt') as f:
            config = json.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=log_level)

from apps import *
from core import *
from core.util import *

