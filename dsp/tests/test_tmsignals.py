# Import official modules
import sys
import unittest
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import irfft
from scipy import signal

# Import my modules
from tmpy import tmsignals as ts
import importlib
importlib.reload(ts)


# INSTRUCTIONS #
# Navigate to project parent directory
# In the REPL type: python -m tests.test_tmsignals
# Add 'plots' at the end (no quotes) to display all plots
#   Example: python -m tests.test_tmsignals plots
# Add function name at the end (no quotes) to display single plots
#   Example: python -m tests.test_tmsignals doLoop
# By default, all plots are hidden


class Test_addSynth(unittest.TestCase):

    def test_addSynth_sawtooth(self):
        harms = np.arange(2,60,2)
        amps = [1/x for x in harms]
        phis = np.zeros(len(harms),dtype=int)
        [t, sig] = ts.addSynth(100,harms,amps,phis,0.05,48000)
        self.assertEqual(len(sig), 2400)
        if plots == "plots" or plots == "addSynth":
            plt.plot(t,sig)
            plt.title('TEST: addSynth, Sawtooth Wave')
            plt.show()


class Test_db2mag(unittest.TestCase):

    def test_db2mag_Single_Positive_Value(self):
        self.assertEqual(ts.db2mag(3), 1.4125375446227544)

    def test_db2mag_Single_Negative_Value(self):
        self.assertEqual(ts.db2mag(-3), 0.7079457843841379)

    def test_db2mag_List_of_Mixed_Values(self):
        self.assertEqual(ts.db2mag([2,-4]), [1.2589254117941673, 0.6309573444801932])


class Test_deg2rad(unittest.TestCase):

    def test_deg2rad_Single_Positive_Value(self):
        self.assertEqual(ts.deg2rad(180), np.pi)

    def test_deg2rad_Single_Negative_Value(self):
        self.assertEqual(ts.deg2rad(-180), -np.pi)

    def test_deg2rad_List_of_Mixed_Values(self):
        rads = ts.deg2rad([-90, 25])
        rads = [round(x,6) for x in rads]
        self.assertEqual(rads, [-1.570796, 0.436332])


class Test_doFFT(unittest.TestCase):

    def test_doFFT_1chan(self):
        [t, sig500] = ts.mkTone(500,0.02)
        [t, sig1500] = ts.mkTone(1200,0.02)
        sig1500 = sig1500 * 0.5
        combo = sig500 + sig1500
        combo = combo / combo.max()
        [xf,yf] = ts.doFFT(combo,48000)
        # Check whether bin at 500 Hz is max amplitude
        ppf = len(xf) / (48000 / 2)
        idx = int(ppf * 500)
        self.assertEqual(yf[idx],yf.max())
        # Plots
        if plots == "plots" or plots == "doFFT_1chan":
            fig, axs = plt.subplots(1,2)
            fig.suptitle('TEST: doFFT 1-Channel')
            # Signal
            plt.subplot(1,2,1)
            plt.plot(t,combo)
            plt.title('1-Channel Signal')
            # FFT
            plt.subplot(1,2,2)
            plt.plot(xf,yf)
            plt.title('FFT')
            plt.show()

    def test_doFFT_2chan(self):
        [t, sig500] = ts.mkTone(500,0.02)
        sig500 = sig500 * 0.3
        [t, sig1200] = ts.mkTone(1200,0.02)
        combo = np.array([sig500, sig1200])
        [xf,yf] = ts.doFFT(combo,48000)
        # Check whether bin at 1200 Hz is max amplitude
        ppf = len(xf) / (48000 / 2)
        idx = int(ppf * 1200)
        self.assertEqual(yf[idx],yf.max())
        # Plots
        if plots == "plots" or plots == "doFFT_2chan":
            fig, axs = plt.subplots(1,2)
            fig.suptitle('TEST: doFFT 2-Channels')
            # Signal
            plt.subplot(1,2,1)
            plt.plot(t,combo[0],color='blue')
            plt.plot(t,combo[1],color='red')
            plt.title('2-Channel Signal')
            # FFT
            plt.subplot(1,2,2)
            plt.plot(xf,yf)
            plt.title('FFT')
            plt.show()

    def test_doFFT_inverse(self):
        [t, sig500] = ts.mkTone(500,0.02)
        [t, sig1500] = ts.mkTone(1200,0.02)
        sig1500 = sig1500 * 0.5
        combo = sig500 + sig1500
        combo = combo / combo.max()
        [xf,yf] = ts.doFFT(combo,48000)
        # Check whether bin at 500 Hz is max amplitude
        ppf = len(xf) / (48000 / 2)
        idx = int(ppf * 500)
        yf[idx - 1 : idx + 2] = 0
        sig = irfft(yf)
        if plots == "plots" or plots == "doFFT_inverse":
            plt.subplot(1,2,1)
            plt.plot(combo)
            plt.xlim([0,(1/500)*48000*4])
            plt.title('500 and 1200 Hz')
            plt.subplot(1,2,2)
            plt.plot(sig)
            plt.xlim([0,(1/500)*48000*4])
            plt.title('1200 Hz tone removed')
            plt.show()


