import flask
import mido
from flask import Flask, request, send_from_directory, jsonify
from flask import Response
from flask import json
import time
import os
import subprocess
import multiprocessing
import mpserver.midi.config
import configparser
import io
from mpserver.midi.parseMidi import *
import sys
os.chdir(os.path.dirname(sys.argv[0]))
import mpserver.midi.Player as Player
import urllib.request
player = Player.Player()
import External
from multiprocessing import Process
