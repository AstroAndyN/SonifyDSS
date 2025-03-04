"""
Given an astronomical object name or coordinate and a field-of-view (in arcmin), this downloads the DSS2 Red and Blue images and converts them into sound in one of three ways (or their reverse): left-to-right sweep, top-to-bottom sweep, clockwise sweep

The DSS2 Red is allocate to the left stereo channel, the DSS2 Blue allocated to the right.

Andy Newsam 01/03/2025
"""

"""
Usage:
    python sonify-dss.py [-h] [-d [{lr,rl,tb,bt,clk,aclk}]] [-s [SAMPLERATE]] [-lf [LOWFREQ]] [-hf [HIGHFREQ]] [-ff] [-ms]
                         [-siz [IMAGESIZE]] [-pic PICTURE] [-mov MOVIE] [-p]
                         object angsize outfile soundlen

    positional arguments:
    object                The astronomical object name or coordinates
    angsize               The angular size (in arcminutes)
    outfile               The output WAV file
    soundlen              The duration of the sound (in seconds)

    optional arguments:
    -h, --help            show this help message and exit
    -d [{lr,rl,tb,bt,clk,aclk}], --direction [{lr,rl,tb,bt,clk,aclk}]
                            The "sweep" direction: Left-to-right, Right-to-left, Top-to-bottom, Bottom-to-top, Clockwise, Anticlockwise (default: lr)
    -s [SAMPLERATE], --samplerate [SAMPLERATE]
                            The sample rate (in Hz) (default: 44100)
    -lf [LOWFREQ], --lowfreq [LOWFREQ]
                            The low frequency limit (in Hz) (default: 30)
    -hf [HIGHFREQ], --highfreq [HIGHFREQ]
                            The high frequency limit (in Hz) (default: 2000)
    -ff, --flipfreq       Flip the frequency range order (default: False)
    -ms, --minsubtract    Subtract the lowest value from each pixel row (default: False)
    -siz [IMAGESIZE], --imagesize [IMAGESIZE]
                            The DSS image size in pixels (default: 1024)
    -pic PICTURE, --picture PICTURE
                            Make an image of DSS data and store it in the given file (default: None)
    -mov MOVIE, --movie MOVIE
                            Make a movie of the "sweep" and store it in the given file (default: None)
    -p, --play            Play the sound when finished (default: False)

"""
"""
Requirements:

Python libraries:

* For audio:
  sounddevice
  soundfile

* For creating the movie
  moviepy

  Also ffmpeg command line programme

* For getting astronomical images and extracting data from them:
  astropy
  astropy.io
  astropy.coordinates
  astroquery.skyview

  matplotlib.pyplot

* Maths and data manipulation:
  numpy
  scipy
  math
  random

* For the command line
  argparse

* For the progress bars:
  progressbar2
"""


# ======================================================================================================
# ==== Import everything needed
# Sound and image IO
import sounddevice as sd
import soundfile as sf

# Astroquery the DSS database
from astropy import units as u
from astropy.io import fits
from astroquery.skyview import SkyView
from astropy.coordinates import SkyCoord

# Making the picture and movie
import matplotlib.pyplot as plt
# Making the movie
import matplotlib.animation as animation
from moviepy import *

# General useful python stuff
import numpy as np
from scipy import interpolate
import math
import random
import progressbar

import argparse

import sys
import os

# ======================================================================================================
# ==== Sound generation functions
# ---- Set up the basic sonifying functions

# Convert a row of values to a sound of a given frequency
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

# As above, but for stereo
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

# Loop around an image to create a radial sweep
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

        snd = row2soundMono(ring, freqs[c], phs[c], soundParameters)

        sound += snd

        pbar.update(c)

    pbar.update(numSnds-1)

    return sound

