import subprocess
import os
import mido
import json
import time
import pprint
from math import floor

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
                if tmp in vars:
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
        self.pid = []
        all_settings=[
            'inPort',
            'outPort',
            'backend',
            {'playbackspeed':0.0},
            {'releaseallmidi':'empty.mid'}
        ]
        self.settings = Settings(settingsfile,all_settings)
        if backend == 'mido':
            self.backend = backend
        ports = self.getPorts()
        print(self.settings)
        
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
        else:
            ports = Commands.Commands().runCommand(['aplaymidi', '--list'])
            ports = ports.split('\n')
            ports.pop(0)
            returnVal = []
            for port in ports:
                port = port.split()
                if len(port) < 3:
                    continue
                returnVal.append(port[0] + " " + port[1] + " " + port[2])
            return {'outputs':returnVal,'inputs':returnVal}

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
                self.settings.outPort = self.getPorts()['outputs'][0]
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
        else:
            print("arecordmidi","--port",self.settings.inPort,"-b", str(BPM),"./" + filename + ".mid")
            self.runCommandNoOutput(["arecordmidi", "--port" , SelectedPort, "-b", str(BPM),"./" + filename + ".mid"])


    def stopRecord(self):

        self.killAllProcesses(1)


    def playmido(self, midofile, meta_messages=False, speed=1.0):
        """Taken from mido library"""
        start_time = time.time()
        input_time = 0.0

        for msg in midofile:
            input_time += msg.time

            playback_time = time.time() - start_time
            duration_to_next_event = (input_time - playback_time) * 1.0

            if duration_to_next_event > 0.0:
                time.sleep(duration_to_next_event)

            if isinstance(msg, mido.MetaMessage) and not meta_messages:
                continue
            else:
                yield msg

    def playFile(self, file, speed=1.0):
        if self.backend == 'mido':
            msgs = []
            if type(file) == str:
                msgs = self.load_midi(file)
            else:
                msgs = file
            port = mido.open_output(self.settings['outPort'])
            for msg in self.playmido(msgs, speed):
                port.send(msg)

    def scanalyzeme(self, msgs):
        songlen = 0.0
        if type(msgs) == str:
            msgs = self.load_midi(msgs)

        tmplist = {}
        for i, msg in enumerate(msgs):
            songlen += msg.time
            timestamps = []
            if (songlen - floor(songlen)) < 0.2:
                if str(floor(songlen)) in tmplist.keys():
                    pass
                else:
                    tmplist[str(float(floor(songlen)))] = [i,songlen]

            elif (songlen - floor(songlen)) < 0.75 and (songlen - floor(songlen)) > 0.4:
                if str(floor(songlen) + 0.5) in tmplist.keys():
                    pass
                else:
                    tmplist[str(floor(songlen) + 0.5)] = [i,songlen]
            elif (songlen - floor(songlen)) > 0.9:
                if str(floor(songlen) + 1) in tmplist.keys():
                    pass
                else:
                    tmplist[str(float(floor(songlen)) + 1)] = [i,songlen]
        return tmplist


    def load_midi(self, filen):
        msgs = []
        print(filen)
        for msg in mido.MidiFile(filen):
            #time.sleep(msg.time)
            if not msg.is_meta:
                msgs.append(msg) # load all messages into ram
        return msgs
        

    def seek(self, msgs, timestamps, time):
        songlen = 0.0
        if type(msgs) == str:
            filen = msgs
            msgs = self.load_midi(msgs)
        nums = [float(x) for x in timestamps.keys()]
        absolute_difference_function = lambda list_value : abs(list_value - float(time))
        closest_value = str(min(nums, key=absolute_difference_function))

        return {'index':timestamps[str(closest_value)],'messages':msgs[int(timestamps[str(closest_value)][0]):],'offset':(float(closest_value) - float(time))}

    def releaseAll(self):
        if type(self.settings['releaseallmidi']) == str:
            self.settings['releaseallmidi'] = self.scanalyzeme(self.settings['releaseallmidi']) # read file into memory
        self.playFile(self.settings['releaseallmidi'])


if __name__ == '__main__':
    p = midiinterface('mido')
    print(p.getPorts())
    # print(p.settings)
    tmp = p.scanalyzeme('RebeccaTest.mid')
    song = p.seek('RebeccaTest.mid', tmp, 60)
    tmp = p.getPorts()
    p.selectOutPort(tmp['outputs'][2])
    print(p.settings['outPort'])
    p.playFile(song['messages'])
    p.releaseAll()
    
    