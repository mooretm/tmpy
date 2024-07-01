""" Calibration view. 

    Written by: Travis M. Moore
    Last edited: May 28, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

# Custom
from tmpy.functions import helper_funcs as hf

##########
# Logger #
##########
logger = logging.getLogger(__name__)

###################
# CalibrationView #
###################
class CalibrationView(tk.Toplevel):
    """ View for manual calibration with a sound level meter. """
    def __init__(self, parent, settings, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        logger.debug("Initializing CalibrationView")

        # Assign attributes
        self.parent = parent
        self.settings = settings

        # Window setup
        self.withdraw()
        self.resizable(False, False)
        self.focus()
        self.title("Calibration")
        self.grab_set()

        # Calibration selection controls #
        # Define variables for file path and radio button value
        self.cal_path = tk.StringVar(
            value='Please choose a calibration stimulus file'
            )
        self.cal_var = tk.StringVar()

        # Draw widgets
        self._draw_widgets()

        # Center calibration window
        self._center_window()


    def _draw_widgets(self):
        """ Draw widgets on MainView. """
        logger.debug("Drawing CalibrationView widgets")

        ##########
        # Frames #
        ##########
        # Options for label frames
        options = {'padx': 10, 'pady': 10}
        options_small = {'padx': 2.5, 'pady': 2.5}

        # Choose calibration file
        lfrm_load = ttk.LabelFrame(self, text="Calibration Stimulus")
        lfrm_load.grid(row=5, column=5, columnspan=10, **options)

        # Presentation controls
        lfrm_playback = ttk.Labelframe(self, text='Playback Controls')
        lfrm_playback.grid(
            row=10, 
            column=5, 
            columnspan=10, 
            **options, 
            sticky='we'
            )

        # SLM reading controls
        lfrm_slm = ttk.Labelframe(self, text='Measured Level')
        lfrm_slm.grid(
            row=15, 
            column=5, 
            columnspan=10, 
            **options, 
            sticky='we'
            )

        ##############################
        # Calibration File Selection #
        ##############################
        # Radio buttons
        # Default white noise stimulus
        rad_wgn = ttk.Radiobutton(
            lfrm_load, 
            text="White Noise", 
            takefocus=0,
            variable=self.cal_var, 
            value='wgn', 
            command=self._cal_type
            )
        rad_wgn.grid(
            row=0, 
            column=5, 
            columnspan=10, 
            sticky='w', 
            **options_small
            )

        # Upload custom calibration stimulus
        rad_custom = ttk.Radiobutton(
            lfrm_load, 
            text="Custom File", 
            takefocus=0, 
            variable=self.cal_var, 
            value='custom', 
            command=self._cal_type
            )
        rad_custom.grid(
            row=1, 
            column=5, 
            columnspan=10, 
            sticky='w', 
            **options_small
            )

        # File path
        self.lbl_calfile1 = ttk.Label(
            lfrm_load, text='File:', 
            state='disabled'
            )
        self.lbl_calfile1.grid(column=5, row=5, sticky='w', **options_small)
        self.lbl_calfile2 = ttk.Label(
            lfrm_load, 
            textvariable=self.cal_path, 
            borderwidth=2, 
            relief="solid", 
            width=60, 
            state='disabled'
            )
        self.lbl_calfile2.grid(row=5, column=10, sticky='w', **options_small)

        # Browse button
        self.btn_browse = ttk.Button(
            lfrm_load, 
            text="Browse", 
            state='disabled', 
            takefocus=0, 
            command=self._load_cal
            )
        self.btn_browse.grid(row=10, column=10, sticky='w', **options_small)
        
        # Set default calibration file type
        if self.settings['cal_file'].get() == 'cal_stim.wav':
            self.cal_var.set('wgn')
            self._set_custom_cntrls_status('disabled')
        else:
            # Set calibration selection to custom
            self.cal_var.set('custom')

            # Fit path length to label
            self._shorten_path(
                full_path=self.settings['cal_file'].get(),
                num_chars=45,
                label_var=self.cal_path
                )

            # Enable custom file controls
            self._set_custom_cntrls_status('enabled')

        #########################
        # Presentation Controls #
        #########################
        # Scaling factor
        ttk.Label(lfrm_playback, text="Level (dB):").grid(
            column=5, row=5, sticky='e', **options_small)
        ent_slm = ttk.Entry(lfrm_playback, 
            textvariable=self.settings['cal_level_dB'], width=6)
        ent_slm.grid(row=5, column=10, sticky='w', **options_small)
 
        # Play calibration stimulus
        btn_play = ttk.Button(lfrm_playback, text="Play", 
            command=self._on_play)
        btn_play.grid(row=10, column=5, columnspan=6, sticky='ew', 
            **options_small)

        # Stop calibration stimulus
        btn_stop = ttk.Button(lfrm_playback, text="Stop", 
            command=self._on_stop)
        btn_stop.grid(row=15, column=5, columnspan=6, sticky='ew', 
            **options_small)

        ##########################
        # Measured Level Widgets #
        ##########################
        # SLM reading entry box
        ttk.Label(lfrm_slm, text="SLM Reading (dB):").grid(
            column=5, row=15, sticky='e', **options_small)
        self.ent_slm = ttk.Entry(lfrm_slm, 
            textvariable=self.settings['slm_reading'],
            width=6, state='disabled')
        self.ent_slm.grid(column=10, row=15, sticky='w', **options_small)

        #################
        # Submit button #
        #################
        self.btn_submit = ttk.Button( 
            self,
            text="Submit", 
            command=self._on_submit, 
            state='disabled'
            )
        self.btn_submit.grid(
            row=25, 
            column=5, 
            columnspan=30, 
            pady=(0, 10)
            )

    #############
    # Functions #
    #############
    def _center_window(self):
        """ Center the TopLevel window over the root window. """
        logger.debug("Centering window over parent")
        # Get updated window size (after drawing widgets)
        self.update_idletasks()

        # Calculate the x and y coordinates to center the window
        x = self.parent.winfo_x() \
            + (self.parent.winfo_width() - self.winfo_reqwidth()) // 2
        y = self.parent.winfo_y() \
            + (self.parent.winfo_height() - self.winfo_reqheight()) // 2
        
        # Set the window position
        self.geometry("+%d+%d" % (x, y))

        # Display window
        self.deiconify()


    def _shorten_path(self, full_path, num_chars, label_var=None):
        # Truncate path
        short_path = hf.truncate_path(
            full_path=full_path,
            num_chars=num_chars
        )
        if label_var:
            # Update label value with truncated path
            label_var.set(short_path)


    def _set_custom_cntrls_status(self, state):
        """ Enable or disable custom cal file controls. """
        logger.debug("Setting custom file option to %s", state)
        self.lbl_calfile1.config(state=state)
        self.lbl_calfile2.config(state=state)
        self.btn_browse.config(state=state)


    def _cal_type(self):
        """ Radio button functions for choosing cal type. """
        # Custom calibration file
        if self.cal_var.get() == 'custom':
            # Enable file browsing controls
            self._set_custom_cntrls_status('enabled')

        # Default white noise
        elif self.cal_var.get() == 'wgn':
            # Assign default cal file
            self.settings['cal_file'].set('cal_stim.wav')
            # Update path text
            self.cal_path.set('Please choose a calibration stimulus file')
            # Disable custom file controls
            self._set_custom_cntrls_status('disabled')


    def _load_cal(self):
        """ Open browser for custom calibration file. """
        logger.debug("User navigating to custom calibration file")

        # Add file to settings dict
        self.settings['cal_file'].set(filedialog.askopenfilename())

        # Fit path length to label
        self._shorten_path(
            full_path=self.settings['cal_file'].get(),
            num_chars=45,
            label_var=self.cal_path
            )


    def _on_play(self):
        """ Send play event to controller. """
        logger.debug("Play button pressed")
        self.parent.event_generate('<<CalPlay>>')
        self.btn_submit.config(state='enabled')
        self.ent_slm.config(state='enabled')


    def _on_stop(self):
        """ Send stop event to controller. """
        logger.debug("Stop button pressed")
        self.parent.event_generate('<<CalStop>>')


    def _on_submit(self):
        """ Send submit event to controller and close window. """
        logger.debug("Sending 'SUBMIT' event to controller")
        self.parent.event_generate('<<CalibrationSubmit>>')
        logger.debug("Destroying CalibrationView instance")
        self.destroy()
