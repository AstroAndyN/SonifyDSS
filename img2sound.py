"""
Img2Sound module
================

Functions to convert image data into sounds in various sweeps etc.

Andy Newsam 26/09/2026

"""

"""
Function list:
--------------

# Convert a row of values to a sound of a given frequency
def row2soundMono(row, freq, phs, sndpars):

# As above, but for stereo
def row2sound(rowL, rowR, freq, phs, sndpars):

# Loop around an image to create a radial sweep
def radialSweepMono(img, sndpars):

# As above, but stereo
def radialSweep(imgL, imgR, sndpars):

# Left-to-right sweep
def left2rightSweep(img, sndpars):

# As above, but stereo
def left2rightSweep(imgL, imgR, sndpars):

# Top-to-bottom sweep
def top2bottomSweep(img, sndpars):

# As above, but stereo
def top2bottomSweep(imgL, imgR, sndpars):

# Write the sound out to a WAV
def writeSoundMono(sound,sndpars):

# As above but stereo
def writeSound(soundL, soundR, sndpars):

# Play a sound
def playSound(soundL, soundR, sndpars):

"""

# Some required packages
# Sound and image IO
import sounddevice as sd
import soundfile as sf

import numpy as np
import math
from scipy import interpolate


import progressbar


# ======================================================================================================
# ==== Sound generation functions
# ---- Set up the basic sonifying functions

# Convert a row of values to a sound of a given frequency
def row2soundMono(row, freq, phs, sndpars):
    # The samples in the final sound in seconds
    times = np.arange(0,sndpars["soundLength"], 1.0/sndpars["sampleRate"])
    # Interpolate the row to the length of the sample
    numPts = row.shape[0]
    _x1 = np.arange(0,numPts)
    _f = interpolate.interp1d(_x1, row)
    _x2 = np.arange(0,numPts-1, (numPts-1)/sndpars["soundLenSam"])
    if(sndpars["flipDirn"]):
        _x2 = np.flip(_x2, axis=None)

    _amp = _f(_x2)
    if(sndpars["minSubtract"]):
        _amp = _amp - np.amin(_amp, axis=None)

    snd = _amp * np.sin(2*np.pi*freq*(times+phs))
    
    return snd

# As above, but for stereo
def row2sound(rowL, rowR, freq, phs, sndpars):
    # The samples in the final sound in seconds
    times = np.arange(0,sndpars["soundLength"], 1.0/sndpars["sampleRate"])
    # Interpolate the row to the length of the sample
    numPts = rowL.shape[0]
    _x1 = np.arange(0,numPts)
    _fL = interpolate.interp1d(_x1, rowL)
    _fR = interpolate.interp1d(_x1, rowR)
    _x2 = np.arange(0,numPts-1, (numPts-1)/sndpars["soundLenSam"])
    if(sndpars["flipDirn"]):
        _x2 = np.flip(_x2, axis=None)

    _ampL = _fL(_x2)
    _ampR = _fR(_x2)
    if(sndpars["minSubtract"]):
        _ampL = _ampL - np.amin(_ampL, axis=None)
        _ampR = _ampR - np.amin(_ampR, axis=None)
        
    _raw = np.sin(2*np.pi*freq*(times+phs))
    sndL = _ampL * _raw
    sndR = _ampR * _raw
    
    return sndL,sndR

# Loop around an image to create a radial sweep
def radialSweepMono(img, sndpars):
    

    # Middle of the image and radius that jsut meets the closest edge
    midpt = np.array([img.shape[0]/2, img.shape[1]/2])
    rad = math.floor(midpt[0]-1) if (midpt[0]<midpt[1]) else math.floor(midpt[1]-1)
    numSnds = rad
    numPts = math.ceil(2.0 * math.pi * rad)

    # We'll need some random phases to start with
    phs = np.random.rand(numSnds) * 2.0 * math.pi

    # The frequences of each row.
    freqs = sndpars["freqMinHz"] + (np.arange(0,numSnds) * (sndpars["freqMaxHz"]-sndpars["freqMinHz"])/numSnds)
    if(sndpars["flipFreq"]):
        freqs = np.flip(freqs, axis=None)

        # The final sound
    sound = np.zeros(sndpars["soundLenSam"], float)
    
        # A progress bar
    pb_widgets = ['Progress: ', 
                  progressbar.GranularBar(), "", 
                  progressbar.ETA()]
    pbar = progressbar.ProgressBar(max_value=numSnds, widgets=pb_widgets).start()
    for c in range(0,numSnds):
        r = (c+1)/numSnds * rad
        ring = np.empty(numPts)
        for a in range(0,numPts):
            ang = 2 * math.pi * a/numPts
            _x = round(midpt[0] + (r * math.sin(ang)))
            _y = round(midpt[1] + (r * math.cos(ang)))
            ring[a] = img[_x,_y]

        snd = row2soundMono(ring, freqs[c], phs[c], sndpars)

        sound += snd

        pbar.update(c)

    pbar.update(numSnds-1)

    return sound