# As above, but stereo
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


        sndL, sndR = row2sound(ringL, ringR, freqs[c], phs[c], soundParameters)

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
        
        snd = row2soundMono(row, freqs[c], phs[c], soundParameters)

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
        
        sndL, sndR = row2sound(rowL, rowR, freqs[c], phs[c], soundParameters)

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
        
        snd = row2soundMono(row, freqs[c], phs[c], soundParameters)

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
        
        sndL, sndR = row2sound(rowL, rowR, freqs[c], phs[c], soundParameters)

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

    # As above but stereo
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


# ======================================================================================================
# ==== Function for getting the DSS data

def getDSSdata(objcoo, angsize, imgpars):
    
    sv = SkyView()
    surv = ['DSS2 Red']
    if(imgpars["RB2Stereo"]):
        surv = ['DSS2 Red','DSS2 Blue']
    scl = None
    if(imgpars["scaling"] != "Default"):
        scl = imgpars["scaling"]
    # For other options, see https://astroquery.readthedocs.io/en/latest/api/astroquery.skyview.SkyViewClass.html#astroquery.skyview.SkyViewClass.get_images
    imgs = sv.get_images(position=objcoo, survey=surv, scaling=scl,
                         coordinates='J2000', pixels=imgpars["pixelSize"], radius=(angsize/2.0 * u.arcmin))
    dataRed = imgs[0][0].data
    if(imgpars["RB2Stereo"]):
        dataBlue = imgs[1][0].data
    

    # Median subtract?
    if(imgpars["medianSubtract"]):
        _tmp = (dataRed - np.median(dataRed)).clip(0.0)
        dataRed = _tmp
        if(imgpars["RB2Stereo"]):
            _tmp = (dataBlue - np.median(dataBlue)).clip(0.0)
            dataBlue = _tmp
            
    if(imgpars["RB2Stereo"]):
        return dataRed,dataBlue
    else:
        return dataRed

# ==== Function to make RGB from DSS data
def DSS2RGB(imgL, imgR):

    # RGB:
    #   * R and B are SQRT scaled from the respective FITs data
    #   * G is the average of R and B
    _i = np.sqrt((imgL - (np.min(imgL))))
    _r = _i / np.max(_i)
    _i = np.sqrt((imgR - (np.min(imgR))))
    _b = _i / np.max(_i)
    _g = 0.5 * (_r + _b)

    return np.dstack((_r, _g, _b))

# ---- Make a picture of the two DSS images and a colour version
def makePicture(imgL, imgR, imgRGB, picfil):

    f, axarr = plt.subplots(1,3,figsize=(15,5))
    axarr[0].imshow(imgL,origin='upper',interpolation='none',cmap='Reds_r')
    axarr[0].set_title('DSS2 Red: Left channel')
    axarr[1].imshow(imgRGB)
    axarr[1].set_title('DSS2 Red+Blue colour')
    axarr[2].imshow(imgR,origin='upper',interpolation='none',cmap='Blues_r')
    axarr[2].set_title('DSS2 Blue: Right channel')

    plt.savefig(picfil, bbox_inches='tight')
    plt.close(f)