class Test_doGate(unittest.TestCase):

    def test_doGate_1chan(self):
        [t, tone1] = ts.mkTone(200,0.1,30,48000)
        onechan = ts.doGate(tone1,0.02,48000)
        self.assertEqual(len(onechan), 4800)
        if plots == "plots" or plots == "doGate":
            plt.plot(onechan)
            plt.title('TEST: doGate, 1-Channel')
            plt.show()

    def test_doGate_2chan(self):
        [t, tone1] = ts.mkTone(200,0.1,30,48000)
        [t, tone2] = ts.mkTone(100,0.1,0,48000)
        combo = np.array([tone1, tone2])
        twochan = ts.doGate(combo,0.02,48000)
        self.assertEqual(len(twochan[0]), 4800)
        self.assertEqual(len(twochan[1]), 4800)
        self.assertEqual(len(twochan.shape), 2)
        if plots == "plots" or plots == "doGate":
            plt.plot(twochan[0],color='blue')
            plt.plot(twochan[1],color='red')
            plt.title('TEST: doGate, 2-Channel')
            plt.show()


class Test_doLoop(unittest.TestCase):
    
    def test_doLoop_1chan(self):
        [t, tone1] = ts.mkTone(200,0.1,30,48000)
        sig = ts.doLoop(tone1,4,0.01,48000)
        if plots == "plots" or plots == "doLoop":
            plt.plot(sig)
            plt.title('TEST: doLoop, 1-Channel')
            plt.show()
    
    def test_doLoop_2chan(self):
        [t, tone1] = ts.mkTone(200,0.1,30,48000)
        [t, tone2] = ts.mkTone(100,0.1,0,48000)
        combo = np.array([tone1, tone2])
        sig = ts.doLoop(combo,4,0.01,48000)
        if plots == "plots" or plots == "doLoop":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: doLoop, 2-Channel')
            plt.show()


class Test_mag2db(unittest.TestCase):

    def test_mag2db_Single_Positive_Value(self):
        self.assertEqual(round(ts.mag2db(0.25),3), -12.041)

    # This passes, but throws a runtime warning
    #def test_mag2db_Single_Negative_Value(self):
    #    self.assertTrue(np.isnan(ts.mag2db(-0.3)))

    def test_mag2db_List_of_Mixed_Values(self):
        rads = ts.mag2db([2, 1.5])
        rads = [round(x,3) for x in rads]
        self.assertEqual(rads, [6.021, 3.522])


