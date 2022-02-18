import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
from . import Playlist
import time
from . import midiinterface
from . import SystemInterface
import os
import json
 
 

from .Song import Song
class MusicQueue():
    def __init__(self):
        pass
        self.songs = []
        self.position = 0
        self.shuffle = 0

    def addSong(self, song):
        if isinstance(song, Song):
            self.songs.append(song)

    def addSongs(self, songlist):
        if isinstance(songlist, list):
            try:
                if isinstance(songlist[0], Song):
                    self.songs.extend(songlist)
            except IndexError:
                pass

    def removeSong(self, song=0, index=0):
        if isinstance(song, Song):
            index = self.songs.index(song)
            self.songs.remove(Song)
            try:
                if index < self.position:
                    self.position -= 1
            except IndexError:
                pass
        else:
            self.songs.pop(index)
    
    def reset(self):
        self.songs  = []
        
    def getCurrentSong(self):
        try:
            return self.songs[self.position]
        except IndexError:
            try:
                self.position  = 0
                return self.position
            except IndexError:
                return 0


    def setCurrentSongIndex(self, index):
        if index > -1 and index <=len(self.songs):
            self.position= index

    def nextSong(self):
        if len(self.songs) > 0:
            try:
                self.position += 1
                self.songs[self.position]

            except IndexError:
                self.position = 0
    
    def previousSong(self):
        if len(self.songs) > 0:
            try:
                self.position -= 1
                self.songs[self.position]

            except IndexError:
                self.position = len(self.songs)

    def setCurrentSong(self, song):
        if isinstance(song, str):
            for val in self.songs:
                if val.getLocation() == song:
                    pass
        self.position += 1
        self.songs.insert(self.position)

    def toJSON(self):
        jsondict = {'songs':[]}

        for val in self.songs:
            jsondict['songs'].append( val.songData)
        jsondict['position'] = self.position
        return jsondict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class Player(midiinterface.midiinterface):

    def __init__(self,db, musicfolder):
        super().__init__(backend="mido",settingsfile = 'midisettings.json')
        scheduler = BackgroundScheduler()
        self.db = db
        self.cursor = self.db.cursor()

        scheduler.add_job(self.refreshData, 'interval', seconds=1.5)
        scheduler.start()

        #Need to do, Create playlist scraper/auto generator for DB, change folder based playlist into DB based

        self.repeat = False
        self.shuffle = False
        self.playNext = True
        self.SysInter = SystemInterface.SystemInterface()
        self.queue = MusicQueue()
        self.playlist_title = self.settings['lastplaylist']
        if self.playlist_title == 0:
            self.playlist_title = self.sql("SELECT title from playlist")[0]
        self.playlist = Playlist.Playlist(f"{self.playlist_title}", self.SysInter,self.db, self.cursor)
        self.queue.addSongs(self.playlist.get_song_list())
        self.song = 0
        self.getLastSong()
        
    def sql(self, statement,returning=True,vars=None,fetchall=False, many=False):
    
        if many:
            self.cursor.executemany(statement, vars)
        else:
            self.cursor.execute(statement, vars=vars)
        self.db.commit()
        if returning:
            if fetchall:
                returnval=self.cursor.fetchall()
            else:
                returnval = self.cursor.fetchone()
            return returnval
        else:
            return

    def refreshData(self):
        if self.status['status'] == 'played':
            # if self.playNext:
                print("PLAYING NEXT SONG")
                self.next()
                self.play()

    def getLastSong(self):
        self.queue.nextSong()
        self.set_current_song(self.queue.getCurrentSong())

    def nowPlayingJSON(self):
        returndata = {}
        returndata["repeat"]  = self.repeat
        returndata["shuffle"]  = self.shuffle
        returndata["playNext"]  = self.playNext
        returndata["playbackData"]  = dict(self.status)
        try:
            returndata["currentSong"]  = self.song.songData
        except AttributeError:
            returndata['currentSong'] = None
        return json.dumps(returndata)


    def startRecording(self, bpm):
        
        print(self.SysInter.getCurrentInPortNumber())
        self.commands.startRecord(BPM=bpm, SelectedPort = self.SysInter.getCurrentInPortNumber())
        self.timer.resetTimer()
        self.timer.startTimer()

    def stopRecording(self):
        self.commands.stopRecord()
        self.timer.stopTimer()
        timeel = self.timer.getTimeElapsed()

        return timeel

    def getplaylists(self): 
        return self.playlist
    
    def getplaylist(self, playlist):
        return self.playlist

    def getQueue(self):
        return self.queue.songs()

    def changePlaylist(self,playlist_title):
        self.stop()
        self.SysInter.setCurrentPlaylist(playlist_title)
        self.playlist_title = playlist_title
        self.playlist = Playlist(playlist_title, self.SysInter)
        self.SysInter.writeData()


    def getContinue(self):
        return self.playNext

    def getContinueGUI(self):
        if self.playNext == "0":
            return "dis"
        else:
            return "ena"

    def setContinue(self, truefalse):
        self.playNext = truefalse

    def next(self):
        self.stop()
        self.queue.nextSong()
        self.set_current_song(self.queue.getCurrentSong())

    def previous(self):
        self.stop()
        self.queue.previousSong()
        self.set_current_song(self.queue.getCurrentSong())


if __name__ == "__main__":
    print("testing")
    p = Player()
    print(p.playlist.get_current_song())
    p.set_current_song(p.queue.getCurrentSong())
    p.play(speed=1)
    time.sleep(9)
    p.stop()
    p.play()
    time.sleep(2)
    # p.play(speed= 2)
    p.next()
    p.play()
    time.sleep(30)