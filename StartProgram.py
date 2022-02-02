import flask
import mido
from flask import Flask, request, send_from_directory, jsonify
from flask import Response
from flask import json
import time
import os
from parseMidi import *
import sys
os.chdir(os.path.dirname(sys.argv[0]))
import Player
def main():
    global player 
    player = Player.Player()
    pass
import urllib.request
def parseRequest(request):
    speed = request.args.get("speed")
    if request.args.get("speed") == None:
        speed = 1
    return speed
# Create the application.
APP = flask.Flask(__name__)

@APP.route('/ajax/setconf/midiout/<midi>')
def setMidiOut(midi):
    player.SysInter.setCurrentPort(midi)
    return Response(json.dumps((get_int(1),0)),  mimetype='application/json')
    
@APP.route('/ajax/setconf/midiin/<midi>')
def setMidiIn(midi):
    player.SysInter.setCurrentPort(midi)
    return Response(json.dumps((get_int(1),0)),  mimetype='application/json')


@APP.route('/static/<name>/')
def staticFile(name):
    """ Displays the page greats who ever comes to visit it.
    """
    return flask.send_file("static/" + name)






@APP.route('/dl/<name>/')
def download(name):
    """ Displays the page greats who ever comes to visit it.
    """
    if ("/" in name or ".." in name or not (name.endswith(".mid") or name.endswith(".MID"))):
        exit() # at least a small degree of security
    return flask.send_file(os.getcwd() + "/playlists/" + player.SysInter.getCurrentPlaylist() + "/" + name)

@APP.route('/selectsong-<index>')
def startSong(index):
    index = int(index)
    player.stop()
    player.queue.setCurrentSongIndex(index)
    player.set_current_song(player.queue.getCurrentSong())
    player.play()
    return Response(player.nowPlayingJSON(),  mimetype='application/json')

@APP.route('/playbackspeed')
def setPlaybackSpeed():
    speed = request.args.get("speed")
    if speed == None:
        speed = 1
    player.setPlaybackSpeed(float(speed))
    return Response(json.dumps({"return":"Success"}),  mimetype='application/json')




@APP.route('/queue')
def queue():
    return player.queue.toJSON()

@APP.route('/nowPlaying')
def nowPlaying():
    return player.nowPlayingJSON()

@APP.route('/pause')
def pause():
    player.pause()
    return player.nowPlayingJSON()

@APP.route('/play')
def play():
    player.play()
    return player.nowPlayingJSON()

@APP.route('/next')
def next():
    player.next()
    player.play()
    return player.nowPlayingJSON()

@APP.route('/previous')
def previous():
    player.previous()
    player.play()
    return player.nowPlayingJSON()

@APP.route('/resume')
def resume():
    player.resume()
    return player.nowPlayingJSON()

@APP.route('/seek-<percent>')
def seek(percent):
    vals = player.seek(float(percent))
    player.play(offset = vals,startingindex=vals[0])
    return player.nowPlayingJSON()


@APP.route('/')
def index():
    """ Displays the index page accessible at '/'
    """
    
    return flask.send_file('./Midirec.html')

app = Flask(__name__, static_url_path='')

def escapeSpaces(stringInput):
    return stringInput.replace(" ", "\\ ")


# from apscheduler.scheduler import Scheduler 
 
 
# sched = Scheduler() # Scheduler object 
# sched.start() 
 
# def refreshData():
#     checkSongEnd(player.playlist.get_current_song())

 
#add your job here 
# sched.add_interval_job(refreshData,minutes=0.05) 

import External
from multiprocessing import Process
if __name__ == '__main__':
    main()
    port = 8079
    # get_int()
    # p = Process(target=External.External, args=(port + 1, '0.0.0.0'))
    # p.start()
    #p.join()
    APP.run(port=port, host='0.0.0.0')