class Test_mkBinauralNoise(unittest.TestCase):

    def test_mkBinauralNoise_Dims(self):
        freqs = np.arange(500,2001)
        sig = ts.mkBinauralNoise(freqs,0.1,-700,1,48000)
        self.assertEqual(len(sig.shape), 2)
        # total duration = len(sig) + itd = 4834 
        self.assertEqual(len(sig[0]), 4834)
        self.assertEqual(len(sig[1]), 4834)

    def test_mkBinauralNoise_RL(self):
        freqs = np.arange(500,2001)
        sig = ts.mkBinauralNoise(freqs,0.1,700,-1,48000)
        self.assertTrue(np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1])), 1)
        self.assertTrue(np.abs(ts.rms(sig[0]) > np.abs(ts.rms(sig[1]))))
        if plots == "plots" or plots == "mkBinauralNoise":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: mkBinauralNoise, ITD: 700, ILD: -1')
            plt.show()

    def test_mkBinauralNoise_LR(self):
        freqs = np.arange(500,2001)
        sig = ts.mkBinauralNoise(freqs,0.1,-700,1,48000)
        self.assertTrue(np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1])), 1)
        self.assertTrue(np.abs(ts.rms(sig[0]) < np.abs(ts.rms(sig[1]))))
        if plots == "plots" or plots == "mkBinauralNoise":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: mkBinauralNoise, ITD: -700, ILD: 1')
            plt.show()

    def test_mkBinauralNoise_0(self):
        freqs = np.arange(500,2001)
        sig = ts.mkBinauralNoise(freqs,0.1,0,0,48000)
        # Check for "0" difference in RMS
        # Rounding errors do not permit straight comparisons to 0
        ILD0 = np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1]))
        self.assertTrue(ILD0 < 0.000001)
        self.assertTrue(ILD0 > -0.000001)
        self.assertTrue(np.abs(ts.rms(sig[0]) == np.abs(ts.rms(sig[1]))))
        # Check for duration without any added ITD
        self.assertEqual(len(sig[0]), 0.1*48000)
        self.assertEqual(len(sig[1]), 0.1*48000)
        if plots == "plots" or plots == "mkBinauralNoise":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],'--',color='red')
            plt.title('TEST: mkBinauralNoise, ITD: 0, ILD: 0')
            plt.show()


class Test_mkGaborClick(unittest.TestCase):

    def test_mkGaborClick_Dims(self):
        sig = ts.mkGaborClick(4000,0.002,500,-2,48000)
        self.assertEqual(len(sig.shape), 2)
        # total duration = len(sig) + itd = 96 + 24 = 120
        itd = 48000 * 500 / 1000000
        dur = 0.002 * 48000
        totaldur = itd + dur
        self.assertEqual(len(sig[0]), totaldur)
        self.assertEqual(len(sig[1]), totaldur)

    def test_mkGaborClick_RL(self):
        sig = ts.mkGaborClick(4000,0.002,500,-2,48000)
        self.assertTrue(np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1])), 2)
        self.assertTrue(np.abs(ts.rms(sig[0]) > np.abs(ts.rms(sig[1]))))
        if plots == "plots" or plots == "mkGaborClicks":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: mkGaborClicks, ITD: 500, ILD: -2')
            plt.show()

    def test_mkGaborClick_LR(self):
        sig = ts.mkGaborClick(4000,0.002,-500,2,48000)
        self.assertTrue(np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1])), 2)
        self.assertTrue(np.abs(ts.rms(sig[0]) < np.abs(ts.rms(sig[1]))))
        if plots == "plots" or plots == "mkGaborClicks":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: mkGaborClicks, ITD: -500, ILD: 2')
            plt.show()

    def test_mkGaborClick_0(self):
        sig = ts.mkGaborClick(4000,0.002,0,0,48000)
        # Check for "0" difference in RMS
        # Rounding errors do not permit straight comparisons to 0
        ILD0 = np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1]))
        self.assertTrue(ILD0 < 0.000001)
        self.assertTrue(ILD0 > -0.000001)
        self.assertTrue(np.abs(ts.rms(sig[0]) == np.abs(ts.rms(sig[1]))))
        # Check for duration without any added ITD
        self.assertEqual(len(sig[0]), 0.002*48000)
        self.assertEqual(len(sig[1]), 0.002*48000)
        if plots == "plots" or plots == "mkGaborClicks":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],'--',color='red')
            plt.title('TEST: mkGaborClicks, ITD: 0, ILD: 0')
            plt.show()


