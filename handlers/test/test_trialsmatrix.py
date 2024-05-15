""" Unit tests for TrialsMatrix. 

    Written by: Travis M. Moore
    Last edited: April 18, 2024
"""

###########
# Imports #
###########
# Testing
import unittest
from unittest.mock import patch, mock_open

# Data
import random

# Custom
from ..handlers.matrixhandler import MatrixHandler
#from models.trialsmatrix import TrialsMatrix
#from models.avoid_tk import MyTkVar


#########
# Begin #
#########
class TestTrialsMatrix(unittest.TestCase):
    """ Unit tests for TrialsMatrix class. """

    def setUp(self):
        """ Create necessary mocks and variables. Automatically 
            runs before each test. 
        """
        # Mock file with data
        self.fake_data_file = mock_open(
            read_data=(
                "wav,condition,level\r\n" # Header
                "whisper.wav,soft,55\r\n" # Row 1
                "chat.wav,average,65\r\n" # Row 2
                "shout.wav,loud,75\r\n" # Row 3
            )
        )

        # Settings
        self.settings = {
            'matrix_file_path': MyTkVar('mock_matrix.csv'),
            'repetitions': MyTkVar(1),
            'randomize': MyTkVar(0)
        }


    def tearDown(self):
        """ Delete objects from setUp. Automatically runs
            after each test.
        """
        del self.fake_data_file
        del self.settings


    def test_import_matrix_file_1_rep(self):
        """ Test whether mock matrix file is imported correctly. """
        # Create class instance and test
        with patch('builtins.open', self.fake_data_file):
            # Create an instance of TrialsMatrix
            tm = TrialsMatrix(self.settings)

            # Make sure private '_matrix_file' attribute was created
            # and matches 1 rep
            self.assertIsNotNone(tm._matrix_file)
            # Test '_matrix_file' df shape based on mock file
            self.assertEqual(tm._matrix_file.shape, (3,3))
            # Test '_matrix_file' values (read original file: 1 presentation)
            self.assertEqual(
                tm._matrix_file.iloc[:, 0].tolist(), 
                ["whisper.wav", "chat.wav", "shout.wav"]
            )
            self.assertEqual(
                tm._matrix_file.iloc[:, 1].tolist(), 
                ["soft", "average", "loud"]
            )
            self.assertEqual(
                tm._matrix_file.iloc[:, 2].tolist(), 
                [55, 65, 75]
            )

            # Make sure public 'matrix' attribute was created
            # and matches 1 rep
            self.assertIsNotNone(tm.matrix)
            # Test 'matrix' df shape based on mock file
            self.assertEqual(tm.matrix.shape, (3,3))
            self.assertEqual(
                tm.matrix.iloc[:, 0].tolist(), 
                ["whisper.wav", "chat.wav", "shout.wav"]
            )
            self.assertEqual(
                tm.matrix.iloc[:, 1].tolist(), 
                ["soft", "average", "loud"]
            )
            self.assertEqual(
                tm.matrix.iloc[:, 2].tolist(), 
                [55, 65, 75]
            )


    def test_import_matrix_file_3_reps(self):
        """ Test whether mock matrix file is imported correctly. """
        # Create 3 repetitions
        self.settings['repetitions'] = MyTkVar(3)

        # Create class instance and test
        with patch('builtins.open', self.fake_data_file):
            # Create an instance of TrialsMatrix
            tm = TrialsMatrix(self.settings)

            # Make sure private '_matrix_file' attribute was created
            # and matches 1 rep (preserves original data)
            self.assertIsNotNone(tm._matrix_file)
            # Test '_matrix_file' df shape based on mock file
            self.assertEqual(tm._matrix_file.shape, (3,3))
            # Test '_matrix_file' values (read original file: 1 presentation)
            self.assertEqual(
                tm._matrix_file.iloc[:, 0].tolist(), 
                ["whisper.wav", "chat.wav", "shout.wav"]
            )
            self.assertEqual(
                tm._matrix_file.iloc[:, 1].tolist(), 
                ["soft", "average", "loud"]
            )
            self.assertEqual(
                tm._matrix_file.iloc[:, 2].tolist(), 
                [55, 65, 75]
            )

            # Make sure public 'matrix' attribute was created
            # and matches 3 reps (modified data)
            self.assertIsNotNone(tm.matrix)
            # Test 'matrix' df shape based on mock file
            self.assertEqual(tm.matrix.shape, (9,3))
            self.assertEqual(
                tm.matrix.iloc[:, 0].tolist(), 
                ["whisper.wav", "chat.wav", "shout.wav"] * 3
            )
            self.assertEqual(
                tm.matrix.iloc[:, 1].tolist(), 
                ["soft", "average", "loud"] * 3
            )
            self.assertEqual(
                tm.matrix.iloc[:, 2].tolist(), 
                [55, 65, 75] * 3
            )


    def test_zero_repetitions(self):
        """ Test that repetitions of '0' or 'None' are
            converted to '1'.
        """
        # Set settings
        self.settings['repetitions'] = MyTkVar(0)

        # Create class instance and test
        with patch('builtins.open', self.fake_data_file):
            tm = TrialsMatrix(self.settings)

        self.assertEqual(tm.matrix.shape, (3,3))


    def test__randomize_called(self):
        """ _randomized should be called when 
            settings['randomize'] == 1
        """
        # Set settings
        self.settings['randomize'] = MyTkVar(1)

        # Create class instance and test
        with patch('builtins.open', self.fake_data_file):
            with patch('random.shuffle') as fake_shuffle:
                TrialsMatrix(self.settings)

        # Test that _randomize was called
        fake_shuffle.assert_called_once()


    def test__randomize_not_called(self):
        """ _randomized should NOT be called when 
            settings['randomize'] == 0
        """
        # Set settings
        self.settings['randomize'] = MyTkVar(0)

        # Create class instance and test
        with patch('builtins.open', self.fake_data_file):
            with patch('random.shuffle') as fake_shuffle:
                TrialsMatrix(self.settings)

        # Test that _randomize was not called
        fake_shuffle.assert_not_called()


    def test__randomize_values_1_rep(self):
        """ Test whether the presentation levels are in 
            a given order after randomizing with a set seed.
        """
        # Modify settings to set repetitions and enable randomization
        self.settings['repetitions'] = MyTkVar(1)
        self.settings['randomize'] = MyTkVar(1)

        # Create local random number generator with fixed seed
        rng = random.Random(40)

        with patch('builtins.open', self.fake_data_file):
            with patch('random.shuffle', side_effect=lambda x, r=rng: r.shuffle(x)):
                tm = TrialsMatrix(self.settings)

                self.assertEqual(tm.matrix.iloc[:,0].tolist(), 
                    ["chat.wav","shout.wav","whisper.wav"]
                )

                self.assertEqual(tm.matrix.iloc[:,1].tolist(), 
                    ["average","loud","soft"]
                )

                self.assertEqual(tm.matrix.iloc[:,2].tolist(), 
                    [65,75,55]
                )

    def test__randomize_values_3_reps(self):
        """ Test whether the presentation levels are in 
            a given order after randomizing with a set seed.
        """
        # Modify settings to set repetitions and enable randomization
        self.settings['repetitions'] = MyTkVar(3)
        self.settings['randomize'] = MyTkVar(1)

        # Create local random number generator with fixed seed
        rng = random.Random(40)

        with patch('builtins.open', self.fake_data_file):
            with patch('random.shuffle', side_effect=lambda x, r=rng: r.shuffle(x)):
                tm = TrialsMatrix(self.settings)

                self.assertEqual(tm.matrix.iloc[:,0].tolist(), 
                    ['chat.wav',
                    'whisper.wav',
                    'shout.wav',
                    'shout.wav',
                    'whisper.wav',
                    'chat.wav',
                    'chat.wav',
                    'shout.wav',
                    'whisper.wav']
                )

                self.assertEqual(tm.matrix.iloc[:,1].tolist(), 
                    ["average",
                    "soft",
                    "loud",
                    "loud",
                    "soft",
                    "average",
                    "average",
                    "loud",
                    "soft"]
                )

                self.assertEqual(tm.matrix.iloc[:,2].tolist(), 
                    [65,55,75,75,55,65,65,75,55]
                )


if __name__ == '__main__':
    unittest.main()
