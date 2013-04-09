# -*- coding: utf-8 -*-
import time
import random
import shared
import astar
import sys
from time import sleep, localtime
from weakref import WeakKeyDictionary
import euclid

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

class ClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """
    def __init__(self, *args, **kwargs):
        self.account = "anonymous"
        Channel.__init__(self, *args, **kwargs)

        self.map = map = shared.MapGen(30,30)
        map.Gen(4, 5, 5, 3, 3, 3)
        self.MobMgr = shared.MobManager(self)
        self.SkillMgr = shared.SkillManager()
        self.SkillMgr.AddSkill(shared.SkillPresets["Fireball"]())
        self.SkillMgr.lmbSkill = self.SkillMgr.originalSkills[0]
        self.MissileMgr = shared.MissileManager()


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

        self.mobMoveD = 2000
        self.mobMoveW = 0

        self.misMoveD = 100
        self.misMoveW = 0

        self.skillD = 300
        self.skillW = 0


        self.pl = shared.ServerPlayer("Player")

    
    def Close(self):
        print 'closed'
        self._server.DelPlayer(self)
        self._server.done = True
    def _IsPlayerInRange(self, mob):
        vec1 = euclid.Vector2(self.x, self.y)
        vec2 = euclid.Vector2(mob.x, mob.y)
        leng = abs(vec1-vec2)
        if leng < 5:
            return True
        return False
    def Tick(self, tick):
        if self.IsAuthed():
            self.DoMob(tick)

            if self.misMoveW + tick > self.misMoveD:
                self.misMoveW = 0
                self.DoMissile()
            self.misMoveW += tick


        self.SkillMgr.Tick(tick)
    def IsShaken(self):
        if self._server.players[self] == GameServer.HANDSHAKEN or self._server.players[self] == GameServer.AUTHED:
            return True
        return False
    def IsAuthed(self):
        if self._server.players[self] == GameServer.AUTHED:
            return True
        return False

    def DoMissile(self):
        for m in self.MissileMgr.serverM:
            if not m.isTargetPlayer:
                self.MissileMgr.MoveToTarget(self.map, m, (m.targetMob.x, m.targetMob.y))
                if (m.x == m.targetMob.x and m.y == m.targetMob.y) or m.count > m.range:
                    m.AttackTarget()
                    self.MissileMgr.RemoveServer(m)
                    self.Send({'action':'delmissile', 'idx':m.idx})
                else:
                    m.count += 1
                    self.Send({'action':'movemissile', 'x':m.x, 'y':m.y, 'idx':m.idx})
            else:
                self.MissileMgr.MoveToTarget(self.map, m, (self.x, self.y))
                if (m.x == self.x and m.y == self.y) or m.count > m.range:
                    m.AttackTarget()
                    self.Send({'action':'sendstats', 'valname':'hp', 'val': self.pl.hp})
                    self.Send({'action':'sendstats', 'valname':'mp', 'val': self.pl.mp})
                    self.MissileMgr.RemoveServer(m)
                    self.Send({'action':'delmissile', 'idx':m.idx})
                else:
                    m.count += 1
                    self.Send({'action':'movemissile', 'x':m.x, 'y':m.y, 'idx':m.idx})

    def DoMob(self, tick):
        if self.mobMoveW + tick > self.mobMoveD:
            self.mobMoveW = 0
            poses = self.MobMgr.MoveToPlayer(self.map, (self.x,self.y), self._IsPlayerInRange)
            for pos in poses:
                x,y,idx = pos
                self.Send({'action':'movemob', 'x':x, 'y':y, 'idx':idx})

        self.mobMoveW += tick

        for mob in self.MobMgr.serverMobs:
            # 이제 여기서 몹이 플레이어를 공격하게 만든다.
            
            if self._IsPlayerInRange(mob) and mob.atkWait >= mob.atkDelay:
                mob.atkWait = 0

                imgRect = (643, 0, 25, 26)
                missile = shared.ServerMissile(imgRect)
                missile.x = mob.x
                missile.y = mob.y
                missile.idx = self.MissileMgr.GenIdx()
                missile.isTargetPlayer = True
                missile.targetMob = self.pl
                packet = self.MissileMgr.GenServer(missile)
                self.Send(packet)

            mob.atkWait += tick

    def SendStats(self):
        self.Send({'action':'sendstats', 'valname':'str', 'val': self.pl.str})
        self.Send({'action':'sendstats', 'valname':'dex', 'val': self.pl.dex})
        self.Send({'action':'sendstats', 'valname':'int', 'val': self.pl.int})
        self.Send({'action':'sendstats', 'valname':'hp', 'val': self.pl.hp})
        self.Send({'action':'sendstats', 'valname':'mp', 'val': self.pl.mp})

    ##################################
    ### Network specific callbacks ###
    ##################################
    def Network_useskill(self, data):
        if self.IsAuthed() and (self.moveW > self.moveD):
            mymob = None
            for mobb in self.MobMgr.serverMobs:
                if mobb.idx == data['idx']:
                    mymob = mobb
                    break

            if not mymob: # 땅에다가 스킬쓰는 걸 하려면 좀 더 복잡함 그냥 AOE도 타겟온리로 하고... AOE와 원타겟 온리로 하고
                return

            for mob in self.MobMgr.serverMobs:
                self.map.map[self.map.w*mob.y+mob.x] = 1

            self.moveW = 0
            prevTime = time.clock()
            def TimeFunc():
                curTime = time.clock()
                return (curTime-prevTime)*1000
            finder = astar.AStarFinder(self.map.map, self.map.w, self.map.h, self.x, self.y, mymob.x, mymob.y, TimeFunc, 3)
            found = finder.Find()
            
            #print data['skillPlace']
            skillRange = 0
            skill = None
            if data["skillPlace"] == 'lmb' and self.SkillMgr.lmbSkill:
                skill = self.SkillMgr.lmbSkill
            if data["skillPlace"] == 'mmb' and self.SkillMgr.mmbSkill:
                skill = self.SkillMgr.mmbSkill
            if data["skillPlace"] == 'rmb' and self.SkillMgr.rmbSkill:
                skill = self.SkillMgr.rmbSkill
            if data["skillPlace"] == 'q' and self.SkillMgr.qwert[0]:
                skill = self.SkillMgr.qwert[0]
            if data["skillPlace"] == 'w' and self.SkillMgr.qwert[1]:
                skill = self.SkillMgr.qwert[1]
            if data["skillPlace"] == 'e' and self.SkillMgr.qwert[2]:
                skill = self.SkillMgr.qwert[2]
            if data["skillPlace"] == 'r' and self.SkillMgr.qwert[3]:
                skill = self.SkillMgr.qwert[3]
            if data["skillPlace"] == 't' and self.SkillMgr.qwert[4]:
                skill = self.SkillMgr.qwert[4]

            if skill and skill.atkType in ["aoe", "single"]:
                skillRange = skill.range
            vec1 = euclid.Vector2(self.x, self.y)
            vec2 = euclid.Vector2(mymob.x, mymob.y)
            leng = abs(vec1-vec2)

            if leng > skillRange and found and len(found) >= 2:
                cX, cY = found[1][0], found[1][1]
                self.pX = self.x
                self.pY = self.y
                self.x = cX
                self.y = cY
                self.Send({'action':'moveto', 'x': cX, 'y': cY})
            else:
                if skill and self.skillW >= self.skillD:
                    self.skillW = 0
                    skill.SkillUsed()

                    randX = self.x
                    randY = self.y
                    imgRect = (643, 0, 25, 26)
                    missile = shared.ServerMissile(imgRect)
                    missile.x = randX
                    missile.y = randY
                    missile.idx = self.MissileMgr.GenIdx()
                    missile.isTargetPlayer = False
                    missile.targetMob = mymob
                    packet = self.MissileMgr.GenServer(missile)
                    self.Send(packet)

                """
                if data["skillPlace"] == 'lmb':
                    if self.SkillMgr.lmbSkill and self.SkillMgr.lmbSkill.IsReady():
                        self.SkillMgr.lmbSkill.SkillUsed()
                        print 'lmb'
                if data["skillPlace"] == 'mmb':
                    if self.SkillMgr.mmbSkill and self.SkillMgr.mmbSkill.IsReady():
                        self.SkillMgr.mmbSkill.SkillUsed()
                        print 'mmb'
                if data["skillPlace"] == 'rmb':
                    if self.SkillMgr.rmbSkill and self.SkillMgr.rmbSkill.IsReady():
                        self.SkillMgr.rmbSkill.SkillUsed()
                        print 'rmb'
                if data["skillPlace"] == 'q':
                    if self.SkillMgr.qwert[0] and self.SkillMgr.qwert[0].IsReady():
                        self.SkillMgr.qwert[0].SkillUsed()
                        print 'q'
                if data["skillPlace"] == 'w':
                    if self.SkillMgr.qwert[1] and self.SkillMgr.qwert[1].IsReady():
                        self.SkillMgr.qwert[1].SkillUsed()
                        print 'w'
                if data["skillPlace"] == 'e':
                    if self.SkillMgr.qwert[2] and self.SkillMgr.qwert[2].IsReady():
                        self.SkillMgr.qwert[2].SkillUsed()
                        print 'e'
                if data["skillPlace"] == 'r':
                    if self.SkillMgr.qwert[3] and self.SkillMgr.qwert[3].IsReady():
                        self.SkillMgr.qwert[3].SkillUsed()
                        print 'r'
                if data["skillPlace"] == 't':
                    if self.SkillMgr.qwert[4] and self.SkillMgr.qwert[4].IsReady():
                        self.SkillMgr.qwert[4].SkillUsed()
                        print 't'
                """
                # use skill here with skill use delay
                
            for mob in self.MobMgr.serverMobs:
                self.map.map[self.map.w*mob.y+mob.x] = 0

    def Network_moveto(self, data):
        if self.IsAuthed() and (self.moveW > self.moveD):
            for mob in self.MobMgr.serverMobs:
                self.map.map[self.map.w*mob.y+mob.x] = 1
            self.moveW = 0
            prevTime = time.clock()
            def TimeFunc():
                curTime = time.clock()
                return (curTime-prevTime)*1000
            finder = astar.AStarFinder(self.map.map, self.map.w, self.map.h, self.x, self.y, data['x'], data['y'], TimeFunc, 3)
            found = finder.Find()

            if found and len(found) >= 2:
                cX, cY = found[1][0], found[1][1]
                self.pX = self.x
                self.pY = self.y
                self.x = cX
                self.y = cY
                self.Send({'action':'moveto', 'x': cX, 'y': cY})
            for mob in self.MobMgr.serverMobs:
                self.map.map[self.map.w*mob.y+mob.x] = 0
    """
    def Network_mobclick(self, data):
        if self.IsAuthed() and (self.moveW > self.moveD):
            idx = data['idx']
            print idx
            button = data['button'] # lmb mmb rmb q w e r t
            foundMob = None
            for mob in self.MobMgr.serverMobs:
                if mob.idx == idx:
                    foundMob = mob
                    break
            if foundMob:
                self.pl
                print mob
    """
    def Network_handshake(self, data):
        if data["msg"] == "ITEMDIGGERS PONG %s" % shared.VERSION:
            self._server.players[self] = GameServer.HANDSHAKEN
            self._server.players[self] = GameServer.AUTHED # for now
            self.Send({'action':'handshaken'})

    def Network_map(self, data):
        if self.IsAuthed():
            self.Send({'action':'map', 'map': self.map.map, 'walls': self.map.walls, 'w': self.map.w, 'h': self.map.h, 'rooms': self.map.rooms, 'x':self.x, 'y':self.y})

            for i in range(4):
                randRoom = self.map.rooms[random.randint(0, len(self.map.rooms)-1)]
                randX = random.randint(randRoom[0], randRoom[0]+randRoom[2]-1)
                randY = random.randint(randRoom[1], randRoom[1]+randRoom[3]-1)
                mob = shared.ServerMob(self.MobMgr, (184, 74, 28, 20), tuple(), randX, randY, self.MobMgr.GenIdx())
                packet = self.MobMgr.GenServer(mob)
                self.Send(packet)
            self.SendStats()


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
    HANDSHAKEN = 2
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

    def Tick(self, tick):
        for p in self.players:
            p.Tick(tick)
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
            self.Tick(tick)

            for p in self.players.iterkeys():
                p.moveW += tick
                p.skillW += tick

            sleep(0.001)
            clockEnd = time.clock()


def main():
    s = GameServer(localaddr=("", int(shared.PORT)))
    s.Launch()

if __name__ == '__main__':
    """
    import logging
    logging.basicConfig(filename='server.log', level=logging.DEBUG,
        filemode="w",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    """

    main()
