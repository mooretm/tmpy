""" Class to check current version number against latest version 
    library on Starfile. If upgrade is available, display
    a message. If upgrade is mandatory, show warning and 
    kill app. 

    Written by: Travis M. Moore
    Created: April 11, 2023
    Last edited: May 07, 2024
"""

###########
# Imports #
###########
# Standard library
import io
import logging
import msoffcrypto

# Third party
import pandas as pd

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

################
# VersionModel #
################
class VersionModel:
    """ Class to check current version number against latest version 
    library on Starfile. If upgrade is available but not mandatory,
    return TRUE and display a message. If upgrade is mandatory, 
    return FALSE, display a message, and kill app. 
    """
    def __init__(self, lib_path, app_name, app_version):
        logger.info("Initializing VersionModel")
        self.lib_path = lib_path
        self.app_name = app_name
        self.app_version = app_version
        self.status = None

        # Import version library to cross-reference
        try:
            self.import_version_library(self.lib_path)
        except FileNotFoundError:
            logger.error("Could not find version library!")
            self.status = 'library_inaccessible'
            return

        # Check version number
        self.check_for_updates()

    def import_version_library(self, lib_path):
        """ Download version library for crossreferencing. 
        Note: version library is in a hidden and password-
        protected XLSX file '...MooreT>Personal Files>admin'.
        """
        logger.info("Importing version library")
        unlocked_file = io.BytesIO()
        with open(lib_path, "rb") as file:
            try:
                excel_file = msoffcrypto.OfficeFile(file)
                excel_file.load_key(password="guest*Cyril*Figgis")
                excel_file.decrypt(unlocked_file)
                self.versions = pd.read_excel(unlocked_file)
            except FileNotFoundError:
                raise FileNotFoundError
            except msoffcrypto.exceptions.InvalidKeyError:
                logger.error("Bad password!")
                raise AttributeError

    def check_for_updates(self):
        """ Check app version against latest available 
        version from library.
        """
        logger.info("Checking for newer versions")
        # Retrieve app record from library 
        bools = self.versions['name'] == self.app_name
        status = self.versions[bools]

        # Check whether current version matches version library
        try:
            if status.iloc[0]['version'] != self.app_version:
                logger.warning('New version available!')
                if status.iloc[0]['mandatory'] == 'yes':
                    self.status = 'mandatory'
                    logger.error(
                        "You must update to version %s", 
                        status.iloc[0]['version']
                    )
                elif status.iloc[0]['mandatory'] == 'no':
                    self.status = 'optional'
                    logger.warning(
                        "Found Version %s, but %s is available",
                        self.app_version, status.iloc[0]['version']
                    )
                # Assign latest version number to public attribute
                self.new_version = status.iloc[0]['version']
            else:
                logger.info("You are up to date!")
                self.status = 'current'
        except IndexError:
            #logger.exception("Cannot retrieve version number!")
            self.status = 'app_not_found'
            logger.error("'%s' cannot be found in the version library!", 
                         self.app_name
                         )

################
# Module Guard #
################
if __name__ == '__main__':
    pass
