""" Customized tkinter widgets. 

Written by: Travis M. Moore (except where otherwise indicated)
Last edited: June 26, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import tkinter as tk
from idlelib.tooltip import Hovertip
from tkinter import filedialog
from tkinter import ttk

# Custom
from tmpy.functions import helper_funcs as hf

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

##############
# LabelInput #
##############
class LabelInput(tk.Frame):
    """ A Label and Entry combination. 
    Written by: Python GUI Programming with Tkinter (Alan D. Moore).
    Modified by: Travis M. Moore
    """
    def __init__(self, parent, label, var, input_class=ttk.Entry, 
                 input_args=None, label_args=None, tool_tip=None, 
                 disable_var=None, 
                 **kwargs):
        super().__init__(parent, **kwargs)

        # Assign attributes
        input_args = input_args or {}
        label_args = label_args or {}
        self.variable = var
        self.variable.label_widget = self

        ###########
        # Widgets #
        ###########
        # Checkbuttons and Buttons don't require an additional label
        if input_class in (ttk.Checkbutton, ttk.Button):
            input_args['text'] = label
        else:
            # Position the label
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            # Add tooltip
            if tool_tip:
                Hovertip(
                    anchor_widget=self.label,
                    text=tool_tip,
                    hover_delay=1000 # ms
                )

        # Add input's control variable. Syntax differs based on 
        # widget type. 
        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            input_args['variable'] = self.variable
        else:
            input_args['textvariable'] = self.variable

        # Radiobuttons
        if input_class == ttk.Radiobutton:
            self.input = tk.Frame(self)
            for v in input_args.pop('values', []):
                button = ttk.Radiobutton(
                    self.input,
                    value=v,
                    text=v,
                    **input_args
                )
                button.pack(
                    side=tk.LEFT,
                    ipadx=10,
                    ipady=2,
                    expand=True,
                    fill='x'
                )
        else:
            self.input = input_class(self, **input_args)
            # Add tooltip
            if tool_tip:
                Hovertip(
                    anchor_widget=self.input,
                    text=tool_tip,
                    hover_delay=1000 # ms
                )
            
        # Position the input
        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
        self.columnconfigure(0, weight=1)

        # Disable switch
        if disable_var:
            self.disable_var = disable_var
            self.disable_var.trace_add('write', self._check_disable)

        # Error label
        self.error = getattr(self.input, 'error', tk.StringVar())
        ttk.Label(self, textvariable=self.error, foreground='red',
                  **label_args).grid(
            row=2, column=0, sticky=(tk.W + tk.E)
        )

    ###########
    # Methods #
    ###########
    def _check_disable(self, *_):
        """ Check value of disable_var and take appropriate action. """
        if not hasattr(self, 'disable_var'):
            return
        if self.disable_var.get():
            self.input.configure(state=tk.DISABLED)
            self.variable.set('')
            self.error.set('')
        else:
            self.input.configure(state=tk.NORMAL)

    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        """ Override grid to add default sticky values. """
        super().grid(sticky=sticky, **kwargs)

################
# AskPathGroup #
################
class AskPathGroup(ttk.Frame):
    """ Group of widgets for navigating to a directory. """
    def __init__(self, parent, var, title_args, 
                 type=None, tool_tip=None, **kwargs):
        super().__init__(parent, **kwargs)

        # Assign values
        self.variable = var
        self.title_args = title_args or {}
        self.type = type
        self.display_var = tk.StringVar()
        
        # Check for number of characters kwarg
        if 'num_chars' in kwargs:
            self.num_chars = kwargs['num_chars']
        else:
            self.num_chars = 35

        # Configure weights
        for ii in range(0,16):
            self.columnconfigure(ii, weight=1)

        # Styles
        style = ttk.Style()
        style.configure(
            'Path.TLabel',
            foreground='gray20',
            borderwidth=3,
            relief='solid'
            )

        options = {
            'sticky': 'we',
            'padx': 10,
            'pady': 2.5
        }

        ###########
        # Widgets #
        ###########
        # Title
        lbl_title = ttk.Label(self, **title_args)
        lbl_title.grid(row=0, column=0, **options)
        if tool_tip:
            Hovertip(
                anchor_widget=lbl_title,
                text=tool_tip,
                hover_delay=1000 # ms
            )

        # Path display
        ttk.Label(
            self, 
            textvariable=self.display_var,
            width=35,
            style='Path.TLabel'
            ).grid(row=1, column=0, ipadx=5, **options
        )

        # Browse button
        ttk.Button(self, text="Browse", command=self.run
                   ).grid(
                       row=2, 
                       column=0, 
                       padx=options['padx'], 
                       pady=options['pady'], 
                       sticky='w'
        )
        
        # Display current (shortened) directory path
        self._update_display()

    ###########
    # Widgets #
    ###########
    def _get_path(self):
        """ Get directory from user via file browser. """
        # Get directory
        if self.type == 'dir':
            mydir = filedialog.askdirectory(title=self.title_args['text'])
            if mydir:
                self.variable.set(mydir)
        # Get file
        if self.type == 'file':
            myfile = filedialog.askopenfilename(
                title=self.title_args['text'],
                filetypes=(("CSV Files","*.csv"),))
            if myfile:
                self.variable.set(myfile)

    def _update_display(self):
        """ Update value in Tk display var. """
        truncated = hf.truncate_string(
            full_string=self.variable.get(),
            num_chars=self.num_chars
        )
        self.display_var.set(truncated)

    def run(self):
        self._get_path()
        self._update_display()

    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        """ Override grid to add default sticky values. """
        super().grid(sticky=sticky, **kwargs)

#############
# BoundText #
#############
class BoundText(tk.Text):
    """ A Text widget with a bound variable. Necessary because 
    a typical Text widget can handle data types that cannot 
    by stored in a tk.StringVar (e.g., images).

    Written by: Python GUI Programming with Tkinter (Alan D. Moore).
    """
    def __init__(self, *args, textvariable=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Assign values
        self._variable = textvariable
        if self._variable:
            self.insert('1.0', self._variable.get())
            self._variable.trace_add('write', self._set_content)
            self.bind('<<Modified>>', self._set_var)

    def _set_var(self, *_):
        """ Set the variable to the text contents. """
        if self.edit_modified():
            # Grab all chars except last (a newline char)
            content = self.get('1.0', 'end-lchars')
            self._variable.set(content)
            # Reset modified flag
            self.edit_modified(False)

    def _set_content(self, *_):
        """ Set the text contents to the variable. """
        self.delete('1.0', tk.END)
        self.insert('1.0', self._variable.get())

################
# Module Guard #
################
if __name__ == '__main__':
    pass
