""" Class to track experiment progress and store data. 

    Procedure: 
    1. Import matrix file as: df
    2. vals = df.iloc[ii].to_dict()
    3. trial = _TrialDict(vals)

    Written by: Travis M. Moore
    Created: April 16, 2024
    Last edited: May 10, 2024
"""

###########
# Imports #
###########
# Standard library
import logging

# Custom
from ._trialdict import _TrialDict

###########
# Logging #
###########
logger = logging.getLogger(__name__)

################
# TrialHandler #
################
class TrialHandler:
    def __init__(self, trials_df):
        """ Instantiate a TrialHandler object. """
        logger.debug("Initializing TrialHandler")
        # Assign variables
        self.trials_df = trials_df
        self.trial_num = 0
        self.index = -1
        self.total_trials = self.trials_df.shape[0]
        self.remaining_trials = self.total_trials
        self.finished = False


    def show_trial_info(self):
        """ Print trial info to console. """
        logger.debug("Current trial info:")
        for key, value in self.trial_info.items():
            logger.debug("%s: %s", key, value)


    def next(self):
        """ Advance to the next trial and store data. """
        logger.debug("'Next' called")
        # Update counts
        self.trial_num += 1
        self.index += 1
        self.remaining_trials -= 1

        # Check for end of trials
        if self.trial_num > self.total_trials:
            self.finished = True
            raise IndexError
        
        # Load next trial parameters
        logger.debug("Loading next trial parameters")
        vals = self.trials_df.iloc[self.index].to_dict()
        vals['trial'] = self.trial_num
        logger.info(vals)
        self.trial_info = _TrialDict(vals)


if __name__ == "__main__":
    pass
