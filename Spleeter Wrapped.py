from __future__ import unicode_literals

import sys
import youtube_dl
from youtubesearchpython import VideosSearch
import warnings
import shutil
import subprocess
import os
from tempfile import gettempdir
from os.path import exists, join
import tkinter
from tkinter import filedialog
from tkinter import *
from spleeter import SpleeterError
from spleeter.commands import create_argument_parser
from spleeter.utils.configuration import load_configuration
from spleeter.utils.logging import (
    enable_logging,
    enable_tensorflow_logging,
    get_logger)

__email__ = 'research@deezer.com'
__author__ = 'Deezer Research'
__license__ = 'MIT License'


def main():
    # Figure out where we are
    working = str((os.getcwdb()))
    try:
        os.system("color 0D")
        os.system("title Spleeter GUI by Dozza")
        print("""  
         ██████  ██▓███   ██▓    ▓█████ ▓█████▄▄▄█████▓▓█████  ██▀███  
        ▒██    ▒ ▓██░  ██▒▓██▒    ▓█   ▀ ▓█   ▀▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒
        ░ ▓██▄   ▓██░ ██▓▒▒██░    ▒███   ▒███  ▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒
          ▒   ██▒▒██▄█▓▒ ▒▒██░    ▒▓█  ▄ ▒▓█  ▄░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄  
        ▒██████▒▒▒██▒ ░  ░░██████▒░▒████▒░▒████▒ ▒██▒ ░ ░▒████▒░██▓ ▒██▒
        ▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░░ ▒░▓  ░░░ ▒░ ░░░ ▒░ ░ ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░
        ░ ░▒  ░ ░░▒ ░     ░ ░ ▒  ░ ░ ░  ░ ░ ░  ░   ░     ░ ░  ░  ░▒ ░ ▒░
        ░  ░  ░  ░░         ░ ░      ░      ░    ░         ░     ░░   ░ 
              ░               ░  ░   ░  ░   ░  ░           ░  ░   ░ 
        GUI by Dozza""")
        # Leave this code here cos it gives us a nice default argument to then parse shit into
        mode = ""
        while mode not in ["1", "2"]:
            mode = input("Which mode would you like?\n"
                         "1. Spleeter from MP3 file\n"
                         "2. Search youtube and download mp3 from top 10 list.")
        if mode == "1":  # Spleeter from mp3 mode.
            # make a TK instance and minimise it, ask for a file name to return to spleeter, then exit.
            root = Tk()
            root.withdraw()
            filename = filedialog.askopenfilename(initialdir=os.environ["HOMEPATH"] + "/Desktop",
                                                  title="Select file",
                                                  filetypes=(("mp3 audio", ".mp3"), ("all files", ".*")))
            root.destroy()

        if mode == "2":
            # input the search term for VideosSearch, store the top 10 results by name and Url
            searchterm = input("Enter search term:")
            videosearch = VideosSearch(searchterm, limit=10)
            searchnames = []
            searchoptions = []  # empty list for URLs.

            #escape the weird dictionary object we get as a result
            results = videosearch.result()["result"]

            #parse the results of the search into useful parameters.
            for index,x in enumerate(results):
                print(f"Result {index}: {x['title']}, {x['link']}")
                searchoptions.append(x["link"])
                searchnames.append((x["title"] + "-" + x["id"]).replace("/", "_"))

            # choose which result to go forward with.
            notpicked = True
            while (notpicked):
                picked = input("Which option would you like to pick?\n")
                if 0 <= int(picked) < 10:
                    notpicked = False
            link = searchoptions[int(picked)]

            # setup for youtube downloader. we can use high quality here since it is volatile and spleeter
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            # the mp3 should be present in the working directory now.
            # rename the mp3 to the searchterm  (which is 100% of the time a shorter and safer sequence of characters guaranteed!
            os.rename(searchnames[int(picked)] + ".mp3", searchterm + ".mp3")
            filename = os.getcwd() + "/" + searchterm + ".mp3"
        #
        print(filename)
        if filename is "":
            # avoid errors when quitting the spleeter GUI
            sys.exit(0)
        [head, tail] = os.path.split(filename)
        arguments = create_argument_parser().parse_args(
            ['separate', '-i', filename, '-o', 'audio_output', '-p', 'spleeter:5stems-16kHz'])
        # ok so now we add our own spicy c-c-custom code.
        arguments.codec = tail.split(".")[1]
        # arguments.command = 'separate'
        # arguments.configuration = 'spleeter:5stems-16kHz'
        # arguments.duration = 600
        arguments.bitrate = '256k'
        arguments.filename_format = '{filename}/{instrument}.{codec}'
        # arguments.offset = 0.0
        # arguments.output_path = 'audio_output'
        arguments.verbose = False
        # print(f"Loaded {tail} from {head}")
        # print("Processing...", end='')
        enable_logging()
        if arguments.verbose:
            enable_tensorflow_logging()
        if arguments.command == 'separate':
            from spleeter.commands.separate import entrypoint
        params = load_configuration(arguments.configuration)
        entrypoint(arguments, params)

        #remove the downloaded mp3 afterwards
        if mode == "2":
            os.remove(filename)

        #pop open the output folder
        outputdir = '"' + working[2:-1] + '\\' + arguments.output_path + '\\' + tail[0:-4] + '\\' + '"'
        os.startfile(outputdir)

    except SpleeterError as e:
        get_logger().error(e)


def entrypoint():
    """ Command line entrypoint. """
    warnings.filterwarnings('ignore')
    main()


if __name__ == '__main__':
    entrypoint()