# As above, but stereo
def radialSweep(imgL, imgR, sndpars):
    
    # Middle of the image and radius that jsut meets the closest edge
    midpt = np.array([imgL.shape[0]/2, imgL.shape[1]/2])
    rad = math.floor(midpt[0]-1) if (midpt[0]<midpt[1]) else math.floor(midpt[1]-1)
    numSnds = rad
    numPts = math.ceil(2.0 * math.pi * rad)

    # We'll need some random phases to start with
    phs = np.random.rand(numSnds) * 2.0 * math.pi

    # The frequences of each row.
    freqs = sndpars["freqMinHz"] + (np.arange(0,numSnds) * (sndpars["freqMaxHz"]-sndpars["freqMinHz"])/numSnds)
    if(sndpars["flipFreq"]):
        freqs = np.flip(freqs, axis=None)
        # The final sound
    soundL = np.zeros(sndpars["soundLenSam"], float)
    soundR = np.zeros(sndpars["soundLenSam"], float)

        # A progress bar
    pb_widgets = ['Progress: ', 
                  progressbar.GranularBar(), "", 
                  progressbar.ETA()]
    pbar = progressbar.ProgressBar(max_value=numSnds, widgets=pb_widgets).start()
    
    for c in range(0,numSnds):
        r = (c+1)/numSnds * rad
        ringL = np.empty(numPts)
        ringR = np.empty(numPts)
        for a in range(0,numPts):
            ang = 2 * math.pi * a/numPts
            _x = round(midpt[0] + (r * math.sin(ang)))
            _y = round(midpt[1] + (r * math.cos(ang)))
            ringL[a] = imgL[_x,_y]
            ringR[a] = imgR[_x,_y]


        sndL, sndR = row2sound(ringL, ringR, freqs[c], phs[c], sndpars)

        soundL += sndL
        soundR += sndR

        pbar.update(c)

    pbar.update(numSnds-1)
    return soundL, soundR


# Left-to-right sweep
def left2rightSweep(img, sndpars):
    
    numSnds = img.shape[0]
    numPts = img.shape[1]

    # We'll need some random phases to start with
    phs = np.random.rand(numSnds) * 2.0 * math.pi

    # The samples in the final sound in seconds
    times = np.arange(0,sndpars["soundLength"], 1.0/sndpars["sampleRate"])

    # The frequences of each row.
    freqs = sndpars["freqMinHz"] + (np.arange(0,numSnds) * (sndpars["freqMaxHz"]-sndpars["freqMinHz"])/numSnds)
    if(sndpars["flipFreq"]):
        freqs = np.flip(freqs, axis=None)
        
        # The final sound
    sound = np.zeros(sndpars["soundLenSam"], float)

        # A progress bar
    pb_widgets = ['Progress: ', 
                  progressbar.GranularBar(), "", 
                  progressbar.ETA()]
    pbar = progressbar.ProgressBar(max_value=numSnds, widgets=pb_widgets).start()

    for c in range(0,numSnds):

        # Interpolate the row of the image to the length of the sample

        row = img[c,:]
        
        snd = row2soundMono(row, freqs[c], phs[c], sndpars)

        sound += snd

        pbar.update(c)

    pbar.update(numSnds-1)
    return sound

# As above, but stereo
def left2rightSweep(imgL, imgR, sndpars):
    
    numSnds = imgL.shape[0]
    numPts = imgL.shape[1]

    # We'll need some random phases to start with
    phs = np.random.rand(numSnds) * 2.0 * math.pi

    # The samples in the final sound in seconds
    times = np.arange(0,sndpars["soundLength"], 1.0/sndpars["sampleRate"])

    # The frequences of each row.
    freqs = sndpars["freqMinHz"] + (np.arange(0,numSnds) * (sndpars["freqMaxHz"]-sndpars["freqMinHz"])/numSnds)
    if(sndpars["flipFreq"]):
        freqs = np.flip(freqs, axis=None)
        
        # The final sound
    soundL = np.zeros(sndpars["soundLenSam"], float)
    soundR = np.zeros(sndpars["soundLenSam"], float)

        # A progress bar
    pb_widgets = ['Progress: ', 
                  progressbar.GranularBar(), "", 
                  progressbar.ETA()]
    pbar = progressbar.ProgressBar(max_value=numSnds, widgets=pb_widgets).start()
    for c in range(0,numSnds):

        # Extract the right row
        rowL = imgL[c,:]
        rowR = imgR[c,:]
        
        sndL, sndR = row2sound(rowL, rowR, freqs[c], phs[c], sndpars)

        soundL += sndL
        soundR += sndR
    
        pbar.update(c)


    pbar.update(numSnds-1)
    return soundL, soundR

