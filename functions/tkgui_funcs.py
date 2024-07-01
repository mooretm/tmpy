""" GUI functions. 

Written by: Travis M. Moore
Last edited: June 19, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import markdown
import os
import tkinter as tk
import webbrowser
from tkinter import ttk

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

#############
# Functions #
#############
def add_frame(parent, label, cols=3):
    """ Add a LabelFrame to a form. """
    logger.info("Adding frame to form")
    frame = ttk.LabelFrame(parent, text=label)
    frame.grid(sticky=(tk.W + tk.E))
    for i in range(cols):
        frame.columnconfigure(i, weight=1)
    return frame

def center_window(window):
    """ Center window over parent window. """
    logger.info("Centering root window after drawing widgets")
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
    x = screen_width/2 - size[0]/2
    y = screen_height/2 - size[1]/2
    window.geometry("+%d+%d" % (x, y))
    window.deiconify()

def center_window_over_parent(window_to_center):
    """ Center the TopLevel window over the root window. """
    logger.info("Centering window over parent")
    # Get updated window size (after drawing widgets)
    window_to_center.update_idletasks()
    # Calculate the x and y coordinates to center the window
    x = window_to_center.parent.winfo_x() \
        + (window_to_center.parent.winfo_width() - window_to_center.winfo_reqwidth()) // 2
    y = window_to_center.parent.winfo_y() \
        + (window_to_center.parent.winfo_height() - window_to_center.winfo_reqheight()) // 2
    # Set the window position
    window_to_center.geometry("+%d+%d" % (x, y))
    # Display window
    window_to_center.deiconify()

def get_errors(error_vars):
    """ Get a list of field errors in the form. """
    logger.info("Checking for field validation errors")
    errors = {}
    for key, var in error_vars.items():
        try:
            inp = var.label_widget.input
            error = var.label_widget.error
            if hasattr(inp, 'trigger_focusout_validation'):
                inp.trigger_focusout_validation()
            if error.get():
                errors[key] = error.get()
        except AttributeError:
            continue
        except tk.TclError:
            logger.warning("Ignoring: %s", key)
    logger.info("Found %d errors", len(errors))
    return errors
    
def get_tk_values(tk_dict):
    """ Make a new dictionary with actual TkVar values. """
    logger.info("Getting Tk control variable values")
    converted = {}
    for key, value in tk_dict.items():
        converted[key] = value.get()
    return converted

def open_in_browser(markdown_path, html_path):
    """ Open HTML file in default browser. 
    
    :param source_path: Path to HTML source code
    :type source_path: str or Path
    :return: None (opens file in browser)
    :rtype: None
    """
    logger.info(
        "Opening %s in default browser", 
        os.path.basename(html_path)
        #Path(markdown_path).stem
    )
    # Read markdown file and convert to html
    with open(markdown_path, 'r') as f:
        text = f.read()
        html = markdown.markdown(text)
    # Create html file for display
    with open(html_path, 'w') as f:
        f.write(html)
    # Open README in default web browser
    webbrowser.open(html_path)

################
# Module Guard #
################
if __name__ == '__main__':
    pass
