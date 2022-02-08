#this file is a placeholder for the scanner which will add midi files
# to database. It will scan recursively and add playlists based on folder name
from . import SystemInterface
from .Song import Song
import os
import psycopg2


class scanner():
    def __init__(self, db, folder, scanner = "src/metamidi/metamidi"):
        self.db = db
        self.folder = folder
        self.scanner = scanner
    
    def scan(self):
        playlists = [name for name in os.listdir(self.folder) if os.path.isdir(name)]
        for playlist in playlists:
            self.insert_playlist(playlist)

                
    def insert_to_db(self, statement):
        pass
        
    def get_from_db(self, query):
        pass
    
    def insert_playlist(self, playlist_name):
            songs_in_playlist = [name for name in os.listdir(self.folder + playlist_name) if (not os.path.isdir(name)) and name.endswith(['.mid','.midi'])]
            song_ids = [self.insert_song(Song(song,1)) for song in songs_in_playlist]
            print(playlist_name)
            # get song ids and create list
            # create song list
            # create playlist connected to song list
            
            self.sql(f"INSERT INTO playlist (title, folderLocation, listID) Values ('{playlist_name}','{self.folder}/{self.playlist_name}',1);")
            
                
            
            
    
    def insert_songlist(self, playlist_id):
        pass
    
    def sql(self, statement):
        try:
            self.db.autocommit = True
            tmp = self.db.cursor()
            tmp.execute(statement)
            self.db.commit()
            returnval = tmp.fetchone()
            tmp.close()
            return returnval
        except psycopg2.errors.UniqueViolation:
            return -1

    def insert_song(self, song: Song) -> int:
            title=song.getTitle()
            rating=song.getStars()
            filelocation=song.getLocation()
            BPM=song.getBPM()
            len=song.getLength()
            numplays=3
            sql= f"""INSERT INTO Song (title, rating, filelocation, BPM, len, numplays)
            VALUES ('{title}', {rating}, '{filelocation}', {BPM}, {len}, {numplays}) RETURNING id;"""
            song_id = self.sql(sql)
            return song_id
            
            
    