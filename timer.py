import time
class Timer:
    def __init__(self):
        self.SongTime = [0,0]
        self.stopped = True

    def getTimeElapsed(self):
        if self.SongTime[0] == 0 and self.stopped == False:
            return self.SongTime[1]
        if self.stopped == True:
            return self.SongTime[1]
        else:
            print("RUNNIN", self.SongTime[1])
            return time.time() + self.SongTime[1] - self.SongTime[0]


    def resetTimer(self):
        self.SongTime[0] = 0
        self.SongTime[1] = 0
        self.stopped = True

    def startTimer(self, verbose = False):
        if self.stopped == True:
            self.SongTime[0] = time.time() - self.SongTime[1] # add time that already existed
            self.stopped = False
        else:
            if verbose == True:
                print("ERROR, Timer already started!")

    def stopTimer(self, verbose = False):
        if self.stopped == False:
            self.SongTime[1] = time.time() - self.SongTime[0]
            self.stopped = True
        else:
            if verbose == True:
                print("ERROR, Timer already stopped!")
        
    def addToTimer(self,timeToAdd):
        self.SongTime[1] = self.SongTime[1] + timeToAdd
