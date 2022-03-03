from __future__ import unicode_literals

# Logging Setup
import logging
from unittest import result
ch = logging.StreamHandler()
logger = logging.getLogger("prog")
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)
logger.propagate = False


import sys
import time
import youtube_dl
import tkinter
from tkinter import filedialog
from youtubesearchpython import VideosSearch
import warnings
import os
from spleeter.commands.separate import entrypoint
from spleeter.commands import create_argument_parser
from spleeter.utils.configuration import load_configuration
from spleeter.utils.logging import (
    enable_logging,
    enable_tensorflow_logging,
    )

__email__ = 'research@deezer.com'
__author__ = 'Deezer Research'
__license__ = 'MIT License'

bootlogo = """  
 ██████  ██▓███   ██▓    ▓█████ ▓█████▄▄▄█████▓▓█████  ██▀███  
▒██    ▒ ▓██░  ██▒▓██▒    ▓█   ▀ ▓█   ▀▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒
░ ▓██▄   ▓██░ ██▓▒▒██░    ▒███   ▒███  ▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒
  ▒   ██▒▒██▄█▓▒ ▒▒██░    ▒▓█  ▄ ▒▓█  ▄░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄  
▒██████▒▒▒██▒ ░  ░░██████▒░▒████▒░▒████▒ ▒██▒ ░ ░▒████▒░██▓ ▒██▒
▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░░ ▒░▓  ░░░ ▒░ ░░░ ▒░ ░ ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░
░ ░▒  ░ ░░▒ ░     ░ ░ ▒  ░ ░ ░  ░ ░ ░  ░   ░     ░ ░  ░  ░▒ ░ ▒░
░  ░  ░  ░░         ░ ░      ░      ░    ░         ░     ░░   ░ 
      ░               ░  ░   ░  ░   ░  ░           ░  ░   ░ """

AUDACITY_PATH = "C:\\Program Files (x86)\\Audacity\\audacity.exe"

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

TONAME = '\\\\.\\pipe\\ToSrvPipe'
FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
EOL = '\r\n\0'





