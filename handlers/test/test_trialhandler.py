""" Unit tests for TrialHandler. 

    Last edited: April 22, 2024
"""

###########
# Imports #
###########
# Testing
import pytest

# System
import sys

# Data
import pandas as pd

# Custom
# sys.path.append("..")
from models.trialhandler import TrialHandler


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
    return TrialHandler(data)


##############
# Unit Tests #
##############
def test_init(handler):
    # Assert
    assert handler.trial_num == 0
    assert handler.index == -1
    assert handler.total_trials == 3
    assert handler.remaining_trials == 3
    assert handler.finished == False


def test_next_increment(handler):
    # Arrange
    handler.next()

    # Assert
    assert handler.trial_num == 1
    assert handler.index == 0
    assert handler.total_trials == 3
    assert handler.remaining_trials == 2
    assert handler.finished == False
    assert handler.trial_info.test1 == 1
    assert handler.trial_info.test2 == 2


def test_next_to_end_of_trials(handler):
    # Arrange
    handler.next()
    handler.next()
    handler.next()

    # Assert 
    assert handler.trial_num == 3
    assert handler.index == 2
    assert handler.remaining_trials == 0
    assert handler.finished == False
    assert handler.trial_info.test1 == 5
    assert handler.trial_info.test2 == 6


def test_next_after_finish(handler):
    handler.next()
    handler.next()
    handler.next()
    handler.next()

    # Assert
    assert handler.finished == True
