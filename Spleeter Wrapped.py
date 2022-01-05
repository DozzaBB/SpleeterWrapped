from __future__ import unicode_literals

import logging
logging.basicConfig(level=logging.DEBUG)


import sys
import time
import youtube_dl
from youtubesearchpython import VideosSearch
import warnings
import os
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

AUDACITY_PATH = "C:\\Program Files (x86)\\Audacity\\audacity.exe"

def main():
    # Figure out where we are
    working = str((os.getcwdb()))
    try:
        os.system("title Spleeter GUI by Dozza")
        logging.info("""  
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
            mode = input("\nWhich mode would you like?\n"
                         "    1. Spleeter from MP3 file\n"
                         "    2. Search youtube and download mp3 from top 10 list.")
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
            search = VideosSearch(searchterm, limit=10).result()["result"]
            results = []
            # Unpack the videosearch generator.
            for i,x in enumerate(search):
                results.append(x)

            #parse the results of the search into useful parameters.
            for index, result in enumerate(results):
                print(f"    Result {index}: {result['title']}, {result['duration']}")


            # Choose a result.
            while True:
                selected_option = input("Which option would you like to pick?\n")
                if  0 <= int(selected_option) < 10:
                    break

            selected_result = results[int(selected_option)]

            # setup for youtube downloader. we can use high quality here since it is volatile and spleeter
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'verbose': True,
                'outtmpl': '%(title)s.%(ext)s'
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                downloaded_filename = ydl.prepare_filename(selected_result)[:-3] + '.mp3'
                logging.info(f"Saving file as {downloaded_filename}")
                ydl.download([selected_result['link']])
            # the mp3 should be present in the working directory now.
            # get the filename 

            filename = os.path.join(os.getcwd(),downloaded_filename)
            if not os.path.isfile(filename):
                root = Tk()
                root.withdraw()
                filename = filedialog.askopenfilename(initialdir=os.cwd(),
                                                    title="Select file",
                                                    filetypes=(("supporter audio", ".mp3 .wav "), ("all files", ".*")))
                root.destroy()
        #
        logging.debug(f"Output full path: {filename}")
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
        arguments.verbose = True
        logging.debug(f"Loaded {tail} from {head}")
        logging.debug("Processing...")
        enable_logging()
        if arguments.verbose:
            enable_tensorflow_logging()
        if arguments.command == 'separate':
            from spleeter.commands.separate import entrypoint
        params = load_configuration(arguments.configuration)
        logging.info("Spleeting...")
        entrypoint(arguments, params)
        logging.info("Done!")

        #remove the downloaded mp3 afterwards
        if mode == "2":
            os.remove(filename)

        #pop open the output folder
        outputdir = '"' + working[2:-1] + '\\' + arguments.output_path + '\\' + tail[0:-4] + '\\' + '"'
        os.startfile(outputdir)

        # audacity time
        os.startfile(AUDACITY_PATH)
        if sys.platform == 'win32':
            logging.debug("pipe-test.py, running on windows")
            TONAME = '\\\\.\\pipe\\ToSrvPipe'
            FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
            EOL = '\r\n\0'
        else:
            logging.debug("pipe-test.py, running on linux or mac")
            TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
            FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
            EOL = '\n'

        logging.debug("Write to  \"" + TONAME +"\"")
        while not os.path.exists(TONAME):
            logging.error(" ..does not exist.  Ensure Audacity is running with mod-script-pipe.")
            time.sleep(1)


        logging.debug("Read from \"" + FROMNAME +"\"")
        while not os.path.exists(FROMNAME):
            logging.error(" ..does not exist.  Ensure Audacity is running with mod-script-pipe.")
            time.sleep(1)

        time.sleep(5)

        logging.debug("-- Both pipes exist.  Good.")

        TOFILE = open(TONAME, 'w')
        logging.debug("-- File to write to has been opened")
        FROMFILE = open(FROMNAME, 'rt')
        logging.debug("-- File to read from has now been opened too\r\n")


        def send_command(command):
            """Send a single command."""
            logging.debug("Send: >>> \n"+command)
            TOFILE.write(command + EOL)
            TOFILE.flush()

        def get_response():
            """Return the command response."""
            result = ''
            line = ''
            while True:
                result += line
                line = FROMFILE.readline()
                if line == '\n' and len(result) > 0:
                    break
            return result

        def do_command(command):
            """Send one command, and return the response."""
            send_command(command)
            response = get_response()
            logging.debug("Rcvd: <<< \n" + response)
            return response

        
        # construct import paths for audio
        importPath = working[2:-1] + '/' + arguments.output_path + '/' + tail[0:-4] + '/'
        importPath = os.path.normpath(importPath)
        do_command('Import2: Filename="' + os.path.join(importPath,'bass.mp3"'))
        do_command('Import2: Filename="' + os.path.join(importPath,'vocals.mp3"'))
        do_command('Import2: Filename="' + os.path.join(importPath,'piano.mp3"'))
        do_command('Import2: Filename="' + os.path.join(importPath,'other.mp3"'))
        do_command('Import2: Filename="' + os.path.join(importPath,'drums.mp3"'))
   
        # Imported!
        logging.info("files imported successfully...")
        sys.exit(1)


    except SpleeterError as e:
        get_logger().error(e)


def entrypoint():
    """ Command line entrypoint. """
    warnings.filterwarnings('ignore')
    main()


if __name__ == '__main__':
    entrypoint()
