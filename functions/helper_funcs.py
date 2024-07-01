""" General helper functions. 

    Written by: Travis M. Moore
    Lasted edited: June 19, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import sys
import os

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

#############
# Functions #
#############
def resource_path(relative_path):
    """ Create the absolute path to compiled resources.

        !DEPRECATED!
        Instead of providing the appData resource path,
        use Path(__file__).parent. 
        
        See tmgui>shared_assets>images>__init__.py for
        example usage. 
    """
    try:
        # PyInstaller creates a temp folder and stores 
        # path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def truncate_string(full_string, num_chars):
    """ Truncate given string to desired number of characters.
     
    :param full_string: String to be truncated
    :type full_string: str
    :return: The truncated string or original string
    :rtype: str
    """
    logger.info("Truncating: %s", full_string)
    # Subtract 3 to account for the leading elipsis
    max_length = int(num_chars) - 3

    # Check length of path against num_chars
    if len(full_string) >= num_chars:
        return '...' + full_string[-(max_length):]
    else:
        return full_string

def flatten_text(text):
    """ Remove special characters, force to lowercase, and 
    replace whitespace with underscores. 
    """
    logger.info("Flattening text")
    # First replace whitespaces with underscores
    no_whitespace = text.replace(' ', '_')
    # Last remove special characters
    cleaned = ''.join(
        c for c in no_whitespace if c == '_' or c.isalnum()
    ).lower()
    return cleaned

def string_to_list(string_list, datatype, sep=", "):
    """ Convert string of comma-separated values to a list
    of the specified data type.
    """
    logger.info("Converting string to list")
    # Split string into individual values
    values = string_list.split(sep)
    try:
        # Create list of specified data type
        if datatype == 'int':
            formatted = [int(ii) for ii in values]
        elif datatype == 'float':
            formatted = [float(ii) for ii in values]
        elif datatype == 'str':
            formatted = [str(ii) for ii in values]
        return formatted
    except ValueError:
        raise ValueError

################
# Module Guard #
################
if __name__ == '__main__':
    pass
