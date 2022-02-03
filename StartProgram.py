import flask
from flask import Flask, request, send_from_directory, jsonify
from flask import Response
from flask import json
import os
from src.parseMidi import *
import sys
# os.chdir(os.path.dirname(sys.argv[0]))
import src.Player as Player
def main():
    global player 
    player = Player.Player()

def parseRequest(request):
    speed = request.args.get("speed")
    if request.args.get("speed") == None:
        speed = 1
    return speed
# Create the application.
APP = flask.Flask(__name__)



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

@APP.route('/getPorts')
def getPorts():
    vals = player.getPorts()
    return Response(json.dumps(vals),  mimetype='application/json')

@APP.route('/setInPort')
def setInPort():
    vals = player.getPorts()
    return Response(json.dumps(vals),  mimetype='application/json')

@APP.route('/setOutPort')
def setOutPort():
    port = request.args.get("port")
    if port == None:
        port = 0
    player.selectOutPort(port)
    
    return Response(json.dumps(player.settings['outPort']),  mimetype='application/json')

@APP.route('/')
def index():
    """ Displays the index page accessible at '/'
    """
    
    return flask.send_file('./Midirec.html')

app = Flask(__name__, static_url_path='')

def escapeSpaces(stringInput):
    return stringInput.replace(" ", "\\ ")

if __name__ == '__main__':
    main()
    port = 8079
    APP.run(port=port, host='0.0.0.0')