class Test_mkIPD(unittest.TestCase):
    def test_mkIPD_Dims(self):
        sig = ts.mkIPD(500,0.1,90,-2,48000)
        # Test for two channels
        self.assertTrue(len(sig.shape), 2)
        # Test each channel is the correct length
        self.assertEqual(len(sig[0]), 4800)
        self.assertEqual(len(sig[1]), 4800)

    def test_mkIPD_RL(self):
        sig = ts.mkIPD(500,0.01,90,-2.5,48000)
        # ILD should = 2.5
        self.assertTrue(np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1])), 2.5)
        # Left channel should have greater intensity
        self.assertTrue(np.abs(ts.rms(sig[0]) > np.abs(ts.rms(sig[1]))))
        # right chan should be +45 deg higher
        self.assertTrue(sig[0][0] < sig[1][0]) 
        if plots == "plots" or plots == "mkIPD":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: mkIPD, IPD: 90, ILD: -2.5')
            plt.show()

    def test_mkIPD_LR(self):
        sig = ts.mkIPD(500,0.01,-90,2.5,48000)
        # ILD should = 2.5
        self.assertTrue(np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1])), 2.5)
        # Right channel should have greater intensity
        self.assertTrue(np.abs(ts.rms(sig[0]) < np.abs(ts.rms(sig[1]))))
        # Left chan should be +45 deg higher
        self.assertTrue(sig[0][0] > sig[1][0])
        if plots == "plots" or plots == "mkIPD":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: mkIPD, IPD: -90, ILD: 2.5')
            plt.show()

    def test_mkIPD_0(self):
        sig = ts.mkIPD(500,0.01,0,0,48000)
        # Check for "0" difference in RMS
        # Rounding errors do not permit straight comparisons to 0
        ILD0 = np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1]))
        self.assertTrue(ILD0 < 0.000001)
        self.assertTrue(ILD0 > -0.000001)
        self.assertTrue(np.abs(ts.rms(sig[0]) == np.abs(ts.rms(sig[1]))))
        # Check for duration without any added ITD
        self.assertEqual(len(sig[0]), 0.01*48000)
        self.assertEqual(len(sig[1]), 0.01*48000)
        if plots == "plots" or plots == "mkIPD":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],'--',color='red')
            plt.title('TEST: mkIPD, IPD: 0, ILD: 0')
            plt.show()


