import mido
import time
class Timer:
    def __init__(self):
        self.SongTime = [0,0]
        self.stopped = True

    def getTimeElapsed(self):
        if self.SongTime[0] == 0 and self.stopped == False:
            return self.SongTime[1]
        if self.stopped == True:
            return self.SongTime[1]
        else:
            print("RUNNIN", self.SongTime[1])
            return time.time() + self.SongTime[1] - self.SongTime[0]

    def resetTimer(self):
        self.SongTime[0] = 0
        self.SongTime[1] = 0
        self.stopped = True

    def startTimer(self, verbose = False):
        if self.stopped == True:
            self.SongTime[0] = time.time() - self.SongTime[1] # add time that already existed
            self.stopped = False
        else:
            if verbose == True:
                print("ERROR, Timer already started!")

    def stopTimer(self, verbose = False):
        if self.stopped == False:
            self.SongTime[1] = time.time() - self.SongTime[0]
            self.stopped = True
        else:
            if verbose == True:
                print("ERROR, Timer already stopped!")
        
    def addToTimer(self,timeToAdd):
        self.SongTime[1] = self.SongTime[1] + timeToAdd

class SystemInterface():
    import subprocess
    def __init__(self):
        self.pid = []
        self.settings = {}
        self.getSettings("settings.json")
        print(self.settings["ports"])

    def getSettings(self, configFile):
        self.configFile = configFile

        if os.path.exists(os.getcwd() + "/" + configFile):
            with open(os.getcwd() + "/" + configFile) as f:
                self.settings = json.load(f)
            ports = self.getPorts()
            self.getPlaylists()
            print(self.settings["playlists"])
            self.settings["ports"] = ports
            if self.settings["selectedPort"] not in self.settings["ports"]:
                self.settings["selectedPort"] = self.settings["ports"][0]
            if self.settings["selectedInPort"] not in self.settings["ports"]:
                self.settings["selectedInPort"] = self.settings["ports"][0]
            if self.settings["playlist"] not in self.settings["playlists"]:
                self.settings["playlist"] = self.settings["playlists"][0]
            
        else:
            self.settings = {}
            self.settings["selectedPort"] = self.getPorts()[0]
            self.settings["selectedInPort"] = self.getPorts()[0]
            self.settings["playlist"] = "Classical-I"
            self.settings["ports"] = self.getPorts()
            self.writeData()
        return self.settings

    def getPlaylists(self):
        playlists = []
        for item in os.listdir(os.getcwd() + "/playlists/"):
            if os.path.isdir(os.getcwd() + "/playlists/" + item):
                playlists.append(item)
        playlists.sort()
        self.settings["playlists"] = playlists
        return playlists

    def writeData(self):
        with open(os.getcwd() + "/" + self.configFile, 'w') as json_file:
            json.dump(self.settings, json_file)

    def getCurrentPortNumber(self):
        return self.settings["selectedPort"].split()[0]

    def getCurrentPort(self):
        return self.settings["selectedPort"]

    def setCurrentPort(self, port):
        self.settings["ports"] = self.getPorts()
        if len(port.split()) == 1:
            for p in self.settings["ports"]:
                if p.split()[0] == port:
                    self.settings["selectedPort"] = p
        else:
            self.settings["selectedPort"] = port

        print(self.settings["selectedPort"])
        self.writeData()

    def getCurrentInPortNumber(self):
        return self.settings["selectedInPort"].split()[0]

    def getCurrentInPort(self):
        return self.settings["selectedInPort"]

    def setCurrentInPort(self, port):
        self.settings["ports"] = self.getPorts()
        if len(port.split()) == 1:
            for p in self.settings["ports"]:
                if p.split()[0] == port:
                    self.settings["selectedInPort"] = p
        else:
            self.settings["selectedInPort"] = port

        print(self.settings["selectedInPort"])
        self.writeData()

    def getCurrentPlaylist(self):
        return self.settings["playlist"]

    def setCurrentPlaylist(self, playlist):
        self.settings["playlist"] = playlist

    def getPorts(self):
        ports = Commands().runCommand(['aplaymidi', '--list'])
        ports = ports.split('\n')
        ports.pop(0)
        returnVal = []
        for port in ports:
            port = port.split()
            if len(port) < 3:
                continue
            returnVal.append(port[0] + " " + port[1] + " " + port[2])
        return returnVal

