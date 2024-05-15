""" Imports. """

# Standard library
from pathlib import Path

# Specify logger directory
LOGGER_DIRECTORY = Path(__file__).parent

# Custom imports
from .jsonformatter import (
    JSONFormatter
)

__all__ = [
    'JSONFormatter'
]

LOGGER_CONFIG_JSON = LOGGER_DIRECTORY / 'logger_config.json'
