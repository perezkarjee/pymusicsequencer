# -*- coding: utf-8 -*-
from subprocess import Popen

client = Popen(["python", "simpleMultiServer.py"])
server = Popen(["python", "simpleMultiPlayer.py"])

client.wait()
server.kill()
"""
앰프 시뮬레이션. 웨이브를 교류에서 절대값을 취해 직류로 바꾼 후에 곱하기 0.1을 하고 +0.5를 한다.
"""
