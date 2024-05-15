""" Unit tests for DataHandler. 

    Last edited: April 22, 2024
"""

###########
# Imports #
###########
# Testing
import pytest
from unittest.mock import MagicMock

# Custom
# sys.path.append("..")
from models.datahandler import DataHandler


############
# Fixtures #
############
@pytest.fixture
def trial_info():
    # Dict of values
    d = {'test7': 7,
         'test8': 8}
    return d

@pytest.fixture
def response():
    # Response dict
    return {'response': 7}

@pytest.fixture
def handler():
    return DataHandler()


##############
# Unit Tests #
##############
def test__merge_dicts(handler, trial_info, response):
    # Arrange
    mylist = [trial_info, response]
    # Assert
    assert handler._merge_dicts(mylist) == trial_info | response


def test__reorder_dict(handler):
    # Arrange
    # Create sample dictionary to reorder
    sample_dict = {
        'a': 1,
        'b': 2,
        'c': 3,
        'd': 4
    }
    # Define desired order
    order = ['d', 'b', 'c', 'a']
    # Call reorder func
    reordered = handler._reorder_dict(sample_dict, order)
    # Assert
    assert list(reordered.keys()) == order


def test_save_data_unordered(monkeypatch, handler, trial_info, response):
    # Mock CSVFile to avoid actually writing to file
    mock_csv_file = MagicMock()
    # Monkeypatch the CSVFile class with the MagicMock object
    monkeypatch.setattr('models.filehandler.CSVFile', mock_csv_file)
    # Arrange
    handler.save_data('data.csv', [trial_info, response])
    # Assert
    mock_csv_file.assert_called_once_with('data.csv', trial_info | response)
    mykeys = list(trial_info.keys()) + list(response.keys())
    assert list(handler.converted.keys()) == mykeys


def test_save_data_ordered(monkeypatch, handler, trial_info, response):
    # Mock CSVFile to avoid actually writing to file
    mock_csv_file = MagicMock()
    # Monkeypatch the CSVFile class with the MagicMock object
    monkeypatch.setattr('models.filehandler.CSVFile', mock_csv_file)
    # Arrange
    order=['test8', 'response', 'test7']
    handler.save_data(
        filepath='data.csv', 
        dict_list=[trial_info, response], 
        order=order)
    # Assert
    mock_csv_file.assert_called_once_with('data.csv', trial_info | response)
    assert list(handler.converted.keys()) == order
