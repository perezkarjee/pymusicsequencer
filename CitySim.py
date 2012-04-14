# -*- coding: utf-8 -*-
#
import os
os.environ['SDL_VIDEO_CENTERED'] = '1'
SW,SH = 640,480
BGCOLOR = (0, 0, 0)

from math import radians 

from OpenGL.GL import *
from OpenGL.GLU import *

import pygame
from pygame.locals import *

import random
import math
import numpy
import pickle
import os

LMB = 1
MMB = 2
RMB = 3
WUP = 4
WDN = 5


class Text:
    def __init__(self):
        pass
            #rects += Text.Write(font, "text", (0, 0), THE_SCREEN)
    def GetSurfDS(self, font, text, pos, color=(255,255,255), shadow=False, shadowColor=(255,255,255)): # drop shadow
        surf = font.render(text, True, color)
        if shadow:
            border = font.render(text,True,shadowColor)
            base = pygame.Surface((border.get_rect().width,border.get_rect().height), flags=SRCALPHA)
            base.blit(border, pygame.Rect(1,1,base.get_rect().width,base.get_rect().height))
            base.blit(surf, pygame.Rect(0,0,base.get_rect().width,base.get_rect().height))
            surf = base
        rect = pygame.Rect(pos[0], pos[1], surf.get_rect().width, surf.get_rect().height)
        return surf, rect
    def GetSurf(self, font, text, pos, color=(255,255,255), border=False, borderColor=(255,255,255)):
        surf = font.render(text, True, color)
        if border:
            base = font.render(text,True,borderColor)
            border = font.render(text,True,borderColor)
            base.blit(border, pygame.Rect(1,0,base.get_rect().width,base.get_rect().height))
            base.blit(border, pygame.Rect(1,1,base.get_rect().width,base.get_rect().height))
            base.blit(border, pygame.Rect(0,1,base.get_rect().width,base.get_rect().height))

            base.blit(border, pygame.Rect(-1,0,base.get_rect().width,base.get_rect().height))
            base.blit(border, pygame.Rect(-1,-1,base.get_rect().width,base.get_rect().height))
            base.blit(border, pygame.Rect(0,-1,base.get_rect().width,base.get_rect().height))

            base.blit(border, pygame.Rect(1,-1,base.get_rect().width,base.get_rect().height))
            base.blit(border, pygame.Rect(-1,1,base.get_rect().width,base.get_rect().height))
            base.blit(surf, pygame.Rect(0,0,base.get_rect().width,base.get_rect().height))
            surf = base
        rect = pygame.Rect(pos[0], pos[1], surf.get_rect().width, surf.get_rect().height)
        return surf, rect

    def Write(self, font, text, pos, screen, color=(255,255,255), centerpos = None):
        surf = font.render(text, True, color)
        if centerpos:
            x,y,w,h = centerpos
            x += w/2
            y += h/2
            rect = surf.get_rect()
            w2,h2 = rect.width, rect.height
            x -= w2/2
            y -= h2/2
            rect = screen.blit(surf, pygame.Rect(x, y, surf.get_rect().width, surf.get_rect().height))
        else:
            rect = screen.blit(surf, pygame.Rect(pos[0], pos[1], surf.get_rect().width, surf.get_rect().height))
        return [rect]

    def GetSize(self, font, text):
        surf = font.render(text, True, (0,0,0))
        rect = surf.get_rect()
        return rect.width, rect.height

Text = Text()
import random

def InRect(x,y,w,h, x2, y2):
    if x <= x2 < x+w and y <= y2 < y+h:
        return True
    else:
        return False

