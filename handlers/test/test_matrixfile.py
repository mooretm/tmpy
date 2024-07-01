""" Unit tests for MatrixFile. 

    Written by: Travis M. Moore
    Last edited: May 22, 2024
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
try:
    sys.path.append(os.environ['TMPY'])
except KeyError:
    sys.path.append('C:\\Users\\MooTra\\Code\\Python')
#from models.matrixmodel import MatrixFile
from tmpy.handlers.matrixfile import MatrixFile

############
# Fixtures #
############
@pytest.fixture
def stimuli():
    files = []
    text = []
    lists = []
    sentence_nums = []
    for list in range(1,11):
        for sentence in range(1,11):
            file = f"stimulus_{list}_{sentence}.wav"
            files.append(file)
            text.append('abc')
            lists.append(list)
            sentence_nums.append(sentence)
    d = {
        'file': files,
        'sentence': text,
        'list_num': lists,
        'sentence_num': sentence_nums
    }
    df = pd.DataFrame(d)
    return df

@pytest.fixture
def mfile():
    mf = MatrixFile()
    return mf

##############
# Unit Tests #
##############
def test_import_file(mfile, stimuli, mocker):
    # Arrange
    mocker.patch('pandas.read_csv', return_value=stimuli)
    trials = mfile.import_file(filepath='fake/file/path')
    
    # Assert assert 
    assert trials.shape == (100, 4)


def test_subset_lists_pass(mfile, stimuli):
    # Arrange
    subset = mfile.subset_lists(
        trials_df=stimuli,
        lists=[3, 5]
    )

    # Assert
    assert subset.shape == (20, 4)
    assert sorted(subset['list_num'].unique()) == sorted([3, 5])


def test_subset_lists_no_trials(mfile):
    # Assert
    with pytest.raises(TypeError):
        mfile.subset_lists(
            lists=[3, 5]
        )


def test_subset_lists_no_lists(mfile, stimuli):
    # Assert
    with pytest.raises(TypeError):
        mfile.subset_lists(
            trials_df=stimuli
        )


def test_truncate_lists(mfile, stimuli):
    # Arrange
    truncated = mfile.truncate_lists(
        trials_df=stimuli,
        sentences_per_list=5
    )

    # Assert
    assert truncated.shape == (50, 4)
    assert sorted(
        truncated['sentence_num'].unique()
        ) == sorted([1, 2, 3, 4, 5])


def test_truncate_lists_no_trials(mfile):
    # Assert
    with pytest.raises(TypeError):
        mfile.truncate_lists(
            sentences_per_list=3
        )


def test_truncate_lists_no_item_num(mfile, stimuli):
    # Assert
    with pytest.raises(TypeError):
        mfile.truncate_lists(
            trials_df=stimuli
        )


def test_assign_values_1_value(mfile, stimuli):
    """ When the number of values == 1, just add a column. """
    # Arrange
    trials = mfile.assign_values(
        trials_df=stimuli,
        values=[80],
        col_name='level'
    )

    # Assert
    assert trials.shape == (100, 5)
    assert 'level' in trials.columns
    assert trials['level'].unique() == 80


def test_assign_values_no_value(mfile, stimuli):
    # Assert
    with pytest.raises(TypeError):
        mfile.assign_values(
            trials_df=stimuli,
            col_name='test'
        )


def test__assign_values_by_list_10_values(mfile, stimuli):
    """ When the number of values == 1, just add a column. """
    # Arrange
    trials = mfile._assign_values_by_list(
        trials_df=stimuli,
        values=list(range(1,11)),
        col_name='level'
    )

    # Assert
    assert trials.shape == (100, 5)
    assert sorted(trials['level'].unique()) == sorted(list(range(1,11)))


def test_assign_values_10_values(mfile, stimuli):
    """ When the number of values == 1, just add a column. """
    # Arrange
    trials = mfile.assign_values(
        trials_df=stimuli,
        values=list(range(1,11)),
        col_name='level'
    )

    # Assert
    assert trials.shape == (100, 5)
    assert sorted(trials['level'].unique()) == sorted(list(range(1,11)))


def test_assign_values_10_speakers(mfile, stimuli):
    """ When the number of values == 1, just add a column. """
    # Arrange
    trials = mfile.assign_values(
        trials_df=stimuli,
        values=list(range(1,11)),
        col_name='speaker'
    )

    # Assert
    assert trials.shape == (100, 5)
    assert sorted(trials['speaker'].unique()) == sorted(list(range(1,11)))


def test_repeat_trials_pass(mfile, stimuli):
    # Arrange
    trials = mfile.repeat_trials(
        trials_df=stimuli,
        repetitions=2
    )

    # Assert
    assert trials.shape == (200, 4)


def test_repeat_trials_no_repetitions(mfile, stimuli):
    # Assert
    with pytest.raises(TypeError):
        mfile.repeat_trials(
            trials_df=stimuli
        )


def test_randomize_pass(mfile, stimuli):
    # Arrange
    original_file_order = stimuli['file']

    trials = mfile.randomize(
        trials_df=stimuli
    )

    # Assert
    assert trials.shape == (100, 4)
    assert sorted(trials['file'][1:3]) != sorted(original_file_order[1:3])


def test_randomize_no_trials(mfile):
    # Assert
    with pytest.raises(TypeError):
        mfile.randomize()
