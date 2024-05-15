""" Unit tests for TrialDict. """

###########
# Imports #
###########
# Testing
import pytest

# System
import sys

# Custom
# sys.path.append("..")
from models.trialdict import TrialDict


############
# Fixtures #
############
@pytest.fixture
def data():
    return {'test1': 1, 'test2': 2, 'test3': 3}

@pytest.fixture
def td(data):
    return TrialDict(data)


##############
# Unit Tests #
##############
def test_success(data):
    # Arrange
    td = TrialDict(data)

    # Assert
    assert td.test1 == 1
    assert td.test2 == 2
    assert td.test3 == 3


def test_missing_key(td):
    # Assert
    with pytest.raises(AttributeError):
        td.test4
    

def test_invalid_data_type():
    # Arrange
    vals = ['condition', 'level']

    # Assert
    with pytest.raises(ValueError):
        TrialDict(vals)