EMgrSt = None
class EventManager(object):
    def __init__(self):
        global EMgrSt
        EMgrSt = self
        self.lastMouseState = MouseState()
        self.lastKeyState = KeyState()
        self.bindMDown = []
        self.bindMUp = []
        self.bindMotion = []
        self.bindTick = []

        self.ldown = []
        self.rdown = []
        self.mdown = []
        self.lup = []
        self.rup = []
        self.mup = []
        self.wup = []
        self.wdn = []
        self.bindLPressing = []
        self.bindMPressing = []
        self.bindRPressing = []
        self.kdown = []
        self.kup = []
        self.tick = 0

        self.prevEvent = 0
        self.eventDelay = 0

    def BindWUp(self, func):
        self.wup += [func]
    def BindWDn(self, func):
        self.wdn += [func]
    def BindLPressing(self, func):
        self.bindLPressing += [func]
    def BindMPressing(self, func):
        self.bindMPressing += [func]
    def BindRPressing(self, func):
        self.bindRPressing += [func]
    def BindLDown(self, func):
        self.ldown += [func]
    def BindLUp(self, func):
        self.lup += [func]
    def BindRDown(self, func):
        self.rdown += [func]
    def BindRUp(self, func):
        self.rup += [func]
    def BindMUp(self, func):
        self.mup += [func]
    def BindMDown(self, func):
        self.mdown += [func]
    def BindMotion(self, func):
        self.bindMotion += [func]
    def BindTick(self, func):
        self.bindTick += [func]
    def BindKeyUp(self, func):
        self.kup += [func]
    def BindKeyDown(self, func):
        self.kdown += [func]

    def Tick(self):
        self.tick = pygame.time.get_ticks()
        self.tick = pygame.time.get_ticks()
        self.lastMouseState.OnTick(self.tick)
        self.tick = pygame.time.get_ticks()
        self.lastKeyState.OnTick(self.tick)
        for func in self.bindTick:
            self.tick = pygame.time.get_ticks()
            func(self.tick, self.lastMouseState, self.lastKeyState)


        pressedButtons = self.lastMouseState.GetPressedButtons()
        for button in pressedButtons.iterkeys():
            if button == LMB:
                for func in self.bindLPressing:
                    self.tick = pygame.time.get_ticks()
                    func(self.tick, self.lastMouseState, self.lastKeyState)
            if button == MMB:
                for func in self.bindMPressing:
                    self.tick = pygame.time.get_ticks()
                    func(self.tick, self.lastMouseState, self.lastKeyState)
            if button == RMB:
                for func in self.bindRPressing:
                    self.tick = pygame.time.get_ticks()
                    func(self.tick, self.lastMouseState, self.lastKeyState)

            

        if self.tick - self.prevEvent > self.eventDelay:
            self.prevEvent = self.tick

    def Event(self, e):
        if e.type is MOUSEBUTTONDOWN:
            x,y = e.pos
            self.lastMouseState.OnMousePressed(x,y,SW,SH,e.button)

            dic = {LMB: self.ldown, MMB: self.mdown, RMB: self.rdown, WUP: self.wup, WDN: self.wdn}
            for button in dic:
                if e.button == button:
                    for func in dic[button]:
                        self.tick = pygame.time.get_ticks()
                        func(self.tick, self.lastMouseState, self.lastKeyState)
                
        elif e.type is MOUSEBUTTONUP:
            x,y = e.pos
            self.lastMouseState.OnMouseReleased(x,y,SW,SH, e.button)
            dic = {LMB: self.lup, MMB: self.mup, RMB: self.rup}
            for button in dic:
                if e.button == button:
                    for func in dic[button]:
                        self.tick = pygame.time.get_ticks()
                        func(self.tick, self.lastMouseState, self.lastKeyState)
        elif e.type is MOUSEMOTION:
            x,y = e.pos
            x2,y2 = e.rel
            self.lastMouseState.OnMouseMoved(x,y,SW,SH,x2,y2,0)
            for func in self.bindMotion:
                self.tick = pygame.time.get_ticks()
                func(self.tick, self.lastMouseState, self.lastKeyState)

        elif e.type is KEYDOWN:
            self.lastKeyState.OnKeyPressed(e.key, e.unicode, e.mod)
            for func in self.kdown:
                self.tick = pygame.time.get_ticks()
                func(self.tick, self.lastMouseState, self.lastKeyState)
        elif e.type is KEYUP:
            self.lastKeyState.OnKeyReleased()
            for func in self.kup:
                self.tick = pygame.time.get_ticks()
                func(self.tick, self.lastMouseState, self.lastKeyState)
            '''
    KEYDOWN	     unicode, key, mod
    KEYUP	     key, mod
            '''

def emptyfunc(pos):
    pass

