# RPi-Diskalvier-network-player
(inspired by Florian Bador)
This player allows for a Raspberry Pi to host a Midi player/recorder server. It has a web interface and ajax/json support for future Alexa and Google home integration.
![](./static/screenshot.png)

Very much a WIP

Currently the player works for selecting songs, playing them, scraping the tempo and other information from midi files, playing back a midi file from a given time (seek, not supported by standard libraries and deceivingly difficult to implement due to tempo changes and timings)
, downloading the songs, and changing the tempo.

Need to fix:
keys stuck down when pausing (sometimes), recording functionality, proper button updates on the web interface, better process management (sometimes a process gets stuck due to the API), tons of little bugs.

Need to add: Database support (to reduce memory overhead and launch time), Playlist support, input/output device selection, auto launch on startup, Google Assistant support (using IFTTT), instrument changer, secure connection (SSL), automated setup (GUI for config file).
