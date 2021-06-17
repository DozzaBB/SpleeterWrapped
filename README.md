# SpleeterWrapped
wrapped nicer version of spleeter with youtube-dl included for speedy filing.


acquire via: 

* pipe client from https://github.com/audacity/audacity/edit/master/scripts/piped-work/pipeclient.py
* conda create -n py37 python=3.7
* clone this repo into your conda env
* conda install -c conda-forge spleeter
* pip install youtube-dl
* pip install youtube-search-python
* install FFmpeg binary https://lame.buanzo.org/#lamewindl

This program should automagically install the spleeter 5stems:16khz model on first run, but if you cant get it to work, try downloading it from an external source or running spleeter from the base source to install the model.

its obviously quite hacked together from spleeter and my basic knowledge of Tkinter python.
