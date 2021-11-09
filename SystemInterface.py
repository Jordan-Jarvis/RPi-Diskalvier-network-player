import mido
import time
import mpserver.midi.timer as timer
import os
import json
import mpserver.Commands as Commands
class SystemInterface():
    import subprocess
    def __init__(self):
        self.pid = []
        self.settings = {}
        self.getSettings("settings.json")
        print(self.settings["ports"])

    def getSettings(self, configFile):
        self.configFile = configFile

        if os.path.exists(os.getcwd() + "/" + configFile):
            with open(os.getcwd() + "/" + configFile) as f:
                self.settings = json.load(f)
            ports = self.getPorts()
            self.getPlaylists()
            print(self.settings["playlists"])
            self.settings["ports"] = ports
            if self.settings["selectedPort"] not in self.settings["ports"]:
                self.settings["selectedPort"] = self.settings["ports"][0]
            if self.settings["selectedInPort"] not in self.settings["ports"]:
                self.settings["selectedInPort"] = self.settings["ports"][0]
            if self.settings["playlist"] not in self.settings["playlists"]:
                self.settings["playlist"] = self.settings["playlists"][0]
            
        else:
            self.settings = {}
            self.settings["selectedPort"] = self.getPorts()[0]
            self.settings["selectedInPort"] = self.getPorts()[0]
            self.settings["playlist"] = "Classical-I"
            self.settings["ports"] = self.getPorts()
            self.writeData()
        return self.settings

    def getPlaylists(self):
        playlists = []
        return playlists
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

    def getPorts(self):
        ports = Commands.Commands().runCommand(['aplaymidi', '--list'])
        ports = ports.split('\n')
        ports.pop(0)
        returnVal = []
        for port in ports:
            port = port.split()
            if len(port) < 3:
                continue
            returnVal.append(port[0] + " " + port[1] + " " + port[2])
        return returnVal
import subprocess 
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