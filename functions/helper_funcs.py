""" Global functions. """

###########
# Imports #
###########
# Import system packages
import sys
import os


#########
# Funcs #
#########
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


def truncate_path(long_path):
    """ Truncate path (if necessary) and return 
        shortened path for display.
    """
    if len(long_path) >= 60:
        short = '...' + long_path[-55:]
        return short
    else:
        if long_path == "":
            return 'Please select a file'
        else:
            return long_path


def flatten_text(text):
    """ Remove special characters, 
        force to lowercase, 
        replace whitespace with underscores. 
    """
    # First replace whitespaces with underscores
    no_whitespace = text.replace(' ', '_')
    # Last remove special characters
    cleaned = ''.join(
        c for c in no_whitespace if c == '_' or c.isalnum()
    ).lower()
    return cleaned


def string_to_list(string_list, datatype):
    """ Convert string of comma-separated values 
        to a list of the specified data type.
    """
    # Split list by comma + space
    no_commas = string_list.split(", ")

    # Create list of specified data type
    if datatype == 'int':
        formatted = [int(ii) for ii in no_commas]
    elif datatype == 'float':
        formatted = [float(ii) for ii in no_commas]
    elif datatype == 'str':
        formatted = [str(ii) for ii in no_commas]
        
    return formatted


if __name__ == '__main__':
    pass