# Top-to-bottom sweep
def top2bottomSweep(img, sndpars):
    
    numSnds = img.shape[0]
    numPts = img.shape[1]

    # We'll need some random phases to start with
    phs = np.random.rand(numSnds) * 2.0 * math.pi

    # The samples in the final sound in seconds
    times = np.arange(0,sndpars["soundLength"], 1.0/sndpars["sampleRate"])

    # The frequences of each row.
    freqs = sndpars["freqMinHz"] + (np.arange(0,numSnds) * (sndpars["freqMaxHz"]-sndpars["freqMinHz"])/numSnds)
    if(sndpars["flipFreq"]):
        freqs = np.flip(freqs, axis=None)
        
        # The final sound
    sound = np.zeros(sndpars["soundLenSam"], float)

        # A progress bar
    pb_widgets = ['Progress: ', 
                  progressbar.GranularBar(), "", 
                  progressbar.ETA()]
    pbar = progressbar.ProgressBar(max_value=numSnds, widgets=pb_widgets).start()

    for c in range(0,numSnds):

        # Interpolate the row of the image to the length of the sample

        row = img[:,c]
        
        snd = row2soundMono(row, freqs[c], phs[c], sndpars)

        sound += snd
        pbar.update(c)

    pbar.update(numSnds-1)
    return sound

# As above, but stereo
def top2bottomSweep(imgL, imgR, sndpars):
    
    numSnds = imgL.shape[0]
    numPts = imgL.shape[1]

    # We'll need some random phases to start with
    phs = np.random.rand(numSnds) * 2.0 * math.pi

    # The samples in the final sound in seconds
    times = np.arange(0,sndpars["soundLength"], 1.0/sndpars["sampleRate"])

    # The frequences of each row.
    freqs = sndpars["freqMinHz"] + (np.arange(0,numSnds) * (sndpars["freqMaxHz"]-sndpars["freqMinHz"])/numSnds)
    if(sndpars["flipFreq"]):
        freqs = np.flip(freqs, axis=None)
        
        # The final sound
    soundL = np.zeros(sndpars["soundLenSam"], float)
    soundR = np.zeros(sndpars["soundLenSam"], float)

        # A progress bar
    pb_widgets = ['Progress: ', 
                  progressbar.GranularBar(), "", 
                  progressbar.ETA()]
    pbar = progressbar.ProgressBar(max_value=numSnds, widgets=pb_widgets).start()

    for c in range(0,numSnds):

        # Extract the right row
        rowL = imgL[:,c]
        rowR = imgR[:,c]
        
        sndL, sndR = row2sound(rowL, rowR, freqs[c], phs[c], sndpars)

        soundL += sndL
        soundR += sndR
        pbar.update(c)

    pbar.update(numSnds-1)
    return soundL, soundR

# Write the sound out to a WAV

def writeSoundMono(sound,sndpars):
    
    # Normalise the sound to signed 16 bit range
    _max = np.amax(np.absolute(sound,axis=None))
    _max16bit = 2**15

    soundInt = ((_max16bit/_max) * sound).astype(np.int16)

    sf.write(sndpars["filename"], soundInt, sndpars["sampleRate"])

    # As above but stereo
def writeSound(soundL, soundR, sndpars):
    
    # Normalise the sound to signed 16 bit range
    _max = np.amax(np.absolute(np.concatenate((soundL,soundR),axis=None)))
    _max16bit = 2**15

    soundLint = ((_max16bit/_max) * soundL).astype(np.int16)
    soundRint = ((_max16bit/_max) * soundR).astype(np.int16)

    soundInt = np.column_stack((soundLint, soundRint))

    sf.write(sndpars["filename"], soundInt, sndpars["sampleRate"])
    
def playSound(soundL, soundR, sndpars):
    
    # Normalise the sound to signed 16 bit range
    _max = np.amax(np.absolute(np.concatenate((soundL,soundR),axis=None)))
    _max16bit = 2**14

    soundLint = ((_max16bit/_max) * soundL).astype(np.int16)
    soundRint = ((_max16bit/_max) * soundR).astype(np.int16)

    soundInt = np.column_stack((soundLint, soundRint))
    sd.play(soundInt, sndpars["sampleRate"])
    status = sd.wait()  # Wait until file is done playing

