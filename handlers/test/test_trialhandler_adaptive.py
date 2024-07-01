""" Unit tests for TrialHandler. 

    Written by: Travis M. Moore
    Last edited: May 13, 2024
"""

###########
# Imports #
###########
# Standard library
import os
import pytest
import sys

# Third party
import pandas as pd

# Custom
# sys.path.append("..")
sys.path.append(os.environ['TMPY'])
from tmpy.handlers.trialhandler_adaptive import AdaptiveTrialHandler

############
# Fixtures #
############
@pytest.fixture
def data():
    # Dict of values for df
    d = {'test1': [1, 3, 5],
         'test2': [2, 4, 6]}
    
    # Create df
    data = pd.DataFrame(d)
    return data


@pytest.fixture
def handler(data):
    return AdaptiveTrialHandler(
        trials_df=data,
        parameter=65,
        step_sizes=[4, 2, 2])


##############
# Unit Tests #
##############
def test_init(handler):
    # Assert
    assert handler.trials_df.shape == (3, 2)
    assert handler.trial_num == 0
    assert handler.index == -1
    assert handler.total_trials == 3
    assert handler.remaining_trials == 3
    assert handler.parameter == 65
    assert handler.step_sizes == [None, 4, 2, 2]
    assert handler.finished == False


def test_prepare_steps_fewer_one(handler):
    # Arrange
    handler.step_sizes = [4]
    handler._prepare_steps()

    # Assert
    assert handler.step_sizes == [None, 4, 4, 4]


def test_prepare_steps_fewer_two(handler):
    # Arrange
    handler.step_sizes = [4, 2]
    handler._prepare_steps()

    # Assert
    assert handler.step_sizes == [None, 4, 2, 2]


def test_next_first_trial(handler):
    # Arrange
    handler.next(None)

    # Assert
    assert handler.trial_num == 1
    assert handler.index == 0
    assert handler.total_trials == 3
    assert handler.remaining_trials == 2
    assert handler.step_sizes[handler.index] == None
    assert handler.trial_info.test1 == 1
    assert handler.trial_info.test2 == 2
    assert handler.parameter == 65
    assert handler.start_flag == False
    assert handler.finished == False


def test_next_correct(handler):
    # Arrange
    handler.next(None)
    handler.next(1)

    # Assert
    assert handler.trial_num == 2
    assert handler.index == 1
    assert handler.total_trials == 3
    assert handler.remaining_trials == 1
    assert handler.step_sizes[handler.index] == 4
    assert handler.trial_info.test1 == 3
    assert handler.trial_info.test2 == 4
    assert handler.parameter == 61
    assert handler.start_flag == False
    assert handler.finished == False


def test_next_incorrect(handler):
    # Arrange
    handler.next(None)
    handler.next(-1)

    # Assert
    assert handler.trial_num == 2
    assert handler.index == 1
    assert handler.total_trials == 3
    assert handler.remaining_trials == 1
    assert handler.step_sizes[handler.index] == 4
    assert handler.trial_info.test1 == 3
    assert handler.trial_info.test2 == 4
    assert handler.parameter == 69
    assert handler.start_flag == False
    assert handler.finished == False


def test_next_to_end_of_trials(handler):
    # Arrange
    handler.next(None) # step: None, level: 65
    handler.next(-1) # step: 4, level: 69
    handler.next(1) # step: 2, level: 67

    # Assert 
    assert handler.trial_num == 3
    assert handler.index == 2
    assert handler.remaining_trials == 0
    assert handler.finished == False
    assert handler.trial_info.test1 == 5
    assert handler.trial_info.test2 == 6
    assert handler.parameter == 67


def test_next_after_finish(handler):
    # Assert
    with pytest.raises(IndexError):
        handler.next(None)
        handler.next(1)
        handler.next(-1)
        handler.next(1)

        assert handler.finished == True
