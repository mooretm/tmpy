""" Implementation of Allen and Berkley (1979) 'shoebox' 
    reverberation simulation.

    Written by: Allen and Berkley (1979)
    DOI: https://doi.org/10.1121/1.382599
    Adapted from Fortran by: Anonymous
    Further adaptations: Travis M. Moore
    Created: January 17, 2022
"""

###########
# Imports #
###########
# Third party
import matplotlib.pyplot as plt
import numpy as np

# Custom
import tmpy.dsp.tmsignals as ts


"""
I'm glad that I was able to save you some trouble. I don't actually work with Fortran 77 (that is the format of the original code; with punchcard-inspired layout) but I've seen it before and can read it without too much trouble.
As for attribution, you can put my full name (Matt Kabelitz) or a Github username (mattkab2) if you would prefer. I'm not too picky.

The next part is pretty easy, it's just a numeric integral and then some interpolation.
The first step is to compute the decay curve in dB (which doesn't need to specify a k value; since the reference of the decay is just the initial energy, it would cancels out anyway).
This is just performing a simple numeric integral, I did the midpoint rule but others are possible.

Then you just need to identify the time that the decay curve drops below some threshold, which is just an interpolation.
I do not know if you need the time after it has dropped 60 db (so the signal value is 40 db) or after it has dropped to 60 db, but whichever you want, just adjust the value in the provided function.

As the paper notes, if the sound has not sufficiently decayed this can lead to misleading results, since chopping the tail off of the decay curve alters the total energy in the system.
It is very important that any results using this method should compare with several values of increasing duration (dur) to ensure the drift of the cutoff time is sufficiently small.
"""

# Simualted Reverb with the Image Method #
def sroom2(r,r0,rL,beta,dur,fs):
    """ 
        Calculate a room impulse response from room parameters. 

            R: x,y,z coordinates of listener in feet
            R0: x,y,z coordinates of sound source in feet
            RL: room dimensions (length, width, height) in feet
            BETA: six absorption coefficients (between 0 and 1).
                Provide a 2x3 array:
                    array([[wall, wall, ceil]
                            [wall, wall, ceil]])
            DUR: duration of the reverb in ms
            FS: sampling rate in Hz; function converts to ms

            EXAMPLE: 
            # in feet
            headPos = np.array([3.75,12.5,5]) 
            srcPos = np.array([6.25,1.25,7.5])
            roomSize = np.array([10,15,12.5])

            wallRef = 0.9
            ceilRef = 0.7
            beta = np.zeros((2,3))
            beta[:,0:2] = wallRef
            beta[:,2] = ceilRef

            dur = 256 # duration in ms
            fs = 8000 # sampling rate in Hz

            ht = sroom2(headPos,srcPos,roomSize,beta,dur,fs)

        From: Allen and Berkley (1979)
            https://doi.org/10.1121/1.382599
        Implemented in Python by: ??
        Adapted by: Travis M. Moore
        Last edited: Jan. 17, 2022
    """
    # Perform unit conversions
    t = 1/fs # sampling rate from Hz to periods
    fs = (1/fs) * 1000 # sampling rate from Hz to ms
    c = 1 # speed of sound in ft/ms
    deltaR = c * fs
    # convert feet to sample periods
    r = np.array([x/deltaR for x in r],dtype=int)
    r0 = np.array([x/deltaR for x in r0],dtype=int)
    rL = np.array([x/deltaR for x in rL],dtype=int)

    #print("Room dimensions in sample periods:")
    #print(rL)

    # Define number of points of the RIR to calculate
    nPts = int(dur/fs)

    # Begin RIR function
    ht = np.zeros(nPts)
    d = np.sqrt(np.sum((r-r0)**2))
    if d < 0.5:
        ht[1] = 1
        return

    bnds = nPts//(2*rL) + 1
    for nx in range(-bnds[0],bnds[0]+1):
        for ny in range(-bnds[1],bnds[1]+1):
            for nz in range(-bnds[2],bnds[2]+1):
                delP = LTHImage2(r,r0,rL,(nx,ny,nz))
                #print(delP) # Needed for calculating reverb time?
                IO = 0
                for i in [0,1]:
                    for j in [0,1]:
                        for k in [0,1]:
                            ID = int(delP[IO]+0.5)
                            IO += 1
                            FDM1 = ID
                            if (ID>=nPts): continue
                            GID =     beta[0,0]**abs(nx-i)*beta[1,0]**abs(nx)
                            GID = GID*beta[0,1]**abs(ny-j)*beta[1,1]**abs(ny)
                            GID = GID*beta[0,2]**abs(nz-k)*beta[1,2]**abs(nz)/FDM1
                            ht[ID] += GID
    w = 8*np.arctan(1.0)*100
    #t = 1.0e-4 now a function parameter

    r1 = np.exp(-w*t)
    r2 = r1
    b1 = 2*r1*np.cos(w*t)
    b2 = -r1*r1
    a1 = -(1+r2)
    a2 = r2
    y1 = 0
    y2 = 0
    y0 = 0
    for i in range(nPts):
        x0 = ht[i]
        ht[i] = y0 + a1*y1+a2*y2
        y2 = y1
        y1 = y0
        y0 = b1*y1+b2*y2+x0
    return ht


