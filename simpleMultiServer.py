# -*- coding: utf-8 -*-
import time
import random
import shared
import astar
import sys
from time import sleep, localtime
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

mapW = 20
mapH = 20
class ClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """
    def __init__(self, *args, **kwargs):
        self.account = "anonymous"
        Channel.__init__(self, *args, **kwargs)

        self.map = map = shared.MapGen(mapW,mapH)
        map.Gen(4, 5, 5, 3, 3)


        self.x = 0
        self.y = 0
        self.pX = 0
        self.pY = 0

        randRoom = self.map.rooms[random.randint(0, len(self.map.rooms)-1)]
        randX = random.randint(randRoom[0], randRoom[0]+randRoom[2]-1)
        randY = random.randint(randRoom[1], randRoom[1]+randRoom[3]-1)
        self.pX = self.x = randX
        self.pY = self.y = randY
        self.moveD = 150
        self.moveW = 0

    
    def Close(self):
        print 'closed'
        self._server.DelPlayer(self)
    
    ##################################
    ### Network specific callbacks ###
    ##################################
    def IsShaked(self):
        if self._server.players[self] == GameServer.HANDSHAKED or self._server.players[self] == GameServer.AUTHED:
            return True
        return False
    def IsAuthed(self):
        if self._server.players[self] == GameServer.AUTHED:
            return True
        return False

    def Network_moveto(self, data):
        if self.IsAuthed() and (self.moveW > self.moveD):
            self.moveW = 0
            prevTime = time.clock()
            def TimeFunc():
                curTime = time.clock()
                return (curTime-prevTime)*1000
            finder = astar.AStarFinder(self.map.map, mapW, mapH, self.x, self.y, data['x'], data['y'], TimeFunc, 3)
            found = finder.Find()

            if found and len(found) >= 2:
                cX, cY = found[1][0], found[1][1]
                self.pX = self.x
                self.pY = self.y
                self.x = cX
                self.y = cY
                self.Send({'action':'moveto', 'x': cX, 'y': cY})

    def Network_handshake(self, data):
        if data["msg"] == "ITEMDIGGERS PONG %s" % shared.VERSION:
            self._server.players[self] = GameServer.HANDSHAKED
            self._server.players[self] = GameServer.AUTHED
            self.Send({'action':'handshaken'})

    def Network_map(self, data):
        if self.IsAuthed():
            self.Send({'action':'map', 'map': self.map.map, 'walls': self.map.walls, 'w': self.map.w, 'h': self.map.h, 'rooms': self.map.rooms, 'x':self.x, 'y':self.y})

    """
    def Network_message(self, data):
        self._server.SendToAll({"action": "message", "message": data['message'], "who": self.nickname})
    
    def Network_nickname(self, data):
        self.nickname = data['nickname']
        self._server.SendPlayers()
    """

class GameServer(Server):
    channelClass = ClientChannel
    ADDED = 1
    HANDSHAKED = 2
    AUTHED = 3
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        self.done = False
        print 'Server launched'
    
    def Connected(self, channel, addr):
        self.players[channel] = self.ADDED
        channel.dataAllowedPerSecond = 100000 # Adjust these to control how much amount of data that can be sent per second
        channel.dataAllowedPer30Second = 1000000 # per 30 seconds. if data amount sent is not under the limit, it will disconnect the client
        channel.Send({"action": "handshake", "msg": "ITEMDIGGERS PING %s" % shared.VERSION})

    def DelPlayer(self, player):
        #print "Deleting Player" + str(player.addr)
        del self.players[player]

    """
        self.AddPlayer(channel)
    
    def AddPlayer(self, player):
        print "New Player" + str(player.addr)
        self.players[player] = True
        self.SendPlayers()
        print "players", [p for p in self.players]
    
    def DelPlayer(self, player):
        print "Deleting Player" + str(player.addr)
        del self.players[player]
        self.SendPlayers()
    
    def SendPlayers(self):
        self.SendToAll({"action": "players", "players": [p.nickname for p in self.players]})
    
    def SendToAll(self, data):
        [p.Send(data) for p in self.players]
    """
    
    def Launch(self):
        clockPrev = time.clock()
        clockEnd = time.clock()
        while not self.done:
            tick = (clockEnd-clockPrev)*1000
            clockPrev = time.clock()
            time.clock()
            self.Pump()

            for p in self.players.iterkeys():
                p.moveW += tick

            sleep(0.001)
            clockEnd = time.clock()


def main():
    s = GameServer(localaddr=("", int(shared.PORT)))
    s.Launch()

if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='server.log', level=logging.DEBUG,
        filemode="w",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    main()
