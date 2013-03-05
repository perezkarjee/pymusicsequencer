# -*- coding: utf-8 -*-
import legume
import astar
import random
import time
class TestPos(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+1
    MessageValues = {
        'name' : 'string 128',
        'x' : 'int',
        'y' : 'int',
        }

legume.messages.message_factory.add(TestPos)




class MapGen(object):
    def __init__(self, w, h):
        self.map = [0 for i in range(w*h)]
        self.w = w
        self.h = h

    def Gen(self):
        """
        사각형의 방을 만든 후 주변의 랜덤한 위치에 길목을 만듬
        각 방들의 길목을 모두 이음
        완성된 길목들의 주변에 벽을 쌓음
        끝
        """
        rooms = []
        for i in range(4):
            x = random.randint(2,self.w-34)
            y = random.randint(2,self.h-34)
            w = random.randint(4,32)
            h = random.randint(4,32)
            rooms += [(x,y,w,h)]
            self.FillOneRoom(x,y,w,h)

        for room in rooms[1:]:
            x = room[0]-1
            y = random.randint(room[1], room[1]+room[3])
            x2 = rooms[0][0]-1
            y2 = random.randint(rooms[0][1], rooms[0][1]+rooms[0][3])
            self.FillRoad((x,y),(x2,y2))


    def FillRoad(self, startPos, endPos):
        prevTime = time.clock()
        def TimeFunc():
            curTime = time.clock()
            return (curTime-prevTime)*1000
        finder = astar.AStarFinder(self.map, self.w, self.h, startPos[0], startPos[1], endPos[0], endPos[1], TimeFunc)
        found = finder.Find()
        for coord in found:
            self.map[coord[1]*self.w + coord[0]] = 1
    def FillOneRoom(self, x,y,w,h):
        for yy in range(h):
            for xx in range(w):
                self.map[(yy+y)*self.w+(x+xx)] = 1

map = MapGen(256,256)
map.Gen()