def LTHImage2(dr,dr0,rl,nr):
    IO = 0
    ret = np.zeros(8)
    rp = np.zeros((3,8))
    r2l = np.zeros(3)
    for i in [-1,1]:
        for j in [-1,1]:
            for k in [-1,1]:
                rp[0,IO] = dr[0]+i*dr0[0]
                rp[1,IO] = dr[1]+j*dr0[1]
                rp[2,IO] = dr[2]+k*dr0[2]
                IO += 1
    r2l[0] = 2*rl[0]*nr[0]
    r2l[1] = 2*rl[1]*nr[1]
    r2l[2] = 2*rl[2]*nr[2]

    for i in range(8):
        ret[i] = np.sqrt(np.sum((r2l[:]-rp[:,i])**2))
    return ret


def htToDb(ht):
    ret = np.zeros(len(ht))
    for i in range(len(ret)):
        ret[i] = sum(ht[i:]**2)
    return 100+10*np.log10(ret/ret[0])


# Assumes equally spaced grid and monotonically decreasing db vals
def rt(grid,db,cutoff=-40):
    lo = np.argmax(db<cutoff)
    frac = (cutoff-db[lo])/(db[lo-1]-db[lo])
    return grid[lo-1] + (1-frac)*(grid[1]-grid[0])


################
# Apply Reverb #
################
def doReverb(sig,amp,r,r0,rL,beta,dur,fs):
    ht = sroom2(r,r0,rL,beta,dur,fs)
    
    try: # RT60 only works when reverb dur and sigdur are equal
        dec = htToDb(ht)
        sigdur = len(sig) / fs
        tbase = np.linspace(0,sigdur,int(len(sig)))
        rt60 = rt(tbase,dec,40)
        #plt.plot(tbase,dec)
        #plt.title("Decay Curve [dB]\n RT60: %.2f" % rt60)
        #plt.show()
    except: # the RIR is not equal to the signal duration
        pass

    revsig = np.convolve(sig,ht) # Convolve RIR with tone
    revsig = ts.setRMS(revsig,amp)
    return revsig


# def ft2smps(ft,T):
#     """ Change feet into sample lengths 
    
#             FT: length in feet
#             T: sampling rate in milliseconds. For example, 
#                 0.125 is a sampling rate of 8000 Hz in ms 
#                 ((1/8000) * 1000)

#             EXAMPLE: ft = ft2smps(10,0.125)

#         From: Allen and Berkley (1979)
#             https://doi.org/10.1121/1.382599
#         Implemented in Python by: ??
#         Adapted by: Travis M. Moore
#         Last edited: Jan. 14, 2022
#     """
#     c = 1 # speed of sound in ft/ms?
#     deltaR = c * T
#     try:
#         samplen = [x/deltaR for x in ft]
#     except:
#         samplen = ft/deltaR
#     return samplen


# def sroom(r,r0,rL,beta,nPts):
#     """ 
#         Calculate a room impulse response from room parameters. 
#         Dimensions are needed in sample periods: use ft2smps() 
#         for this conversion. 

