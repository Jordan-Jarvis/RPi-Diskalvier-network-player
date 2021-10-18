#!/usr/bin/env python

import os
import sys
import signal
import time
import getopt
import shlex
import re
import types
import json
from struct import pack
import random
from tempfile import mkstemp

PY3 = sys.version_info[0] == 3

if PY3:  
    # We are using Python 3.x
    from tkinter import *
    import tkinter.messagebox as tkMessageBox
    import tkinter.filedialog as tkFileDialog
    import tkinter.simpledialog as tkSimpleDialog
    import functools
else:
    # Python 2.x
    from Tkinter import *
    import tkSimpleDialog, tkFileDialog, tkMessageBox
    
# A few few globals

PlayPID = None        # PID of currently playing midi
DisplayPID = None     # PID for the display program

Version = 5.0

#######################################################
## Unified option class. This would be easier and more
## pythonic if the options and save/load functions were
## in a separate module. But, for a little program like
## this it's easier to have all the code in one file.
## This class is never instantiated. It operates much
## like a struct in C.
##
## These values are all stored in the ~/.xpmidirc.opts file
## Most can be modified in the options tab.

class Opts():

    # These are our globals. The are saved/loaded in the
    # ./xpmidiOps file. The defaults are just reasonable
    # choices and are mostly overwritten by the user prefs
    # in the file.
    FavoriteDirs = [] 
    CurrentDir =  ['.']
    Bcolor =  'white'
    Fcolor = 'medium blue'
    PlayOpts = '' 
    HumanSort = False
    MidiPlayer = 'aplaymidi' 
    KillOnAbort = True
    PDFdisplay = ''
    PDFopts = ''
    PlayListFile =  ''
    PDFsDir = []
    LastPlayDisplay = False
    LastFilePlayed = ''
    
    #######################################################
    # These variables start with '_' and are not saved into the rc file
    
    _rcFile=os.path.expanduser("~/.xpmidiOpts")
    _fullsize = False

    #######################################################
    # Functions are all staticmethod since we've not
    # instantiated the class and there is no "self".
    
    @staticmethod
    def saveopts():
        dt = {}
        for a in vars(Opts):
            if not a.startswith('_' )and  type(getattr(Opts,a)) != types.FunctionType:
                dt[a]=getattr(Opts, a)
        try:
            f = open(Opts._rcFile, "w")
        except:
            return
        f.write("### Xpmidi options file. Do not modify!!!!\n")
        f.write("### Created %s, version: %s\n" % (time.asctime(), Version))
        json.dump(dt, f, sort_keys=True, indent=4)

    @staticmethod
    def loadopts():
        try:
            f = open(Opts._rcFile)
        except:
            return

        f.readline()
        f.readline()
        data = json.load(f)
        
        for key, value in data.items():
            setattr(Opts, key, value)

    @staticmethod
    def cmdLine():
        """ Parse the command line. Return """
        
        try:
            opts, args = getopt.gnu_getopt(sys.argv[1:],  "vf", [])
        except getopt.GetoptError:
            Opts.usage()

        for o,a in opts:
            if o == '-v':
                print (Version)
                sys.exit(0)
            elif o == '-f':
                Opts._fullsize = True
            else:
                Opts.usage()

        # Parse remaining cmd line params. This can be 1 directory name or
        # a number of midi files.

        dcount = 0
        files = []

        for f in args:
            if os.path.isdir(f):
                dcount+=1
            elif os.path.isfile(f):
                files.append(f)
            else:
                print ("%s is an Unknown filetype") % f
                sys.exit(1)

        if dcount and files:
            print ("You can't mix filenames and directory names on the command line.")
            sys.exit(1)

        if dcount > 1:
            print ("Only 1 directory can be specified on the command line.")
            sys.exit(1)

        # Read the RC file if it exists. Set global variables
        Opts.loadopts()

        # If a dir was specified make it current
        if dcount:
            Opts.CurrentDir = [os.path.abspath(os.path.expanduser(args[0]))]

        # all done, return list of files or empty list
        return files

    @staticmethod
    def usage():
        """ Display usage message and exit. """

        text = ("Xpmidi, GUI frontend for MIDI Player",
               "(c) 2003-18, Bob van der Poel <bob@mellowood.ca>",
               "Version: %s" % Version,
               "Usage: xpmidi [opts] [dir | Midifiles]",
               "Options:",
               "   -f    start full size",
               "   -v    display version number" )
        for a in text:
            print (a)
        sys.exit(0)


