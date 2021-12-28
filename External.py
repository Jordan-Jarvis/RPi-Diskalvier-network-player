import flask
import urllib.request
APPExternal = flask.Flask(__name__)
pp = 0
class External:
    def __init__(self, port, ip): 

        global pp
        pp = port - 1
        APPExternal.run(port=port, host=ip)

    @APPExternal.route("/ajax/play-start/")
    def sendStartRequest():
        print(pp)
        urllib.request.urlopen("http://127.0.0.1:" + str(pp) + "/ajax/play-start")
        return("yep")

    @APPExternal.route("/ajax/play-stop/")
    def sendStopRequest():
        print(pp)
        urllib.request.urlopen("http://127.0.0.1:" + str(pp) + "/ajax/play-stop")
        return("yep")


