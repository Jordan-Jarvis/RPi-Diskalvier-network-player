import os
import json
from . import Song
class Playlist():
    
    def __init__(self,location, systemSettings, db):
        self.db = db
        self.currentSong = -1
        self.systemSettings = systemSettings
        # query playlist table and songs
        
        
        self.refresh(location) # need to do, get playlist from DB, create scanner to add songs and playlists from folder structure.
        
    
    def refresh(self, location):
        songs = os.listdir(location)
        songs.sort()
        self.SongList = []
        for item in songs:
            if item.endswith(".mid") or item.endswith(".MID"):
                try:
                    self.SongList.append(Song.Song(f"{location}/{item}",self.db, autoWriteData=True))
                    
                except FileNotFoundError:
                    raise FileNotFoundError("Could not find metamidi")
                except:
                    print("the following song is not readable and will be skipped:")
                    print(item)


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

from shutil import copyfile
