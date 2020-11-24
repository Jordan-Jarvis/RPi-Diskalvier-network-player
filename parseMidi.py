import mido
import time
class Timer:
    def __init__(self):
        self.SongTime = [0,0]
        self.stopped = True

    def getTimeElapsed(self):
        if self.stopped == True:
            return self.SongTime[1]
        else:
            return time.time() + self.SongTime[1] - self.SongTime[0]

    def resetTimer(self):
        self.SongTime[0] = 0
        self.SongTime[1] = 0

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
    def releaseAll(self):
        self.runCommandNoOutput([os.getcwd() + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c", cwd + "/empty.mid"])
        self.runCommandNoOutput([os.getcwd() + "/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c", cwd + "/empty.mid"])

    def runCommand(self, command):
        process = subprocess.Popen(command,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout, stderr
        encoding = 'utf-8'
        print(stdout)
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
class Song:
    
    def __init__(self, fileLocation, playlist, autoWriteData = False):
        
        self.autoWriteData = autoWriteData
        self.songData = {}
        self.newData = False
        self.cwd = os.getcwd()
        self.playlist = playlist
        self.systemInter = SystemInterface()

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
        return self.songData["BPM"]

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
        return self.songData["stars"]

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
        midiFile = mido.MidiFile(self.cwd + '/playlists/' + self.playlist + "/" + fileLocation)
        mid = []
        
        midiinfo = self.systemInter.runCommand([self.cwd + '/metamidi/metamidi', '-l' , self.cwd + '/playlists/' + self.playlist + "/" + fileLocation])
        midiinfo = midiinfo.split(';')
        try:
            return fileLocation, '2020-04-20', "6:15 pm", midiFile.length, int(midiinfo[6].split(',')[0].split('.')[0]), "250", fileLocation, "4",0,"1"
        except:
            print(midiFile)

    def writeData(self):
        with open(os.getcwd() + "/playlists/" + self.playlist + "/" + self.getLocation() + ".json", 'w') as json_file:
            json.dump(self.songData, json_file)

    def getDict(self):
        return self.songData

    def getList(self):
        return [self.songData['title'],self.songData["date"],self.songData["time"], self.songData["length"],self.songData["bpm"],self.songData["userBPM"], self.songData["location"],self.songData["stars"],self.songData["playing"], self.songData["disk"]]

import os
import json
class Playlist(Song):
    def __init__(self,location):
        self.currentSong = -1
        songs = os.listdir(os.getcwd() + "/playlists/" + location)
        songs.sort()
        self.SongList = []
        for item in songs:
            if item.endswith(".mid") or item.endswith(".MID"):
                self.SongList.append(Song(item,location, autoWriteData=True))
        
        
    def refresh(self):
        pass

    def get_current_song(self):
        if self.currentSong == -1:
            return self.SongList[0]
            self.currentSong = 0
        else:
            return self.SongList[self.currentSong]


    def set_current_song(self, title):
        for i in len(self.SongList):
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

    

class Settings():
    def settings(self):
        pass



class Player():
    def __init__(self, playlist_title="midirec-default"):
        self.playing = False
        self.repeat = False
        self.shuffle = False
        self.playlist_title = playlist_title
        self.timer = Timer()
        self.playlist = Playlist(playlist_title)

    def play(self, Song=0):
        if Song == 0:
            print(self.playlist.get_current_song())
        else:
            self.playlist.set_current_song(Song)
        self.resetTimer()
        self.killAllProcesses()
        self.releaseAll()


    def pause(self):
        pass

    def resume(self):
        pass

    def next(self):
        if self.playlist.get_current_song_index() + 1 == len(self.playlist.SongList):
            self.playlist.set_current_song_index(0)
        else:
            self.playlist.set_current_song_index(self.playlist.get_current_song_index() + 1)

    def status(self):
        pass




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

def playlistTest():
    playlist = Playlist("midirec-default")
    print(playlist.get_song_list()[0].getLocation())

def playerTest():
    player = Player("Chopin")
    print(player.playlist.get_current_song().getTitle())
    player.next()
    print(player.playlist.get_current_song().getTitle())
    print(player.playlist.get_song_list_dict())
    


if __name__ == "__main__":
    playerTest()
    playlistTest()
    timerTest()