####################################################################
## These functions create various frames. Maintains consistency
## between different windows (and makes cleaner code??).

def makeLabelBox(parent, justify=CENTER, row=0, column=0, text=''):
    """ Create a label box. """

    f = Frame(parent)
    b = Label(f,justify=justify, text=text)
    b.grid()
    f.grid(row=row, column=column, sticky=E+W)
    f.grid_rowconfigure(0, weight=1)

    return b

def makeButtonBar(parent, row=0, column=0, buttons=(())):
    """ Create a single line frame with buttons. """

    bf=Frame(parent)
    c=0
    for txt, cmd in buttons:
        Button(bf, text=txt, height=1, command=cmd).grid(column=c, row=0, pady=5)
        c+=1
    bf.grid(row=row, column=column, sticky=W)
    return bf

def makeListBox(parent, width=50, height=10, selectmode=BROWSE, row=0, column=0):
    """ Create a list box with x and y scrollbars. """
    
    f=Frame(parent)
    ys=Scrollbar(f)
    xs=Scrollbar(f)
    lb=Listbox(f,
               bg=Opts.Bcolor,
               fg=Opts.Fcolor,
               width=width,
               height=height,
               yscrollcommand=ys.set,
               xscrollcommand=xs.set,
               exportselection=FALSE,
               selectmode=selectmode )

    ys.config(orient=VERTICAL, command=lb.yview)
    ys.grid(column=0,row=0, sticky=N+S)

    xs.config(orient=HORIZONTAL, command=lb.xview)
    xs.grid(column=1, row=1, sticky=E+W)

    lb.grid(column=1,row=0, sticky=N+E+W+S)

    f.grid(row=row, column=column, sticky=E+W+N+S) 
    f.grid_rowconfigure(0, weight=1)   
    f.grid_columnconfigure(1, weight=1)
    
    return  lb


def makeEntry(parent, label="Label", var=None, column=0, row=0):
    f=Frame(parent)
    l=Label(f, anchor=E, width=15, padx=20, pady=10, text=label).grid(column=0, row=0)
    e=Entry(f, textvariable=var, width=30)
    e.grid(column=1, row=0, sticky=W)
    f.grid( column=column, row=row)
    
    return e

def makeCheck(parent, label="Label", var=None, column=0, row=0):
    f=Frame(parent)
    l=Label(f, anchor=E, width=15, padx=20, pady=10, text=label).grid(column=0, row=0)
    e=Checkbutton(f, anchor=W, width=30, variable=var)
    e.grid(column=1, row=0, sticky=W)
    f.grid( column=column, row=row)
    
    return e

#########################################
# We have 3 class, 1 for each window we create.


########################################
# Options dialog