class SpleeterGUI:
    def __init__(self):
        # You cant have tkinter Variables without fucking intantiating tkinter first...
        self.root = tkinter.Tk()
        self.root.withdraw()
        # Init all the damn variables.
        self.working = str((os.getcwdb()))
        self.open_audacity = tkinter.BooleanVar(value=False)
        self.then_spleet = tkinter.BooleanVar(value=True) # control whether the spleet will run once the youtube download occurs.
        self.local_file_path = tkinter.StringVar() # Where to get the file to spleet.
        self.youtube_results = []
        self.search_term = tkinter.StringVar(value="") # The youtube search term
        self.forgettable_elements = []
        self.chosen_yt_result = tkinter.IntVar(0)
        
    def open_ui(self):
        self.root.geometry("590x550")
        self.root.title("Spleeter GUI by Dozza")
        frame = tkinter.Frame(self.root)
        tkinter.Label(self.root, text=bootlogo, justify="left", font="consolas").grid(row=0)
        frame.grid(row=1, padx=5, pady=5)
        tkinter.Button(frame, text="Spleet Local File", command=self.ask_local_file).pack(side=tkinter.LEFT, padx=5)
        tkinter.Button(frame, text="Search Youtube", command=self.search_youtube).pack(side=tkinter.LEFT, padx=5)
        ent = tkinter.Entry(frame, textvariable=self.search_term)
        ent.bind('<Return>', self.hit_search_youtube) # now THIS is epic
        ent.pack(side=tkinter.LEFT, padx=5)
        ent.focus()
        frame2 = tkinter.Frame(frame)
        tkinter.Checkbutton(frame2, text="Open Audacity After Spleet", variable=self.open_audacity).grid(row=0)
        tkinter.Checkbutton(frame2, text="Spleet After Youtube DL", variable=self.then_spleet).grid(row=1)
        frame2.pack(side=tkinter.LEFT, padx=5)
        ExitButton = tkinter.Button(frame, text="Quit", command=sys.exit)
        ExitButton.pack(side=tkinter.TOP)
        tkinter.Pack()
        self.root.update()
        self.root.deiconify()
        self.root.mainloop()

    def hit_search_youtube(self, arg):
        self.search_youtube()

    
    def ask_local_file(self, spleet_after = True):
        self.local_file_path.set(filedialog.askopenfilename(initialdir=os.environ["HOMEPATH"] + "/Desktop",
                                                  title="Select file",
                                                  filetypes=(("mp3 audio", ".mp3 .wav"), ("all files", ".*"))))
        if spleet_after:
            self.spleet_file(False)


    def spleet_file(self, remove_file = False):
        warnings.filterwarnings('ignore')
        # Do some cool shit.
        filename = self.local_file_path.get()
        logger.info('Spleeting')
        logger.info(f"Local file is {self.local_file_path.get()}")
        logger.debug(f"Output full path: {filename}")
        [self.head, self.tail] = os.path.split(filename)
        self.arguments = create_argument_parser().parse_args(
            ['separate', '-i', filename, '-o', 'audio_output', '-p', 'spleeter:5stems-16kHz'])
        # ok so now we add our own spicy c-c-custom code.
        self.arguments.codec = self.tail.split(".")[1]
        # arguments.command = 'separate'
        # arguments.configuration = 'spleeter:5stems-16kHz'
        # arguments.duration = 600
        self.arguments.bitrate = '256k'
        self.arguments.filename_format = '{filename}/{instrument}.{codec}'
        # arguments.offset = 0.0
        # arguments.output_path = 'audio_output'
        self.arguments.verbose = True
        logger.debug(f"Loaded {self.tail} from {self.head}")
        logger.debug("Processing...")
        enable_logging()
        enable_tensorflow_logging()
        params = load_configuration(self.arguments.configuration)
        logger.info("Spleeting...")
        entrypoint(self.arguments, params)
        logger.info("Done!")

        #remove the downloaded mp3 afterwards
        if remove_file:
            os.remove(filename)

        #pop open the output folder
        os.startfile('"' + self.working[2:-1] + '\\' + self.arguments.output_path + '\\' + self.tail[0:-4] + '\\' + '"')
        if self.open_audacity.get():
            self.open_audacity_and_import()

    def search_youtube(self):
        searchterm = self.search_term.get()
        logger.info(f"Search term is: \"{searchterm}\"")
        search = VideosSearch(searchterm, limit=10).result()["result"]
        results = []
        # Unpack the videosearch generator.
        for i,x in enumerate(search):
            results.append(x)

        #parse the results of the search into useful parameters.
        self.youtube_results = []
        for item in self.forgettable_elements:
            item.pack_forget()
            item.destroy()

        self.youtube_buttons = []
        frame = tkinter.Frame(self.root)
        frame.grid() # see where it puts it???

        Dlbutton = tkinter.Button(frame, text=f"Download and Spleet YT", command=self.download_file_from_yt)
        Dlbutton.grid(row=0, sticky=tkinter.W)

        self.forgettable_elements.append(Dlbutton)
        self.forgettable_elements.append(frame)

        for index, result in enumerate(results):
            try:
                self.youtube_results.append(result)
                logger.info(f"{index}\t{result['title']} - {result['duration']} = {result['link']}")
                rad = tkinter.Radiobutton(frame, variable=self.chosen_yt_result, value=index, text=f"{result['title']} - {result['duration']}")
                rad.grid(sticky=tkinter.W, row=index+1)
                self.forgettable_elements.append(rad)
            except Exception as e:
                logger.exception(e)

        tkinter.Pack()



    def download_file_from_yt(self):
        selected_result = self.youtube_results[self.chosen_yt_result.get()]
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            downloaded_filename = ydl.prepare_filename(selected_result)[:-3] + '.mp3'
            logger.info(f"Saving file as {downloaded_filename}")
            ydl.download([selected_result['link']])
            self.local_file_path.set(os.path.join(os.getcwd(),downloaded_filename))
        if self.then_spleet.get():
            self.spleet_file(True)
    
    def open_audacity_and_import(self):
        # audacity time
        os.startfile(AUDACITY_PATH)
        logger.debug("pipe-test.py, running on windows")

        logger.debug("Write to  \"" + TONAME +"\"")
        while not os.path.exists(TONAME):
            logger.error(" ..does not exist.  Ensure Audacity is running with mod-script-pipe.")
            time.sleep(1)


        logger.debug("Read from \"" + FROMNAME +"\"")
        while not os.path.exists(FROMNAME):
            logger.error(" ..does not exist.  Ensure Audacity is running with mod-script-pipe.")
            time.sleep(1)

        time.sleep(5)

        logger.debug("-- Both pipes exist.  Good.")

        TOFILE = open(TONAME, 'w')
        FROMFILE = open(FROMNAME, 'rt')
        logger.debug("-- File to write to has been opened")
        logger.debug("-- File to read from has now been opened too\r\n")


        def send_command(command):
            """Send a single command."""
            logger.debug("Send: >>>  "+command)
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
            logger.debug("Rcvd: <<< " + response)
            return response

        
        # construct import paths for audio
        importPath = self.working[2:-1] + '/' + self.arguments.output_path + '/' + self.tail[0:-4] + '/'
        importPath = os.path.normpath(importPath)
        do_command('Import2: Filename="' + os.path.join(importPath,f'vocals.{self.arguments.codec}"'))
        do_command('Import2: Filename="' + os.path.join(importPath,f'bass.{self.arguments.codec}"'))
        do_command('Import2: Filename="' + os.path.join(importPath,f'piano.{self.arguments.codec}"'))
        do_command('Import2: Filename="' + os.path.join(importPath,f'other.{self.arguments.codec}"'))
        do_command('Import2: Filename="' + os.path.join(importPath,f'drums.{self.arguments.codec}"'))
         # Select the first track for vocal split,
        do_command('SelectTracks:')
        do_command("SelTrackStartToEnd:")
        # Duplicate the first track to the last track.
        do_command('Duplicate: ')
        do_command('SelectTracks:Mode="Set" Track="0.5" TrackCount="0.5"')
        do_command('Silence:Use_Preset="<Factory Defaults>"')
        do_command('SelectTracks:Mode="Set" Track="0" TrackCount="1"')
        do_command('Stereo to Mono:')
        do_command('Amplify:Ratio="2.0"')
        do_command('SelectTracks:Mode="Set" Track="5" TrackCount="0.5"')
        do_command('Silence:Use_Preset="<Factory Defaults>"')
        do_command('SelectTracks:Mode="Set" Track="5" TrackCount="1"')
        do_command('Stereo to Mono:')
        do_command('Amplify:Ratio="2.0"')
        do_command('SelectTracks:Mode="Set" Track="5" TrackCount="1"')
        do_command("Invert:")
        do_command("SortByName:")

        # Imported!
        logger.info("files imported successfully...")


def main():
    # Create the class.
    GUI = SpleeterGUI()
    GUI.open_ui()


if __name__ == '__main__':
    main()
