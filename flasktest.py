import flask
import mido
from flask import Flask, request, send_from_directory, jsonify
from flask import Response
from flask import json
import time
import os
import subprocess
import multiprocessing
import config
import configparser
import io
from parseMidi import *

def main():
    pass

# Create the application.
player = Player()
APP = flask.Flask(__name__)

@APP.route('/ajax/setconf/midiout/<midi>')
def setMidiOut(midi):
    player.SysInter.setCurrentPort(midi)
    return Response(json.dumps((get_int(1),0)),  mimetype='application/json')

@APP.route('/ajax/setconf/midiin/<midi>')
def setMidiIn(midi):
    player.SysInter.setCurrentPort(midi)
    return Response(json.dumps((get_int(1),0)),  mimetype='application/json')


@APP.route('/ajax/setplaylist/<playlist>')
def setplaylist(playlist):
    player.changePlaylist(playlist)
    player.commands.killAllProcesses()
    return Response(json.dumps((get_int(1),0)),  mimetype='application/json')

    return get_int(0)

@APP.route('/ajax/rec-start-<bpm>')
def startRecording(bpm):
    player.pause()
    player.startRecording(bpm)
    idToChange = []
    idToChange.append(["prog","recording"])
    idToChange.append(["but_rec", "stop"])
    idToChange.append(["but_ply", ""])
    idToChange.append(["rating","star" + "4"])
    idToChange.append(["but_con","dis"])
    idToChange.append(["but_rep","ena"])
    response = []
    response.append("PLAYER")   # 0 position
    response.append(idToChange) # 1 position
    response.append(5)         # 2 position
    response.append(0)      # 3 position
    response.append(120)        # 4 position
    response.append(0)         # 5 position
    response.append(2)          # 6 position
    response.append(0)          # 7 position

    return Response(json.dumps((response,0)),  mimetype='application/json')


@APP.route('/ajax/rec-stop')
def stopRecording():
    player.pause()
    player.stopRecording()


    idToChange = []
    idToChange.append(["prog",0])
    idToChange.append(["but_rec", ""])
    idToChange.append(["but_ply", ""])
    idToChange.append(["rating","star" + "4"])
    idToChange.append(["but_con","dis"])
    idToChange.append(["but_rep","ena"])
    response = []
    response.append("PLAYER")   # 0 position
    response.append(idToChange) # 1 position
    response.append(5)         # 2 position
    response.append(0)      # 3 position
    response.append(120)        # 4 position
    response.append(0)         # 5 position
    response.append(0)          # 6 position
    response.append(0)          # 7 position

    return Response(json.dumps((response,0)),  mimetype='application/json')

    return flask.send_file("static/")

@APP.route('/static/<name>/')
def staticFile(name):
    """ Displays the page greats who ever comes to visit it.
    """
    return flask.send_file("static/" + name)

@APP.route('/ajax/start')
def start(returnArray = 0):
        	# [1] : setIdClass : array of ids to change classes and therefore styles for.
		# [2] : progress
		# [3] : timeElapsed
		# [4] : bpm
		# [5] : total Time of song
		# [6] : timer enable
        # [7] : numDisks
    player.play()
    CurrentSong = player.playlist.get_current_song() 
    idToChange = []
    idToChange.append(["prog",0])
    idToChange.append(["but_rec", ""])
    idToChange.append(["but_ply", "pause"])
    idToChange.append(["rating","star" + CurrentSong.getStars()])
    idToChange.append(["but_con","ena"])
    idToChange.append(["but_rep","ena"])
    response = []
    response.append("PLAYER")   # 0 position
    response.append(idToChange) # 1 position
    response.append(5)         # 2 position
    response.append(0)      # 3 position
    response.append(CurrentSong.getBPM())        # 4 position
    response.append(CurrentSong.getLength())         # 5 position
    response.append(1)          # 6 position
    response.append(0)          # 7 position
    if returnArray == 1:
        return response
    return Response(json.dumps((response,get_int(1))),  mimetype='application/json')



