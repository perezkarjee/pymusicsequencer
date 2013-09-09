# -*- coding: utf8 -*-

import asyncore
import asynchat
import socket
import sqlite3
import threading
import json
class Lobby(object):
    def __init__(self):
        self.clients = set()
 
    def Leave(self, client):
        client.game.Leave(client.gameObject)
        self.clients.remove(client)
        print "Leave: " + str(client.addr)
    def Join(self, client):
        self.clients.add(client)
 
    def Broadcast(self, data):
        for client in self.clients:
            client.push(data)
 
 
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

        self.game.lock.acquire()

        gameObject = GameObject()
        self.game.gameObjects.add(gameObject)
        gameObject.game = self.game
        client = Client(sock, addr, self.lobby, self.game, gameObject)

        client.OnConnect()
        gameObject.OnConnect()
        self.game.lock.release()
        
class Client(asynchat.async_chat):
    def __init__(self, conn, addr, lobby, game, gameObject):
        asynchat.async_chat.__init__(self, sock=conn)
        self.in_buffer = ""
        self.set_terminator(chr(127)+chr(64)+chr(127)+chr(64)+chr(127)+chr(64))
        self.addr = addr
 
        self.lobby = lobby
        self.lobby.Join(self)

        self.game = game
        self.gameObject = gameObject
        self.gameObject.client = self

        self.isDestroyed = False


    def OnConnect(self):
        print "Client object created for " + str(self.addr)
 
    def collect_incoming_data(self, data):
        self.in_buffer += data
        if len(self.in_buffer) > 1000:
            print "Receiving too much data without terminator! -> Closing..."
            self.lobby.Leave(self)
            self.close()
 
    def found_terminator(self):
        """
        if self.in_buffer.rstrip() == "QUIT":
            self.lobby.leave(self)
            self.close_when_done()
        else:
        """
        self.lobby.Broadcast(self.in_buffer + self.terminator)
        self.gameObject.ProcessLine(self.in_buffer)
        self.in_buffer = ""

    def handle_close(self):
        if not self.isDestroyed:
            self.isDestroyed = True
            self.lobby.Leave(self)

class GameObject(object):
    def __init__(self):
        self.client = None
        self.game = None
        self.msgs = []

    def OnConnect(self):
        print "Game object created for " + str(self.client.addr)

    def ProcessLine(self, buffer):
        self.game.lock.acquire()
        buffer = unicode(buffer, "utf8")
        #txt = json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
        try:
            obj = json.loads(buffer)
            self.msgs += [obj]
        except:
            self.game.lock.release()
            print "Data inconsistency found! --> Closing."
            self.client.close()

        if "msgtype" in obj and obj["msgtype"] == "txt" and "txt" in obj:
            self.OnRawTxt(obj["txt"])
        self.game.lock.release()

    def OnRawTxt(self, txt):
        print txt
    def Tick(self):
        pass

class Game(object):
    def __init__(self):
        self.server = None
        self.conn = sqlite3.connect('example.db') 
        self.gameObjects = set()
        self.lock = threading.Lock()

    def Leave(self, gameObject):
        self.gameObjects.remove(gameObject)

    def Tick(self):
        self.lock.acquire()
        for go in self.gameObjects:
            go.Tick()
        self.lock.release()

    def SaveGame(self):
        self.lock.acquire()
        conn.commit()
        self.lock.release()
    def Quit(self):
        conn.close()


if __name__ == '__main__':
    lobby = Lobby()
    game = Game()
    server = Server()

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

    print "Shutting down..."
    server.shutdown()
    asyncore.loop()
