""" Shared logging functions. 

    Written by: Travis M. Moore
    Last edited: May 24, 2024
"""

###########
# Imports #
###########
# Standard library
import json
import logging.config
import logging.handlers
import os
from pathlib import Path

# Custom
from ..logger import LOGGER_CONFIG_JSON
from ..logger import JSONFormatter
from .helper_funcs import flatten_text


def setup_logging(NAME):
    """ Create output log file path. 
        Import and update logging config JSON file.
        Apply config to logger.
    """
    # Create logging output file path based on app name
    flat_name = flatten_text(NAME)
    _app_with_ext = flat_name + '.log.jsonl'
    filename = os.path.join(Path.home(), flat_name, _app_with_ext)

    # Specify logging config file path
    try:
        config_file = os.path.join(
            os.environ['TMPY'],
            'tmpy',
            'logger',
            'logger_config.json'
        )
    except KeyError:
        config_file = LOGGER_CONFIG_JSON

    # Import and update logging config file
    with open(config_file) as f_in:
        config = json.load(f_in)
        # Update output file location based on app name
        config['handlers']['file']['filename'] = filename
        # Pass in custom JSONFormatter
        config['formatters']['json']['()'] = JSONFormatter

    # Apply logging config
    return config
    #logging.config.dictConfig(config)
