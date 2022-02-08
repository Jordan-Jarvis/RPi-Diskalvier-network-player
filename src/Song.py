import os
import json
import os.path, time
import mido
import sys
import psycopg2
platform = sys.platform
from . import SystemInterface
Systeminterface = SystemInterface.SystemInterface()
class Song:
    
    def __init__(self, fileLocation, db, autoWriteData = False):
        self.db=db
        self.autoWriteData = autoWriteData
        self.songData = {}
        self.newData = False
        self.cwd = os.getcwd()



        if os.path.exists(fileLocation + '.json'):
            with open(fileLocation + ".json") as f:
                self.songData = json.load(f)
        else:
            self.songData['title'],self.songData["date"],self.songData["time"], self.songData["length"],self.songData["bpm"],self.songData["userBPM"], self.songData["location"],self.songData["stars"],self.songData["playing"], self.songData["disk"] = self.getMidiInfo(fileLocation)
            self.newData = True
            if self.autoWriteData:
                self.writeData()
    
    def save_to_db(self):
        try:
            self.db.autocommit = True
            title=self.getTitle()
            rating=self.getStars()
            filelocation=self.getLocation()
            BPM=self.getBPM()
            len=self.getLength()
            numplays=3
            tmp = self.db.cursor()
            sql= f"""INSERT INTO Song (title, rating, filelocation, BPM, len, numplays)
            VALUES ('{title}', {rating}, '{filelocation}', {BPM}, {len}, {numplays});"""
            tmp.execute(sql)
            self.db.commit()
            tmp.close()
        except psycopg2.errors.UniqueViolation:
            pass

    
    def toJSON(self):
        return json.dumps(self.songData)
                
    def getTimings(self):
        return self.songData['timings']
    
    def setTimings(self, timings):
        self.songData['timings'] = timings

    def get_messages(self):
        return self.messages

    def set_messages(self, msgs):
        self.messages = msgs

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

    
    def getMidiInfo(self, file):
        if platform == 'windows':
            ext = '.exe'
        else:
            ext = ""
        
        midiFile = mido.MidiFile(file)
        mid = []
        midiinfo = Systeminterface.runCommand([self.cwd + f'/metamidi/metamidi{ext}', '-l' , file])
        midiinfo = midiinfo.split(';')
        LastModifiedTime = self.parseDate(file)
        try:
            return file, LastModifiedTime, "6:15 pm", midiFile.length, int(midiinfo[6].split(',')[0].split('.')[0]), int(midiinfo[6].split(',')[0].split('.')[0]), file, "4",0,"1"
        except:
            print(midiinfo)
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
        with open(self.getLocation() + ".json", 'w') as json_file:
            json.dump(self.songData, json_file)

    def getDicot(self):
        return self.songData

    def setTimestamps(self, timestamps):
        self.timestamps = timestamps
    
    def getTimestamps(self):
        try:
            self.timestamps
            return self.timestamps
        except:
            return None

    def getList(self):
        return [self.songData['title'],self.songData["date"],self.songData["time"], self.songData["length"],self.songData["bpm"],self.songData["userBPM"], self.songData["location"],self.songData["stars"],self.songData["playing"], self.songData["disk"]]
