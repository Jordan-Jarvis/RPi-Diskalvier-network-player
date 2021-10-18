import mpserver.midi.Playlist as Playlist
import mpserver.midi.SystemInterface as SystemInterface
import mpserver.midi.timer as timer
import time
import mpserver.Commands as Commands
import os
class Player():
    def __init__(self):
        self.status = {}
        self.status = "stopped" # stopped, recording, paused, playing
        self.repeat = False
        self.shuffle = False
        self.playNext = True
        self.SysInter = SystemInterface.SystemInterface()
        self.playlist_title = self.SysInter.getCurrentPlaylist()

        self.timer = timer.Timer()
        self.playlist = Playlist.Playlist(self.playlist_title, self.SysInter)
        self.commands = Commands.Commands()
        self.song = 0

    def get_time(self):
        self.timer.stopTimer()
        temp = int(self.timer.getTimeElapsed())
        self.timer.startTimer()
        return temp

    def get_position(self):
        if self.song == 0:
            return 0
        return self.get_time()/self.song.duration
        

    def startRecording(self, bpm):
        
        self.status = "recording"
        print(self.SysInter.getCurrentInPortNumber())
        self.commands.startRecord(BPM=bpm, SelectedPort = self.SysInter.getCurrentInPortNumber())
        self.timer.resetTimer()
        self.timer.startTimer()

    def stopRecording(self):
        self.status = "stopped"
        self.commands.stopRecord()
        self.timer.stopTimer()
        timeel = self.timer.getTimeElapsed()

        return timeel

    def play(self, song=0):
        self.song = song
        self.status = "playing"
        self.timer.resetTimer()
        self.commands.killAllProcesses()
        self.commands.releaseAll(self.SysInter.getCurrentPortNumber())
        self.commands.runCommandNoOutput([os.getcwd() + "/mpserver/midi/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , self.SysInter.getCurrentPortNumber(), "-c", os.getcwd() + "/" + self.song.filepath])
        self.timer.startTimer()

    def changePlaylist(self,playlist_title):
        self.stop()
        self.status = "stopped"
        self.SysInter.setCurrentPlaylist(playlist_title)
        self.playlist_title = playlist_title
        self.playlist = Playlist(playlist_title, self.SysInter)
        self.SysInter.writeData()

    def changeTime(self, currentPercent):
        currentSong = self.song
        numSecondsIntoSong = int(currentPercent * currentSong.duration)
        BPM = currentSong.songData["userBPM"]
        self.commands.killAllProcesses()
        self.commands.releaseAll(self.SysInter.getCurrentPortNumber())
        self.timer.resetTimer()
        self.timer.addToTimer(numSecondsIntoSong)


        self.commands.runCommandNoOutput([os.getcwd() + "/mpserver/midi/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , self.SysInter.getCurrentPortNumber(), "-c","-s " + str(numSecondsIntoSong),"-b " + str(BPM), os.getcwd() + "/" + self.song.filepath])
        self.timer.startTimer()

    def stop(self):
        pass

    def getContinue(self):
        return self.playNext

    def getContinueGUI(self):
        if self.playNext == "0":
            return "dis"
        else:
            return "ena"

    def setContinue(self, truefalse):
        self.playNext = truefalse

    def pause(self):
        if self.status == "paused":
            return
        self.status = "paused"
        self.commands.killAllProcesses()
        self.timer.stopTimer()
        self.commands.releaseAll(self.SysInter.getCurrentPortNumber())
        time.sleep(0.5)
        self.commands.releaseAll(self.SysInter.getCurrentPortNumber())
        time.sleep(0.5)
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

    def getStatus(self, asInt = 0):
        if asInt == 0:
            return self.status
        else:
            if self.status == "playing":
                return 1
            if self.status == "paused":
                return 2
            if self.status == "stopped":
                return 0
            if self.status == "recording":
                return 3

    def setStatus(self, status):
        self.status = status

