""" Class for importing matrix files and organizing trials. 

Written by: Travis M. Moore
Last edited: July 1, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import random

# Third party
import pandas as pd

###########
# Logging #
###########
logger = logging.getLogger(__name__)

#################
# MatrixHandler #
#################
class MatrixHandler:
    def __init__(self, filepath, repetitions, randomize, **kwargs):
        logger.debug("Initializing MatrixHandler")
        
        # Assign attributes
        self.filepath = filepath
        if not repetitions:
            self.repetitions = 1
        else:
            self.repetitions = repetitions
        self.randomize = randomize
        self.kwargs = kwargs

        # If a file path was provided, import the matrix file
        if filepath:
            # Import matrix file
            self._load_matrix()
            # Make trial repetitions
            self._do_reps()
            # If specified, randomize trials
            if self.randomize == 1:
                self._randomize()
        else:
            raise ValueError

    def _load_matrix(self):
        """ Import matrix file specified in settings. """
        logger.info("Importing matrix file")
        try:
            # Create private attribute of raw matrix file
            self._matrix_file = pd.read_csv(self.filepath)
        except FileNotFoundError as e:
            logger.error("File not found!")
            raise

    def _do_reps(self):
        """ Repeat trials the specified number of times. """
        # Create a copy of private raw matrix import
        # to preserve it and avoid multiple versions issues
        self.matrix = self._matrix_file.copy()

        # Make sure there is at least 1 'repetition'
        if (self.repetitions == 0) or \
        (self.repetitions == None):
            self.repetitions = 1

        # Create repeated trials
        logger.info('Creating trial repetitions')
        self.matrix = pd.concat(
            [self.matrix] * self.repetitions,
            ignore_index=True
        )

    def _randomize(self):
        """ Randomize trials in self.matrix. """
        logger.info('Randomizing trials')
        # Get trial numbers from matrix df index
        trials = list(self.matrix.index)
        # Shuffle (in place)
        random.shuffle(trials)
        # Create new df column with shuffled trial order
        self.matrix['order'] = trials
        # Sort by new order column
        self.matrix.sort_values(by='order', inplace=True)
        # Remove order column
        self.matrix.drop('order', axis=1, inplace=True)
        # Reset index
        self.matrix.reset_index(drop=True, inplace=True)

    # def _add_full_audio_paths(self):
    #     """ Add the audio dir from settings to audio file 
    #         names from matrix file.
    #     """
    #     # Get audio files directory
    #     audio_dir = Path(self.settings['audio_files_dir'].get())
    #     for row in self._matrix_file.index:
    #         # Create full path to audio file
    #         full_path = os.path.join(
    #             audio_dir, self._matrix_file.iloc[row,0]
    #         )
    #         # Update name in _matrix_file df
    #         self._matrix_file.iloc[row,0] = full_path

################
# Module Guard #
################
if __name__ == '__main__':
    pass
