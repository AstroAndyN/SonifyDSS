# SonifyDSS
Generate sounds from Digitized Sky Survey data using "sonification" techniques.

# Outline
SonifyDSS is a python code that using sonification techniques to turn FITS data from the Digitized Sky Survey 2 collected from the NSAS SkyView system (https://skyview.gsfc.nasa.gov) into sounds. It is focussed on generating sounds for composition or exploring data and so is highly configurable.

It is command-line based system and requires a modicum of experience of python.

# The Sonification technique:
The sonfication technique maps from image brightness of a single pixel to volume of a particular frequency.

So, given a selection of image data from the DSS a line can be chosen across the image and all the pixels along that line allocated to different frequencies (with low frequency at one end, high frequency at the other). A sine wave at each frequency is generated with the amplitude determined by the brightness of the pixel and all the sine waves combined to produce a short sound.

The line can then be moved around the image data, producing a different pattern of pixels and hence a different sound. That is then appended to the previous sound and so on to create a sound of arbitrary length.

To generate stereo sounds, Red DSS2 survey data is used for the left channel and the Blue DSS2 data for the right.

## What the code does
The software enables:
* A particular piece of the sky to be downloaded from the DSS surveys.
* A line to be "swept" across the data in a particular direction (top-to-bottom, circularly etc).
* The sounds generated to be combined into a single audio file of chosen duration.

Optionally the code can also produce an image showing the DSS data and/or a movie showing the line "sweeping" over the image data (see the [Examples](/Examples))

# Usage
```
python sonify-dss.py [-h] [-d [{lr,rl,tb,bt,clk,aclk}]] [-s [SAMPLERATE]] [-lf [LOWFREQ]] [-hf [HIGHFREQ]] [-ff] [-ms]
                         [-siz [IMAGESIZE]] [-pic PICTURE] [-mov MOVIE] [-p]
                         object angsize outfile soundlen
```
The four compulsory command line arguments are:
* `object`: The name of the astronomical object of interest or a suitable celestial coordinate to centre the DSS data on. The format is as used in the SkyView interface - see https://skyview.gsfc.nasa.gov/current/help/fields.html#position
* `angsize`: The size on the sky of the data to sonify. This is given in arcminutes. Large areas (more than a few 10s of arcminutes) will take a long time to get from the DSS server.
* `outfile`: The output audio file. The software will try to generate sound in a format based on the file extension, but the most reliable will be ".avi".
* `soundlen`: The duration of the sound to be generated (in seconds).

The option parameters allow more detailed configuration:
* `-h / --help`: Display the usage "help"" and exit.
* `-d / --direction {lr,rl,tb,bt,clk,aclk}`: Determine the direction of the "sweep":
  * `lr`: Left to right (the default).
  * `rl`: Right to left.
  * `tb`: Top to bottom.
  * `bt`: Bottom to top.
  * `clk`: A clockwise circular sweep with the fixed point in the centre of the image data.
  * `aclk`: As above but anti-clockwise.
* `-s / --samplerate [samplerate]`: Set the same rate of the output audio file. Default is 44100Hz.
* `-lf / --lowfreq [lowfreq]`: Set the lower frequency limit for one end of the sweeping line. Default is 30Hz.
* `-hf / --highfreq [highreq]`: As above but for the high frequency end of the line. Default is 2000Hz.
* `-ff / --flipfreq` : Flip the order of frequencies along the sweep line.
* `-ms / --minsubtract`: Subtract the minimum value from each pixel row before generating sound. This may not have much effect for most realistic data but could reduce some background sounds.
* `-siz / --imagesize [imagesize]`: The size (in pixels) of the image to get from the DSS survey. Smaller sizes will be quicker to process but larger ones may give more subtle distinctions between frequencies. The default is 500 pixels which should be a suitable value for most uses.
* `-pic / --picture [picture file]`: Make an image of DSS data and store it in the given file. The file extension will give the file type (e.g. `.jpg` for  JPEG, `.png` for a PNG etc)
* `-mov / --movie [movie file]`: Make an movies of the line "sweeping" over DSS data and store it in the given file. The file extension will give the file type (e.g. `.mp4` for MPEG-4 etc)
* `-p / --play`: Play the sound when finished.

# Set up
The code makes use of a number of python libraries. Each should be installed using your local tools - usually `pip`.

## Python libraries
### Libraries for audio:
  sounddevice

  soundfile

### Library for creating the movie:
  moviepy

  Also the ffmpeg command line programme will be needed. See https://ffmpeg.org/

### Libraries for getting astronomical images and extracting data from them:
  astropy

  astropy.io

  astropy.coordinates

  astroquery.skyview

  matplotlib.pyplot

### Libraries for maths and data manipulation:
  numpy

  scipy

  math

  random

### Library for the command line:
  argparse

### Library for the progress bars:
  progressbar2

