import atexit
import subprocess
import os
import mido
import json
import time
import pprint
import src.timer
from . import Song
from math import floor
from multiprocessing import Process, Manager, Value
from mido import messages

class Settings:
    def __init__(self, settingsfile, all_settings):
        self.dictionary = {}
        self.settingsfile = settingsfile
        if os.path.exists(settingsfile):
            f = open(settingsfile)
            self.dictionary = json.load(f)
            f.close()


        self.ensure_existence(all_settings)
        self.save_settings()

    def __getitem__(self, idx):
        return self.dictionary[idx]

    def __setitem__(self, idx, setting):
        self.dictionary[idx] = setting
        self.save_settings()

    def __str__(self):
        return(pprint.pformat(self.dictionary))

    def ensure_existence(self,vars):
        for setting in vars:
            if type(setting) == str:
                if setting not in self.dictionary:
                    self.dictionary[setting] = 0

            if type(setting) == dict:
                tmp = list(setting.keys())[0]
                if tmp in list(self.dictionary.keys()):
                    continue
                self.dictionary[tmp] = setting[tmp]

    def save_settings(self):
        with open(self.settingsfile, 'w') as f:
            json.dump(self.dictionary, f, ensure_ascii=False, indent=4)
class NoPortsFound(Exception):
    pass
class InvalidPort(Exception):
    pass