class setOptions(object):

    
    def __init__(self):
        def getColor():
            return(askcolor()[-1])

        if PlayPID:  # don't set options while playing song
            return

        self.f=f=Toplevel()
        if root.winfo_viewable():  
            f.transient(root)

        bf=makeButtonBar(f, row=0, column=0, 
            buttons=(("Cancel", self.f.destroy), ("Apply", self.apply) ))

        self.tkmidi = StringVar()
        self.tkmidi.set(Opts.MidiPlayer)
        makeEntry(f, label="MIDI Player", var=self.tkmidi, row=1)

        self.tkpopt = StringVar()
        self.tkpopt.set(Opts.PlayOpts)
        makeEntry(f, label="Player Options", var=self.tkpopt, row=2)

        self.abort = BooleanVar()
        self.abort.set(Opts.KillOnAbort)
        makeCheck(f, label="Kill notes on abort", var=self.abort, row=3)
        
        self.human = BooleanVar()
        self.human.set(Opts.HumanSort)
        makeCheck(f, label="Human Sort", var=self.human, row=4)
        
        self.lastplay = BooleanVar()
        self.lastplay.set(Opts.LastPlayDisplay)
        makeCheck(f, label="Start with Last Played", var=self.lastplay, row=5)

        self.tkfcolor = StringVar()
        self.tkfcolor.set(Opts.Fcolor)
        makeEntry(f, label="Foreground Color", var=self.tkfcolor,   row=6)
        
        
        self.tkbcolor = StringVar()
        self.tkbcolor.set(Opts.Bcolor)
        makeEntry(f, label="Background Color", var=self.tkbcolor,   row=7)

        self.tkpdfd = StringVar()
        self.tkpdfd.set(Opts.PDFdisplay)
        makeEntry(f, label="PDF Display", var=self.tkpdfd, row=8)

        self.tkdispopt = StringVar()
        self.tkdispopt.set(Opts.PDFopts)
        makeEntry(f, label="PDF Options", var=self.tkdispopt, row=9)

        self.tkdispdir = StringVar()
        self.tkdispdir.set(', '.join(Opts.PDFsDir))
        makeEntry(f, label="PDF (list) Path", var=self.tkdispdir, row=10)

        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

       	f.grab_set()
        root.wait_window(f)	

 
    def apply(self): 
        Opts.MidiPlayer = self.tkmidi.get()
        Opts.PlayOpts = self.tkpopt.get()

        Opts.KillOnAbort = self.abort.get()

        if self.human.get() != Opts.HumanSort:
            Opts.HumanSort = self.human.get()
            app.updateList()

        Opts.LastPlayDisplay = self.lastplay.get()
        Opts.PDFdisplay = self.tkpdfd.get()
        Opts.PDFopts = self.tkdispopt.get()
        Opts.PDFsDir = self.tkdispdir.get().split(',')
        
        fg = self.tkfcolor.get()
        bg = self.tkbcolor.get()

        try:
            app.lb.config(fg=fg)
            Opts.Fcolor = fg
        except TclError:
            tkMessageBox.showerror("Set Forground Color", "Illegal foreground color value")

        try:
            app.lb.config(bg=bg)
            Opts.Bcolor = bg
        except TclError:
            tkMessageBox.showerror("Set Background Color", "Illegal background color value")


        self.f.destroy()


########################################
# A listbox with the favorites directory

class selectFav(object):

    def __init__(self):

        if PlayPID:
            return

        self.f=f=Toplevel()
        if root.winfo_viewable():  
            f.transient(root)

        makeLabelBox(f, text="Select Favorite Directory", row=0, column=0)

        bf=makeButtonBar(f, row=1, column=0, 
               buttons=(("Done", self.f.destroy),
                        ("Delete", self.delete),
                        ("Add Current", self.addToFav),
                        ("Select", self.select) ) )
      
        self.lb = lb = makeListBox(f, height=10, selectmode=MULTIPLE, row=2, column=0)
        lb.bind("<Double-Button-1>", self.dclick)
        
        # Make the listbox frame expandable

        f.grid_rowconfigure(2, weight=1)
        f.grid_columnconfigure(0, weight=1)

        self.updateBox()

        f.grab_set()
        f.focus_set()
        f.wait_window(f)



    def dclick(self, w):
        """ Callback for doubleclick. Just do one dir. """

        self.doSelect( [self.lb.get(self.lb.nearest(w.y))] )


    def select(self):
        """ Callback for the 'select' button. """

        l=[]
        for n in self.lb.curselection():
            l.append(self.lb.get(int(n)))
        self.doSelect(l)


    def doSelect(self, n):
        """ Update the filelist. Called from select button or doubleclick."""

        if n:
            Opts.CurrentDir = n
            app.updateList()
        self.f.destroy()


    def addToFav(self):
        """ Add the current directory (what's displayed) to favorites."""

        for n in Opts.CurrentDir:
            if n and not Opts.FavoriteDirs.count(n):
                Opts.FavoriteDirs.append(n)

        Opts.FavoriteDirs.sort()
        self.updateBox()

    def delete(self):
        """ Delete highlighted items, Called from 'delete' button. """

        l=[]
        for n in self.lb.curselection():
            l.append(self.lb.get(int(n)))

        if l:
            if tkMessageBox.askyesno("Delete Directory",
                     "Are you sure you want to delete the "
                     "highlighted directories from the favorites list?",
                      parent=self.f):

                for n in l:
                    Opts.FavoriteDirs.remove(n)

                self.updateBox()


    def updateBox(self):
        self.lb.delete(0, END)
        for n in Opts.FavoriteDirs:
            self.lb.insert(END, n)


