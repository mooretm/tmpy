""" Custom validated widgets.

Written by: Travis M. Moore (except where otherwise indicated)
Last edited: July 1, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import re
import tkinter as tk
from datetime import datetime
from tkinter import ttk

# Third party
from tmpy.functions import helper_funcs as hf

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

##################
# ValidatedMixin #
##################
class ValidatedMixin:
    """ Adds a validation fucntionality to an input widget. 
    Written by: Python GUI Programming with Tkinter (Alan D. Moore).
    """
    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)

        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)
        self.configure(
            validate='all',
            validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
            invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    def _toggle_error(self, on=False):
        """ Change color of any entered text to red/black. """
        self.configure(foreground=('red' if on else 'black'))

    def _validate(self, proposed, current, char, event, index, action):
        """ Registered validation method (see init). Runs every time 
        something changes on the GUI (e.g., keystroke). Calls methods
        that can be overridden in specific widget classes.
        """
        self.error.set("")
        self._toggle_error()
        valid=True
        # If the widget is disabled, don't validate
        state = str(self.configure('state')[-1])
        if state == tk.DISABLED:
            return valid
        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
                )
        return valid

    def _focusout_validate(self, **kwargs):
        """ To be overridden by specific widget class. """
        return True
    
    def _key_validate(self, **kwargs):
        """ To be overridden by specific widget class. """
        return True
    
    def _invalid(self, proposed, current, char, event, index, action):
        """ Called when validation fails. """
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event == 'key':
            self._key_invalid(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
            )

    def _focusout_invalid(self, **kwargs):
        """ Handle invalid data on a focus event. """
        self._toggle_error(True)

    def _key_invalid(self, **kwargs):
        """ Handle invalid data on a key event.
        By default we want to do nothing.
        """
        pass

    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid

#################
# RequiredEntry #
#################
class RequiredEntry(ValidatedMixin, ttk.Entry):
    """ An Entry that requires a value. 
    Written by: Python GUI Programming with Tkinter (Alan D. Moore).
    """
    logger.info("Initializing RequiredEntry")

    def _focusout_validate(self, event):
        """ Validation on focusout. """
        valid = True
        if not self.get():
            valid = False
            logger.error("A value is required")
            self.error.set("A value is required")
        return valid

##################
# BoundListEntry #
##################
class BoundListEntry(ValidatedMixin, ttk.Entry):
    """ An Entry that validates itself based on the value
    of another BoundEntry. Requires a value. 
    """
    def __init__(self, *args, max_var=None, focus_update_var=None, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Initializing BoundListEntry")

        # Assign instance variables
        self.max_var = max_var
        self.focus_update_var = focus_update_var
        self.list_length = None
    
    def _focusout_validate(self, event):
        # Begin assuming no errors
        valid = True

        # Check for empty Entry
        if not self.get():
            logger.error("A value is required")
            self.error.set("A value is required")
            logger.debug("Returned False")
            return False
        
        # Check that list matches pattern
        pattern = r'^\w+(, \w+)*$'
        valid = bool(re.fullmatch(pattern, self.get()))
        if not valid:
            logger.error("Invalid format!")
            self.error.set("Invalid format!")
            logger.debug("Returned False")
            return False

        # Check for invalid data types while getting list length
        try:
            self.list_length = len(hf.string_to_list(self.get(), 'float'))
        except ValueError:
            logger.error("Invalid data type in entry: %s", self.get())
            self.error.set("Invalid data type!")
            return False
        logger.info("Found list of length: %d", self.list_length)

        # If provided, update focus_update_var with length
        # This variable is then used to set a maximum for 
        # other widgets. 
        if self.focus_update_var and not self.error.get():
            self.focus_update_var.set(self.list_length)
            logger.info("Updated list_length to: %d", self.list_length)

        # If provided, check that list_length either:
        #    Equals the length of provided max
        #    Has a length of 1
        if self.max_var:
            max = self.max_var.get()
            if self.list_length > max:
                logger.error("Too many items! " +
                    "Expected %s, got %s", max, self.list_length
                )
                self.error.set("Too many items!")
                logger.debug("Returned False")
                return False
            elif self.list_length < max:
                if self.list_length != 1:
                    logger.error("Too few items! " +
                                 "Expected %s, got %s", max, self.list_length
                    )
                    self.error.set("Too few items!")
                    logger.debug("Returned False")
                    return False
        logger.debug("Returned True")
        return valid

#############
# ListEntry #
#############
class ListEntry(ValidatedMixin, ttk.Entry):
    """ An Entry that requires multiple values to be 
    separated by a comma and a space.
    """
    logger.info("Initializing ListEntry")

    def _check_list_format(self, input_string):
        """ Compare input with regex pattern to ensure:
        1. The string starts and ends without any spaces.
        2. Each value is separated by a comma and exactly one whitespace.
        3. There is no trailing comma.
        """
        pattern = r'^\w+(, \w+)*$'
        return bool(re.fullmatch(pattern, input_string))

    def _focusout_validate(self, event):
        """ Validation on focusout. """
        valid = True
        if self._check_list_format(self.get()):
            valid = True
        else:
            valid = False
            logger.error("Invalid list: %s", self.get())
            self.error.set("Invalid list")
        return valid

#############
# DateEntry #
#############
class DateEntry(ValidatedMixin, ttk.Entry):
    """ An Entry that only accepts ISO date strings. """
    logger.info("Initializing DateEntry")

    def _key_validate(self, action, index, char, **kwargs):
        """ Validation on key stroke. """
        valid = True
        if action == '0': # delete action
            valid = True
        elif index in ('0', '1', '2', '3', '5', '6', '8', '9'):
            valid = char.isdigit()
        elif index in ('4', '7'):
            valid = char == '-'
        else:
            valid = False
        return valid

    def _focusout_validate(self, event):
        """ Validation on focusout. """
        errors = []
        # Check for empty field
        if not self.get():
            logger.error("A value is required")
            self.error.set("A value is required")
            return False
        # Check for valid date
        try:
            datetime.strptime(self.get(), '%Y-%m-%d')
        except ValueError:
            logger.error("Invalid date")
            self.error.set("Invalid date")
            return False
        # Check for matching string pattern
        pattern = r'^\S{4}-\S{2}-\S{2}$'
        if not bool(re.fullmatch(pattern, self.get())):
            logger.error("Invalid date")
            self.error.set("Invalid date")
            return False
        return True

################
# Module Guard #
################
if __name__ == '__main__':
    pass
