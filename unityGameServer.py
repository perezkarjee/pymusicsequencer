# -*- coding: utf8 -*-

import asyncore
import asynchat
import socket
import sqlite3
import threading
import json
import time

class Lobby(object):
    def __init__(self):
        self.clients = set()
        self.game = None
 
    def Leave(self, client):
        client.game.Leave(client.gameObject)
        self.clients.remove(client)
        print "Leave: " + str(client.addr)
    def Join(self, client):
        self.clients.add(client)
 
    def Broadcast(self, data):
        self.game.Lock()
        for client in self.clients:
            client.Send(data)
        self.game.Unlock()
 
 
class Server(asynchat.async_chat):
    def __init__(self):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("127.0.0.1", 54321))
        self.listen(5)
        self.lobby = None
        self.game = None

 
    def set_lobby(self, lobby):
        self.lobby = lobby
 
    def handle_accept(self):
        sock, addr = self.accept()
        print "Client connected: " + str(addr)

        self.game.Lock()

        gameObject = GameObject()
        client = Client(sock, addr, self.lobby)

        self.game.gameObjects.add(gameObject)
        gameObject.game = self.game
        gameObject.client = client
        client.game = self.game
        client.gameObject = gameObject

        client.OnConnect()
        gameObject.OnConnect()

        self.game.Unlock()

        
class Client(asynchat.async_chat):
    def __init__(self, conn, addr, lobby):
        asynchat.async_chat.__init__(self, sock=conn)
        self.in_buffer = ""
        self.set_terminator(chr(127)+chr(64)+chr(127)+chr(64)+chr(127)+chr(64))
        self.addr = addr
 
        self.lobby = lobby
        self.lobby.Join(self)
        self.game = None
        self.gameObject = None

        self.isDestroyed = False

        self.hsmsg = "THEPGAMERPG"
        self.hs = json.dumps({"msgtype":"handshake", "hs": self.hsmsg}) # Handshake
        self.hsed = False


        self.dataPerSec = 3000 # in bytes
        self.dataDown = 0
        self.prevTime = time.clock()
        self.wait = 0


    def SendHandshake(self):
        print "Sending Handshake..." + str(self.addr)
        self.Send(self.hs)
    def Send(self, msgTxt):
        self.push(msgTxt + self.terminator)
    def OnConnect(self):
        #print "Client object created for " + str(self.addr)
        self.SendHandshake()

    def collect_incoming_data(self, data):

        # Check if client if sending too much data in one second
        curTime = time.clock()
        diff = curTime-self.prevTime
        self.prevTime = curTime
        self.wait += diff

        if self.wait > 1.0:
            self.dataDown = 0
            self.wait = 0.0

        self.dataDown += len(data)
        if len(data) > self.dataPerSec:
            print "Receiving too much data in one second! -> Closing..."
            self.lobby.Leave(self)
            self.close()




        if not self.isDestroyed:
            self.game.Lock()
            self.in_buffer += data
            if len(self.in_buffer) > 1000:
                print "Receiving too much data without terminator! -> Closing..."
                self.lobby.Leave(self)
                self.game.Unlock()
                self.close()

            self.game.Unlock()
    
    def found_terminator(self):
        """
        if self.in_buffer.rstrip() == "QUIT":
            self.lobby.leave(self)
            self.close_when_done()
        else:
        """
        if not self.isDestroyed:
            #self.lobby.Broadcast(self.in_buffer)

            self.ProcessLine(self.in_buffer)
            self.game.Lock()
            self.in_buffer = ""
            self.game.Unlock()

    def ProcessLine(self, buffer):
        self.game.Lock()
        buffer = unicode(buffer, "utf8")
        #txt = json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
        try:
            obj = json.loads(buffer)
        except:
            self.lobby.Leave(self)
            self.game.Unlock()
            print "Data inconsistency found! --> Closing."
            self.client.close()

        if not self.hsed:
            if "msgtype" in obj and obj["msgtype"] == "handshake" and "hs" in obj and obj["hs"] == self.hsmsg:
                self.hsed = True
                print "Handshaken!: " + str(self.addr)
            else:
                print "Handshake failed -> Closing...: " + str(self.addr)
                self.game.Unlock()
                self.close()
                return
        else:
            self.gameObject.PushMsg(obj)
        self.game.Unlock()

    def handle_close(self):
        self.game.Lock()
        if not self.isDestroyed:
            self.isDestroyed = True
            self.lobby.Leave(self)
        self.game.Unlock()


class GameObject(object):
    def __init__(self):
        self.client = None
        self.game = None
        self.msgs = []

    def OnConnect(self):
        pass
        #print "Game object created for " + str(self.client.addr)

    def PushMsg(self, msg):
        self.msgs += [msg]
    def CheckMsg1(self,msg):
        if "msgtype" not in msg:
            return False
        return True
    def CheckMsg2(self, msg,args):
        for arg in args:
            if arg not in msg:
                return False
        return True


    def Tick(self):
        funcTable = {
            "txt": [self.OnRawTxt, "txt"], # msgtype: [HandlerFunc, arg1, arg2, ..., argN]
            "login": [self.OnLogin, "acc", "pw"],
            "txtpluslevel": [self.OnStruct, "txt", "level"],
        }

        for msg in self.msgs:
            if self.CheckMsg1(msg):
                typ = msg["msgtype"]
                for func in funcTable:
                    if typ == func and self.CheckMsg2(msg, funcTable[func][1:]):
                        funcTable[func][0](msg)

        self.msgs = []

    def OnStruct(self, msg):
        print msg["txt"], msg["level"]
    def OnRawTxt(self, msg):
        print msg["txt"]
    def OnLogin(self, msg):
        acc = msg["acc"]
        pw = msg["pw"]
        print acc, pw

class SQLite3Utils(object):
    def __init__(self):
        self.conn = sqlite3.connect('example.db') 
    def Save(self):
        self.conn.commit()
    def Close(self):
        self.conn.close()
    def CheckTableExists(self):
        "SELECT name FROM sqlite_master WHERE type='table' AND name='table_name'"

class Game(object):
    def __init__(self):
        self.server = None
        self.gameObjects = set()
        self.lock = threading.Lock()
        self.db = SQLite3Utils()

    def Lock(self):
        self.lock.acquire()
    def Unlock(self):
        self.lock.release()

    def Leave(self, gameObject):
        self.gameObjects.remove(gameObject)
    def Tick(self):
        self.Lock()
        for go in self.gameObjects:
            go.Tick()
        self.Unlock()

    def SaveGame(self):
        self.Lock()
        self.db.Save()
        self.Unlock()
    def Quit(self):
        self.db.Close()


if __name__ == '__main__':
    lobby = Lobby()
    game = Game()
    server = Server()

    lobby.game = game
    game.server = server
    server.game = game

    server.set_lobby(lobby)
    print "Server started!"

    try:
        while True:
            # Process events
            # msg = ...
            game.Tick()
            asyncore.loop(
                    timeout=0.1,
                    count=1
                    )
    except KeyboardInterrupt:
        game.SaveGame()
        game.Quit()