class Commands():
    def __init__(self):
        self.pid = []
        pass
    
    def startRecord(self, playlist, filename = "Title", SelectedPort = "20:0", BPM = 120 ):
        self.runCommandNoOutput([os.getcwd() + "/alsa-utils-1.2.2/seq/aplaymidi/arecordmidi", "-p" , SelectedPort, "-b", str(BPM), "./" + filename + ".mid"])

    def stopRecord(self):
        self.killAllProcesses()


    def releaseAll(self, SelectedPort = "20:0"):
        self.runCommandNoOutput([os.getcwd() + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c", os.getcwd() + "/empty.mid"])
        self.runCommandNoOutput([os.getcwd() + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c", os.getcwd() + "/empty.mid"])

    def runCommand(self, command):
        process = subprocess.Popen(command,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout, stderr
        encoding = 'utf-8'
        #print(stdout)
        stdout = stdout.decode('utf-8',errors="ignore")
        return stdout

    def runCommandNoOutput(self, command):
        process = subprocess.Popen(command)
        self.pid.append(process.pid)
        return process.pid

    def killAllProcesses(self):
        for p in self.pid:
            try:
                os.kill(p, 9)
                print("killed" + str(p))
                os.kill(p, 9)
            except OSError: 
                print("The process: " + str(p) + " is already dead.")
                pass
        for i in range(len(self.pid)):
            self.pid.pop()

import os
import json
import subprocess
import os.path, time
class Song:
    
    def __init__(self, fileLocation, playlist, systemSettings, autoWriteData = False):
        
        self.autoWriteData = autoWriteData
        self.songData = {}
        self.newData = False
        self.cwd = os.getcwd()
        self.playlist = playlist
        self.systemInter = systemSettings

        if os.path.exists(os.getcwd() + "/playlists/" + playlist + "/" + fileLocation + ".json"):
            with open(os.getcwd() + "/playlists/" + playlist + "/" + fileLocation + ".json") as f:
                self.songData = json.load(f)
        else:
            self.songData['title'],self.songData["date"],self.songData["time"], self.songData["length"],self.songData["bpm"],self.songData["userBPM"], self.songData["location"],self.songData["stars"],self.songData["playing"], self.songData["disk"] = self.getMidiInfo(fileLocation)
            self.newData = True
            if self.autoWriteData:
                self.writeData()

    def getTitle(self):
        return self.songData["title"]

    def setTitle(self, title):
        self.songData["title"] = title
        if self.autoWriteData:
            self.writeData()

    def getDate(self):
        return self.songData["date"]

    def setDate(self, date):
        self.songData["date"] = date
        self.newData = True
        if self.autoWriteData:
            self.writeData()

    def getTime(self):
        return self.songData["time"]

    def getLength(self):
        return self.songData["length"]

    def getBPM(self):
        return self.songData["bpm"]

    def getUserBPM(self):
        return self.songData["userBPM"]

    def setUserBPM(self, BPM):
        self.songData["userBPM"] = BPM
        self.newData = True
        if self.autoWriteData:
            self.writeData()

    def getLocation(self):
        return self.songData["location"]

    def getStars(self):
        return str(self.songData["stars"])

    def setStars(self, stars):
        if stars < 0 or stars > 5:
            print("ERROR! NOT IN BOUNDS.")
            return
        self.songData["stars"] = int(stars)
        if self.autoWriteData:
            self.writeData()
        self.newData = True

    def getPlaying(self):
        return self.songData["playing"]

    def setPlaying(self, playing):
        self.songData["playing"] = playing
        self.newData = True

    def getNewData(self):
        return self.songData["newData"]

    def setNewData(self, newData):
        self.newData = newData

    
    def getMidiInfo(self, fileLocation):
        file = self.cwd + '/playlists/' + self.playlist + "/" + fileLocation
        
        midiFile = mido.MidiFile(file)
        mid = []
        midiinfo = Commands().runCommand([self.cwd + '/metamidi/metamidi', '-l' , file])
        midiinfo = midiinfo.split(';')
        LastModifiedTime = self.parseDate(file)
        try:
            return fileLocation, LastModifiedTime, "6:15 pm", midiFile.length, int(midiinfo[6].split(',')[0].split('.')[0]), int(midiinfo[6].split(',')[0].split('.')[0]), fileLocation, "4",0,"1"
        except:
            print("DSFAASDDDDDDDDDDDDDDDDDDDDDDD")

    def parseDate(self,fileLocation):
        temp = time.ctime(os.path.getmtime(fileLocation))
        temp = temp.split()
        if(temp[1] == "Jan"):
            temp[1] = "01"
        if(temp[1] == "Feb"):
            temp[1] = "02"
        if(temp[1] == "Mar"):
            temp[1] = "03"
        if(temp[1] == "Apr"):
            temp[1] = "04"
        if(temp[1] == "May"):
            temp[1] = "05"
        if(temp[1] == "Jun"):
            temp[1] = "06"
        if(temp[1] == "Jul"):
            temp[1] = "07"
        if(temp[1] == "Aug"):
            temp[1] = "08"
        if(temp[1] == "Sep"):
            temp[1] = "09"
        if(temp[1] == "Oct"):
            temp[1] = "10"
        if(temp[1] == "Nov"):
            temp[1] = "11"
        if(temp[1] == "Dec"):
            temp[1] = "12"
        
        return(temp[4] + "-"+ str(temp[1])+ "-" +temp[2])

    def writeData(self):
        with open(os.getcwd() + "/playlists/" + self.playlist + "/" + self.getLocation() + ".json", 'w') as json_file:
            json.dump(self.songData, json_file)

    def getDicot(self):
        return self.songData

    def getList(self):
        return [self.songData['title'],self.songData["date"],self.songData["time"], self.songData["length"],self.songData["bpm"],self.songData["userBPM"], self.songData["location"],self.songData["stars"],self.songData["playing"], self.songData["disk"]]


import os
import json
class Playlist():
    def __init__(self,location, systemSettings):
        self.currentSong = -1
        songs = os.listdir(os.getcwd() + "/playlists/" + location)
        songs.sort()
        self.SongList = []
        for item in songs:
            if item.endswith(".mid") or item.endswith(".MID"):
                try:
                    self.SongList.append(Song(item,location, systemSettings, autoWriteData=True))
                except:
                    print("the following song is not readable and will be skipped:")
                    print(item)
        
        
    def refresh(self):
        pass

    def get_current_song(self):
        if self.currentSong == -1:
            return self.SongList[0]
            self.currentSong = 0
        else:
            return self.SongList[self.currentSong]


    def set_current_song(self, title):
        for i in range(len(self.SongList)):
            if self.SongList[i].getTitle() == title:
                self.currentSong = i

    def get_current_song_index(self):
        if self.currentSong == -1:
            self.set_current_song_index(0)
        return self.currentSong

    def set_current_song_index(self, index):
        self.currentSong = index

    def get_song_list(self):
        for i in range(len(self.SongList)):
            self.SongList[i].setPlaying(0) # reset all songs
        self.SongList[i].setPlaying(1) # set the one song to playing
        return self.SongList
    
    def get_song_list_dict(self):
        for i in range(len(self.SongList)):
            self.SongList[i].setPlaying(0) # reset all songs
        self.SongList[i].setPlaying(1) # set the one song to playing
        TempSongList = []
        for song in self.SongList:
            TempSongList.append(song.getDict())
        return TempSongList

    def get_song_list_list(self):
        for i in range(len(self.SongList)):
            self.SongList[i].setPlaying(0) # reset all songs
        self.SongList[self.get_current_song_index()].setPlaying(1) # set the one song to playing
        TempSongList = []
        for song in self.SongList:
            TempSongList.append(song.getList())
        return TempSongList

    
class Player():
    def __init__(self):
        self.status = {}
        self.status = "stopped" # stopped, recording, paused, playing
        self.repeat = False
        self.shuffle = False
        self.SysInter = SystemInterface()
        self.playlist_title = self.SysInter.getCurrentPlaylist()

        self.timer = Timer()
        self.playlist = Playlist(self.playlist_title, self.SysInter)
        self.commands = Commands()


    def startRecording(self, bpm):
        
        self.status = "recording"
        self.commands.startRecord(self.playlist_title,BPM=bpm, SelectedPort = self.SysInter.getCurrentInPort())
        self.timer.resetTimer()
        self.timer.startTimer()

    def stopRecording(self):
        self.status = "stopped"
        self.commands.stopRecord()
        self.timer.stopTimer()
        return self.timer.getTimeElapsed()


    def play(self, song=0):
        self.status = "playing"
        if song == 0:
            CurrentSong = self.playlist.get_current_song()
        else:
            listlist = self.playlist.get_song_list_list()
            for i in range(len(listlist)):
                #print(listlist[i][0],song)

                if listlist[i][0] == song:
                    self.playlist.set_current_song_index(i)
                    break
            self.playlist.set_current_song(song)
            CurrentSong = self.playlist.get_current_song()
        self.timer.resetTimer()
        self.commands.killAllProcesses()
        self.commands.releaseAll()
        self.commands.runCommandNoOutput([os.getcwd() + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , self.SysInter.getCurrentPortNumber(), "-c", os.getcwd() + "/playlists/" + self.playlist_title + "/" + CurrentSong.getTitle()])
        self.timer.startTimer()

    def changePlaylist(self,playlist_title):
        self.stop()
        self.status = "stopped"
        self.SysInter.setCurrentPlaylist(playlist_title)
        self.playlist_title = playlist_title
        self.playlist = Playlist(playlist_title, self.SysInter)
        self.SysInter.writeData()

    def changeTime(self, time, time2):
        currentSong = self.playlist.get_current_song()
        currentPercent = int(time)/int(time2)
        numSecondsIntoSong = int(currentPercent * currentSong.getLength())
        BPM = currentSong.getUserBPM()
        self.commands.killAllProcesses()
        self.commands.releaseAll()
        self.timer.resetTimer()
        self.timer.addToTimer(numSecondsIntoSong)


        self.commands.runCommandNoOutput([os.getcwd() + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , self.SysInter.getCurrentPortNumber(), "-c","-s " + str(numSecondsIntoSong),"-b " + str(BPM), os.getcwd() + "/playlists/" + self.SysInter.getCurrentPlaylist() + "/" + self.playlist.get_current_song().getLocation()])
        self.timer.startTimer()

    def stop(self):
        pass

    def pause(self):
        self.status = "paused"
        self.commands.killAllProcesses()
        self.timer.stopTimer()
        self.commands.releaseAll(self.SysInter.getCurrentPortNumber())
        self.SysInter.getCurrentPortNumber()


    def resume(self):
        self.status = "playing"
        self.commands.killAllProcesses()
        self.commands.runCommandNoOutput([os.getcwd() + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , self.SysInter.getCurrentPortNumber(), "-c","-s " + str(self.timer.getTimeElapsed()),"-b " + str(self.playlist.get_current_song().getBPM()), os.getcwd() + "/playlists/" + self.SysInter.getCurrentPlaylist() + "/" + self.playlist.get_current_song().getLocation()])
        self.timer.startTimer()

    def next(self):
        self.status = "playing"
        if self.playlist.get_current_song_index() + 1 == len(self.playlist.SongList):
            self.playlist.set_current_song_index(0)
        else:
            self.playlist.set_current_song_index(self.playlist.get_current_song_index() + 1)

    def getStatus(self):
        return self.status

    def setStatus(self, status):
        self.status = status




def timerTest():
    print("Runing tests for timer")
    result = []
    timer = Timer()
    timer.resetTimer()
    timer.startTimer()
    time.sleep(3)
    if (int(timer.getTimeElapsed()) == 3):
        print("PASS")
    else:
        print("FAIL")
    
    time.sleep(2)
    timer.stopTimer()
    time.sleep(2)
    if (int(timer.getTimeElapsed()) == 5):
        print("PASS")
    else:
        print("FAIL")
    timer.addToTimer(5)
    if (int(timer.getTimeElapsed()) == 10):
        print("PASS")
    else:
        print("FAIL")
    timer.startTimer()
    time.sleep(2)
    timer.stopTimer()
    if (int(timer.getTimeElapsed()) == 12):
        print("PASS")
    else:
        print("FAIL")
    timer.startTimer()
    print(timer.getTimeElapsed())

    timer.resetTimer()
    if (int(timer.getTimeElapsed()) == 0):
        print("PASS")
    else:
        print("FAIL", timer.getTimeElapsed())
    
    timer.addToTimer(5)
    timer.startTimer()
    timer.stopTimer()
    if (int(timer.getTimeElapsed()) == 5):
        print("PASS")
    else:
        print("FAIL", timer.getTimeElapsed())
    
    

def playlistTest():
    playlist = Playlist("midirec-default", SystemInterface())
    print(playlist.get_song_list()[0].getLocation())

def playerTest():
    player = Player()
    print(player.playlist.get_current_song().getTitle())
    player.next()
    print(player.playlist.get_current_song().getTitle())
    #print(player.playlist.get_song_list_dict())
    
def SystemInterfaceTest():
    sysInter = SystemInterface()
    sysInter.writeData()

if __name__ == "__main__":

    SystemInterfaceTest()
    playerTest()
    playlistTest()
    timerTest()
    print("OVERLAY\t<input id=ren_input type=text value=\"")
    print("\"><a class=button style=\"top:10%;left:75%;width:20%\" onclick=\"var title = gebi('ren_input').value.toLowerCase().replace(/[^a-z\\d]+/g,'-'); sendRequest('ren-confirm/$status->{selected_file}/'+title,this)\">RENAME</a>\nFOCUS\tren_input\nKEYBOARD\tren_input\n")