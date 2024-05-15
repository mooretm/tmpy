# Import official modules
import sys
import unittest
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

# Import my modules
from tmpy import tmsignals as ts
from tmpy import tmreverb as tr

# INSTRUCTIONS #
# Navigate to project parent directory
# In the REPL type: python -m tests.test_tmreverb
# Add 'plots' at the end (no quotes) to display all plots
#   Example: python -m tests.test_tmreverb plots
# Add function name at the end (no quotes) to display single plots
#   Example: python -m tests.test_tmreverb sroom
# By default, all plots are hidden


class Test_sroom(unittest.TestCase):

    def test_sroom_Allen_Berkley(self):
        # Distances in feet, from Allen and Berkley (1979)
        headPos = np.array([3.75,12.5,5]) 
        srcPos = np.array([6.25,1.25,7.5])
        roomSize = np.array([10,15,12.5])
        # Absorption coefficients, from Allen and Berkley (1979)
        wallRef = 0.9
        ceilRef = 0.7
        beta = np.zeros((2,3))
        beta[:,0:2] = wallRef
        beta[:,2] = ceilRef
        # Other parameters
        dur = 256 # duration in ms, from Allen and Berkley (1979)
        fs = 8000 # sampling rate in Hz, from Allen and Berkley (1979)

        # Calculate room impulse response
        ht = tr.sroom2(headPos,srcPos,roomSize,beta,dur,fs)
        if plots == "plots" or plots == "sroom":
            grid = np.linspace(0,256,2049)
            plt.figure()
            plt.plot(grid[1:],ht)
            plt.title("Room Impulse Response")
            plt.show()

        # Convert to dB decay curve
        dec = tr.htToDb(ht)

        # Synthesize tone
        [t,sig] = ts.mkTone(500,dur/1000,0,fs)
        sig = ts.doGate(sig,0.02,fs)
        sig = ts.setRMS(sig,-20)
        if plots == "plots" or plots == "sroom":
            sd.play(sig.T,fs)
            sd.wait(dur/1000+0.1)
            plt.plot(sig)
            plt.title('Dry Tone (anechoic)')
            plt.show()

            # Analyze decay curve to get RT60
            rt60 = tr.rt(t,dec,40)
            print("Computed RT60: %.2f ms" % (1000*rt60))
            # Plot decay curve
            plt.plot(t,dec)
            plt.title("Decay Curve [dB]\n RT60: %.2f ms" % (1000*rt60))
            plt.show()

        # Apply reverb to tone
        revsig = np.convolve(sig,ht) # Convolve RIR with tone
        revsig = ts.setRMS(revsig,-15)
        if plots == 'plots' or plots == 'sroom':
            sd.play(revsig.T,fs)
            sd.wait(dur/1000+0.1)
            plt.plot(revsig)
            plt.title('Wet Tone (reverb)')
            plt.show()



if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Assign REPL value to plots
        # Remove REPL value from sys.argv list to avoid
        # messing with the unittest.main() list
        plots = sys.argv.pop()
    elif len(sys.argv) == 1:
        plots = 0 # does nothing
    unittest.main()
