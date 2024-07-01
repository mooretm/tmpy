""" Classes to write data to various file types. 

Author: Travis M. Moore
Created: March 07, 2024
Last edited: June 25, 2024
"""

###########
# IMPORTS #
###########
# Standard library
import csv
import logging
import os
from pathlib import Path
from tkinter import filedialog

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

###############
# FileHandler #
###############
class FileHandler:
    """ Generic file class to be inherited by specific file type classes. """

    def __init__(self, filepath, data, **kwargs):
        """ Initialize a generic FileHandler instance (to be inherited).

        :param filepath: Full path of file with extension
        :type filepath: string
        :param file_browser: A kwarg that can prompt a file browser on save
        :type file_browser: bool
        :return: Writes provided data to file.
        :rtype: Write to file, or None
        """
        # Test for valid file extension
        if not filepath.endswith(self.ext):
            msg = 'Invalid file format!'
            logger.critical(msg, exc_info=True)
            raise TypeError(msg)
        
        # Create file directory variables
        self.filepath = Path(filepath)
        self.dirname, self.filename = os.path.split(filepath)

        # Look for kwargs
        # FILE BROSWER
        if 'file_browser' in kwargs:
            if kwargs['file_browser']:
                self._get_directory_from_browser()

        # Call save function
        self.save(data)

    def _get_directory_from_browser(self):
        """ Get save directory from consumer via file dialog. """
        try:
            self.dirname = filedialog.askdirectory()
        except:
            pass

        # Create new filepath from provided directory and filename
        self.filepath = os.path.join(self.dirname, self.filename)
        self.filepath = Path(self.filepath)

    def _check_for_data_folder(self):
        """ Check for existing directory. Create specified directory if
        it doesn't currently exist.
        """
        # Does directory already exist?
        data_dir_exists = os.access(self.dirname, os.F_OK)

        if not data_dir_exists:
            if self.dirname == '':
                # Drop directory if empty (i.e., use root)
                pass
            else:
                # Create new directory
                logger.info(
                    'Data directory "%s" not found - creating it.', 
                    self.dirname
                )
                os.makedirs(self.dirname)
                logger.info(
                    'Successfully created "%s"', 
                    self.dirname
                )
        else:
            logger.info('Found data directory "%s"', self.dirname)

    def _check_write_access(self):
        """ Check for write access to store CSV. """
        # Convert filepath to Path object for testing
        if not isinstance(self.filepath, Path):
            self.filepath = Path(self.filepath)

        file_exists = os.access(self.filepath, os.F_OK)
        parent_writable = os.access(self.filepath.parent, os.W_OK)
        file_writable = os.access(self.filepath, os.W_OK)
        if (
            (not file_exists and not parent_writable) or
            (file_exists and not file_writable)
        ):
            msg = f"Permission denied accessing file: {self.filename}"
            logger.critical(msg)
            raise PermissionError(msg)

    def _write(self, data):
        """ To be overridden by specific file classes. """
        pass

    def save(self, data):
        """ Save a dictionary of data to .csv file. """
        # Create directory if it does not exist
        self._check_for_data_folder()

        # Check for write access
        try:
            self._check_write_access()
        except PermissionError:
            raise

        # Write data to file
        self._write(data)

###########
# CSVFile #
###########
class CSVFile(FileHandler):
    """ Specific file type: CSV. """
    # Extension checked by FileHandler
    ext = "csv"

    def _write(self, data):
        """ Write dict data to CSV. Subsequent calls append to file.
        Includes header for new files.
        """
        # Write file
        logger.info('Attempting to update: %s', self.filename)
        try:
            newfile = not self.filepath.exists()
            with open(self.filepath, 'a', newline='') as fh:
                csvwriter = csv.DictWriter(fh, fieldnames=data.keys())
                if newfile:
                    csvwriter.writeheader()
                csvwriter.writerow(data)
            logger.info('Data successfully written')
        except AttributeError as e:
            logger.critical('%s', e)

################
# Module Guard #
################
if __name__ == "__main__":
    pass