############################
# Main display screen

class Application(object):

    # The second part ([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?) matches
    # a floating point number with optional exponential part.
    HUMAN_NUMBER_SORT_RE = re.compile(r'(.*)([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?).*')

    def __init__(self):
        """ Create 3 frames:
               bf - the menu bar
               lf - the list box with a scroll bar
               mf - a label at the bottom with the current filename.
        """

        self.msgbox = makeLabelBox(root, justify=LEFT, row=2, column=0)

        self.lb=lb = makeListBox(root, height=28, row=1, column=0)

        self.elasped = 0
       
        bf = makeButtonBar(root, row=0, column=0, buttons=(
             ("Quit", self.quitall ),
             ("Stop", self.stopPmidi ),
             ("New Dir", self.chd),
             ("Load Playlist", self.playList),
             ("Favorites", selectFav ),
             ("Options", setOptions ) ) )

    
        self.timeButton = Button(bf, width=5, height=1)
        self.timeButton.grid(column=6, row=0, padx=10)
        
        
        # Make the listbox frame expandable

        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # some bindings 

        lb.bind("<Return>",  self.loadfileRet)
        lb.bind("<Button-1>", self.loadfileClick)

        lb.bind('<Button-3>', self.stopPmidi)
        root.bind('<Escape>', self.stopPmidi)

        # This one catches the mouse hitting the window 'X' button
        root.protocol("WM_DELETE_WINDOW", self.quitall)
        root.bind('<Control-q>', self.quitall)
        root.bind('<Alt-q>', self.quitall)

        for a in 'abcdefghijklmnopqrstuvwxyz-':
            root.bind(a, self.keyPress)

        lb.bind('<F1>', self.displayOnly)
        lb.bind('<F2>', self.rotateDisplayList)
 
        for a in "=+":
            root.bind(a, self.rndSelect)

        # end bindings

        lb.focus_force()   # make the listbox use keyboard

        self.CurrentFile = None
        self.fileList = {}    # dict of files in listbox. Key is displayed name, data=actual

        if Opts.PlayListFile:
            self.playList(Opts.PlayListFile)
        else:
            self.updateList()
            if Opts.LastPlayDisplay and Opts.LastFilePlayed:
                # Step though the midi filenames to see if the last file
                # from the previous session is there. Just skip out if not.
                for x,a in enumerate(self.lb.get(0, END)):
                    if a == Opts.LastFilePlayed:
                        self.lb.update()      # needed to center slection
                        self.lb.select_clear(ACTIVE)   # needed to un-hilite existing selection
                        self.lb.see(x)        # set display for new selection
                        self.lb.activate(x)   # make it active
                        self.lb.select_set(x) # and hilighted
                        break
        self.welcome()

    def welcome(self):
        """ Display (c) message in status box. """

        if Opts.CurrentDir:
            c=', '.join(Opts.CurrentDir)
        else:
            c = ' '
        self.msgbox.config(text="XPmidi\n%s" % c)

    lastkey = ''
    lastkeytime = 0

    def rndSelect(self, ev):
        """ Callback to select a random song. """

        l = self.lb.get(0, END)

        x = random.randrange(len(l)-1)
        self.lb.select_clear(ACTIVE)   # needed to un-hilite existing selection
        self.lb.activate(x)
        self.lb.see(x)
        self.lb.select_set(x)
    

    def keyPress(self, ev):
        """ Callback for the alpha keys a..z. Finds 1st entry matching keypress. """

        c=self.lastKeyHit = ev.char.upper()

        # Timer. If there is less than 3/4 second between this key and
        # the previous we concat the keypress string. Else, start with 
        # new key.

        tm = time.time()
        delay = tm - self.lastkeytime 
        self.lastkeytime = tm     # save time of this key for next time

        if delay < .75:
            self.lastkey += c
        else:
            self.lastkey = c

        # the search target and size
        c = self.lastkey
        sz = len(c)

        l=self.lb.get(0, END)

        for x,a in enumerate(l):
            if a[0:sz].upper() >= c:
                self.lb.select_clear(ACTIVE)   # needed to un-hilite existing selection
                self.lb.activate(x)
                self.lb.see(x)
                self.lb.select_set(x)
                break
    


    """ Play a selected file. This is a listbox callback. 
        Two callback funcs are needed: one for a mouse click,
        the other for a <Return>.
    """

    def loadfileRet(self, w):
        """ Callback for <Return>. """

        self.loadfile(self.lb.get(ACTIVE) )

    def loadfileClick(self, w):
        """ Callback for <Button-1>. """

        self.lb.activate(self.lb.nearest(w.y))
        self.loadfile(self.lb.get(self.lb.nearest(w.y)))
            
    def loadfile(self, f):
        global PlayPID

        if not f:
            return

        f=self.fileList[f]
        self.stopPmidi()

        self.displayPDF(f)
        PlayPID = self.playfile(f)
        
        self.CurrentFile = f.split('/')[-1]

        # Save the current filename, without mid extension
        # we skip the extension since the listbox doesn't have them
        Opts.LastFilePlayed = self.CurrentFile.rsplit(".", 1)[0]

        cdir = '/'.join(f.split('/')[:-1])
        if cdir:
            cdir = '\nDir: ' + cdir
        else:
            cdir = '\n'
        self.msgbox.config(text="Playing: %s%s" % (self.CurrentFile, cdir))

        root.update()


    def checkfor(self):
        """ Callback for the "after" timer. Called while file is playing. """

        global PlayPID, DisplayPID

        if DisplayPID:
            try:
                os.waitpid(DisplayPID, os.WNOHANG)
            except OSError:   # our display is gone, kill the player
                DisplayPID = None
                self.stopPmidi()
                
        # PlayPID is set in loadfile(). If not set, then we are not
        # playing at all, or the "terminate midi" file is being played. 
        if PlayPID:
            t = time.time() - self.startPlayTime
            self.timeButton.config(text="%0d:%02d" % (int(t/60), int(t % 60) ))

            try:
                s = os.waitpid(PlayPID, os.WNOHANG)
                # after is one-time only so needs to reset after call
                root.after(500, self.checkfor)
                
            except OSError:  # player is gone, kill display
                if DisplayPID:
                    os.kill(DisplayPID, signal.SIGKILL) 
                DisplayPID = None
                PlayPID = None
                # reset the start time, but leave the display with
                # the time of the last play.
                self.startPlayTime = 0
                self.welcome()

    stopMidiNotes = None  # a file with the stop midi data
    
    def stopPmidi(self, w=''):
        """ Stop currently playing MIDI. """

        global PlayPID, DisplayPID

        if not PlayPID and not DisplayPID:    # nothing playing, just return
            return

        if DisplayPID:
            os.kill(DisplayPID, signal.SIGKILL)
            DisplayPID = None

        cPID = PlayPID
        PlayPID = None

        self.msgbox.config(text="Stopping...%s\n" % self.CurrentFile)
        root.update_idletasks()

        """ See if last run is still running. The call to os.waitpid()
            returns a process ID and a status indication. We check the PID
            returned. If this value is equal to the current PID then
            the process has died ... and we can ignore the whole issue.
        """ 
        
        if cPID:
            try:
                pid,s = os.waitpid(cPID, os.WNOHANG)
            except OSError:
                return

            if pid:
                return
            
            # stop current player, there may be hanging notes
            x=os.kill(cPID, signal.SIGKILL)

            if Opts.KillOnAbort:
                if not self.stopMidiNotes:   # only create the file once
                    
                # Create a standard MIDI file which sets all notes to OFF.
                    _, self.stopMidiNotes = mkstemp(prefix='xpmidi-alloff-', suffix='.mid')
                    with open(self.stopMidiNotes, 'wb') as fout:
                        # Standard midi file header, track count=1
                        fout.write(b"MThd\0\0\0\6\0\1\0\1\0\xc0")
                        # track header, len = 78 bytes
                        fout.write(b"MTrk\0\0\0L")
                        # all notes off for each channel
                        for channel in range(16):
                            fout.write(b"\0" + bytearray((0xb0 | channel,)) + b"\x7b\0")
                        # midi reset sysex (at 4 ticks offset)
                        fout.write(b"\4\xf0\5\x7e\x7f\x09\1\xf7")
                        # EOF status event (4 ticks offset)
                        fout.write(b"\4\xff\x2f\0")
                
                self.playfile(self.stopMidiNotes, wait=os.P_WAIT)

        self.welcome()


    def playfile(self, f, wait=os.P_NOWAIT):
        """ Call the midi player. Used by loadfile() and stopPmidi(). """

        root.after(500, self.checkfor)
        self.startPlayTime = time.time()

        # 3rd arg is a list! Player name, options and filename.
        
        ##a=os.spawnvp(os.P_NOWAIT, "sync", []) # avoid delays while playing (maybe!)
        
        op = shlex.split(Opts.PlayOpts)

        return os.spawnvp(wait, Opts.MidiPlayer, [Opts.MidiPlayer] + op + [f]  ) 

    # PDF display

    def rotateDisplayList(self, w):
        """ Callback for <F2>. Rotate display PDF list"""

        if not len(Opts.PDFsDir):
            return

        Opts.PDFsDir.append(Opts.PDFsDir.pop(0))
        opts={'aspect':4}
        tkMessageBox.showinfo(message="DisplayPDF dir: %s" % Opts.PDFsDir[0])
        
    def displayOnly(self, w):
        """ Callback for <F1>. """

        self.stopPmidi()
        self.displayPDF(self.fileList[self.lb.get(ACTIVE)] )

        
    def displayPDF(self, midifile):
        """ Find and display a PDF for the currently playing file. """

        global DisplayPID

        if not Opts.PDFdisplay:
            return
        
        if DisplayPID:
            os.kill(DisplayPID, signal.SIGKILL)
            DisplayPID = None
            
        f = os.path.basename(midifile).replace(".mid", ".pdf")
        if len(Opts.PDFsDir):
            t = os.path.join(os.path.expanduser(Opts.PDFsDir[0]), f)
            if os.path.exists(t):
                DisplayPID = os.spawnvp(os.P_NOWAIT, Opts.PDFdisplay, [Opts.PDFdisplay] \
                        + Opts.PDFopts.split() + [t]  )
        else:
            displayPID = None


    def chd(self):
        """ Callback from <New Dir> button. Changes to new directory and updates list.  """

        if PlayPID:
            return

        d=tkFileDialog.askdirectory(initialdir=Opts.CurrentDir)

        if d:
            Opts.PlayListFile = ''
            Opts.CurrentDir = [d]
            app.updateList()

    # You can reach this with any of the quit bindings, or by aborting
    # the program with a signal.
    def quitall(self, ex=''):
        """ All done. Save current dir, stop playing and exit. """
        
        self.stopPmidi()
        
        Opts.saveopts()

        # Remove possible midi-stop file
        try:
            os.remove(self.stopMidiNotes)
        except:
            pass
    
        sys.exit(0)


    def playList(self, fn=''):
        if not fn:
            infile = tkFileDialog.askopenfilename(
                filetypes=[("Playlists","*.xpmidilst")], initialdir="~")
        else:
            infile = fn
            
        try:
            inpath = open(os.path.expanduser(infile), 'r')
            Opts.PlayListFile = infile
        except:
            self.updateList()
            return

        flist=[]
        dir=''
        while 1:
            l=inpath.readline()
            if not l:
                break
            l=l.strip()
            if l.startswith("#") or not l:
                continue

            if l.upper().startswith("DIR:"):
                dir = l[4:]
            else:
                flist.append(os.path.expanduser(os.path.join(dir, l)))
        
        self.updateList(flist, 0)
        

    def updateList(self, files=None, sort=1):
        """ Update the list box with with midi files in the selected directories.
    
            1. If files is NOT None, it has to be a list of midi file names. If
               there are files, skip (2).
            2. Create a list of all the files with a .mid(i) extension in all the dirs,
            3. Strip out the actual filename (less the mid ext) from each entry
               and create a dic entry with the filename as the key and the complete
               path as the data.
            4. Update the listbox 
        """

        
        if not files:
            files=[]
            for f in Opts.CurrentDir:
                f = os.path.expanduser(f)
                for a in os.listdir(f):
                    if os.path.splitext(a)[-1].lower() in ('.mid', '.midi'):
                        files.append(os.path.join(f,a))

        self.fileList = {}  # dict of filenames indexed to display name
        tlist = []          # tmp list for dislay

        # Create a display list. This is the basenames without ext.
        # of the found midi files.

        for f in files:
            a = os.path.splitext(os.path.basename(f))[0]  # base filename without ext
            self.fileList[a] = f
            tlist.append(a)
            
        self.lb.delete(0, END)

        if sort:
            if Opts.HumanSort:
                if PY3:
                    tlist.sort(key=functools.cmp_to_key(self.human_sort_cmp))
                else:
                    tlist.sort(cmp=self.human_sort_cmp)
                    
            else:
                tlist.sort()
                
        for f in tlist:
            self.lb.insert(END, f)
            self.lb.select_set(0)
        
        self.welcome()


    def human_sort_cmp(self, first, second):
        crit1, crit2 = first, second
        match1 = self.HUMAN_NUMBER_SORT_RE.match(first)
        match2 = self.HUMAN_NUMBER_SORT_RE.match(second)
        if match1 and match2:
            crit1, num1 = match1.groups()[:2]
            crit2, num2 = match2.groups()[:2]
            if crit1 == crit2:
                crit1, crit2 = float(num1), float(num2)
            # If they're still equal, then that means that the first
            # numbers are the same, onwards to the next part of the file title.
            if crit1 == crit2:
                first = first[first.index(num1) + len(num1):]
                second = second[second.index(num2) + len(num2):]
                return self.human_sort_cmp(first, second)
        rval = 0
        if crit1 < crit2:
            rval = -1
        elif crit1 > crit2:
            rval = 1
        return rval


###################################################
# Initial setup
####################################################


# Parse options and read rc file
filelist = Opts.cmdLine()

# Start the tk stuff. If you want to change the font size, do it here!!!

root = Tk()
root.title("Xpmidi - pmidi frontend")

root.option_add('*font', "Georgia 20 bold")
#if Opts._fullsize:
#    root.geometry("%dx%s" % root.maxsize())

app=Application()

# MIDI files listed on cmd line. Use them for display
if filelist:
    app.updateList(filelist)

root.mainloop()




