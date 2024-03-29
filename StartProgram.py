import operator
import flask
from flask import Flask, request, send_from_directory, jsonify
from flask import Response
from flask import json
import os
from src.parseMidi import *
import sys
import src.dbconnect as db
cur = db.connection

# cur.execute("SELECT * FROM song;")
# print(cur.fetchmany(size=20))

import src.scanner as scanner
scan = scanner.scanner(cur, '/app/src/music')
scan.scan()
# os.chdir(os.path.dirname(sys.argv[0]))

import src.Player as Player
def main():
    global player 
    player = Player.Player(db.connection, '/app/src/music')

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

@APP.route('/getPlaylists')
def getPlaylists():
    """ Displays the page greats who ever comes to visit it.
    """
    return Response(json.dumps(player.getPlaylists()),  mimetype='application/json')

@APP.route('/getPlaylist')
def getPlaylist():
    """ Displays the page greats who ever comes to visit it.
    """
    
    playlist = request.args.get("playlist")
    if playlist is None:
        playlist = 'Classical-I'
    return Response(player.getPlaylist(playlist).to_json(),  mimetype='application/json',content_type='application/json',)


@APP.route('/dl/<name>/')
def download(name):
    """ Displays the page greats who ever comes to visit it.
    """
    if ("/" in name or ".." in name or not (name.endswith(".mid") or name.endswith(".MID"))):
        exit() # at least a small degree of security
    return flask.send_file(os.getcwd() + "/playlists/" + player.SysInter.getCurrentPlaylist() + "/" + name)

@APP.route('/selectsong-<index>')
def startSong(index):
    try:
        index = int(index)
        player.stop()
        player.queue.setCurrentSongIndex(index)
    except:
        player.stop()
        
        #index is a song name, less reliable, but will attempt
        
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

@APP.route('/dbtest')
def dbtest():
    songs = db.pandas.read_sql('SELECT s.title, s.rating from playlist as p join songlist as sl on p.listID=sl.listid join song s on sl.songid=s.id; ', db.connection)
    return Response(songs.to_json(),  mimetype='application/json')

@APP.route('/queue')
def queue():
    return player.queue.toJSON()

@APP.route('/nowPlaying')
def nowPlaying():
    return player.nowPlayingJSON()

@APP.route('/pause')
def pause():
    player.playlist.get_current_song() # Save current song to db?
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
    return routes()
    
    #return flask.send_file('./Midirec.html')

@APP.route("/site-map")
def routes():
    'Display registered routes'
    rules = []
    for rule in APP.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        rules.append((rule.endpoint, methods, str(rule)))

    sort_by_rule = operator.itemgetter(2)
    for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
        route = '{:50s} {:25s} {}'.format(endpoint, methods, rule)
        print(route)
    return rules



def escapeSpaces(stringInput):
    return stringInput.replace(" ", "\\ ")

if __name__ == '__main__':
    main()
    port = 8079
    APP.run(port=port, host='0.0.0.0')