
import os
import json
import subprocess 

class SystemInterface():
    def __init__(self):
        self.pid = []
        self.settings = {}
        self.getSettings("settings.json")

    def getSettings(self, configFile):
        self.configFile = configFile

        if os.path.exists(os.getcwd() + "/" + configFile):
            with open(os.getcwd() + "/" + configFile) as f:
                self.settings = json.load(f)
            self.getPlaylists()
            print(self.settings["playlists"])
            if self.settings["playlist"] not in self.settings["playlists"]:
                self.settings["playlist"] = self.settings["playlists"][0]
            
        else:
            self.settings = {}
            self.settings["playlist"] = "Classical-I"
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

    def runCommandNoOutput(self, command, track = 1):
        process = subprocess.Popen(command)
        if track == 1:
            self.pid.append(process.pid)
        return process.pid