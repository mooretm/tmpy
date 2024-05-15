""" Unit tests for calmodel. 

    Written by: Travis M. Moore
    Created: September 14, 2023
    Last edited: March 25, 2024
"""

###########
# Imports #
###########
# Testing
import unittest
from unittest.mock import patch

# GUI
import tkinter as tk

# System
import os
import sys
import time

# Custom
sys.path.append(os.environ["TMPY"])
from tmgui.shared_models.calmodel import CalModel


#########
# Begin #
#########    
class TestCalModel(unittest.TestCase):
    """ Unit tests for calmodel. """

    def setUp(self):
        # Root window (so tk variable work)
        self.root = tk.Tk()

        # Fake sessionpars
        self.fake_sessionpars = {
            'cal_file': tk.StringVar(value='cal_stim.wav'),
            'slm_reading': tk.DoubleVar(value=75.5),
            'cal_level_dB': tk.DoubleVar(value=-30),
            'slm_offset': tk.DoubleVar(value=1.0),
            'adjusted_level_dB': tk.DoubleVar(value=1.0),
            'desired_level_dB': tk.DoubleVar(value=1.0)
        }


    def tearDown(self):
        del self.root
        del self.fake_sessionpars


    def test_calmodel_init(self):
        c = CalModel(self.fake_sessionpars)


    def test_get_cal_file_exists(self):
        c = CalModel(self.fake_sessionpars)
        c.get_cal_file()


    @patch('tmgui.shared_assets.audio.CALSTIM_WAV', 'fake_calstim.wav')
    def test_get_cal_file_not_exists(self):
        c = CalModel(self.fake_sessionpars)
        with self.assertRaises(AttributeError):
            c.get_cal_file()


    def test_calc_offset(self):
        time.sleep(0.5)
        c = CalModel(self.fake_sessionpars)
        c.calc_offset()
        self.assertEqual(self.fake_sessionpars['slm_offset'].get(), 105.5)


    def test_calc_level(self):
        self.fake_sessionpars['slm_offset'].set(105.5)
        c = CalModel(self.fake_sessionpars)
        c.calc_level(80)
        self.assertEqual(
            self.fake_sessionpars['adjusted_level_dB'].get(), 
            -25.5
        )


if __name__ == '__main__':
    unittest.main()
