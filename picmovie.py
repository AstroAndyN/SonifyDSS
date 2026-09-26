"""
Picture and Movie module
========================

Functions to make pictures and movies for inptu data and sound sweeps.

Andy Newsam 26/09/2026

"""

"""
Function list:
--------------

Make a picture of the two Red/Blue images and a colour version
def makePictureRB(imgL, imgR, imgRGB, picfil):

Make a movie showing the "sweep" over the colour image.
def makeMovie(imgRGB, sndpars, movfil, sndfil):

"""

# Making the picture and movie
import matplotlib.pyplot as plt
# Making the movie
import matplotlib.animation as animation
from moviepy import *

# General useful python stuff
import numpy as np
import math
import random
import progressbar
import os


# ---- Make a picture of the two images in Red and Blue and an RGB version
def makePictureRB(imgL, imgR, imgRGB, picfil, caption=""):

    _c = ""
    if len(caption) != 0:
        _c = caption + " "
    f, axarr = plt.subplots(1,3,figsize=(15,5))
    axarr[0].imshow(imgL,origin='upper',interpolation='none',cmap='Reds_r')
    axarr[0].set_title(_c + 'Red: Left channel')
    axarr[1].imshow(imgRGB)
    axarr[1].set_title(_c + 'Red+Blue colour')
    axarr[2].imshow(imgR,origin='upper',interpolation='none',cmap='Blues_r')
    axarr[2].set_title(_c + 'Blue: Right channel')

    plt.savefig(picfil, bbox_inches='tight')
    plt.close(f)

# --- Make a movie showing the "sweep" over the RGB colour image.
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
    _movfn, _movext = os.path.splitext(movfil)

    _mov = _movfn + "__" + str(random.randint(100000, 999999)) + "_" + _movext
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


