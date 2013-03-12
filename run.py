# -*- coding: utf-8 -*-
from subprocess import Popen

client = Popen(["python", "simpleMultiServer.py"])
server = Popen(["python", "simpleMultiPlayer.py"])

client.wait()
server.kill()
