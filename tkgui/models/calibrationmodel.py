""" Class for loading calibration file, determining calibration 
    offset, and calculating adjusted presentation level.

    Written by: Travis M. Moore
    Last edited: April 30, 2024
"""

############
# IMPORTS  #
############
# Standard library
import logging
import os

# Custom
from ..shared_assets import audio

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

#########
# MODEL #
#########
class CalibrationModel:
    """ Calculate and apply calibration offset. """
    def __init__(self, settings):
        logger.info("Initializing CalibrationModel")
        # Assign variables
        self.settings = settings

    def get_cal_file(self):
        """ Load specified calibration file. """
        logger.info("Importing calibration file")
        if self.settings['cal_file'].get() == 'cal_stim.wav':
            self.cal_file = audio.CALSTIM_WAV
            file_exists = os.access(self.cal_file, os.F_OK)
            if not file_exists:
                raise AttributeError
        else: 
            # Custom file was provided
            self.cal_file = self.settings['cal_file'].get()
        logger.info("Using %s", self.cal_file)

    def calc_offset(self):
        """ Calculate sound level meter offset. """
        # Calculate SLM offset
        logger.info("Calculating SLM offset")
        slm_offset = self.settings['slm_reading'].get() - self.settings['cal_level_dB'].get()
        self.settings['slm_offset'].set(slm_offset)
        # Provide console feedback
        logger.info("Starting level (dB FS): %s",
                     self.settings['cal_level_dB'].get()
                    )
        logger.info("SLM reading (dB): %s",
                     self.settings['slm_reading'].get()
                     )
        logger.info("SLM offset: %s",
                     self.settings['slm_offset'].get()
                     )
        # SLM offset not yet saved!
        # This must happen in controller using: self._save_settings()

    def calc_level(self, desired_level_dB):
        # Calculate presentation level
        logger.info("Calculating presentation level")
        self.settings['desired_level_dB'].set(desired_level_dB)
        scaled_level = desired_level_dB - self.settings['slm_offset'].get()
        self.settings['adjusted_level_dB'].set(scaled_level)
        
        # Provide feedback
        logger.info("Desired level in dB: %f",
                     self.settings['desired_level_dB'].get()
                    )
        logger.info("SLM offset: %f",
                     self.settings['slm_offset'].get()
                    )
        logger.info("Adjusted level (dB): %f",
                     self.settings['adjusted_level_dB'].get()
                     )
        # Calculated level not yet saved! 
        # This must happen in controller using: self._save_settings()

################
# Module Guard #
################
if __name__ == '__main__':
    pass
