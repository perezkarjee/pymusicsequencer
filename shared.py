# -*- coding: utf-8 -*-
#XXX 몹을 일정수준 이상 죽이면 슬롯머신 게이지가 차서 슬롯머신을 돌리면 오브나 레어 유닉등이 떨어진다!
import legume
import astar
import random
import time
import pyglet

PORT = 3117
VERSION = "0.0.1"

W = 1020
H = 720
mapW = 30
mapH = 30
posX = W//2
posY = H//2
tileW = 32
tileH = 32

class MobManager(object):
    def __init__(self):
        self.mobs = []
        self.waited = 0
        self.delay = 2000
        self.serverMobs = []
        self.curIdx = 0

    def GenIdx(self):
        self.curIdx += 1
        return self.curIdx - 1
    def AddMob(self, mob):
        self.mobs += [mob]

    def RemoveMobServer(self, mob):
        del self.serverMobs[self.serverMobs.index(mob)]
    def RemoveMob(self, mob):
        del self.mobs[self.mobs.index(mob)]

    def Draw(self):
        for mob in self.mobs:
            mob.Draw()

    def GenServer(self, mob):
        self.serverMobs += [mob]
        return {'action': 'genmob', 'imgRect': mob.imgRect, 'imgBGRect': mob.imgBGRect, 'x': mob.x, 'y': mob.y, 'idx': mob.idx}

    def MoveToPlayer(self, map, playerPos, inRange):
        newPoses = []
        newMap = map.map
        newMap[mapW*playerPos[1]+playerPos[0]] = 1
        for mob in self.serverMobs:
            newMap[mapW*mob.y+mob.x] = 1
        for mob in self.serverMobs:
            newMap[mapW*mob.y+mob.x] = 0
            prevTime = time.clock()
            def TimeFunc():
                curTime = time.clock()
                return (curTime-prevTime)*1000
            if inRange(mob):
                finder = astar.AStarFinder(newMap, mapW, mapH, mob.x, mob.y, playerPos[0], playerPos[1], TimeFunc, 3)
            else:
                finder = astar.AStarFinder(newMap, mapW, mapH, mob.x, mob.y, mob.x+random.randint(-4,4), mob.y+random.randint(-4,4), TimeFunc, 3)
            found = finder.Find()
            if found and len(found) >= 2:
                cX, cY = found[1][0], found[1][1]
                mob.SetPos(cX,cY)
                newPoses += [(cX,cY,mob.idx)]
            newMap[mapW*mob.y+mob.x] = 1

        for mob in self.serverMobs:
            newMap[mapW*mob.y+mob.x] = 0
        newMap[mapW*playerPos[1]+playerPos[0]] = 0
        return newPoses
    def Move(self, map):
        newPoses = []
        newMap = map.map
        newMap[mapW*playerPos[1]+playerPos[0]] = 1
        for mob in self.serverMobs:
            newMap[mapW*mob.y+mob.x] = 1
        for mob in self.serverMobs:
            newMap[mapW*mob.y+mob.x] = 0
            prevTime = time.clock()
            def TimeFunc():
                curTime = time.clock()
                return (curTime-prevTime)*1000
            finder = astar.AStarFinder(map.map, mapW, mapH, mob.x, mob.y, mob.x+random.randint(-4,4), mob.y+random.randint(-4,4), TimeFunc, 3)
            found = finder.Find()
            if found and len(found) >= 2:
                cX, cY = found[1][0], found[1][1]
                mob.SetPos(cX,cY)
                newPoses += [(cX,cY,mob.idx)]
            newMap[mapW*mob.y+mob.x] = 1

        for mob in self.serverMobs:
            newMap[mapW*mob.y+mob.x] = 0
        newMap[mapW*playerPos[1]+playerPos[0]] = 0
        return newPoses

