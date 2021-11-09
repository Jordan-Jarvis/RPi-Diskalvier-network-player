#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from configparser import RawConfigParser
from datetime import datetime

from mpserver.config import __version__
from mpserver.musicserver import MusicServer
from mpserver.tools import Colors
from mpserver.tools import colorstring as c

# TODO: let user select config file from cmd argument
inifile = 'config.ini'
musicserver = None  # type: musicserver.MusicServer

# Start main program
banner = c("\n"
           "\tMelonMusicPlayer made by Melle Dijkstra © " + str(datetime.now().year) + "\n"
           "\tVersion: " + __version__ + "\n",
           Colors.BLUE)

if __name__ == '__main__':
    # Check if program is run with root privileges, which is needed for socket communication
    try:
        print(banner)

        # Get configuration for the application
        config = RawConfigParser(defaults={})
        if os.path.exists(inifile):
            config.read_file(open(inifile))
        else:
            print(c('configuration file ('+inifile+') does not exist', Colors.WARNING))

        musicserver = MusicServer(config)
        # This method will start the server and wait for anyone to connect
        musicserver.serve()
    except KeyboardInterrupt as e:
        print(c("Aborting MelonMusicPlayer...", Colors.BOLD))
        musicserver.shutdown()

musicserver.shutdown()
