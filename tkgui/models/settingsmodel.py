""" Model for reading/writing application settings. """

###########
# IMPORTS #
###########
# Standard library
import os
import json
import logging
import sys
from pathlib import Path

# Custom
from tmpy.functions import helper_funcs as hf

###########
# Logging #
###########
logger = logging.getLogger(__name__)

#################
# SettingsModel #
#################
class SettingsModel:
    """ Class to save/load user settings. """
    # Dict to hold version checking variable values
    fields = {}


    def __init__(self, parent, settings_vars, app_name):
        """ Check for/create config directory and empty config file. """
        logger.debug("Initializing SettingsModel")

        # Assign attributes
        self.parent = parent
        SettingsModel.fields = settings_vars

        # Flatten app name
        flat_name = hf.flatten_text(app_name)

        # Create a folder to store the session parameters file
        # in user's home directory
        directory = Path.home() / flat_name

        if not os.path.exists(directory):
            logger.warning("No config file directory found - creating it")
            os.makedirs(directory)

        # Path to file
        self.filepath = directory / 'config.json'

        # Attempt to load session parameters file
        self.load()


    def load(self):
        """ Attempt to load session parameters from file. """
        # If the file doesn't exist, use default values
        logger.debug("Checking for config file...")
        if not self.filepath.exists():
            logger.debug("No settings file found; " +
                  "using default values")
            # Save values to config.json
            # Requires some delay to allow setup to finish
            self.parent.after(
                1000, 
                lambda: self.parent.event_generate('<<SettingsSubmit>>')
            )
            logger.debug("Saved default settings after 1 s delay")
            return

        # Open the file and read in the raw values
        logger.debug("File found - reading raw values from " +
            "config file")
        with open(self.filepath, 'r') as fh:
            raw_values = json.load(fh)

        # Populate settings dictionary
        # Don't implicitly trust the raw values: only get known keys
        logger.debug("Loading vals into settingsmodel " +
            "if they match model keys")
        for key in self.fields:
            if key in raw_values and 'value' in raw_values[key]:
                raw_value = raw_values[key]['value']
                self.fields[key]['value'] = raw_value


    def save(self):
        """ Save current settings to file. """
        # Write to JSON file
        with open(self.filepath, 'w') as fh:
            json.dump(self.fields, fh)


    def set(self, key, value):
        """ Set Tk variables for running dict. """
        if (
            key in self.fields and 
            type(value).__name__ == self.fields[key]['type']
        ):
            self.fields[key]['value'] = value
        else:
            logger.exception("Bad key or wrong variable type")
            raise ValueError("Bad key or wrong variable type")


if __name__ == "__main__":
    pass
