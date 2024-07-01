""" Class to replace TkVar data types during testing.

    Necessary because Tk.root is not cleaned up properly
    during testing.

    Written by: Travis M. Moore
    Last edited: April 18, 2024
"""

###########
# Imports #
###########
# Standard library
import json
import tkinter as tk

###########
# MyTkVar #
###########
class MyTkVar:
    """ Class to replace TkVar data types during automated testing. """
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value
    def set(self, newval):
        self.value = newval
    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return str(self.value)


class JSONVar(tk.StringVar):
    """ A Tk varible that can hold dicts and lists. """
    def __init__(self, *args, **kwargs):
        kwargs['value'] = json.dumps(kwargs.get('value'))
        super().__init__(*args, **kwargs)


    def set(self, value, *args, **kwargs):
        string = json.dumps(value)
        super().set(string, *args, **kwargs)


    def get(self, *args, **kwargs):
        string = super().get(*args, **kwargs)
        return json.loads(string)


if __name__ == '__main__':
    pass
