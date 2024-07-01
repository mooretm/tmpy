""" Matrix file class for Speech Tasker.

Includes attributes and methods to import and organize 
stimuli to create a matrix file. 

Written by: Travis M. Moore
Last edited: July 1, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import os
import random

# Third party
import pandas as pd

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

##############
# MatrixFile #
##############
class MatrixFile:
    """ Base class for working with matrix files. """
    logger.info("Initializing MatrixFile base class")

    def import_file(self, filepath):
        """ Import matrix file. 
        
        :param filepath: Path to the desired matrix file
        :type filepath: string or raw string
        :return: Imported CSV data
        :rtype: DataFrame
        """
        logger.info("Importing stimulus CSV file: %s", os.path.basename(filepath))
        try:
            return pd.read_csv(filepath)
        except FileNotFoundError as e:
            logger.error("File not found: %s", filepath)
            raise

    def subset_lists(self, trials_df, lists):
        """ Grab only specified lists. 

        :return: Revised DataFrame with only specified list items
        :rtype: DataFrame
        """
        logger.info("Grabbing lists: %s", lists)
        try:
            mask = trials_df['list_num'].isin(lists)
            return trials_df[mask].copy()
        except TypeError as e:
            logger.error(e)
            raise

    def truncate_lists(self, trials_df, sentences_per_list):
        """ Grab the first n sentences from each provided list. 
        
        :return: A revised DataFrame with n sentences per list
        :rtype: DataFrame
        """
        logger.info("Retaining %d items per list", sentences_per_list)
        try:
            return trials_df.groupby('list_num').head(sentences_per_list
                ).reset_index(drop=True).copy()
        except TypeError as e:
            logger.error(e)
            raise

    def _assign_values_by_list(self, trials_df, values, col_name):
        """ Handle assigning values by list number. """
        logger.info("Assigning %s values", col_name)
        try:
            # Get unique list numbers
            list_nums = trials_df['list_num'].unique()

            if (len(values) > 1) and (len(values) == len(list_nums)):
                # Create dictionary of list numbers and values
                level_key = dict(zip(list_nums, values))
                # Assign level by list number
                trials_df[col_name] = \
                    trials_df['list_num'].apply(lambda x: level_key[x])
                return trials_df
            else:
                logger.error("%s is an invalid number of %s values!", values, col_name)
                raise ValueError
        except TypeError as e:
            logger.error(e)
            raise

    def assign_values(self, trials_df, values, col_name):
        """ Assign a value to each trial. 
        
        :param trials_df: A DataFrame of speech task stimuli
        :type trials_df: DataFrame
        :param values: One or more values to be applied
        :type values: list
        :return: Revised DataFrame with values column
        :rtype: DataFrame
        """
        logger.info("Assigning a single %s value to all trials", col_name)
        try:
            # Add value column with single value
            if len(values) == 1:
                trials_df[col_name] = values[0]
                return trials_df
            
            # Add values based on list number
            if len(values) > 1:
                try:
                    return self._assign_values_by_list(
                        trials_df=trials_df, 
                        values=values, 
                        col_name=col_name)
                except ValueError:
                    logger.error("Cannot assign values!")
                    raise
        except TypeError as e:
            logger.error(e)
            raise

    def repeat_trials(self, trials_df, repetitions):
        """ Repeat trials the specified number of times. """
        try:
            # Make sure there is at least 1 'repetition'
            if (repetitions == 0) or (repetitions == None):
                repetitions = 1
            # Create repeated trials
            logger.info("Creating %d presentation(s)", repetitions)
            repeated_trials = pd.concat(
                [trials_df] * repetitions,
                ignore_index=True
            )
            return repeated_trials
        except TypeError as e:
            logger.error(e)
            raise

    def randomize(self, trials_df):
        """ Randomize trials. """
        logger.info('Randomizing trials')
        try:
            # Get trial numbers from matrix df index
            trials = list(trials_df.index)
            # Shuffle (in place)
            random.shuffle(trials)
            random.shuffle(trials)
            random.shuffle(trials)
            random.shuffle(trials)
            # Create new df column with shuffled trial order
            trials_df['order'] = trials
            # Sort by new order column
            trials_df.sort_values(by='order', inplace=True)
            # Remove order column
            trials_df.drop('order', axis=1, inplace=True)
            # Reset index
            trials_df.reset_index(drop=True, inplace=True)
            return trials_df
        except TypeError as e:
            logger.error(e)
            raise
