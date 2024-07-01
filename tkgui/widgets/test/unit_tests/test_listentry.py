""" Unit tests for ListEntry. 

Written by: Travis M. Moore
Last edited: June 13, 2024
"""

###########
# Imports #
###########
# Standard library
import pytest
import re

############
# Fixtures #
############
@pytest.fixture
def pattern():
    return r'^\w+(, \w+)*$'

##############
# Unit Tests #
##############
def test_proper_format(pattern):
    # Arrange
    mystring = '1, 2, 3, 45, 777, 90'

    # Assert
    assert bool(re.fullmatch(pattern, mystring)) == True

def test_single_value(pattern):
    # Assert
    assert bool(re.fullmatch(pattern, '5')) == True

def test_emtpy_list(pattern):
    # Assert
    assert bool(re.fullmatch(pattern, '')) == False

def test_leading_whitespace(pattern):
    # Arrange
    mystring = ' 1, 2, 3, 45, 777, 90'

    # Assert
    assert bool(re.fullmatch(pattern, mystring)) == False

def test_trailing_whitespace(pattern):
    # Arrange
    mystring = '1, 2, 3, 45, 777, 90 '

    # Assert
    assert bool(re.fullmatch(pattern, mystring)) == False

def test_trailing_comma(pattern):
    # Arrange
    mystring = '1, 2, 3, 45, 777, 90,'

    # Assert
    assert bool(re.fullmatch(pattern, mystring)) == False

def test_no_commas_with_whitespace(pattern):
    # Arrange
    mystring = '1 2 3 45 777 90'

    # Assert
    assert bool(re.fullmatch(pattern, mystring)) == False

def test_no_whitespace_with_commas(pattern):
    # Arrange
    mystring = '1,2,3,45,777,90'

    # Assert
    assert bool(re.fullmatch(pattern, mystring)) == False

def test_mixed_whitespace_with_commas(pattern):
    # Arrange
    mystring = '1, 2,3, 45, 777, 90'

    # Assert
    assert bool(re.fullmatch(pattern, mystring)) == False

def test_more_than_one_whitespace_with_commas(pattern):
    # Arrange
    mystring = '1, 2,  3, 45, 777, 90'

    # Assert
    assert bool(re.fullmatch(pattern, mystring)) == False


# Guard
if __name__ == '__main__':
    pass