@APP.route('/dl/<name>/')
def download(name):
    """ Displays the page greats who ever comes to visit it.
    """
    if ("/" in name or ".." in name or not (name.endswith(".mid") or name.endswith(".MID"))):
        exit() # at least a small degree of security
    return flask.send_file(os.getcwd() + "/playlists/" + player.SysInter.getCurrentPlaylist() + "/" + name)

@APP.route('/ajax/prog-<time>-<time2>')
def changeTime(time, time2):
    CurrentSong = player.playlist.get_current_song()
    currentPercent = int(time)/int(time2)
    idToChange = []
    idToChange.append(["prog", currentPercent])
    idToChange.append(["but_rec", ""])
    idToChange.append(["but_ply", "pause"])
    idToChange.append(["rating","star" + CurrentSong.getStars()])
    idToChange.append(["but_con","ena"])
    idToChange.append(["but_rep","ena"])
    response = []
    response.append("PLAYER")   # 0 position
    response.append(idToChange) # 1 position
    response.append(5)         # 2 position
    response.append(int(currentPercent * CurrentSong.getLength()))      # 3 position
    response.append(CurrentSong.getBPM())        # 4 position
    response.append(CurrentSong.getLength())         # 5 position
    response.append(1)          # 6 position
    response.append(0)          # 7 position

    player.changeTime(time,time2)
    return Response(json.dumps((response,0)),  mimetype='application/json')

@APP.route('/ajax/selectsong-<song>')
def startSong(song):
    player.play(song)
    response = []
    response.append(get_int(1))
    response.append(play_stop(1))
    return Response(json.dumps((get_int(1),start(1))),  mimetype='application/json')

@APP.route('/ajax/rate-<rating>')
def changeRating(rating):
    player.playlist.get_current_song().setStars(int(rating))
    CurrentSong = player.playlist.get_current_song()
    idToChange = []
    idToChange.append(["rating","star" + CurrentSong.getStars()])
    response = []
    response.append("BYID")   # 0 position
    response.append(idToChange) # 1 position

    return Response(json.dumps((response,get_int(1))),  mimetype='application/json')

    return get_int()

@APP.route('/ajax/menu')
def sendMenu():

    midiIn = player.SysInter.getPorts()
    midiOut = midiIn

    sendMenu = '''<div id=menu_midiin><label>MIDI input</label><select onchange="sendRequest('setconf/midiin/'+this.value)">'''
    for device in midiIn:
        sendMenu = sendMenu + '''<option value="''' + device.split()[0] + '"'
        if device.split()[0] == player.SysInter.getCurrentPortNumber():
            sendMenu = sendMenu + ''' selected="selected"'''
        sendMenu = sendMenu + '>' + device + '''</option>'''
    
    sendMenu = sendMenu + '''</select></div><div id=menu_midiout><label>MIDI output</label><select onchange="sendRequest('setconf/midiout/'+this.value)">'''
    
    for device in midiOut:
        sendMenu = sendMenu + '''<option value="''' + device.split()[0] + '"'
        if device.split()[0] == player.SysInter.getCurrentPortNumber():
            sendMenu = sendMenu + ''' selected="selected"'''
        sendMenu = sendMenu + '>' + device + '''</option>'''
    
    sendMenu = sendMenu + '''</select></div><div id=menu_noteoff><input id=menu_noteoff_chk type=checkbox name=menu_noteoff_chk value=1 checked onchange="sendRequest('setconf/noteoff/'+( this.checked ? 1 : 0) )"><label for=menu_noteoff_chk>Send notes-off before playing</label></div><div id=menu_usb><label>USB Drives</label></div><div id=menu_ply><label>Playlist Folder</label>'''
    sendMenu = sendMenu + '''<select onchange="sendRequest('setplaylist/'+this.value)">'''
    for folder in player.SysInter.getPlaylists():
        sendMenu = sendMenu + '''<option value="''' + folder + '"'
        if folder == player.SysInter.getCurrentPlaylist():
            sendMenu = sendMenu + ''' selected="selected"'''
        sendMenu = sendMenu + '>' + folder + '''</option>'''
    
    sendMenu = sendMenu + '''</div><a id=menu_shut onclick="sendRequest('shut-open',this)">SHUTDOWN</a><div id=menu_shut_info>Or close Chrome kiosk with ALT+F4</div>'''

    response = []
    response.append("OVERLAY")   # 0 position
    response.append(sendMenu) # 1 position
    return Response(json.dumps((response,0)),  mimetype='application/json')