class Test_mkITD(unittest.TestCase):

    def test_mkITD_Dims(self):
        sig = ts.mkITD(500,0.05,800,0,0.01,48000)
        # Test for two channels
        self.assertTrue(len(sig.shape), 2)
        # Test each channel is the correct length
        sig_len = np.ceil(0.05 * 48000 + (800*48000/1000000))
        self.assertEqual(len(sig[0]), sig_len)
        self.assertEqual(len(sig[1]), sig_len)
        env_left = np.abs(signal.hilbert(sig[0]))
        env_right = np.abs(signal.hilbert(sig[1]))
        if plots == "plots" or plots == "mkITD":
            plt.plot(sig[0],color='blue')
            plt.plot(env_left,color='blue')
            plt.plot(sig[1],color='red')
            plt.plot(env_right,color='red')
            plt.title('TEST: mkITD with envelope confirmation')
            plt.show()

    def test_mkITD_RL(self):
        sig = ts.mkITD(500,0.05,500,-2,0.01,48000)
        # ILD should = 2
        self.assertTrue(np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1])), 2)
        # Left channel should have greater intensity
        self.assertTrue(np.abs(ts.rms(sig[0]) > np.abs(ts.rms(sig[1]))))
        if plots == "plots" or plots == "mkITD":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: mkITD, ITD: 500, ILD: -2')
            plt.show()

    def test_mkITD_LR(self):
        sig = ts.mkITD(500,0.05,-500,2,0.01,48000)
        # ILD should = 2
        self.assertTrue(np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1])), 2)
        # Right channel should have greater intensity
        self.assertTrue(np.abs(ts.rms(sig[0]) < np.abs(ts.rms(sig[1]))))
        if plots == "plots" or plots == "mkITD":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: mkITD, ITD: -500, ILD: 2')
            plt.show()

    def test_mkITD_0(self):
        sig = ts.mkITD(500,0.05,0,0,0.01,48000)
        # Check for "0" difference in RMS
        # Rounding errors do not permit straight comparisons to 0
        ILD0 = np.abs(ts.rms(sig[0])) - np.abs(ts.rms(sig[1]))
        self.assertTrue(ILD0 < 0.000001)
        self.assertTrue(ILD0 > -0.000001)
        self.assertTrue(np.abs(ts.rms(sig[0]) == np.abs(ts.rms(sig[1]))))
        # Check for duration without any added ITD
        self.assertEqual(len(sig[0]), 0.05*48000)
        self.assertEqual(len(sig[1]), 0.05*48000)
        if plots == "plots" or plots == "mkITD":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],'--',color='red')
            plt.title('TEST: mkITD, ITD: 0, ILD: 0')
            plt.show()


class Test_mkNoise(unittest.TestCase):

    def test_mkNoise_Dims(self):
        freqs = np.arange(250,3010,10)
        sig = ts.mkNoise(freqs,0.5,48000)
        self.assertEqual(len(sig), 24000)
        if plots == "plots" or plots == "mkNoise":
            plt.plot(sig)
            plt.title('TEST: mkNoise')
            plt.show()


class Test_mkTone(unittest.TestCase):

    def test_mkTone_Dims(self):
        t, sig = ts.mkTone(500,1,0,48000)
        self.assertEqual(len(t), 48000)
        self.assertEqual(len(sig), 48000)

    def test_mkTone_Phase(self):
        # phase = 0 deg
        t, sig = ts.mkTone(500,0.01,0,48000)
        self.assertEqual(sig[0], 0)
        # phase = 90 deg
        t, sig = ts.mkTone(500,0.01,90,48000)
        self.assertEqual(sig[0], 1)
        if plots == "plots" or plots == "mkTone":
            plt.plot(sig)
            plt.title('TEST: mkTone, phi = 90 deg')
            plt.show()


class Test_phase2time(unittest.TestCase):

    def test_phase2time(self):
        self.assertEqual(ts.phase2time(500,90), 500)
        self.assertEqual(ts.phase2time(8000,72), 25)


class Test_rad2deg(unittest.TestCase):

    def test_rad2deg_Single_Value(self):
        self.assertEqual(ts.rad2deg(2*np.pi), 360)

    def test_rad2deg_Single_Negative_Value(self):
        self.assertEqual(ts.rad2deg(-np.pi), -180)

    def test_rad2deg_List_of_Mixed_Values(self):
        degs = ts.rad2deg([1, -(0.5*np.pi)])
        degs = [round(x,4) for x in degs]
        self.assertEqual(degs, [57.2958, -90])


class Test_rms(unittest.TestCase):

    def test_rms(self):
        sig = [0,1,2,3,2,1,0,-1,-2,-3,-2,-1,0]
        self.assertEqual(round(ts.rms(sig),4),1.7097)


