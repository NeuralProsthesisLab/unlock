import os
import json
import inspect
import logging.config

def setup_logging(config=None, log_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration """
    if not config:
        config=os.path.join(os.path.dirname(inspect.getfile(setup_logging)), 'logging.json')
        
    value = os.getenv(env_key, None)        
    if value:
        config = value
        
    if os.path.exists(config):
        with open(config, 'rt') as file_descriptor:
            json_binary = file_descriptor.read()
            json_string = json.loads(json_binary)
        logging.config.dictConfig(json_string)
    else:
        logging.basicConfig(level=log_level)
        
setup_logging()

from apps import *
from core import *
from util import *