@APP.route('/ajax/ren-open')
def renameFile():
    response = []
    response.append("OVERLAY")   # 0 position
    sendMenu = '''<input id=plylst_input type=text value=""><a class=button style="top:10%;left:75%;width:20%" onclick="var name = gebi('plylst_input').value.toLowerCase().replace(/[^a-z\d]+/g,'-'); sendRequest('newlist-make/'+name,this)">CREATE</a>'''
    response.append(sendMenu) # 1 position
    response2 = []
    response2.append("FOCUS")
    response2.append("plylst_input")
    response3 = []
    response3.append("KEYBOARD")
    response3.append("plylst_input")
    return Response(json.dumps((response,response2,response3)),  mimetype='application/json')

    
    response = APP.response_class(
        response=sendMenu,
        status=200,
        mimetype='text/plain')
    return response

@APP.route('/ajax/get-int/')
def get_int(returnArray = 0):
    masterList = player.playlist.get_song_list_list()
    masterList.insert(0,'PLAYLIST')
    if (returnArray == 1):
        return masterList
    return Response(json.dumps((masterList,0)),  mimetype='application/json')

@APP.route('/ajax/play-start/')
def play_start():
    CurrentSong = player.playlist.get_current_song()

    	# [1] : setIdClass : array of ids to change classes and therefore styles for.
		# [2] : progress
		# [3] : timeElapsed
		# [4] : bpm
		# [5] : total Time of song
		# [6] : timer enable
        # [7] : numDisks
    CurrentSong = player.playlist.get_current_song()

    idToChange = []
    idToChange.append(["prog",70])
    idToChange.append(["but_rec", ""])
    idToChange.append(["but_ply", "pause"])
    idToChange.append(["rating","star" + str(CurrentSong.getStars())])
    idToChange.append(["but_con","ena"])
    idToChange.append(["but_rep","ena"])
    response = []
    response.append("PLAYER")   # 0 position
    response.append(idToChange) # 1 position
    response.append(5)         # 2 position
    response.append(player.timer.getTimeElapsed())      # 3 position
    response.append(CurrentSong.getBPM())        # 4 position
    response.append(CurrentSong.getLength())         # 5 position
    response.append(1)          # 6 position
    response.append(0)          # 7 position
    player.resume()

    return Response(json.dumps((response,0)),  mimetype='application/json')

@APP.route('/ajax/nextSong/')
def play_next():
    player.next()
    return start()

@APP.route('/ajax/play-stop/')
def play_stop(returnArray = 0): 
    	# [1] : setIdClass : array of ids to change classes and therefore styles for.
		# [2] : progress
		# [3] : timeElapsed
		# [4] : bpm
		# [5] : total Time of song 
		# [6] : timer enable
        # [7] : numDisks
    player.pause()
    idToChange = []
    idToChange.append(["prog",70])
    idToChange.append(["but_rec", ""])
    idToChange.append(["but_ply", "play"])
    idToChange.append(["but_con","ena"])
    idToChange.append(["but_rep","ena"])
    response = []
    response.append("PLAYER")   # 0 position
    response.append(idToChange) # 1 position
    response.append(50)                         # 2 position
    print(player.timer.getTimeElapsed())
    response.append(player.timer.getTimeElapsed())      # 3 position
    response.append(0)        # 4 position
    response.append(player.playlist.get_current_song().getLength())         # 5 position
    response.append(0)          # 6 position
    response.append(1)          # 7 position
    if returnArray == 1:
        return response
    return Response(json.dumps((response, None)),  mimetype='application/json')


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
    APP.debug=True
    APP.run()