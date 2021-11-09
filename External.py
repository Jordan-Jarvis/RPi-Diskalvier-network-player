import flask
import upnp
import urllib.request
APPExternal = flask.Flask(__name__)
pp = 0
class External:
    def __init__(self, port, ip): 
        import miniupnpc # start externally accessible web requests for google home and alexa
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 10
        upnp.discover()
        upnp.selectigd()
        global pp
        pp = port - 1
        upnp.addportmapping(port, 'TCP', upnp.lanaddr, port, 'testing', '')
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


