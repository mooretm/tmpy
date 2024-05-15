""" Class to hold current trial values in a modified
    dict class that allows accessing values using
    dot notation with keys. 

    Written by: psychopy (https://psychopy.org)
"""

###########
# Imports #
###########
# Standard library
import logging

###########
# Logging #
###########
logger = logging.getLogger(__name__)

#############
# TrialDict #
#############
class _TrialDict(dict):
    """ Create a special case dictionary that can be
        querried using dot notation. 
    """
    logger.debug("Creating TrialDict with current trial values")
    def __getattribute__(self, name):
        try:
            return dict.__getattribute__(self, name)
        except AttributeError:
            try:
                return self[name]
            except KeyError:
                msg = f"TrialType has no attribute (or key) {name}"
                logger.exception(msg)
                raise AttributeError(msg)


if __name__ == "__main__":
    pass
