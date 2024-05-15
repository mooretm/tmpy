""" Class to replace TkVar data types during testing.

    Necessary because Tk.root is not cleaned up properly
    during testing.

    Written by: Travis M. Moore
    Last edited: April 18, 2024
"""

class MyTkVar:
    """ Class to replace TkVar data types during testing. """
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


if __name__ == '__main__':
    pass
