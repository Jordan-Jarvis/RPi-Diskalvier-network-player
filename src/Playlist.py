import os
import json
from . import Song
class Playlist():
    
    def __init__(self,title, systemSettings, db, cursor):
        self.db = db
        self.cursor = cursor
        self.currentSong = -1
        self.systemSettings = systemSettings
        self.SongList = []
        # query playlist table and songs 	id serial,
        songs = self.sql("SELECT s.title, s.rating, s.filelocation, s.BPM, s.len, s.numplays from playlist as p join songlist as sl on p.id=sl.listid join song s on sl.songid=s.id where p.title=%s",fetchall=True, vars=(title,))
        print(songs[0])
        for song in songs:
            self.SongList.append(Song.Song(song[2],self.db,prepopdata=song, autoWriteData=True))
        
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
        return self.SongList
    
    def get_song_list_dict(self):
        TempSongList = []
        for song in self.SongList:
            TempSongList.append(song.getDict())
        return TempSongList

    def get_song_list_list(self):
        TempSongList = []
        for song in self.SongList:
            TempSongList.append(song.getList())
        return TempSongList