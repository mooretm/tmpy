""" Audio class for importing and presenting audio.

    Accepted audio types: WAV files and numpy arrays.

    Written by: Travis M. Moore
    Last edited: June 14, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import os
from pathlib import Path

# Third party
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import sounddevice as sd
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# Custom
from ..audio_handlers import audio_exceptions

##########
# Logger #
##########
# Create custom logger
logger = logging.getLogger(__name__)

###############
# AudioPlayer #
###############
class AudioPlayer:
    """ Import and play back WAV or numpy array. """

    def __init__(self, audio, **kwargs):
        """ Create audio object using file path or signal array
            audio: a Path object from pathlib, or a numpy array
            kwargs: must provide a sampling rate when passing an array
        """
        logger.info("Initializing AudioPlayer")

        # Assign attributes
        self.audio = audio
        
        # If AUDIO argument is a Path, import .wav file;
        if isinstance(audio, Path):
            self._import_wav_file()

        # If AUDIO is an array, assign it to signal
        # and grab provided sampling rate
        elif isinstance(audio, np.ndarray):
            #print("audiomodel: Found audio ndarray object")
            logger.info("Found ndarray audio")
            self.signal = self.audio
            try:
                self.fs = kwargs['sampling_rate']
            except: 
                logger.exception("Please provide a sampling rate " \
                               "for numpy array signals!")
                raise audio_exceptions.MissingSamplingRate()
        else:
            logger.exception("Unrecognized audio type!")
            raise audio_exceptions.InvalidAudioType(type(self.audio))

        # Get audio details
        self._get_audio_details()


    def _import_wav_file(self):
        logger.info("Attempting to load %s", os.path.basename(self.audio))

        # Parse file path
        self.directory = os.path.split(self.audio)[0]
        self.name = os.path.basename(self.audio)

        # Read audio file
        file_exists = os.access(self.audio, os.F_OK)
        if not file_exists:
            logger.exception("Audio file not found!")
            raise FileNotFoundError
        else:
            self.signal, self.fs = sf.read(self.audio)
            logger.info("Sampling rate: %d", self.fs)


    def _get_audio_details(self):
        # Get number of channels
        try:
            self.num_channels = self.signal.shape[1]
        except IndexError:
            self.num_channels = 1
        self.channels = np.array(range(1, self.num_channels+1))
        logger.info("Channels in signal: %d", self.num_channels)

        # Assign audio file attributes
        self.dur = len(self.signal) / self.fs
        self.t = np.arange(0, self.dur, 1/self.fs)
        secs = np.round(self.dur, 2)
        mins = np.round(self.dur/60, 2)
        logger.info("Duration: %.1f seconds (%.1f minutes)", secs, mins) 

        # Get data type
        self.data_type = self.signal.dtype
        logger.info("Data type: %s", str(self.data_type))


    def stop(self):
        """ Stop audio presentation. """
        logger.info("Stop called")
        sd.stop()


    def play(self, level=None, device_id=None, routing=None):
        """ Assign device id. Truncate audio/routing, if necessary,
            based on number of audio device channels. Set level.
        """
        logger.info("Preparing for playback")

        # Initialization
        self.level = level
        self.device_id = device_id
        self.routing = routing

        # Create a temporary audio file to modify
        self.temp = self.signal.copy()
        self.temp = self.temp.astype(np.float32)
        logger.info("Data type converted to %s", str(self.temp.dtype))

        # Assign default sounddevice settings
        try:
            self._set_defaults()
        except sd.PortAudioError:
            logger.error("Invalid audio device!")
            raise audio_exceptions.InvalidAudioDevice(self.device_id)

        # Check channel routing
        if (self.num_channels != len(self.routing)) or (not self.routing):
            logger.error("Invalid channel routing!")
            raise audio_exceptions.InvalidRouting(
                self.num_channels, self.routing)

        # Set level
        self._set_level()

        # Check for clipping after level has been applied
        try:
            self._check_clipping()
        except audio_exceptions.Clipping:
            logger.error("Presentation level caused clipping!")
            raise

        # Truncate audio file channels and routing, if necessary, 
        # based on available audio device channels
        self._check_channels_and_routing()

        # Present audio
        logger.info("Attempting to present audio")
        sd.play(self.temp, mapping=self.routing)
        logger.info("Successful")


    #####################
    # Play Helper Funcs #
    #####################
    def _set_defaults(self):
        """ Set default sounddevice settings based on provided values. """
        # Assign audio device default
        try:
            sd.default.device = self.device_id
            device_name = sd.query_devices(sd.default.device)['name']
            logger.info("Audio device: %s", device_name)
        except sd.PortAudioError:
            raise
        
        # Get number of available audio device channels
        self.num_outputs = sd.query_devices(
            sd.default.device)['max_output_channels']
        logger.info("Device outputs: %d", self.num_outputs)

        # Assign audio device sampling rate based on 
        # provided audio sampling rate
        sd.default.samplerate = self.fs


    def _check_channels_and_routing(self):
        # Check that audio device has enough channels for audio
        if self.num_outputs < self.num_channels:
            logger.warning("%d-channel file, but only %d audio device " \
                           "channels!", self.num_channels, self.num_outputs)
            dropped = self.num_channels - self.num_outputs
            logger.warning("Dropping %d audio file channels", dropped)

            # Update audio file and channel routing dimensions to 
            # match number of available audio device outputs
            self.temp = self.temp[:, 0:self.num_outputs]
            self.routing = self.routing[:self.temp.shape[1]]
        logger.info("Audio shape: %s", self.temp.shape)


    def _set_level(self):  
        """ Set presentation level and check for clipping. """
        if self.level == None:
            # Normalize if no level is provided
            logger.warning("No level provided; normalizing to +/-1")
            if self.num_channels > 1:
                for chan in range(0, self.num_channels):
                    # Remove DC offset
                    self.temp[:, chan] = self.temp[:, chan] - np.mean(self.temp[:, chan])
                    # Normalize
                    self.temp[:, chan] = self.temp[:, chan] / np.max(np.abs(self.temp[:, chan]))
                    # account for num channels
                    self.temp[:, chan] = self.temp[:, chan] / self.num_channels 
            elif self.num_channels == 1:
                # Remove DC offset
                self.temp = self.temp - np.mean(self.temp)
                # Normalize
                self.temp = self.temp / np.max(np.abs(self.temp))
                # account for num channels
                self.temp = self.temp / 1
        else:
            # Convert level in dB to magnitude
            mag = self.db2mag(self.level)
            logger.info("Adjusted level (dB): %f", self.level)
            logger.info("Multiplying signal by: %f", mag)
            # Apply scaling factor to self.temp
            self.temp = self.temp * mag


    def _check_clipping(self):
        """ Plot clipped waveform for visual inspection. """
        if np.max(np.abs(self.temp)) > 1:
            # Raise exception to prevent playback
            #self.plot_waveform()
            logger.error("Clipping has occurred!")
            raise audio_exceptions.Clipping


    def plot_waveform(self, title=None):
        """ Plot all channels overlaid. """
        logger.info("Creating waveform plot")
        # Create time base
        dur = len(self.temp) / self.fs
        t = np.arange(0, dur, 1/self.fs)
        # Plot
        plt.plot(t, self.temp)
        plt.title(title)
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.axhline(y=1, color='red', linestyle='--')
        plt.axhline(y=-1, color='red', linestyle='--')
        plt.show()


    ###########################
    # Signal Processing Funcs #
    ###########################
    def db2mag(self, db):
        """ Convert decibels to magnitude. Takes a single
        value or a list of values.
        """
        # Must use this form to handle negative db values!
        try:
            mag = [10**(x/20) for x in db]
            return mag
        except:
            mag = 10**(db/20)
            return mag


    def mag2db(self, mag):
        """Convert magnitude to decibels. Takes a single
        value or a list of values.
        """
        try:
            db = [20 * np.log10(x) for x in mag]
            return db
        except:
            db = 20 * np.log10(mag)
            return db


    def rms(self, sig):
        """ Calculate the root mean square of a signal. 
            
        NOTE: np.square will return invalid, negative 
            results if the number excedes the bit 
            depth. In these cases, convert to int64
            EXAMPLE: sig = np.array(sig,dtype=int)

        Written by: Travis M. Moore
        Last edited: Feb. 3, 2020
        """
        theRMS = np.sqrt(np.mean(np.square(sig)))
        return theRMS


    def setRMS(self, sig, amp, eq='n'):
        """Set RMS level of a 1-channel or 2-channel signal.
        
        SIG: a 1-channel or 2-channel signal
        AMP: the desired amplitude to be applied to 
            each channel. Note this will be the RMS 
            per channel, not the total of both channels.
        EQ: takes 'y' or 'n'. Whether or not to equalize 
            the levels in a 2-channel signal. For example, 
            a signal with an ILD would lose the ILD with 
            EQ='y', so the default in 'n'.

        EXAMPLE: 
        Create a 2 channel signal
        [t, tone1] = mkTone(200,0.1,30,48000)
        [t, tone2] = mkTone(100,0.1,0,48000)
        combo = np.array([tone1, tone2])
        adjusted = setRMS(combo,-15)
        """
        if len(sig.shape) == 1:
            rmsdb = self.mag2db(self.rms(sig))
            refdb = amp
            diffdb = np.abs(rmsdb - refdb)
            if rmsdb > refdb:
                sigAdj = sig / self.db2mag(diffdb)
            elif rmsdb < refdb:
                sigAdj = sig * self.db2mag(diffdb)
            # Edit 5/17/22
            # Added handling for when rmsdb == refdb
            elif rmsdb == refdb:
                sigAdj = sig
            return sigAdj

        elif len(sig.shape) == 2:
            rmsdbLeft = self.mag2db(self.rms(sig[0]))
            rmsdbRight = self.mag2db(self.rms(sig[1]))

            ILD = np.abs(rmsdbLeft - rmsdbRight) # get lvl diff

            # Determine lvl advantage
            if rmsdbLeft > rmsdbRight:
                lvlAdv = 'left'
                #print("Adv: %s" % lvlAdv)
            elif rmsdbRight > rmsdbLeft:
                lvlAdv = 'right'
                #print("Adv: %s" % lvlAdv)
            elif rmsdbLeft == rmsdbRight:
                lvlAdv = None

            #refdb = amp - 3 # apply half amp to each channel
            refdb = amp
            diffdbLeft = np.abs(rmsdbLeft - refdb)
            diffdbRight = np.abs(rmsdbRight - refdb)

            # Adjust left channel
            if rmsdbLeft > refdb:
                sigAdjLeft = sig[0] / self.db2mag(diffdbLeft)
            elif rmsdbLeft < refdb:
                sigAdjLeft = sig[0] * self.db2mag(diffdbLeft)
            # Adjust right channel
            if rmsdbRight > refdb:
                sigAdjRight = sig[1] / self.db2mag(diffdbRight)
            elif rmsdbRight < refdb:
                sigAdjRight = sig[1] * self.db2mag(diffdbRight)

            # If there is a lvl difference to maintain across channels
            if eq == 'n':
                if lvlAdv == 'left':
                    sigAdjLeft = sigAdjLeft * self.db2mag(ILD/2)
                    sigAdjRight = sigAdjRight / self.db2mag(ILD/2)
                elif lvlAdv == 'right':
                    sigAdjLeft = sigAdjLeft / self.db2mag(ILD/2)
                    sigAdjRight = sigAdjRight * self.db2mag(ILD/2)

            sigBothAdj = np.array([sigAdjLeft, sigAdjRight])
            return sigBothAdj