# --- Make a movie showing the "sweep" over the DSS colour image.
def makeMovie(imgRGB, sndpars, movfil, sndfil):

    # Movie setup
    fps = 24
    numsec = sndpars["soundLength"]
    numfrms = int(fps * numsec)
    dirn = sndpars["sweepDirn"]
    flip = sndpars["flipDirn"]

    # Make the basic figure with RGB image
    fig = plt.figure( figsize=(8,8) )
    ax = fig.add_subplot()
    im = ax.imshow(imgRGB)

    # Progress bar
    pb_widgets = ['Progress: ', 
                  progressbar.GranularBar(), "", 
                  progressbar.ETA()]
    pbar = progressbar.ProgressBar(max_value=numfrms, widgets=pb_widgets).start()


    def animateMov(i):

        # Remove any existing lines
        for ln in list(ax.lines):
            ln.remove()

        # Draw a line for the current "sweep" position
        x = []
        y = []
        if dirn == "LR":
            # Sweep left-to-right (or reverse)
            _x = imgRGB.shape[0] * (i/numfrms)
            if(flip):
                _x = (imgRGB.shape[0]-1) - _x
            x = [_x, _x]
            y = [1, imgRGB.shape[1]-1]
        elif dirn == "TB":
            # Sweep to-to-bottom (or reverse)
            x = [1, imgRGB.shape[0]-1]
            _y = imgRGB.shape[1] * (i/numfrms)
            if(flip):
                _y = (imgRGB.shape[1]-1) - _y
            y = [_y, _y]
        elif dirn == "RAD":
            # Sweep in a circle
            _x1 = imgRGB.shape[0]/2
            _y1 = imgRGB.shape[1]/2
            rad = math.floor(_x1-1) if (_x1<_y1) else math.floor(_y1-1)
            ang = 2 * math.pi * i/numfrms
            if(flip):
                ang = (2 * math.pi) - ang
            _x2 = round(_x1 + (rad * math.cos(ang)))
            _y2 = round(_y1 + (rad * math.sin(ang)))

            x = [_x1, _x2]
            y = [_y1, _y2]

        # Draw a faint background "highlight" line that fades out
        ax.plot(x, y, color='#fff1', linewidth=6)
        ax.plot(x, y, color='#fff1', linewidth=4)

        # Draw a line of green gradient to mark the higher (pale green) and lower (dark green)

        _n = int(imgRGB.shape[0] / 4) if imgRGB.shape[0] < 128 else 32
        _x = np.linspace(x[0], x[1], _n)
        _y = np.linspace(y[0], y[1], _n)
          # Don't use the full range of greens, just the middle bit (to avoid near-white and near-black)
        _cols = plt.colormaps['Greens'](np.linspace(0.3, 0.8, _n))
        for j in range(_n - 1):
            if(sndpars['flipFreq']):
                _c = _cols[j]
            else:
                _c = _cols[(_n-2)-j]
            plt.plot([_x[j], _x[j+1]], [_y[j], _y[j+1]], color=_c, linewidth=2)
        #ax.plot(x, y, color='green', linewidth=2)

        pbar.update(i)

    anim = animation.FuncAnimation(
                               fig, 
                               animateMov, 
                               frames = numfrms,
                               interval = 1000 / fps, # in ms
                               )
    
    # Write to a temporary file
    _mov = "__" + str(random.randint(100000, 999999)) + "_" + movfil
    anim.save(_mov, fps=fps, dpi=100, extra_args=['-vcodec', 'libx264'])

    pbar.update(numfrms-1)
    print("\n  Combining video and audio")

    video_clip = VideoFileClip(_mov)
    audio_clip = AudioFileClip(sndfil)

    video_clip.audio = audio_clip
    video_clip.write_videofile(movfil, codec='libx264', audio_codec='aac', logger=None)

    video_clip.close()
    audio_clip.close()

    # Get rid of the temporary file
    os.remove(_mov)





# ======================================================================================================
# ==== Parse the command line ====

