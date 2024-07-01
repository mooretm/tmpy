""" Audio device view. 

    Written by: Travis M. Moore
    Last edited: June 25, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Third party
import sounddevice as sd

# Custom
from tmpy import functions
from tmpy import tkgui

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

#############
# AudioView #
#############
class AudioView(tk.Toplevel):
    """ Audio device view. """
    def __init__(self, parent, settings, *args, **kwargs):
        super().__init__(parent, *args, *kwargs)
        logger.info("Initializing AudioView")

        # Assign attributes
        self.parent = parent
        self.settings = settings

        # Window setup
        self.withdraw()
        self.focus()
        self.title("Audio Settings")
        self.resizable(False, False)
        self.columnconfigure(5, weight=1)
        self.grab_set() # Disable root window (toplevel as modal window)

        # Get list of audio devices
        self.devices = self._query_audio_devices()
        # Draw widgets
        self._draw_widgets()
        # Center window
        self._center_window()

    def _draw_widgets(self):
        """ Draw widgets on AudioView. """
        logger.info("Drawing AudioView widgets")

        #################
        # Custom Styles #
        #################
        style = ttk.Style()
        style.configure(
            'Bold.TLabel', 
            font=('TkDefaultFont', 12, 'bold'), 
            )

        ##########
        # Frames #
        ##########
        # Options for label frames
        options = {'padx':10, 'pady':10}

        # Channel routing entry box
        lfrm_routing = ttk.LabelFrame(self, text="Channel Routing")
        lfrm_routing.grid(row=5, column=5, **options, sticky='we')
        lfrm_routing.columnconfigure(5, weight=1)

        # Audio device table
        self.frm_tree = ttk.Frame(self)
        self.frm_tree.grid(row=10, column=5, **options)

        # Submit button
        frm_submit = ttk.Frame(self)
        frm_submit.grid(row=15, column=5, **options)

        ###########
        # Widgets #
        ###########
        # Routing
        tkgui.LabelInput(
            lfrm_routing,
            label="Channels (format: 1, 2, 3...)",
            var=self.settings['channel_routing'],
            input_class=tkgui.ListEntry,
            tool_tip="Channels for playback. Separate multiple channels "
                + "by a comma and a space: 1, 2, 3"
        ).grid(row=5, column=5, padx=10, pady=(10, 0))

        # Audio device
        audio_device_name = self._get_audio_device_name()
        self.audio_var = tk.StringVar(value=audio_device_name)
        tkgui.LabelInput(
            lfrm_routing,
            label="Audio Device (click below to select)",
            var=self.audio_var,
            input_class=ttk.Label,
            input_args={
                'relief': 'solid', 
                'borderwidth': 1, 
                'style': 'Gray.TLabel'
                },
            tool_tip="Select an audio device from the list below."
        ).grid(row=10, column=5, padx=10, pady=(0, 10))

        # Treeview instructions label
        ttk.Label(self.frm_tree, text="Click an audio device below to " +
            "select it.", style='Bold.TLabel').grid(row=5, column=5)
        # Create treeview
        self.tree = self._create_tree_widget()

        # Submit button
        ttk.Button(frm_submit, text="Submit", command=self._on_submit).grid(
            column=5, columnspan=15, row=5)

    def _get_audio_device_name(self):
        """ Get the audio device name from the device ID. """
        logger.info("Getting audio device name from device ID")
        try:
            audio_device_name = [item[1] for item in self.devices if \
                item[0] == self.settings['audio_device'].get()][0]
        except IndexError:
            audio_device_name = "No audio device selected"
        return audio_device_name

    def _create_tree_widget(self):
        """ Create and populate treeview. """
        logger.info("Creating tree")
        # Create tree widget
        columns = ('device_id', 'device_name', 'channels_out')
        tree = ttk.Treeview(self.frm_tree, columns=columns, show='headings')
        # Define headings
        tree.heading('device_id', text='Device ID')
        tree.heading('device_name', text='Device Name')
        tree.heading('channels_out', text='Outputs')
        # Define columns
        tree.column('device_id', width=60, anchor=tk.CENTER)
        tree.column('device_name', width=400, anchor=tk.W)
        tree.column('channels_out', width=60, anchor=tk.CENTER)
        # Bind command
        tree.bind('<<TreeviewSelect>>', self._item_selected)
        tree.grid(row=10, column=5, sticky=tk.NSEW)
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.frm_tree, 
                                  orient=tk.VERTICAL, 
                                  command=tree.yview
        )
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=10, column=6, sticky='ns')
        # Populate tree
        for self.device in self.devices:
            tree.insert('', tk.END, values=self.device)
        return tree

    def _query_audio_devices(self):
        """ Create list of tuples with specified device information. """
        logger.info("Querrying audio devices")
        # Get list of audio devices
        deviceList = sd.query_devices()
        # Create list of tuples with device info
        devices = []
        for ii in range(0,len(deviceList)):
            if deviceList[ii]['max_output_channels'] > 0:
                devices.append((ii, deviceList[ii]['name'], 
                                deviceList[ii]['max_output_channels']))
        return devices

    #############
    # Functions #
    #############
    def _center_window(self):
        """ Center the TopLevel window over the parent window. """
        functions.tkgui_funcs.center_window_over_parent(
            window_to_center=self
        )

    def _item_selected(self, event):
        """ Update audio device ID with the device selected
        from the tree.
        """
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            # Update settings with device id
            logger.info("Updating settings with selected device ID")
            self.settings['audio_device'].set(record[0])
            self.audio_var.set(record[1])

    def _on_submit(self):
        """ Send submit event to controller. """
        logger.info("SUBMIT button pressed")
        errors = functions.tkgui_funcs.get_errors(self.settings)
        if errors:
            logger.error("Found %d errors", len(errors))
            messagebox.showerror(
                title="Invalid Entry",
                message="Unable to save form!",
                detail="Error in fields:\n{}"
                .format('\n'.join(errors.keys()))
            )
            return
        logger.info("Sending save audio device event")
        self.parent.event_generate('<<AudioViewSubmit>>')
        logger.info("Destroying AudioView instance")
        self.destroy()

################
# Module Guard #
################
if __name__ == "__main__":
    pass
