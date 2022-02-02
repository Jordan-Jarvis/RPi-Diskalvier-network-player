




from .timer import Timer
import time

def timerTest():
    print("Runing tests for timer")
    result = []
    timer = Timer()
    timer.resetTimer()
    timer.startTimer()
    time.sleep(3)
    if (int(timer.getTimeElapsed()) == 3):
        print("PASS")
    else:
        print("FAIL")
    
    time.sleep(2)
    timer.stopTimer()
    time.sleep(2)
    if (int(timer.getTimeElapsed()) == 5):
        print("PASS")
    else:
        print("FAIL")
    timer.addToTimer(5)
    if (int(timer.getTimeElapsed()) == 10):
        print("PASS")
    else:
        print("FAIL")
    timer.startTimer()
    time.sleep(2)
    timer.stopTimer()
    if (int(timer.getTimeElapsed()) == 12):
        print("PASS")
    else:
        print("FAIL")
    timer.startTimer()
    print(timer.getTimeElapsed())

    timer.resetTimer()
    if (int(timer.getTimeElapsed()) == 0):
        print("PASS")
    else:
        print("FAIL", timer.getTimeElapsed())
    
    timer.addToTimer(5)
    timer.startTimer()
    timer.stopTimer()
    if (int(timer.getTimeElapsed()) == 5):
        print("PASS")
    else:
        print("FAIL", timer.getTimeElapsed())
    
    

def playlistTest():
    playlist = Playlist("midirec-default", SystemInterface())
    print(playlist.get_song_list()[0].getLocation())

def playerTest():
    player = Player()
    print(player.playlist.get_current_song().getTitle())
    player.next()
    print(player.playlist.get_current_song().getTitle())
    #print(player.playlist.get_song_list_dict())
    
def SystemInterfaceTest():
    sysInter = SystemInterface()
    sysInter.writeData()

if __name__ == "__main__":

    SystemInterfaceTest()
    playerTest()
    playlistTest()
    timerTest()
    print("OVERLAY\t<input id=ren_input type=text value=\"")
    print("\"><a class=button style=\"top:10%;left:75%;width:20%\" onclick=\"var title = gebi('ren_input').value.toLowerCase().replace(/[^a-z\\d]+/g,'-'); sendRequest('ren-confirm/$status->{selected_file}/'+title,this)\">RENAME</a>\nFOCUS\tren_input\nKEYBOARD\tren_input\n")