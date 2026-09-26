"""
DSS Data module
===============

Function to get DSS image data.

Andy Newsam 26/09/2026

"""

"""

Function list:
--------------

Function for getting the DSS data
def getDSSdata(objcoo, angsize, imgpars):

Function to make RGB from DSS data
def DSS2RGB(imgL, imgR):

"""


# Astroquery the DSS database
from astropy import units as u
from astropy.io import fits
from astroquery.skyview import SkyView
from astropy.coordinates import SkyCoord

import numpy as np
import math



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