class MobBase(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.idx = 0


class ServerMob(MobBase):
    def __init__(self, imgRect, imgBGRect, x, y, idx):
        MobBase.__init__(self,x,y)
        self.idx = idx
        self.imgRect = imgRect
        self.imgBGRect = imgBGRect
    def SetPos(self, x, y):
        self.x = x
        self.y = y
    def AttackTarget(self, target, skill):
        pass



class Mob(MobBase):
    def __init__(self, MobMgrS, img, bgImg = None):
        MobBase.__init__(self,0,0)
        self.MobMgrS = MobMgrS
        self.img = img
        self.bgImg = bgImg
        if bgImg:
            self.sprBG = pyglet.sprite.Sprite(img=img, x=0, y=0)
        else:
            self.sprBG = None
        self.spr = pyglet.sprite.Sprite(img=img, x=0, y=0)
        self.MobMgrS.AddMob(self)

    
    def Draw(self):
        if self.sprBG:
            self.sprBG.draw()
        self.spr.draw()
    def Delete(self):
        self.MobMgrS.RemoveMob(self)

    def SetPos(self, x, y):
        self.x = x
        self.y = y
        if self.sprBG:
            self.sprBG.x = x*tileW+posX
            self.sprBG.y = y*tileH+posY
        self.spr.x = x*tileW+posX
        self.spr.y = y*tileH+posY

class SkillManager(object):
    def __init__(self):
        self.lmbSkill = None
        self.mmbSkill = None
        self.rmbSkill = None
        self.qwert = [None for i in range(5)]
        self.originalSkills = []

    def AddSkill(self, skill):
        self.originalSkills += [skill]

    def Tick(self, tick):
        for s in self.originalSkills:
            s.Tick(tick)


class Skill(object):
    def __init__(self, name, dmgType, dmg, atkType, range, cost):
        self.name = name
        self.dmgType = dmgType #"fire" # fire ice electric
        self.dmg = dmg #10
        self.dmgMultiplier = 1.8
        self.atkType = atkType #"single" # single, aoe, aura
        self.range = range #4
        self.pointPerLevel = 30
        self.pointMultiplier = 2.5
        self.cost = cost
        self.costMultiplier = 1.2
        self.curPoint = 0
        self.level = 1
        self.wait = 0
        self.delay = 300

        self.radius = 3 # only if it's aoe
    def Tick(self, tick):
        self.wait += tick
    def IsReady(self):
        if self.wait > self.delay:
            return True
        return False
    def SkillUsed(self):
        self.wait = 0

    def GetNextPoint(self, level):
        next = self.pointPerLevel
        for i in range(level-1):
            next += next * self.pointMultiplier
        return next

    def AddPoint(self, point):
        self.curPoint += point
        leveledUp = False
        while self.curPoint >= self.GetNextPoint(self.level):
            self.curPoint -= self.GetNextPoint(self.level)
            self.level += 1
            leveledUp = True
        return leveledUp

    def GetDamage(self):
        next = self.dmg
        for i in range(self.level):
            next += next * self.dmgMultiplier
        return next

    def GetManaCost(self):
        next = self.cost
        for i in range(self.level):
            next += next * self.costMultiplier
        return next


    

SkillPresets = {
        "Fireball": lambda: Skill("Fireball", "fire", 5, "single", 5, 3),
        "Snowball": lambda: Skill("Snowball", "ice", 5, "single", 5, 3),
        "Lightning": lambda: Skill("Lightning", "elec", 5, "single", 5, 3),
        "Bomb": lambda: Skill("Bomb", "fire", 5, "aoe", 5, 8),
        "Blizzard": lambda: Skill("Blizzard", "ice", 5, "aoe", 5, 8),
        "ThunderStorm": lambda: Skill("ThunderStorm", "elec", 5, "aoe", 5, 8),
        "FireAura": lambda: Skill("FireAura", "fire", 5, "aura", 5, 15),
        "IceAura": lambda: Skill("IceAura", "ice", 5, "aura", 5, 15),
        "ElectricAura": lambda: Skill("ElectricAura", "elec", 5, "aura", 5, 15),
        }


class MissileBase(object):
    def __init__(self):
        self.skill = None
        self.x = 0
        self.y = 0
        self.idx = 0

class ServerMissile(MissileBase):
    def __init__(self, imgRect):
        MissileBase.__init__(self)
        self.imgRect = imgRect
        self.targetMob = None
        self.isTargetPlayer = False
    def SetPos(self, x, y):
        self.x = x
        self.y = y
    def AttackTarget(self):
        pass


class Missile(MissileBase):
    def __init__(self, Mgr, img):
        MissileBase.__init__(self)
        self.Mgr = Mgr
        self.img = img
        self.spr = pyglet.sprite.Sprite(img=img, x=0, y=0)
        self.Mgr.Add(self)
    
    def Draw(self):
        self.spr.draw()
    def Delete(self):
        self.Mgr.Remove(self)

    def SetPos(self, x, y):
        self.x = x
        self.y = y
        self.spr.x = x*tileW+posX
        self.spr.y = y*tileH+posY
class MissileManager(object):
    def __init__(self):
        self.missiles = []
        self.serverM = []
        self.curIdx = 0
    def MoveToTarget(self, map, missile, targetPos):
        newMap = map.map

        prevTime = time.clock()
        def TimeFunc():
            curTime = time.clock()
            return (curTime-prevTime)*1000

        finder = astar.AStarFinder(newMap, mapW, mapH, missile.x, missile.y, targetPos[0], targetPos[1], TimeFunc, 3)
        found = finder.Find()
        if found and len(found) >= 2:
            cX, cY = found[1][0], found[1][1]
            missile.SetPos(cX,cY)

    def GenIdx(self):
        self.curIdx += 1
        return self.curIdx - 1

    def RemoveServer(self, m):
        del self.serverM[self.serverM.index(m)]
    def Remove(self, m):
        del self.missiles[self.missiles.index(m)]
    def Add(self, m):
        self.missiles += [m]
    def Draw(self):
        for m in self.missiles:
            m.Draw()

    def GenServer(self, m):
        self.serverM += [m]
        return {'action': 'genmissile', 'imgRect': m.imgRect, 'x': m.x, 'y': m.y, 'idx': m.idx}

class PlayerBase(object):
    def __init__(self, name):
        self.name = name
        self.hp = 20
        self.mp = 20
        self.maxhp = 20
        self.maxmp = 20
        self.str = 10
        self.dex = 10
        self.int = 10
        self.points = 0

class ServerPlayer(PlayerBase):
    def __init__(self, name):
        PlayerBase.__init__(self, name)

    def AttackMob(self, mob, skill):
        pass

class Player(PlayerBase):
    def __init__(self, name):
        PlayerBase.__init__(self, name)

def InRect(x,y,w,h, x2, y2):
    if x <= x2 < x+w and y <= y2 < y+h:
        return True
    else:
        return False
def RectRectCollide2(rect1,rect2):
    """
    boolean rectangle_collision(float x_1, float y_1, float width_1, float height_1, float x_2, float y_2, float width_2, float height_2)
    {
    return !(x_1 > x_2+width_2 || x_1+width_1 < x_2 || y_1 > y_2+height_2 || y_1+height_1 < y_2);
    }
    """


    x,y,w,h = rect1
    xx,yy,ww,hh = rect2

    return not (x > xx+ww or x+w < xx or y > yy+hh or y+h < yy)

class MapGen(object):
    def __init__(self, w, h):
        self.map = [1 for i in range(w*h)]
        self.w = w
        self.h = h
        self.rooms = []
        self.walls = []

    def Gen(self, numRooms, roomW=10, roomH=10, roomMinW=4, roomMinH=4, numConnection=3):
        """
        사각형의 방을 만든 후 주변의 랜덤한 위치에 길목을 만듬
        각 방들의 길목을 모두 이음
        완성된 길목들의 주변에 벽을 쌓음
        끝
        """
        rooms = []
        counter = 0
        failCount = 0
        while counter < numRooms:
            x = random.randint(2,self.w-2-roomW)
            y = random.randint(2,self.h-2-roomH)
            w = random.randint(roomMinW,roomW)
            h = random.randint(roomMinH,roomH)
            if rooms:
                found = False
                for room in rooms:
                    if RectRectCollide2(room, (x,y,w,h)):
                        found = True
                if not found:
                    rooms += [(x,y,w,h)]
                    self.FillOneRoom(x,y,w,h)
                    counter+=1
                else:
                    failCount += 1
            else:
                rooms += [(x,y,w,h)]
                self.FillOneRoom(x,y,w,h)
                counter+=1


            if failCount > 10:
                break


        for room in rooms[1:]:
            x = room[0]
            y = random.randint(room[1], room[1]+room[3]-1)
            x2 = rooms[0][0]
            y2 = random.randint(rooms[0][1], rooms[0][1]+rooms[0][3]-1)
            self.FillRoad((x,y),(x2,y2))

        conn = []
        for i in range(numConnection):
            conn += [(random.randint(0, len(rooms)-1), random.randint(0, len(rooms)-1))]

        for con in conn:
            roomA, roomB = con
            x = rooms[roomA][0]
            y = random.randint(rooms[roomA][1], rooms[roomA][1]+rooms[roomA][3]-1)
            x2 = rooms[roomB][0]
            y2 = random.randint(rooms[roomB][1], rooms[roomB][1]+rooms[roomB][3]-1)
            self.FillRoad((x,y),(x2,y2))

        walls = [0 for i in range(self.w*self.h)]
        self.walls = walls
        for y in range(1,self.h-1):
            for x in range(1,self.w-1):
                if self.map[(y)*self.w + x] == 0:
                    if self.map[(y-1)*self.w + x-1] == 1:
                        self.walls[(y-1)*self.w + x-1] = 1
                    if self.map[(y-1)*self.w + x] == 1:
                        self.walls[(y-1)*self.w + x] = 1
                    if self.map[(y-1)*self.w + x+1] == 1:
                        self.walls[(y-1)*self.w + x+1] = 1
                    if self.map[(y)*self.w + x-1] == 1:
                        self.walls[(y)*self.w + x-1] = 1
                    if self.map[(y)*self.w + x+1] == 1:
                        self.walls[(y)*self.w + x+1] = 1
                    if self.map[(y+1)*self.w + x-1] == 1:
                        self.walls[(y+1)*self.w + x-1] = 1
                    if self.map[(y+1)*self.w + x] == 1:
                        self.walls[(y+1)*self.w + x] = 1
                    if self.map[(y+1)*self.w + x+1] == 1:
                        self.walls[(y+1)*self.w + x+1] = 1

        self.rooms = rooms



    def FillRoad(self, startPos, endPos):

        """
        prevTime = time.clock()
        def TimeFunc():
            curTime = time.clock()
            return (curTime-prevTime)*1000
        finder = astar.AStarFinder(self.map, self.w, self.h, startPos[0], startPos[1], endPos[0], endPos[1], TimeFunc)
        found = finder.Find()
        for coord in found:
            self.map[coord[1]*self.w + coord[0]] = 1
        """
        startX = startPos[0]
        startY = startPos[1]
        endX = endPos[0]
        endY = endPos[1]

        """
        A 
        [방1]
        #
        #
        #
        #
        ##########[방2]
        
        B
        ##########[방2]
        #
        #
        #
        #
        [방1]
        방1 -> 방2 : sameStartX startY->endY
                     sameEndY startX->endX
        방2 -> 방1 : sameStartY startX->endX
                     sameEndX startY->endY



        방1 -> 방2 : sameX startY->endY
                     sameY startX->endX


        왼쪽위 오른쪽아래일때 다안됨 A가안됨 가로길의 Y가 틀림
        이건
        startX <= endX
        startY <= endY 또는

        startX > endX
        startY > endY
        """

        if startX <= endX and startY <= endY: # A1->2
            # sameEndY, startX->endX +
            # sameStartX, startY->endY +
            for x in range(endX-startX):
                self.map[(endY)*self.w + startX+x] = 0
            for y in range(endY-startY):
                self.map[(startY+y)*self.w + startX] = 0

        elif startX > endX and startY <= endY: # B2->1
            # sameStartY, startX->endX -
            # sameEndX, startY->endY +
            for x in range(startX-endX):
                self.map[(startY)*self.w + endX+x] = 0
            for y in range(endY-startY):
                self.map[(startY+y)*self.w + endX] = 0
        elif startX <= endX and startY > endY: # B1->2
            # sameEndY, startX->endX +
            # sameStartX, startY->endY -
            for x in range(endX-startX):
                self.map[(endY)*self.w + startX+x] = 0
            for y in range(startY-endY):
                self.map[(endY+y)*self.w + startX] = 0
        elif startX > endX and startY > endY: # A2->1
            # sameStartY, startX->endX -
            # sameEndX, startY->endY -
            for x in range(startX-endX):
                self.map[(startY)*self.w + endX+x] = 0
            for y in range(startY-endY):
                self.map[(endY+y)*self.w + endX] = 0


    def FillOneRoom(self, x,y,w,h):
        for yy in range(h):
            for xx in range(w):
                self.map[(yy+y)*self.w+(x+xx)] = 0

if __name__ == "__main__":
    map = MapGen(256,256)
    map.Gen(8)