parser = argparse.ArgumentParser(description='Sonify DSS images.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('object', help='The astronomical object name or coordinates')
parser.add_argument('angsize', type=float, help='The angular size (in arcminutes)')
parser.add_argument('outfile', help='The output WAV file')
parser.add_argument('soundlen', type=float, help='The duration of the sound (in seconds)')
parser.add_argument('-d', '--direction', nargs='?', type=str.lower, default='lr', choices=['lr','rl','tb','bt','clk','aclk'], help='The "sweep" direction: Left-to-right, Right-to-left, Top-to-bottom, Bottom-to-top, Clockwise, Anticlockwise')
parser.add_argument('-s', '--samplerate', nargs='?', type=int, default=44100, help='The sample rate (in Hz)')
parser.add_argument('-lf', '--lowfreq', nargs='?', type=float, default=30, help='The low frequency limit (in Hz)')
parser.add_argument('-hf', '--highfreq', nargs='?', type=float, default=2000, help='The high frequency limit (in Hz)')
parser.add_argument('-ff', '--flipfreq', action='store_true', help='Flip the frequency range order')
parser.add_argument('-ms', '--minsubtract', action='store_true', help='Subtract the lowest value from each pixel row')
parser.add_argument('-siz', '--imagesize', nargs='?', type=int, default=500, help='The DSS image size in pixels')

parser.add_argument('-pic', '--picture', nargs=1, help='Make an image of DSS data and store it in the given file')
parser.add_argument('-mov', '--movie', nargs=1, help='Make a movie of the "sweep" and store it in the given file')

parser.add_argument('-p', '--play', action='store_true', help='Play the sound when finished')

args=parser.parse_args()


if args.lowfreq >= args.highfreq:
    sys.exit('The low frequency limit must be less than the high frequency limit')

ObjectName = args.object

# ==== Define DSS image processing parameters in a dictionary
imageParameters = {
    "pixelSize": args.imagesize,
    "RB2Stereo": True,
    "medianSubtract": True,
    "scaling": "Default"  # ++TODO++ Does nothing yet
}


# ==== Determine the direction of the "sweep"
_s = args.direction
sdirn = _s.upper()
if sdirn == 'LR':
    SweepDirn = "LR"
    SweepFlip = False
elif sdirn == "RL":
    SweepDirn = "LR"
    SweepFlip = True
elif sdirn == "TB":
    SweepDirn = "TB"
    SweepFlip = False
elif sdirn == "BT":
    SweepDirn = "TB"
    SweepFlip = True
elif sdirn == "CLK":
    SweepDirn = "RAD"
    SweepFlip = False
elif sdirn == "ACLK":
    SweepDirn = "RAD"
    SweepFlip = True
else:
    sys.exit('Unknown direction for the "sweep": '+args.direction)


# ==== Define the parameters of the sounds in a dictionary


soundParameters = {
    "filename": args.outfile,
    "sampleRate": args.samplerate,
    "soundLength": args.soundlen,
    "freqMinHz": args.lowfreq,
    "freqMaxHz": args.highfreq,
    "flipFreq": args.flipfreq,  # Reverse the order of frequencies
    "flipDirn": SweepFlip,  # Reverse the direction of the sweep
    "minSubtract": args.minsubtract # Subtract the minimum from each amplification row
}
soundParameters["soundLenSam"] = int(soundParameters["sampleRate"] * soundParameters["soundLength"])



# ==== Load an image

print("Loading DSS data for "+ObjectName)
imgL,imgR = getDSSdata(ObjectName, args.angsize, imageParameters)

# Make RGB data (not always needed but will be for "pic" or "movie" so worth putting together quickly)
imgRGB = DSS2RGB(imgL, imgR)

if args.picture:
    print("Making images of the DSS data. See "+args.picture[0])
    makePicture(imgL, imgR, imgRGB, args.picture[0])
    
# ==== Create the actual sound

print("Creating sound")
soundParameters["sweepDirn"] = SweepDirn
if SweepDirn == "LR":
    # Sweep left-to-right (or reverse)
    soundL, soundR = left2rightSweep(imgL, imgR, soundParameters)
elif SweepDirn == "TB":
    # Sweep to-to-bottom (or reverse)
    soundL, soundR = top2bottomSweep(imgL, imgR, soundParameters)
elif SweepDirn == "RAD":
    # Sweep radial line around clockwise (or reverse)
    soundL, soundR = radialSweep(imgL, imgR, soundParameters)


print("\nWriting sound to "+args.outfile)
writeSound(soundL, soundR, soundParameters)

if args.movie:
    print('Making "sweep" movie of the DSS data. See '+args.movie[0])
    makeMovie(imgRGB, soundParameters, args.movie[0], args.outfile)

if args.play:
    print("Playing sound")
    playSound(soundL, soundR, soundParameters)


print("Finished")



