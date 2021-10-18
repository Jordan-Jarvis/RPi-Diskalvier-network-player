from abc import abstractmethod
from typing import List

from tinytag import TinyTag

from mpserver.grpc import mmp_pb2 as proto
import mpserver.Commands as Commands
#from mpserver.midi import StartApp

class Protoble:
    """
    This class makes sure the extended class is able to represent as a protobuf object
    Which then can be used to transfer over a network
    """

    @abstractmethod
    def to_protobuf(self):
        """
        This method makes a protobuf object from this class

        :return: this class as protobuf object
        """
        return None

import os
import json
import os.path, time
class Song:
    
    def __init__(self, fileLocation, playlist, systemSettings, autoWriteData = False):
        
        self.autoWriteData = autoWriteData
        self.songData = {}
        self.newData = False
        self.cwd = os.getcwd()
        self.playlist = playlist
        self.systemInter = systemSettings

        if os.path.exists(fileLocation + ".json"):
            with open(fileLocation + ".json") as f:
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

class UnreadableFileError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


import mido
class SongModel(Protoble):
    """ A song model which is used to store song information """

    def __init__(self, title: str, filepath: str):
        super(SongModel, self).__init__()
        self.id = id(self)
        self.title = title
        self.filepath = filepath
        self.songData = {}
        # This operation can go wrong when another program is using the filepath
        if not filepath.endswith('.mid'):
            try:
                self._tags = TinyTag.get(self.filepath, False, True)
                print(self._tags)
                self.duration = round(self._tags.duration)
            except:
                self.duration = None
        else:
            if os.path.exists(filepath + ".json"):
                with open(filepath + ".json") as f:
                    self.songData = json.load(f)
            else:
                try:
                    self.songData['title'],self.songData["date"],self.songData["time"], self.songData["duration"],self.songData["bpm"],self.songData["userBPM"], self.songData["location"],self.songData["stars"],self.songData["playing"], self.songData["disk"] = self.getMidiInfo(filepath)
                except TypeError:
                    print(filepath, "is not readable and will be skipped.")
                    raise UnreadableFileError('UnreadableFileError',"The file "+ filepath + " is not readable by mido")
                self.newData = True
                # if self.autoWriteData:
                self.writeData(filepath)
            self._tags = self.songData
            try:
                self.duration = self.songData["duration"] 
            except KeyError:
                self.songData['title'],self.songData["date"],self.songData["time"], self.songData["duration"],self.songData["bpm"],self.songData["userBPM"], self.songData["location"],self.songData["stars"],self.songData["playing"], self.songData["disk"] = self.getMidiInfo(filepath)
                self.writeData(filepath)
                self.duration = self.songData["duration"] 


                  
    def getMidiInfo(self, fileLocation):
        print(fileLocation)
        midiFile = mido.MidiFile(fileLocation)
        mid = []
        midiinfo = Commands.Commands().runCommand([os.getcwd() + '/mpserver/midi/metamidi/metamidi', '-l' , fileLocation])
        
        midiinfo = midiinfo.split(';')
        try:
            return fileLocation, 0, "6:15 pm", midiFile.length, int(midiinfo[6].split(',')[0].split('.')[0]), int(midiinfo[6].split(',')[0].split('.')[0]), fileLocation, "4",0,"1"
        except:
            print("DSFAASDDDDDDDDDDDDDDDDDDDDDDD")

    def writeData(self, fileLocation):
        with open(fileLocation + ".json", 'w') as json_file:
            json.dump(self.songData, json_file)

    def to_protobuf(self) -> proto.Song:
        s = proto.Song()
        s.id = self.id
        s.title = self.title
        s.duration = int(self.duration)
        return s


class AlbumModel(Protoble):
    """ Album class which is used to store album information """

    def __init__(self, title: str, location: str):
        """
        :param title:
        :param location:
        """
        super(AlbumModel, self).__init__()
        self.id = id(self)
        self.title = title
        self.location = location
        self.songlist = []  # type: List[SongModel]

    def getsong(self, song_id: int):
        """
        Gets a song from this album by ID or False if not found
        :rtype: SongModel
        """
        return self.songlist[song_id] if len(self.songlist) >= song_id > 0 else None

    def getsonglist(self) -> List[SongModel]:
        return self.songlist

    def set_song_list(self, songlist: list):
        self.songlist = songlist

    def to_protobuf(self) -> proto.Album:
        a = proto.Album()
        a.id = self.id
        a.title = self.title
        lis = []
        for song in self.songlist:
            try:
                lis.append(song.to_protobuf())
            except TypeError:
                print("error on", a.title)
        a.song_list.extend(lis)

        return a
