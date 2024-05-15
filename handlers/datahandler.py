""" Class to organize and write data. 

    Written by: Travis M. Moore
    Created: April 18, 2024
    Last edited: May 09, 2024
"""

###########
# Imports #
###########
# Standard library
import logging

# Custom
#from tmpy import readwrite
from ..readwrite import CSVFile
#from tmpy.readwrite import CSVFile

###########
# Logging #
###########
logger = logging.getLogger(__name__)

###############
# DataHandler #
###############
class DataHandler:
    """ Class to organize and write data to file. """
    def __init__(self):
        logger.debug("Initializing DataHandler")


    def _merge_dicts(self, dict_list):
        """ Loop through list of dicts and merge. """
        logger.debug("Merging list of dictionaries")
        merged = {}
        for d in dict_list:
            merged.update(d)
        return merged


    def _get_py_vars(self, tkvar_dict):
        """ Get values from Tk Vars. """
        logger.debug("Collecting TkVars values")
        # New empty dict
        converted = {}
        # Get TkVar values, if possible
        for key in tkvar_dict:
            try:
                converted[key] = tkvar_dict[key].get()
            except:
                converted[key] = tkvar_dict[key]
        # Return dict with TkVar values
        return converted


    def _reorder_dict(self, data_dict, order):
        """ Reorder a provided dictionary. Exclude unmentioned keys. """
        logger.debug("Reordering output dictionary")
        try:
            reordered = dict((i, data_dict[i]) for i in order)
            return reordered
        except KeyError as e:
            logger.exception("Unexpected key '%s'", e)
            raise KeyError


    def save_data(self, filepath, dict_list, **kwargs):
        """ Merge/convert/reorder dicts and write to file. """
        logger.debug("Organizing data to write to file")
        # Look for kwargs
        order = kwargs.pop('order', None)

        # Merge list of dicts into single dict
        merged = self._merge_dicts(dict_list)

        # Get PY_VAR values
        converted = self._get_py_vars(merged)

        # Reorder dict if kwarg 'order' was provided
        if order:
            converted = self._reorder_dict(converted, order)

        # Send merged dicts to filehandler
        logger.debug("Attempting to write data to file")
        try:
            #readwrite.CSVFile(filepath, converted)
            CSVFile(filepath, converted)
        except PermissionError as e:
            raise
        except OSError as e:
            raise
        logger.debug("Save successful")
