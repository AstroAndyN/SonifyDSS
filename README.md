# SonifyDSS
Generate sounds from Digitized Sky Survey data using "sonification" techniques

# Outline
SonifyDSS is a python code that using sonification techniques to turn FITS data from the Digitized Sky Survey 2 collected from the NSAS SkyView system (https://skyview.gsfc.nasa.gov) into sounds. It is focussed on generating sounds for composition or exploring data and so is highly configurable.

It is command-line based system and requires a modicum of experience of python.

# The Sonification technique:
The sonfication technique maps from image brightness of a single pixel to volume of a particular frequency.

So, given a bit of image data from the DSS a line can be chosen across the image and all the pixels along that line allocated to different frequencies (with low frequency at one end, high frequency at the other). A sine wave at each frequency is generated with the amplitude determined by the brightness of the pixel and all the sine eaves combined to produce a short sound.

The line can then be moved around the image data, producing a different pattern of pixels and hence a different sound. That is then appended to the previous sound and so on to create a sound of arbitrary length.

To generate stereo sounds, Red DSS2 survey data is used for the left channel and the Blue DSS2 data for the right.

## What the code does
The software enables:
* A particular piece of the sky to be downloaded from the DSS surveys.
* A line to be "swept" across the data in a particular direction (top-to-bottom, circularly etc).
* The sounds generated to be combined into a single audio file of chosen duration.

Optionally the code can also produce an image showing the DSS data and/or a movie showing the line "sweeping" over the image data (see the [Examples](/Examples)

# Usage
```
python sonify-dss.py [-h] [-d [{lr,rl,tb,bt,clk,aclk}]] [-s [SAMPLERATE]] [-lf [LOWFREQ]] [-hf [HIGHFREQ]] [-ff] [-ms]
                         [-siz [IMAGESIZE]] [-pic PICTURE] [-mov MOVIE] [-p]
                         object angsize outfile soundlen
```
The four compulsory command line arguments are:
* `object`: The name of the astronomical object of interest or a suitable celestial coordinate to centre the DSS data on. The format is as used in the SkyView interface - see https://skyview.gsfc.nasa.gov/current/help/fields.html#position
* `angsize`: The size on the sky of the data to sonify. This is given in arcminutes. Large areas (more than a few 10s of arcminutes) will take a long time to get from the DSS server.
* `outfile`: The output audio file. The software will try to generate sound in a format based on the file extension, but the most reliable will be ".avi"
* `soundlen`: The duration of the sound to be generated (in seconds)

The option parameters allow more detailed