class Test_setRMS(unittest.TestCase):

    def test_setRMS_1chan(self):
        [t, tone1] = ts.mkTone(200,0.1,30,48000)
        # Should be at 0.5 on the plot
        sig = ts.setRMS(tone1,-6)
        self.assertEqual(round(ts.mag2db(ts.rms(sig)),5), -6)
        self.assertEqual(len(sig), 0.1*48000)
        self.assertEqual(len(sig.shape), 1)
        if plots == "plots" or plots == "setRMS":
            plt.plot(sig)
            plt.title('TEST: setRMS, 1chan, -6 dB')
            plt.show()

    def test_setRMS_2chan_Equalized(self):
        [t, tone1] = ts.mkTone(200,0.05,30,48000)
        [t, tone2] = ts.mkTone(100,0.05,0,48000)
        tone2 = tone2 * ts.db2mag(-6)
        sig = np.array([tone1, tone2])
        if plots == "plots" or plots == "setRMS":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: setRMS, before correction')
            plt.show()
        adj = ts.setRMS(sig,-10,'y')
        self.assertEqual(len(adj.shape), 2) # Check for 2 channels
        self.assertEqual(len(adj[0]), 0.05*48000)
        self.assertEqual(len(adj[1]), 0.05*48000)
        # Check each channel is set to the same RMS
        self.assertEqual(round(ts.mag2db(ts.rms(adj[0])),5), -10)
        self.assertEqual(round(ts.mag2db(ts.rms(adj[1])),5), -10)
        if plots == "plots" or plots == "setRMS":
            plt.plot(adj[0],color='blue')
            plt.plot(adj[1],color='red')
            plt.title('TEST: setRMS, AFTER correction, with equalization')
            plt.show()

    def test_setRMS_2chan_Unequalized_L(self):
        sig = ts.mkITD(250,0.01,0,-2,0.005,48000)
        if plots == "plots" or plots == "setRMS":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: setRMS, before correction')
            plt.show()
        adj = ts.setRMS(sig,-10,'n')
        self.assertEqual(round(ts.mag2db(ts.rms(adj[0])),5), -9)
        self.assertEqual(round(ts.mag2db(ts.rms(adj[1])),5), -11)
        if plots == "plots" or plots == "setRMS":
            plt.plot(adj[0],color='blue')
            plt.plot(adj[1],color='red')
            plt.title('TEST: setRMS, AFTER correction, without equalization, ILD: -2')
            plt.show()

    def test_setRMS_2chan_Unequalized_R(self):
        sig = ts.mkITD(250,0.01,0,2,0.005,48000)
        if plots == "plots" or plots == "setRMS":
            plt.plot(sig[0],color='blue')
            plt.plot(sig[1],color='red')
            plt.title('TEST: setRMS, before correction')
            plt.show()
        adj = ts.setRMS(sig,0.5)
        self.assertEqual(round(ts.mag2db(ts.rms(adj[0])),5), -0.5)
        self.assertEqual(round(ts.mag2db(ts.rms(adj[1])),5), 1.5)
        if plots == "plots" or plots == "setRMS":
            plt.plot(adj[0],color='blue')
            plt.plot(adj[1],color='red')
            plt.title('TEST: setRMS, AFTER correction, without equalization, ILD: 2')
            plt.show()


class Test_specLvl(unittest.TestCase): 
    def test_specLvl(self):
        sig = ts.mkNoise(np.arange(2000,4001),0.1,48000)
        SPLnb = ts.specLvl(sig,4000,2000)
        self.assertTrue(ts.rms(sig) > ts.rms(SPLnb))


class Test_time2phase(unittest.TestCase):

    def test_time2phase(self):
        self.assertEqual(ts.time2phase(500,250), 45)
        self.assertEqual(ts.time2phase(8000,25), 72)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Assign REPL value to plots
        # Remove REPL value from sys.argv list to avoid
        # messing with the unittest.main() list
        plots = sys.argv.pop()
    elif len(sys.argv) == 1:
        plots = 0 # does nothing
    unittest.main()
