import flask
import mido
from flask import Flask, request, send_from_directory, jsonify
from flask import Response
from flask import json
import time
import os
import subprocess
import multiprocessing

cwd = os.getcwd()
currentPlaylist = "Classical-I"
playlists = []
for item in os.listdir(cwd + "/playlists/"):
    if os.path.isdir(cwd + "/playlists/" + item):
        playlists.append(item)
try:
    currentPlaylist = playlists[0]
    print(currentPlaylist)
except:
    currentPlaylist = "Classical-I" 
currentPlaylist = "Classical-I"
masterList = []
masterSongList = []
pid = []
SongTime = [0,0] # start time for song, end/kill time
SelectedPort = "20:0" 
def getCurrentSongPos():
    CurrentSongPos = -1
    for i in range(1,len(masterList)):
        if masterList[i][8] == 1:
            CurrentSongPos = i
    if (CurrentSongPos == -1):
        masterList[0][8] = 1
        CurrentSongPos = 0
    return CurrentSongPos

def setCurrentSongPos(indexLocation):
    for i in range(1,len(masterList)):
        masterList[i][8] = 0
    print(indexLocation)
    masterList[indexLocation][8] = 1
    return
# Create the application.
APP = flask.Flask(__name__)

@APP.route('/ajax/setplaylist/<playlist>')
def setplaylist(playlist):
    global currentPlaylist
    currentPlaylist = playlist
    global masterSongList
    masterSongList = []
    global masterList
    masterList = []
    killAllProcesses()
    return Response(json.dumps((get_int(1),0)),  mimetype='application/json')

    return get_int(0)


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
    killAllProcesses()
    resetTimer()
    startTimer()
    CurrentSongPos = getCurrentSongPos()
    SelectedPort = "20:0"
    runCommandNoOutput([cwd + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c", cwd + "/playlists/" + currentPlaylist + "/" + masterList[CurrentSongPos][0]])
    idToChange = []
    idToChange.append(["prog",0])
    idToChange.append(["but_rec", ""])
    idToChange.append(["but_ply", "pause"])
    idToChange.append(["rating","star4"])
    idToChange.append(["but_con","ena"])
    idToChange.append(["but_rep","ena"])
    response = []
    response.append("PLAYER")   # 0 position
    response.append(idToChange) # 1 position
    response.append(5)         # 2 position
    response.append(0)      # 3 position
    response.append(masterList[CurrentSongPos][4])        # 4 position
    response.append(masterList[CurrentSongPos][3])         # 5 position
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
    return flask.send_file(cwd + "/playlists/" + currentPlaylist + "/" + name)

@APP.route('/ajax/prog-<time>-<time2>')
def changeTime(time, time2):
    """ Displays the page greats who ever comes to visit it.
    """
    print(time2)
    killAllProcesses()
    releaseAll()
    CurrentSongPos = getCurrentSongPos()
    currentPercent = int(time)/int(time2)
    numSecondsIntoSong = int(currentPercent * masterList[CurrentSongPos][3])

    idToChange = []
    idToChange.append(["prog", currentPercent])
    idToChange.append(["but_rec", ""])
    idToChange.append(["but_ply", "pause"])
    idToChange.append(["rating","star" + masterList[CurrentSongPos][7]])
    idToChange.append(["but_con","ena"])
    idToChange.append(["but_rep","ena"])
    response = []
    response.append("PLAYER")   # 0 position
    response.append(idToChange) # 1 position
    response.append(5)         # 2 position
    response.append(int(currentPercent * masterList[CurrentSongPos][3]))      # 3 position

    response.append(masterList[CurrentSongPos][4])        # 4 position
    response.append(masterList[CurrentSongPos][3])         # 5 position
    response.append(1)          # 6 position
    response.append(0)          # 7 position
    resetTimer()
    addToTimer(numSecondsIntoSong)
    startTimer()

    runCommandNoOutput([cwd + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c","-s " + str(int(currentPercent * masterList[CurrentSongPos][3])),"-b " + str(masterList[CurrentSongPos][4]), cwd + "/playlists/" + currentPlaylist + "/" + masterList[CurrentSongPos][0]])
    return Response(json.dumps((response,0)),  mimetype='application/json')




    

    return flask.send_file("static/" + time)

@APP.route('/ajax/selectsong-<song>')
def startSong(song):
    i = 0
    resetTimer()
    killAllProcesses()
    releaseAll()
    for i in range(1,len(masterList)):
        print(song + " " + masterList[i][0])
        if song == masterList[i][0]:
            masterList[i][8] = 1
        else:
            print(masterList[i])
            masterList[i][8] = 0
    response = []
    response.append(get_int(1))
    response.append(play_stop(1))
    return Response(json.dumps((get_int(1),start(1))),  mimetype='application/json')

@APP.route('/ajax/rate-<rating>')
def changeRating(rating):
    i = 0

    for i in range(1,len(masterList)):
        if masterList[i][8] == 1:
            masterList[i][7] = rating
        else:
            pass
    return get_int()

@APP.route('/summary')
def summary():
    data = make_summary()
    response = APP.response_class(
        response=json.dumps({'status':'OK','user':user,'pass':password}),
        status=200,
        mimetype='application/json'
    )
    return response

@APP.route('/ajax/menu')
def sendMenu():


    midiIn = []
    midiIn.append("herroro")
    midiIn.append("heo")
    midiOut = []
    midiOut.append("herroro")
    midiOut.append("heo")


    sendMenu = '''OVERLAY\n<div id=menu_midiin><label>MIDI input</label><select onchange="sendRequest('setconf/midiin/'+this.value)">'''
    for device in midiIn:
        sendMenu = sendMenu + '''<option value="''' + device + '">' + device + '''</option>'''
    sendMenu = sendMenu + '''</select></div><div id=menu_midiout><label>MIDI output</label><select onchange="sendRequest('setconf/midiout/'+this.value)">'''
    
    for device in midiOut:
        sendMenu = sendMenu + '''<option value="''' + device + '">' + device + '''</option>'''
    
    sendMenu = sendMenu + '''</select></div><div id=menu_noteoff><input id=menu_noteoff_chk type=checkbox name=menu_noteoff_chk value=1 checked onchange="sendRequest('setconf/noteoff/'+( this.checked ? 1 : 0) )"><label for=menu_noteoff_chk>Send notes-off before playing</label></div><div id=menu_usb><label>USB Drives</label></div><div id=menu_ply><label>Playlist Folder</label>'''
    sendMenu = sendMenu + '''<select onchange="sendRequest('setplaylist/'+this.value)">'''
    for folder in playlists:
        sendMenu = sendMenu + '''<option value="''' + folder + '"'
        if folder == currentPlaylist:
            sendMenu = sendMenu + ''' selected="selected"'''
        sendMenu = sendMenu + '>' + folder + '''</option>'''
    
    sendMenu = sendMenu + '''</div><a id=menu_shut onclick="sendRequest('shut-open',this)">SHUTDOWN</a><div id=menu_shut_info>Or close Chrome kiosk with ALT+F4</div>'''
    
    
    response = APP.response_class(
        response=sendMenu,
        status=200,
        mimetype='text/plain'
    )
    return response



@APP.route('/ajax/get-int/')
def get_int(returnArray = 0):
    container = []

    songlist = os.listdir(cwd + "/playlists/" + currentPlaylist)
    print(currentPlaylist)
    global masterSongList
    global masterList
    if len(songlist) != len(masterSongList):
        masterSongList = []
        for song in songlist:
            masterSongList.append(song)

        tempval = 0
        for i in range(1, len(masterList)):
            if masterList[i][8] == 1:
                tempval = i #find current assigned value position
        masterList = []
        masterList.append('PLAYLIST')
        for item in songlist:
            if item.endswith(".mid") or item.endswith(".MID"):
                try:
                    masterList.append(getMidiInfo(item))
                except:
                    print("Skipping outdated stuff.")
                    pass
        if tempval == 0:
            pass
            #masterList[1][8] = "1" # re-assign current selection
        else:
            masterList[tempval][8] = 1
    if (returnArray == 1):
        return masterList
    return Response(json.dumps((masterList,0)),  mimetype='application/json')

@APP.route('/ajax/play-start/')
def play_start():

    CurrentSongPos = getCurrentSongPos()
    	# [1] : setIdClass : array of ids to change classes and therefore styles for.
		# [2] : progress
		# [3] : timeElapsed
		# [4] : bpm
		# [5] : total Time of song
		# [6] : timer enable
        # [7] : numDisks
    killAllProcesses()
    runCommandNoOutput([cwd + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c","-s " + str(SongTime[1]),"-b " + str(masterList[CurrentSongPos][4]), cwd + "/playlists/" + currentPlaylist + "/" + masterList[CurrentSongPos][0]])

    idToChange = []
    idToChange.append(["prog",70])
    idToChange.append(["but_rec", ""])
    idToChange.append(["but_ply", "pause"])
    idToChange.append(["rating","star" + masterList[CurrentSongPos][7]])
    idToChange.append(["but_con","ena"])
    idToChange.append(["but_rep","ena"])
    response = []
    response.append("PLAYER")   # 0 position
    response.append(idToChange) # 1 position
    response.append(5)         # 2 position
    response.append(getTimeElapsed())      # 3 position
    startTimer()
    response.append(masterList[CurrentSongPos][4])        # 4 position
    response.append(masterList[CurrentSongPos][3])         # 5 position
    response.append(1)          # 6 position
    response.append(0)          # 7 position

    return Response(json.dumps((response,0)),  mimetype='application/json')

@APP.route('/ajax/nextSong/')
def play_next():
    currentPos = getCurrentSongPos()
    if currentPos + 1 == len(masterList):
        setCurrentSongPos(1)
    else:
        setCurrentSongPos(currentPos + 1)
    
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
    CurrentSongPos = getCurrentSongPos()
    killAllProcesses()
    stopTimer()
    SelectedPort = "20:0"
    releaseAll()
    idToChange = []
    idToChange.append(["prog",70])
    idToChange.append(["but_rec", ""])
    idToChange.append(["but_ply", "play"])
    idToChange.append(["but_con","ena"])
    idToChange.append(["but_rep","ena"])
    response = []
    response.append("PLAYER")   # 0 position
    response.append(idToChange) # 1 position
    response.append(50)         # 2 position
    response.append(getTimeElapsed())      # 3 position
    response.append(0)        # 4 position
    response.append(masterList[CurrentSongPos][3])         # 5 position
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


def getMidiInfo(fileLocation):
    

    midiFile = mido.MidiFile(cwd + '/playlists/' + currentPlaylist + "/" + fileLocation)
    mid = []
    
    midiinfo = runCommand([cwd + '/metamidi/metamidi', '-l' , cwd + '/playlists/' + currentPlaylist + "/" + fileLocation])
    midiinfo = midiinfo.split(';')
    #print(midiinfo[1].split(',')[0])
    try:
        return [fileLocation, '2020-04-20', "6:15 pm", midiFile.length, int(midiinfo[6].split(',')[0].split('.')[0]), "250", fileLocation, "4",0,"1"]
    except:
        print(midiFile)

def runCommand(command):
    process = subprocess.Popen(command,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout, stderr
    encoding = 'utf-8'
    stdout = stdout.decode('utf-8')
    return stdout

def runCommandNoOutput(command):
    process = subprocess.Popen(command)
    pid.append(process.pid)
    return process.pid

def killAllProcesses():
    for p in pid:
        try:
            os.kill(p, 9)
            print("killed" + str(p))
            os.kill(p, 9)
        except OSError: 
            print("The process: " + str(p) + " is already dead.")
            pass
    for i in range(len(pid)):
        pid.pop()

def releaseAll():
    runCommandNoOutput([cwd + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c", cwd + "/empty.mid"])
    runCommandNoOutput([cwd + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c", cwd + "/empty.mid"])

def getTimeElapsed():
    return int(SongTime[1])

def resetTimer():
    SongTime[0] = 0
    SongTime[1] = 0

def startTimer():
    SongTime[0] = time.time() - SongTime[1] # add time that already existed

def stopTimer():
    SongTime[1] = time.time() - SongTime[0]

def addToTimer(timeToAdd):
    print("I ADDED :" + str(timeToAdd))
    SongTime[1] = SongTime[1] + timeToAdd
    print("the current timer is:" + str(getTimeElapsed()))

def escapeSpaces(stringInput):
    return stringInput.replace(" ", "\\ ")

if __name__ == '__main__':
    APP.debug=True
    APP.run()
    
 