class midiinterface:


    def __init__(self,backend, settingsfile = 'midisettings.json'):
        manager = Manager()
        self.status = manager.dict()
        self.pid = ''
        all_settings=[
            'inPort',
            'outPort',
            'backend',
            {"end":"end"},
            {'speed':1.0}
        ]
        self.settings = Settings(settingsfile,all_settings)
        if backend == 'mido':
            self.backend = backend
        ports = self.getPorts()
        
        print(self.settings)
        self.msgs = []
        self.status['input_time'] = 0.0
        self.status['playbacktime'] = 0.0
        self.status['status']= "stopped"

    def setPlaybackSpeed(self, speed):
        speed = float(speed)
        self.settings['speed'] = speed

        
    def set_current_song(self, song):
        self.song = song
        self.msgs = []
        self.status['input_time'] = 0.0
        self.status['playbacktime'] = 0.0

        if self.song.getTimestamps() == None:
            self.song.setTimestamps(self.scanalyzeme(self.song.getLocation()))
        self.song.set_messages(self.load_midi(self.song.getLocation()))
        

    
    def getPorts(self):
        """Check for indeces created in version 5 and upgrade them to version 6 by reindexing them.
    
    Args:
        host (str, required): The full url to the host elastic host to operate against
        dry_run (bool, required): If true, just show which restores we would do
        
    Raises:
       InvalidURL: if the host url specified isn't valid
       HTTPError: if there is an error returned from the restore operation for an index
       
       """
        returns = {}
        if self.backend == 'mido':

            returns['outputs'] = mido.get_output_names()
            returns['inputs'] = mido.get_input_names()
            return returns

    def selectInPort(self, port = 0):
        try:
            if port == 0:
                self.settings.inPort = self.getPorts()['inputs'][0]
            else:
                if port not in self.getPorts()['inputs']:
                    raise InvalidPort(f"Port {port} does not exist in the list of inputs {self.getPorts()['inputs']}")
                self.settings.inPort = self.getPorts()['inputs']
        except IndexError:
            raise NoPortsFound("Couldn't detect any ports")

    def selectOutPort(self,port = 0):
        
        try:
            if port == 0:
                self.settings['outPort'] = self.getPorts()['outputs'][0]
            else:
                if port not in self.getPorts()['outputs']:
                    raise InvalidPort(f"Port {port} does not exist in the list of outputs {self.getPorts()['outputs']}")
                self.settings['outPort'] = port
                
                
        except IndexError:
            raise NoPortsFound("Couldn't detect any ports")

    def startRecord(self, filename = "Title", BPM = 120 ):
        if self.backend == 'mido':
            port = mido.open_output(self.settings.outPort)
            for msg in mido.MidiFile(filename).play():
                if self.stop == True:
                    break
                port.send(msg)

    def stopRecord(self):

        self.killAllProcesses(1)





    def playFile(self, file, offset=0, speed=1.0, status = "", startingindex = 0):
        print("Playing")
        try:
            self.outport = mido.open_output(self.settings['outPort'])
        except:
            self.selectOutPort()
            self.outport = mido.open_output(self.settings['outPort'])

            
        self.outport.reset()

        if self.backend == 'mido':
            msgs = []
            self.song = file
            # if type(file) == str:
            #     msgs = self.load_midi(file)
            # elif type(file) == Song:
                
            # else:
            #     msgs = file

            status['status'] = 'playing'
            status['playback_time'] = 0.0
            status['start_time']  = 0.0
            status['input_time'] = 0.0
            if isinstance(offset, list):
                status['input_time'] = offset[1]
                offset = offset[1]-offset[2]
            try:
                time.sleep(offset)
            except ValueError:
                pass
            status['start_time'] = time.time() - (offset + status['input_time'])
            looping = 0
            for msg in self.song.get_messages()[startingindex:]:
                status['input_time'] += msg.time * (1/speed) 
                

                status['playback_time'] = time.time() - status['start_time']
                duration_to_next_event = (status['input_time'] - status['playback_time']) 
                while status['status'] != 'playing':
                    looping = 1
                    if status['status']  == 'pausing':
                        status['playbacktime'] = status["playback_time"]
                        status['status'] = 'paused'
                        self.outport.reset()
                    elif status['status'] == 'paused':

                        time.sleep(.2)
                            
                    if status['status'] == 'stopping':
                        self.outport.close()
                        status['status'] = 'stopped'
                        return

                if looping == 1:
                    looping = 0
                    status['playback_time'] = status['playbacktime']
                    status['start_time'] = time.time() - status['playback_time']
                if duration_to_next_event > 0.0:
                    time.sleep(duration_to_next_event)

                if isinstance(msg, mido.MetaMessage):
                    continue
                else:
                    self.outport.send(msg)
                    



            self.outport.reset()
            status['status'] = 'played'


    def play(self, offset=0,speed=1, startingindex = 0):
        if type(self.pid) != str:
          if self.pid.is_alive() == True:
            self.pid.terminate()
        self.status['status'] = "playing"
        self.pid = Process(target=self.playFile, args=(self.song, offset, self.settings['speed'], self.status, startingindex))
        self.pid.start()
        print(self.pid)
        
        
    def resume(self):
        self.status['status'] = "playing"


    def pause(self):
        self.status['status'] = 'pausing'

    def get_playback_time(self):
        if self.status['status'] == "playing":
            return(time.time() - self.status['start_time'])
        else:
            return(self.status['playbacktime'])

    def stop(self):
        self.status['playbacktime']=0.0
        if self.status["status"] != "playing":
            self.status["status"] = "stopped"
            return
        if self.status["status"] == "playing":
            self.status["status"] = "stopping"
        while self.status["status"] != "stopped":
            time.sleep(0.1)



    def scanalyzeme(self, msgs):
        songlen = 0.0
        if type(msgs) == str:
            msgs = self.load_midi(msgs)

        tmplist = {}
        x=0
        songlen = 0
        for k in range(0,int(floor(self.song.getLength()))* 2):
            j = k/2
            try:
                while songlen < j:
                    songlen += msgs[x].time
                    x += 1
                tmplist[str(j)] = [x, songlen]
            except IndexError:
                break

        for i, msg in enumerate(msgs):
            songlen += msg.time


        return tmplist


    def load_midi(self, filen):
        msgs = []
        print(filen)
        for msg in mido.MidiFile(filen):
            #time.sleep(msg.time)

            if not msg.is_meta:
                msgs.append(msg) # load all messages into ram
        self.msgs = msgs
        return msgs
        
    def seek(self, percent):
        if percent > 1:
            percent = 1
        if percent < 0:
            percent = 0
        timestamps = self.song.getTimestamps()
        songlen = self.song.getLength()
        seconds = songlen * percent
        print(seconds)
        key = str(round(seconds*2)/2)
        print(key)
        while True:
            if key  == "0.0":
                return 0
            try:
                print(timestamps[key])
                break
            except:
                print("Dictionary error! key out of range")
                key = str(float(key)-0.5)
        timestamps[key].append(seconds)
        return timestamps[key]
        
    def releaseAll(self):
        try:
            self.outport
        except:
            self.outport = mido.open_output(self.settings['outPort'])

        self.outport.close()

import argparse

if __name__ == '__main__':
    manager = Manager()

    parser = argparse.ArgumentParser(description='Restore all snapshots for the specified index within the given timeframe (years)')

    parser.add_argument('--clear',
                        type=str,
                        default='',
                        help='Required, api key for imperva')
    args = parser.parse_args()

    p = midiinterface('mido')
    atexit.register(p.releaseAll)
    rtest = Song.Song("RebeccaTest.mid")
    
    p.set_current_song(rtest)
    tmp = p.getPorts()
    print(tmp)
    p.selectOutPort(tmp['outputs'][2])
    if args.clear != "":
        p.releaseAll()
        exit()

    print(p.settings['outPort'])
    p.play()
    time.sleep(4)
    p.pause()
    for val in range(3):
        print(p.get_playback_time())
        time.sleep(2)
    print(p.get_playback_time())

    p.resume()
    time.sleep(3)
    p.stop()
    vals = p.seek(0.9)
    print(vals)
    p.play(offset = vals,startingindex=vals[0],speed= 0.3)
    while p.pid.is_alive() == True:
        time.sleep(0.2)
        print(time.time() - p.status['start_time'] )



    
    