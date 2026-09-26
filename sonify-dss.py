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

import img2sound as i2s
import dssdata as dss
import picmovie as picmov


# General useful python stuff
import numpy as np
import argparse
import sys






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
imgL,imgR = dss.getDSSdata(ObjectName, args.angsize, imageParameters)

# Make RGB data (not always needed but will be for "pic" or "movie" so worth putting together quickly)
imgRGB = dss.DSS2RGB(imgL, imgR)

if args.picture:
    print("Making images of the DSS data. See "+args.picture[0])
    picmov.makePictureRB(imgL, imgR, imgRGB, args.picture[0], "DSS2")
    
# ==== Create the actual sound

print("Creating sound")
soundParameters["sweepDirn"] = SweepDirn
if SweepDirn == "LR":
    # Sweep left-to-right (or reverse)
    soundL, soundR = i2s.left2rightSweep(imgL, imgR, soundParameters)
elif SweepDirn == "TB":
    # Sweep to-to-bottom (or reverse)
    soundL, soundR = i2s.top2bottomSweep(imgL, imgR, soundParameters)
elif SweepDirn == "RAD":
    # Sweep radial line around clockwise (or reverse)
    soundL, soundR = i2s.radialSweep(imgL, imgR, soundParameters)


print("\nWriting sound to "+args.outfile)
i2s.writeSound(soundL, soundR, soundParameters)

if args.movie:
    print('Making "sweep" movie of the DSS data. See '+args.movie[0])
    picmov.makeMovie(imgRGB, soundParameters, args.movie[0], args.outfile)

if args.play:
    print("Playing sound")
    i2s.playSound(soundL, soundR, soundParameters)


print("Finished")



