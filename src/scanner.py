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
        self.db.autocommit = True
        self.cursor = self.db.cursor()
    
    def __del__(self):
        self.cursor.close()

    
    def scan(self):
        playlists = [name for name in os.listdir(self.folder) if os.path.isdir(self.folder + "/" + name)]
        for playlist in playlists:
            self.insert_playlist(playlist)
            print(playlist)

                
    def insert_to_db(self, statement):
        pass
        
    def get_from_db(self, query):
        pass
    
    def insert_playlist(self, playlist_name):
            songs_in_playlist = [name for name in os.listdir(self.folder + "/" + playlist_name) if (not os.path.isdir(name)) and name.endswith(('.mid','.midi'))]
            song_titles = [val for val in songs_in_playlist if not (len(list(self.sql("SELECT title from song where title=%s;",vars=(val,),returning=True, fetchall=True)))) > 0]
            # currently have tuples
            song_ids = []
            for song in song_titles:
                try:
                    tmp_song = Song(self.folder + "/" + playlist_name + "/" + song,1)
                except TypeError:
                    print("Cannot read " + song)
                    continue
                try:
                    tmp_song.getTitle()
                    song_ids.append(self.insert_song(tmp_song))
                    
                except KeyError:
                    continue
                print("hhhh")
            print(song_ids)

            song_ids = [id[0] for id in song_ids]
            print(playlist_name)
            # exit()
            # get song ids and create list
            # create song list
            # create playlist connected to song list
            
            playlist_id = self.sql("INSERT INTO playlist (title, folderLocation) Values (%s,%s) RETURNING id;",vars=(playlist_name, f'{self.folder}/{playlist_name}'))
            songslist = []
            for i, song in enumerate(song_ids):
                songslist.append((playlist_id[0],song))
            for song in songslist:
                #STILL DUPLICATING ENTRIES! FIX IT!
                songlist = f"INSERT INTO songlist (listID, songID) VALUES (%s, %s) RETURNING id;"
                self.sql(songlist,vars=song)

            # alter playlist
            # self.sql(f"UPDATE playlist SET listID = {songlist_id[0]} WHERE id = {playlist_id[0]};", returning=False)


            
                
            
            
    
    def insert_songlist(self, playlist_id):
        pass
    
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


    def insert_song(self, song: Song) -> int:
            title=song.getTitle().split('/')[-1]
            rating=song.getStars()
            filelocation=song.getLocation()
            BPM=song.getBPM()
            len=song.getLength()
            numplays=3
            print(f"Adding song {title}")
            sql= "INSERT INTO Song (title, rating, filelocation, BPM, len, numplays) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
            try:
                song_id = self.sql(sql, vars=(title,rating,filelocation,BPM,len,numplays))
            except psycopg2.errors.UniqueViolation:
                sql = "SELECT id FROM song WHERE title = %s AND filelocation = %s;"
                song_id = self.sql(sql,vars=(title,filelocation))
            return song_id
            
            
    