class MouseState(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.relX = 0
        self.relY = 0
        self.relZ = 0
        self.pressedButtons = {}

    def OnMouseMoved(self, x, y, w, h, relX, relY, relZ):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.relX = relX
        self.relY = relY
        self.relZ = relZ
    def OnMousePressed(self, x, y, w, h, id):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.pressedButtons[id] = 0
    def OnMouseReleased(self, x, y, w, h, id):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        try:
            del self.pressedButtons[id]
        except:
            pass
    def UpdateWithMouseState(self, mouseState):
        self.x, self.y, self.w, self.h = mouseState.GetValues()
        self.relX, self.relY = self.GetRelativeMovements()
        for key in mouseState.GetPressedButtons().iterkeys():
            self.pressedButtons[key] = mouseState.GetPressedButtons()[key]
    def OnTick(self, time):
        for key in self.pressedButtons.iterkeys():
            self.pressedButtons[key] += time

    def GetValues(self):
        return self.x, self.y, self.w, self.h
    def GetRelativeMovements(self):
        return self.relX, self.relY
    def GetWheelMovement(self):
        return self.relZ
    def GetPressedButtons(self):
        return self.pressedButtons
    def _GetScreenVector(self, x, y, w, h):
        if w and h:
            mx = float(x) - float(w)/2.0
            my = float(y) - float(h)/2.0
            vectorX, vectorY = mx/(float(w)/2.0), -my/(float(h)/2.0)
            return vectorX, vectorY
        else:
            return 0, 0
    def GetScreenVector(self):
        return self._GetScreenVector(*self.GetValues())

    def GetScreenVectorDegree(self):
        vector = self.GetScreenVector()
        return Vector2ToAngle(*vector)

def DegreeTo8WayDirection(degree):
    degrees = [((360 / 8)*i)-360/16 for i in range(9)]
    degrees[0] += 360
    if (0 <= degree < degrees[1]) or (degrees[0] <= degree < 360) or (degree == 360):
        return "e"

    directions = ["ne", "n", "nw", "w", "sw", "s", "se"]
    
    idx = 0
    for degIdx in range(len(degrees[1:])):
        deg1 = degrees[1:][idx]
        deg2 = degrees[1:][idx+1]
        if deg1 <= degree < deg2:
            return directions[idx]
        idx += 1
'''

          +
          +
          +
          +
          +
----------------------
          +
          +
          +
          +
          +
'''

def Vector2ToAngle(x, y):
    vecOrg = Vector2(1.0, 0.0)
    vecPos = Vector2(x, y)
    vecPos = vecPos.normalised()
    dotted = vecOrg.dotProduct(vecPos)
    if dotted == 0.0:
        dotted = 0.0001
    convert = 360.0/(2*math.pi)

    angle = math.acos(dotted)*convert
    if y < 0:
        angle = -angle
    angle %= 360
    return angle

class KeyState(object):
    def __init__(self):
        self.pressedKey = None
        self.pressedChar = None
        self.pressedMod = None
        self.timePressedFor = None

    def OnKeyPressed(self, key, text, mod):
        self.pressedKey = key
        self.pressedChar = text
        self.pressedMod = mod
        self.timePressedFor = 0
    def OnTick(self, time):
        if self.timePressedFor:
            self.timePressedFor += time
    def OnKeyReleased(self):
        self.pressedKey = None
        self.pressedChar = None
        self.pressedMod = None
        self.timePressedFor = None

    def GetPressedKey(self):
        return self.pressedKey
    def GetPressedTime(self):
        return self.timePressedFor

class Vector2(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    def normalised(self):
        l = self.length()
        if l == 0.0:
            l = 1
        return Vector2(self.x / l, self.y / l)
    def __neg__(self):
        return Vector2(-self.x, -self.y)
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    def __radd__(self, other):
        return self.__add__(other)
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    def __rsub__(self, other):
        return self.__sub__(other)
    def __mul__(self, other):
        if type(other) in (int, float):
            return Vector2(self.x * other, self.y * other)
        else: # dot product
            return self.x * other.x + self.y * other.y
    def __rmul__(self, other):
        return self.__mul__(other)
    def __div__(self, other):
        return Vector2(self.x / other, self.y / other)
    def dotProduct(self, other):
        return self.x * other.x + self.y * other.y

def tangent(a, b):
    return (a-b)/2.0

class FPS:
    def __init__(self):
        self.fpsCounter = 0
        self.fpsSum = 0
        self.start = 0.0
        self.end = 0.0
        self.delay = 4000
        self.sumStart = pygame.time.get_ticks()
    def Start(self):
        timetaken = float(self.end-self.start)
        if timetaken == 0: timetaken = 1.0
        fps = 1000.0/timetaken
        self.fpsSum += fps
        self.fpsCounter += 1
        self.start = pygame.time.get_ticks()

    def End(self):
        self.end = pygame.time.get_ticks()
    def GetFPS(self):
        if self.fpsCounter == 0:
            fps = 0
        else:
            fps = self.fpsSum/self.fpsCounter
        tick = pygame.time.get_ticks()
        if tick - self.sumStart > self.delay:
            self.sumStart = pygame.time.get_ticks()
            self.fpsCounter = 0
            self.fpsSum = 0
        return fps
def Clip(min,max,x):
    if x < min:
        x = min
    if x > max:
        x = max
    return x

class Game:
    def __init__(self):
        self.gold = 0
        self.gas = 0
        self.min = 0
        self.food = 0
import cPickle
GUIW = 256
class BuildButtons:
    def __init__(self, font):
        self.font = font
        self.buttons = []
        self.buttons2 = []
        self.buttons3 = []
        self.buttons4 = []
        self.allButtons = [self.buttons,self.buttons2,self.buttons3,self.buttons4]
        self.buttonPage = 0
        EMgrSt.BindLDown(self.LDown)
    def AddButton(self, page, txt, func, rect):
        self.allButtons[page] += [(txt,func,rect)]
    def LDown(self,t,m,k):
        for button in self.allButtons[self.buttonPage]:
            txt,func,rect = button
            x,y = rect
            color = 200,200,128
            bcolor = 40, 50, 24
            name, rect = Text.GetSurf(self.font, txt, (x, y), color=color, border=True, borderColor=bcolor)
            x,y,w,h = rect
            if InRect(x,y,w,h,m.x,m.y):
                func()
                break
    def Render(self,scr):
        for button in self.allButtons[self.buttonPage]:
            txt,func,rect = button
            x,y = rect
            color = 200,200,128
            bcolor = 40, 50, 24

            name, rect = Text.GetSurf(self.font, txt, (x, y), color=color, border=True, borderColor=bcolor)
            scr.fill((50,50,50), rect)
            scr.blit(name, rect)

class Map:
    def __init__(self, font):
        self.w = 3000
        self.w-=self.w%16
        self.h = 3000
        self.h-=self.h%16
        self.scrX = 0
        self.scrY = 0
        self.tiles = {}
        self.buildings = {}
        self.font = font
        self.game = Game()
        self.buttons = BuildButtons(self.font)
        y = 100
        for i in range(4):
            self.buttons.AddButton(i, u"  I   ", self.SetButtonMode1, (SW-GUIW+5,y))
            self.buttons.AddButton(i, u"  II  ", self.SetButtonMode2, (SW-GUIW+5+32,y))
            self.buttons.AddButton(i, u"  III ", self.SetButtonMode3, (SW-GUIW+5+32+32,y))
            self.buttons.AddButton(i, u"  IV  ", self.SetButtonMode4, (SW-GUIW+5+32+32+32,y))
        y += 30
        self.buttons.AddButton(0, u"Build Mineral Mine", self.BuildMineral, (SW-GUIW+5,y))
        y += 30
        self.buttons.AddButton(0, u"Build Gas Mine", self.BuildGasMineral, (SW-GUIW+5,y))
        y += 30
        self.buttons.AddButton(0, u"Build Farm", self.BuildFarm, (SW-GUIW+5,y))
        y += 30
        self.buttons.AddButton(0, u"Build House", self.BuildHouse, (SW-GUIW+5,y))
        """
        Print(SW-GUIW+5, y, )
        Print(SW-GUIW+5, y, u"Build Gas Mine")
        """
    
        self.buildMode = False
        self.building = None


        self.bDef = {
                "HQ": [(16,64,64), (4,4), [0,0,16,0]], # headquater 
                "M": [(16,16,64), (2,2), [0,0,16,0]], # mineral
                "G": [(16,64,16), (2,2), [0,0,16,0]], # gas
                "GM": [(32,128,32), (2,2), [16,0,16,0]], # gas mine
                "MM": [(32,32,128), (2,2), [16,0,16,0]], # mineral mine
                "H": [(32,32,32), (2,2), [8,8,8,8]], # house
                "F": [(128,64,64), (2,2), [8,0,8,8]], # farm
                }

        self.delay = 1000
        self.wait = pygame.time.get_ticks()
        EMgrSt.BindMotion(self.Motion)
        EMgrSt.BindLDown(self.LDown)
        EMgrSt.BindKeyDown(self.KDown)
        EMgrSt.BindTick(self.Tick)

    def Tick(self,t,m,k):
        if t-self.wait > self.delay:
            self.wait = t
            for c in self.buildings:
                x,y=c
                b = self.buildings[c]
                if b == "HQ":
                    self.game.gold += 2
                    self.game.food += 2
                    self.game.min += 2
                    self.game.gas += 2
                if b == "MM":
                    self.game.min += 1
                if b == "GM":
                    self.game.gas += 1
                if b == "F":
                    self.game.food += 1
                if b == "H":
                    self.game.gold += 1
    def KDown(self,t,m,k):
        if k.pressedKey == K_ESCAPE:
            self.buildMode = False
            self.building = None
    def SetButtonMode1(self):
        self.buttons.buttonPage = 0
    def SetButtonMode2(self):
        self.buttons.buttonPage = 1
    def SetButtonMode3(self):
        self.buttons.buttonPage = 2
    def SetButtonMode4(self):
        self.buttons.buttonPage = 3
    def BuildGasMineral(self):
        self.buildMode = True
        self.building = "GM"
    def BuildFarm(self):
        self.buildMode = True
        self.building = "F"
    def BuildHouse(self):
        self.buildMode = True
        self.building = "H"
    def BuildMineral(self):
        self.buildMode = True
        self.building = "MM"
    def LDown(self,t,m,k):
        x,y = m.x,m.y
        x += self.scrX
        y += self.scrY
        x -= x%16
        y -= y%16

        b = self.building
        if m.x < SW-GUIW:
            if b == "MM":
                if (x,y) in self.buildings and self.buildings[(x,y)] == "M":
                    del self.buildings[(x,y)]
                    del self.tiles[(x,y)]
                    if self.Add(b, x,y):
                        self.buildMode = False
            elif b == "GM":
                if (x,y) in self.buildings and self.buildings[(x,y)] == "G":
                    del self.buildings[(x,y)]
                    del self.tiles[(x,y)]
                    if self.Add(b, x,y):
                        self.buildMode = False
            else:
                if self.Add(b, x,y):
                    self.buildMode = False
    def GenCoords(self,x,y,w,h):
        coords = [(x+1,y+1)]
        for yy in range(1,h):
            for xx in range(1,w):
                coords += [(x+xx*16, y+yy*16)]
        return coords
    def Add(self, building, x,y):
        cost = self.bDef[building][2]
        g,f,m,ga = cost
        if self.game.gold >= g and self.game.food >= f and self.game.min >= m and self.game.gas >= ga:
            self.game.gold -= g
            self.game.food -= f
            self.game.min -= m
            self.game.gas -= ga
        else:
            return False
        self.AddForce(building,x,y)
        return True
    def AddForce(self, b, x,y):
        self.AddRect(x,y,self.bDef[b][0],b,self.bDef[b][1])
        x = x-x%16
        y = y-y%16
        self.buildings[(x,y)] = b
    def AddRect(self, x,y,color,text,size):
        x = x-x%16
        y = y-y%16
        w,h=size
        coords = self.GenCoords(x-w*16,y-h*16,w*2,h*2)
        found = False
        for coord in coords:
            if coord in self.tiles:
                found = True
                break
        if x+w*16-16 > self.w or y+h*16-16 > self.h:
            found = True
        if not found:
            self.tiles[(x,y)] = [color,text,size]
    def Motion(self,t,m,k):
        if RMB in m.pressedButtons and InRect(0,0,SW-GUIW,SH,m.x,m.y):
            self.scrX -= m.relX
            self.scrY -= m.relY
            self.scrX = Clip(0,self.w-SW,self.scrX)
            self.scrY = Clip(0,self.h-SH,self.scrY)


    def Render(self, scr,t,m,k):
        color = 54,54,54
        for yy in range(SH/16+2):
            for xx in range((SW-GUIW)/16+1):
                scr.fill(color, pygame.Rect(xx*16-self.scrX%16,0,1,SH))
            scr.fill(color, pygame.Rect(0,yy*16-self.scrY%16,SW-GUIW,1))

        for coord in self.tiles:
            color,text,size = self.tiles[coord]
            x,y=coord
            w,h = size
            w*=16
            h*=16
            if InRect(self.scrX,self.scrY,SW,SH,x,y) or InRect(self.scrX,self.scrY,SW,SH,x+w,y) or InRect(self.scrX,self.scrY,SW,SH,x+w,y+h) or InRect(self.scrX,self.scrY,SW,SH,x,y+h):
                scr.fill(color, pygame.Rect(x-self.scrX+1,y-self.scrY+1,w-1,h-1))

                color = 200,200,128
                bcolor = 40, 50, 24
                Text.Write(self.font, text, (x-self.scrX,y-self.scrY), scr, color=color, centerpos = (x-self.scrX,y-self.scrY,w,h))
                #scr.blit(*Text.GetSurf(self.font, text, (x, y), color=color, border=True, borderColor=bcolor))

        if self.buildMode:
            b = self.building
            x,y = m.x,m.y
            x += self.scrX%16
            y += self.scrY%16
            x -= x%16
            y -= y%16
            x -= self.scrX%16
            y -= self.scrY%16
            color, size, cost = self.bDef[b]
            w,h=size
            w*=16
            h*=16
            scr.fill(color, pygame.Rect(x+1,y+1,w-1,h-1))
            color = 200,200,128
            bcolor = 40, 50, 24
            Text.Write(self.font, b, (x,y), scr, color=color, centerpos = (x,y,w,h))


        self.RenderGUI(scr)

    def RenderGUI(self,scr):
        scr.fill((16,16,16),(SW-GUIW,0,GUIW,SH))
        def Print(x,y,str_):
            color = 200,200,128
            bcolor = 40, 50, 24
            scr.blit(*Text.GetSurf(self.font, str_, (x, y), color=color, border=True, borderColor=bcolor))
        if self.buildMode:
            Print(SW-GUIW+5, 5, u"Gold: %d  -%d" % (self.game.gold, self.bDef[self.building][2][0]))
            Print(SW-GUIW+5, 5+20, u"Food: %d  -%d" % (self.game.food, self.bDef[self.building][2][1]))
            Print(SW-GUIW+5, 5+20+20, u"Mineral: %d  -%d" % (self.game.min, self.bDef[self.building][2][2]))
            Print(SW-GUIW+5, 5+20+20+20, u"Gas: %d  -%d" % (self.game.gas, self.bDef[self.building][2][3]))
        else:
            Print(SW-GUIW+5, 5, u"Gold: %d" % self.game.gold)
            Print(SW-GUIW+5, 5+20, u"Food: %d" % self.game.food)
            Print(SW-GUIW+5, 5+20+20, u"Mineral: %d" % self.game.min)
            Print(SW-GUIW+5, 5+20+20+20, u"Gas: %d" % self.game.gas)
        self.buttons.Render(scr)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption('CitySim')
    #screen.blit(background, (0, 0))
    done = False
    font = pygame.font.Font("./fonts/FanwoodText.ttf", 16)
    emgr = EventManager()
    startTick = pygame.time.get_ticks()
    endTick = pygame.time.get_ticks()
    fps = FPS()
    map = Map(font)
    map.AddForce("HQ", 16,16)
    map.AddForce("GM", 16,64+16+16)
    map.AddForce("MM", 64+16+16,16)
    for j in range(10):
        for i in range(10):
            map.AddForce("G", random.randint(0,3000), random.randint(0,3000))
            map.AddForce("M", random.randint(0,3000), random.randint(0,3000))
    while not done:
        #fightCountTick += endTick-startTick
        startTick = pygame.time.get_ticks()
        fps.Start()
        emgr.Tick()
        for event in pygame.event.get():
            emgr.Event(event)
            if event.type == QUIT:
                done = True
            elif event.type == MOUSEBUTTONDOWN:
                #OnMouseDown(event, g)
                """
            elif event.type == MOUSEBUTTONUP:
                fist.unpunch()
                """



        screen.fill((0,0,0))
        color = 200,200,128
        bcolor = 40, 50, 24
        map.Render(screen, emgr.tick, emgr.lastMouseState, emgr.lastKeyState)


        screen.blit(*Text.GetSurf(font, str(int(fps.GetFPS())), (0, 0), color=color, border=True, borderColor=bcolor))
        screen.blit(*Text.GetSurf(font, str(map.scrX), (SW-GUIW, SH-32), color=color, border=True, borderColor=bcolor))
        screen.blit(*Text.GetSurf(font, str(map.scrY), (SW-GUIW+45, SH-32), color=color, border=True, borderColor=bcolor))
        pygame.display.flip()
        endTick = pygame.time.get_ticks()
        fps.End()

if __name__ == "__main__":
    main()

"""
시뮬레이션을 만드는데
농장
공장
럼버잭
유정
마인
집
상점
발전소를 짓고 발전한다.
"""

