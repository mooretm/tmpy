""" Unit tests for TrialHandler. """

###########
# Imports #
###########
# System
import sys

# Custom
# sys.path.append("..")
from models.avoid_tk import MyTkVar


##############
# Unit Tests #
##############
def test_get_string():
    # Arrange
    s = MyTkVar('hello')

    # Assert
    assert type(s.get()) == str
    assert s.get() == 'hello'
    assert str(s) == 'hello'


def test_set_string():
    # Arrange
    s = MyTkVar('hello')
    s.set('goodbye')

    # Assert
    assert type(s.get()) == str
    assert s.get() == 'goodbye'
    assert str(s) == 'goodbye'


def test_get_string():
    # Arrange
    s = MyTkVar('hello')

    # Assert
    assert type(s.get()) == str
    assert s.get() == 'hello'
    assert str(s) == 'hello'


def test_set_string():
    # Arrange
    s = MyTkVar('hello')
    s.set('goodbye')

    # Assert
    assert type(s.get()) == str
    assert s.get() == 'goodbye'
    assert str(s) == 'goodbye'
