# -*- coding: utf-8 -*-
#XXX 몹을 일정수준 이상 죽이면 슬롯머신 게이지가 차서 슬롯머신을 돌리면 오브나 레어 유닉등이 떨어진다!
import legume
import astar
import random
import time
import pyglet

PORT = 3117
VERSION = "0.0.1"

W = 800
H = 600
mapW = 20
mapH = 20
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

    def RemoveMob(self, mob):
        del self.mobs[self.mobs.index(mob)]

    def Draw(self):
        for mob in self.mobs:
            mob.Draw()

    def GenServer(self, mob):
        self.serverMobs += [mob]
        return {'action': 'genmob', 'imgRect': mob.imgRect, 'imgBGRect': mob.imgBGRect, 'x': mob.x, 'y': mob.y, 'idx': mob.idx}

    def Move(self, map):
        newPoses = []
        for mob in self.serverMobs:
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
        return newPoses


class ServerMob(object):
    def __init__(self, imgRect, imgBGRect, x, y, idx):
        self.imgRect = imgRect
        self.imgBGRect = imgBGRect
        self.x = x
        self.y = y
        self.idx = idx
    def SetPos(self, x, y):
        self.x = x
        self.y = y

class Mob(object):
    def __init__(self, MobMgrS, img, bgImg = None):
        self.MobMgrS = MobMgrS
        self.img = img
        self.bgImg = bgImg
        if bgImg:
            self.sprBG = pyglet.sprite.Sprite(img=img, x=0, y=0)
        else:
            self.sprBG = None
        self.spr = pyglet.sprite.Sprite(img=img, x=0, y=0)
        self.x = 0
        self.y = 0
        self.MobMgrS.AddMob(self)
        self.idx = 0

    
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

    def Gen(self, numRooms, roomW=10, roomH=10, roomMinW=4, roomMinH=4):
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

        """
        conn = []
        for i in range(4):
            conn += [(random.randint(0, len(rooms)-1), random.randint(0, len(rooms)-1))]

        for con in conn:
            roomA, roomB = con
            x = rooms[roomA][0]
            y = random.randint(rooms[roomA][1], rooms[roomA][1]+rooms[roomA][3]-1)
            x2 = rooms[roomB][0]
            y2 = random.randint(rooms[roomB][1], rooms[roomB][1]+rooms[roomB][3]-1)
            self.FillRoad((x,y),(x2,y2))
        """
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



