""" Unit tests for filehandler model. 

    Written by: Travis M. Moore
    Created: March 18, 2023
    Last edited: March 25, 2024
"""

###########
# Imports #
###########
# Standard library
import os
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Custom
from tmpy.readwrite import filehandler as fh

############
# Fixtures #
############
# Fixture for test data
@pytest.fixture
def test_data():
    return {"test1": 1, "test2": 2}

# Fixture for temporary directory
@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

# Fixture for temporary file in temporary directory
@pytest.fixture
def temp_file(temp_dir):
    _path = temp_dir / "test_file.csv"
    return str(_path)

# Clean up: Remove the temp files after the tests
@pytest.fixture(autouse=True)
def cleanup_temp_files(temp_dir):
    yield
    print("\nCleaning up stored files")
    for file in temp_dir.iterdir():
        if file.is_file():
            os.remove(file)


#########
# Tests #
#########
def test_file_type_pass(test_data, monkeypatch):
    # Mock out save function
    mock_save = Mock()
    monkeypatch.setattr('tmgui.shared_models.filehandler.CSVFile.save', mock_save)
    
    # Arrange
    mycsv = fh.CSVFile(filepath="fake/file/path/data.csv", data=test_data)

    # Assert
    assert mycsv.ext == "csv"
    mock_save.assert_called_once_with(test_data)


def test_file_type_fail(test_data, monkeypatch):
    # Mock out save function
    mock_save = Mock()
    monkeypatch.setattr('tmgui.shared_models.filehandler.CSVFile.save', mock_save)
    
    # Arrange
    with pytest.raises(TypeError, match="Invalid file format!"):
        fh.CSVFile(filepath="fake/file/path/data.xml", data=test_data)


def test_check_for_data_folder_missing(temp_dir, test_data, monkeypatch):
    # Arrange
    # Mock out save function
    mock_write = Mock()
    mock_check_access = Mock()
    monkeypatch.setattr('tmgui.shared_models.filehandler.CSVFile._write', mock_write)
    monkeypatch.setattr('tmgui.shared_models.filehandler.CSVFile._check_write_access', mock_check_access)

    new_dir = temp_dir / "datadir"
    new_file_path = os.path.join(new_dir, "data.csv")

    # Assert new_dir does not exist yet
    assert os.path.isdir(new_dir) == False
    assert os.path.isfile(new_file_path) == False
    
    # Arrange
    fh.CSVFile(new_file_path, test_data)

    # Assert
    assert mock_write.called_once_with(test_data)
    assert mock_check_access.assert_called_once
    assert os.path.isdir(new_dir) == True


def test_check_write_access_denied(temp_file, test_data, monkeypatch):
    # Mock out write and check for data folder functions
    mock_write = Mock()
    mock_check_for_data_folder = Mock()
    monkeypatch.setattr('tmgui.shared_models.filehandler.CSVFile._write', mock_write)
    monkeypatch.setattr('tmgui.shared_models.filehandler.CSVFile._check_for_data_folder', mock_check_for_data_folder)

    # Create mock os.access function
    def mock_access(path, access):
        return False
    
    monkeypatch.setattr(os, 'access', mock_access)
    
    # Assert
    with pytest.raises(PermissionError, match=f"Permission denied accessing file: {os.path.split(temp_file)[1]}"):
        fh.CSVFile(str(temp_file), test_data)

        assert mock_write.assert_called_once_with(test_data)
        assert mock_check_for_data_folder.assert_called_once


def test_csv_public_attributes(temp_file, test_data):
    # Arrange
    mycsv = fh.CSVFile(temp_file, test_data)

    # Assert: public attributes
    assert mycsv.dirname == os.path.split(temp_file)[0]
    assert mycsv.ext == "csv"
    assert mycsv.filename == os.path.split(temp_file)[1]
    assert mycsv.filepath == Path(temp_file)


def test_write_csv(temp_file, test_data):
    # Arrange
    fh.CSVFile(filepath=temp_file, data=test_data)

    # Assert: file exists
    assert os.path.exists(temp_file)

    # Assert: file content == test_data
    with open(temp_file, "r") as f:
        content = f.read()
    assert content == "test1,test2\n1,2\n"


def test_append_csv(temp_file, test_data):
    # Arrange
    mycsv = fh.CSVFile(filepath=temp_file, data=test_data)
    for _ in range(0, 3):
        mycsv.save(test_data)

    # Assert: file content == test_data * 4
    with open(temp_file, "r") as f:
        content = f.read()
    assert content == "test1,test2\n1,2\n1,2\n1,2\n1,2\n"
