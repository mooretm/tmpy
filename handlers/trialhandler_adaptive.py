""" Class to control experiment progress in an adaptive manner.

    Adaptive handler to increment/decrement a given parameter
    according to user responses.

    Written by: Travis M. Moore
    Created: May 13, 2024
    Last edited: May 13, 2024
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

########################
# AdaptiveTrialHandler #
########################
class AdaptiveTrialHandler:
    def __init__(self, trials_df, parameter, step_sizes):
        """ Instantiate a TrialHandler object. """
        logger.debug("Initializing TrialHandler")
        # Assign variables
        self.trials_df = trials_df
        self.trial_num = 0
        self.index = -1
        self.total_trials = self.trials_df.shape[0]
        self.remaining_trials = self.total_trials
        self.parameter = parameter
        self.step_sizes = step_sizes
        self.start_flag = True
        self.finished = False

        # Validate step sizes
        self._prepare_steps()


    def _prepare_steps(self):
        """ Create list of step sizes based on number of trials. """
        num_steps = len(self.step_sizes)

        if num_steps == self.total_trials:
            pass
        elif num_steps < self.total_trials:
            reps = [self.step_sizes[-1]] * (self.total_trials - num_steps)
            self.step_sizes += reps
        # elif num_steps < self.total_trials:
        #     raise ValueError

        # Pad with empty initial step size to offset first
        # "next()" call with None
        self.step_sizes.insert(0, None)
        

    def _adjust_paramter(self, response):
        """ Increase/decrease paramter based on response. """
        if response == 1:
            self.parameter -= self.step_sizes[self.index]
        elif response == -1:
            self.parameter += self.step_sizes[self.index]
        else:
            raise ValueError


    def next(self, response):
        """ Advance to the next trial or end. """
        logger.debug("'Next' called")
        logger.debug("Updating trial counts")
        # Update counts
        self.trial_num += 1
        self.index += 1
        self.remaining_trials -= 1

        # Check for end of trials
        logger.debug("Checking for end of trials")
        if self.trial_num > self.total_trials:
            self.finished = True
            raise IndexError
        
        # Adjust parameter if not first trial
        if not self.start_flag:
            self._adjust_paramter(response)

        if self.start_flag:
            logger.debug("Setting start flag to False")
            self.start_flag = False

        # Load next trial parameters
        logger.debug("Loading next trial parameters")
        vals = self.trials_df.iloc[self.index].to_dict()
        vals['trial'] = self.trial_num
        vals['parameter'] = self.parameter
        vals['step_size'] = self.step_sizes[self.index]
        vals['response'] = response
        logger.info(vals)
        self.trial_info = _TrialDict(vals)


    def show_trial_info(self):
        """ Log trial info and display to console. """
        logger.debug("Logging trial info")
        for key, value in self.trial_info.items():
            logger.debug("%s: %s", key, value)


if __name__ == "__main__":
    pass
