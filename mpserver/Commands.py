import subprocess
import os
class Commands():
    def __init__(self):
        self.pid = []
        pass
    
    def startRecord(self, SelectedPort, filename = "Title", BPM = 120 ):
        print("arecordmidi","--port",SelectedPort,"-b", str(BPM),"./" + filename + ".mid")
        self.runCommandNoOutput(["arecordmidi", "--port" , SelectedPort, "-b", str(BPM),"./" + filename + ".mid"])

    def stopRecord(self):

        self.killAllProcesses(1)


    def releaseAll(self, SelectedPort):
        self.runCommandNoOutput([os.getcwd() + "/mpserver/midi/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c", os.getcwd() + "/mpserver/midi/empty.mid"])
        self.runCommandNoOutput([os.getcwd() + "/mpserver/midi/alsa-utils-1.2.2/seq/aplaymidi/aplaymidi", "-p" , SelectedPort, "-c", os.getcwd() + "/mpserver/midi/empty.mid"])

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

    def killAllProcesses(self, nice = 0):
        for p in self.pid:
            print(len(self.pid))
            if nice == 0:
                try:
                    os.kill(p, 9)
                    print("killed" + str(p))
                    os.kill(p, 9)
                except OSError: 
                    print("The process: " + str(p) + " is already dead.")

            else:
                self.runCommand(["kill", "-SIGINT",str(p)])

        for i in range(len(self.pid)):
            self.pid.pop()