#             R: vector radius to receiver in sample 
#                 periods. I.E., x,y,z coordinates of listener 
#                 in sample periods. 
#             R0: vector radius to sound source. I.E., x,y,z 
#                 coordinates of sound source in sample periods. 
#             RL: three room dimensions (length, width, height) 
#                 in sample periods. 
#             BETA: six absorption coefficients (between 0 and 1)
#             NPTS: number of points (samples) of the RIR to 
#                 calculate. Equal to the duration in ms divided 
#                 by the sampling rate in ms. 
#                 For example:
#                     fs = 10000 Hz = 0.0001 s = 0.1 ms
#                     dur = 256 ms
#                     nPts = int(dur/fs) = 2560

#             EXAMPLE: 
#             dur = 256 # in ms
#             fs = 0.1 # in ms
#             detPos = np.array([30.0,100.0,40.0])
#             srcPos = np.array([50.0,10.0,60.0])
#             roomSize = np.array([80,120,100])
            
#             wallRef = 0.9
#             ceilRef = 0.7
#             beta = np.zeros((2,3))
#             beta[:,0:2] = wallRef
#             beta[:,2] = ceilRef

#             ht = sroom(detPos,srcPos,roomSize,beta,int(dur/fs))

#         From: Allen and Berkley (1979)
#             https://doi.org/10.1121/1.382599
#         Implemented in Python by: ??
#         Adapted by: Travis M. Moore
#         Last edited: Jan. 17, 2022
#     """
#     ht = np.zeros(nPts)
#     d = np.sqrt(np.sum((r-r0)**2))
#     if d < 0.5:
#         ht[1] = 1
#         return

#     bnds = nPts//(2*rL) + 1
#     for nx in range(-bnds[0],bnds[0]+1):
#         for ny in range(-bnds[1],bnds[1]+1):
#             for nz in range(-bnds[2],bnds[2]+1):
#                 delP = LTHImage(r,r0,rL,(nx,ny,nz))
#                 #print(delP)
#                 IO = 0
#                 for i in [0,1]:
#                     for j in [0,1]:
#                         for k in [0,1]:
#                             ID = int(delP[IO]+0.5)
#                             IO += 1
#                             FDM1 = ID
#                             if (ID>=nPts): continue
#                             GID =     beta[0,0]**abs(nx-i)*beta[1,0]**abs(nx)
#                             GID = GID*beta[0,1]**abs(ny-j)*beta[1,1]**abs(ny)
#                             GID = GID*beta[0,2]**abs(nz-k)*beta[1,2]**abs(nz)/FDM1
#                             ht[ID] += GID
#     w = 8*np.arctan(1.0)*100
#     t = 1.0e-4

#     r1 = np.exp(-w*t)
#     r2 = r1
#     b1 = 2*r1*np.cos(w*t)
#     b2 = -r1*r1
#     a1 = -(1+r2)
#     a2 = r2
#     y1 = 0
#     y2 = 0
#     y0 = 0
#     for i in range(nPts):
#         x0 = ht[i]
#         ht[i] = y0 + a1*y1+a2*y2
#         y2 = y1
#         y1 = y0
#         y0 = b1*y1+b2*y2+x0
#     return ht


# def LTHImage(dr,dr0,rl,nr):
#     IO = 0
#     ret = np.zeros(8)
#     rp = np.zeros((3,8))
#     r2l = np.zeros(3)
#     for i in [-1,1]:
#         for j in [-1,1]:
#             for k in [-1,1]:
#                 rp[0,IO] = dr[0]+i*dr0[0]
#                 rp[1,IO] = dr[1]+j*dr0[1]
#                 rp[2,IO] = dr[2]+k*dr0[2]
#                 IO += 1
#     r2l[0] = 2*rl[0]*nr[0]
#     r2l[1] = 2*rl[1]*nr[1]
#     r2l[2] = 2*rl[2]*nr[2]

#     for i in range(8):
#         ret[i] = np.sqrt(np.sum((r2l[:]-rp[:,i])**2))
#     return ret
