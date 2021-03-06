# -*- coding: utf-8 -*-
import os
os.environ['SDL_VIDEO_CENTERED'] = '1'
SW,SH = 1024,768
BGCOLOR = (0, 0, 0)

import sys
from ctypes import *
from math import radians 
from OpenGL import platform
from OpenGL.GL.EXT.texture_filter_anisotropic import *
import math
gl = platform.OpenGL

from OpenGL.GL import *
from OpenGL.GLU import *

import pygame
from pygame.locals import *
import chunkhandler

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

GL_FRAGMENT_SHADER = 0x8B30
GL_VERTEX_SHADER = 0x8B31
GL_COMPILE_STATUS = 0x8B81
GL_LINK_STATUS = 0x8B82
GL_INFO_LOG_LENGTH = 0x8B84
 
def print_log(shader):
    length = c_int()
    glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(length))
 
    if length.value > 0:
        log = create_string_buffer(length.value)
        log = glGetShaderInfoLog(shader)
        print log

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    length = c_int(-1)
    glShaderSource(shader, source)
    glCompileShader(shader)
    
    status = c_int()
    glGetShaderiv(shader, GL_COMPILE_STATUS, byref(status))
    if not status.value:
        print_log(shader)
        glDeleteShader(shader)
        raise ValueError, 'Shader compilation failed'
    return shader
 
def compile_program(vertex_src, fragment_src):
    '''
    Compile a Shader program given the vertex
    and fragment sources
    '''
    
    shaders = []
    
    program = glCreateProgram()

    for shader_type, src in ((GL_VERTEX_SHADER, vertex_src),
                             (GL_FRAGMENT_SHADER, fragment_src)):
        shader = compile_shader(src, shader_type)
        glAttachShader(program, shader)
        shaders.append(shader)

    glLinkProgram(program)
 
    for shader in shaders:
        glDeleteShader(shader)
 
    return program
 
class ButtonGame(object):
    def __init__(self, ren, txt, func, x,y):
        self.rect = x,y
        self.func = func
        self.ren = ren
        self.txtID = ren.NewTextObject(txt, (0,0,0))
        AppSt.BindRenderGameGUI(self.Render)
        EMgrSt.BindLDown(self.OnClick)
        self.enabled = True
    def OnClick(self, t,m,k):
        if self.enabled:
            w,h = self.ren.GetDimension(self.txtID)
            if InRect(self.rect[0],self.rect[1],w+10,h+10,m.x,m.y):
                self.func()
    def Render(self):
        w,h = self.ren.GetDimension(self.txtID)
        DrawQuad(self.rect[0],self.rect[1],w+10,h+10,(164,164,164,255),(164,164,164,255))
        self.ren.RenderText(self.txtID, (self.rect[0]+5,self.rect[1]+5))
class Button(object):
    def __init__(self, ren, txt, func, x,y):
        self.rect = x,y
        self.func = func
        self.ren = ren
        self.txtID = ren.NewTextObject(txt, (0,0,0))
        AppSt.BindRenderGUI(self.Render)
        EMgrSt.BindLDown(self.OnClick)
        self.enabled = True
    def OnClick(self, t,m,k):
        if self.enabled:
            w,h = self.ren.GetDimension(self.txtID)
            if InRect(self.rect[0],self.rect[1],w+10,h+10,m.x,m.y):
                self.func()
    def Render(self):
        w,h = self.ren.GetDimension(self.txtID)
        DrawQuad(self.rect[0],self.rect[1],w+10,h+10,(164,164,164,255),(164,164,164,255))
        self.ren.RenderText(self.txtID, (self.rect[0]+5,self.rect[1]+5))

class EnemyDef:
    def __init__(self, tileIdx, name, x, y, args):
        self.tileIdx = tileIdx
        self.name = name
        self.pos = [x,y]
        self.args = args
    def Gen(self):
        return Enemy(self.tileIdx, self.name, self.pos[0], self.pos[1], self.args)

class Stage:
    def __init__(self):
        self.scrX = 0
        self.scrY = 0
        self.tiles = {}
        self.enemies = []
        self.enemyDefs = {}
        self.doors = {}
        self.gems = {}
        self.gameGems = {}


    def AddGem(self,x,y,tile):
        self.gems[(x,y)] = tile
    def DelGem(self,x,y):
        try:
            del self.gems[(x,y)]
        except:
            pass
    def EndGame(self):
        try:
            EMgrSt.bindTick.remove(self.Tick)
        except:
            pass
        for enemy in self.enemies:
            enemy.Delete()
        self.enemies = []
    def Tick(self,t,m,k):
        x,y = AppSt.player.pos
        x -= 32
        y -= 128
        w=64
        h=128
        for gem in self.gameGems.iterkeys():
            xx,yy = gem
            ww = 64
            hh = 64
            if RectRectCollide((x,y,w,h),(xx,yy,ww,hh)):
                gem_ = self.gameGems[gem]
                del self.gameGems[gem]
                if gem_ == 0:
                    AppSt.player.args["maxhp"] += 50
                elif gem_ == 1:
                    AppSt.player.args["maxmana"] += 50
                elif gem_ == 2:
                    AppSt.player.args["atk"] += 50
                elif gem_ == 3:
                    AppSt.player.args["heal"] += 50
                break




        pass

    def StartGame(self):
        EMgrSt.BindTick(self.Tick)
        for enemy in self.enemies:
            enemy.Delete()
        self.enemies = []
        for enemy in self.enemyDefs.itervalues():
            self.enemies += [enemy.Gen()]
        import copy
        self.gameGems = copy.copy(self.gems)
    def ScrollTo(self,x,y):
        self.scrX = x
        self.scrY = y

    def GetTiles(self):
        x = self.scrX-SW
        y = self.scrY-SH
        w = SW*3
        h = SH*3
        tiles = []
        for coord in self.tiles:
            cx,cy = coord
            if InRect(x-64,y-64,w+64,h+64,cx,cy):
                tiles += [(cx,cy,self.tiles[coord])]
        return tiles
    def AddDoor(self,x,y):
        self.doors[(x,y)] = GUISt.curDoorIdx
        GUISt.curDoorIdx += 1
    def DelDoor(self,x,y):
        try:
            del self.doors[(x,y)]
        except:
            pass
    def AddEnemy(self,enemy):
        self.enemyDefs[tuple(enemy.pos)] = enemy

    def DelEnemy(self,x,y):
        try:
            del self.enemyDefs[(x,y)]
        except:
            pass
    def AddTile(self,x,y,tile):
        self.tiles[(x,y)] = tile
    def DelTile(self,x,y):
        try:
            del self.tiles[(x,y)]
        except:
            pass


class Enemy:
    LEFT=0
    RIGHT=1
    def Delete(self):
        EMgrSt.bindTick.remove(self.Tick)
    def __init__(self, tileIdx, name, x, y, args):
        self.hp = 100
        self.args = args

        self.tileIdx = tileIdx
        self.pos = [x,y]
        self.name = name
        self.leftOn = False
        self.rightOn = False
        self.jumpOn = False
        self.atkOn = False
        EMgrSt.BindTick(self.Tick)

        self.fallSpeed = 15
        self.fallWait = pygame.time.get_ticks()
        self.fallDelay = 25
        self.facing = self.RIGHT
        self.jumping = False
        self.jumpStart = 0
        self.jumpMax = 500
        self.jumpMin = 250
        self.grounded = False
        self.moving = False
        self.keyBinds = {
                "UP": K_w,
                "LEFT": K_a,
                "DOWN": K_s,
                "RIGHT": K_d,
                "ATK": K_j,
                "JUMP": K_k,
                "ACT": K_u,
                "ACT2": K_i,
                }
        self.beamDelay = 250
        self.prevBeam = pygame.time.get_ticks()
        self.beams = []

        self.prevLeft = pygame.time.get_ticks()
        self.moveDelay = 1000
        self.goleft = False
        self.atkWait = pygame.time.get_ticks()
        self.atkDelay = 500

        self.prevJump = pygame.time.get_ticks()
        self.jumpOffDelay = 1000
        self.jumpDelay = 3000

    def Attack(self, t):
        ppos = AppSt.player.pos
        pos = self.pos
        ppos = Vector2(*ppos)
        pos = Vector2(*pos)
        if (ppos-pos).length() < 1024:
            if (ppos.x < pos.x and self.facing == self.LEFT) or (ppos.x >= pos.x and self.facing == self.RIGHT):
                self.atkWait = t
                beamY = self.pos[1]-128
                if self.facing == self.LEFT:
                    beamX = self.pos[0]-128-32
                else:
                    beamX = self.pos[0]+32

                self.beams += [Beam(beamX,beamY,self.facing,self.args["atk"],self)]



    def Tick(self, t,m,k):
        if GUISt.emode == GUISt.GAME_MODE:
            if not self.jumpOn:
                if t-self.prevJump > self.jumpDelay:
                    self.prevJump = t
                    self.jumpOn = not self.jumpOn
            elif self.jumpOn:
                if t-self.prevJump > self.jumpOffDelay:
                    self.prevJump = t
                    self.jumpOn = not self.jumpOn
            ppos = AppSt.player.pos
            pos = self.pos
            ppos = Vector2(*ppos)
            pos = Vector2(*pos)
            if (ppos-pos).length() < SW/2+100:

                if t-self.atkWait > self.atkDelay:
                    self.Attack(t)

                if t-self.prevLeft > self.moveDelay:
                    self.prevLeft = t
                    self.goleft = not self.goleft
                if self.goleft:
                    self.facing = self.LEFT
                    self.leftOn = True
                    self.rightOn = False
                else:
                    self.facing = self.RIGHT
                    self.leftOn = False
                    self.rightOn = True
                if self.hp <= 0:
                    try:
                        GUISt.stages[GUISt.curStageIdx].enemies.remove(self)
                
                        EMgrSt.bindTick.remove(self.Tick)
                    except:
                        pass
                    x = self.pos[0]-32
                    y = self.pos[1]-64-32
                    GUISt.deads += [DeadEnemy(x,y)]
                if t-self.fallWait > self.fallDelay:
                    self.fallWait = t
                    tiles = GUISt.stages[GUISt.curStageIdx].GetTiles()
                    self.moving = False

                    if not self.jumping:
                        collide = False
                        collideY = 0
                        for tile in tiles:
                            x,y,t_ = tile
                            w = 64
                            h = 64
                            px,py = self.pos
                            xx = px-32
                            yy = py-128+self.fallSpeed
                            ww = 64
                            hh = 128
                            if RectRectCollide((x+1,y+1,w-1,h-1),(xx+1,yy+1,ww-1,hh-1)):
                                collide = True
                                collideY = y
                        if not collide:
                            self.pos[1] += self.fallSpeed
                        else:
                            self.grounded = True
                            self.pos[1] = collideY
                    else:
                        collide = False
                        collideY = 0
                        for tile in tiles:
                            x,y,t_ = tile
                            w = 64
                            h = 64
                            px,py = self.pos
                            xx = px-32
                            yy = py-128-self.fallSpeed
                            ww = 64
                            hh = 128
                            if RectRectCollide((x+1,y+1,w-1,h-1),(xx+1,yy+1,ww-1,hh-1)):
                                collide = True
                                collideY = y+h+128
                        if not collide:
                            self.pos[1] -= self.fallSpeed
                        else:
                            self.pos[1] = collideY

                    if self.leftOn:
                        self.moving = True
                        self.facing = self.LEFT
                        collide = False
                        collideX = 0
                        for tile in tiles:
                            x,y,t_ = tile
                            w = 64
                            h = 64
                            px,py = self.pos
                            xx = px-32-self.fallSpeed
                            yy = py-128
                            ww = 64
                            hh = 128
                            if RectRectCollide((x+1,y+1,w-1,h-1),(xx+1,yy+1,ww-1,hh-1)):
                                collide = True
                                collideX = x+w+32
                        if not collide:
                            self.pos[0] -= self.fallSpeed
                        else:
                            self.pos[0] = collideX

                    if self.rightOn:
                        self.moving = True
                        self.facing = self.RIGHT
                        collide = False
                        collideX = 0
                        for tile in tiles:
                            x,y,t_ = tile
                            w = 64
                            h = 64
                            px,py = self.pos
                            xx = px-32+self.fallSpeed
                            yy = py-128
                            ww = 64
                            hh = 128
                            if RectRectCollide((x+1,y+1,w-1,h-1),(xx+1,yy+1,ww-1,hh-1)):
                                collide = True
                                collideX = x-32
                        if not collide:
                            self.pos[0] += self.fallSpeed
                        else:
                            self.pos[0] = collideX
                    if self.jumpOn:
                        if not self.jumping and self.grounded:
                            self.jumping = True
                            self.jumpStart = t
                            self.grounded = False
                    else:
                        if self.jumping and t-self.jumpStart > self.jumpMin:
                            self.jumping = False

                    if self.atkOn:
                        if t-self.prevBeam > self.beamDelay:
                            self.prevBeam = t
                            beamY = self.pos[1]-128
                            if self.facing == self.LEFT:
                                beamX = self.pos[0]-128-32
                            else:
                                beamX = self.pos[0]+32
                            self.beams += [Beam(beamX,beamY,self.facing, self.args["atk"], self)]

                if t-self.jumpStart > self.jumpMax:
                    self.jumping = False


GUISt = None
class ConstructorGUI(object):
    ADDREMOVE_TILE = 0
    ADD_MOB = 1
    ADD_DOOR = 2
    ADD_GEM = 3
    EDIT_MODE = 0
    GAME_MODE = 1
    def __init__(self):
        global GUISt
        GUISt = self
        self.sounds = {
                "Beam": pygame.mixer.Sound("./snds/beam.wav"),
                "Hurt": pygame.mixer.Sound("./snds/hurt.wav"),
                "Jump": pygame.mixer.Sound("./snds/jump.wav"),
                }

        self.tex = -1
        """
        self.botimg = pygame.image.load("./img/guibottombg.png")
        self.guiRenderer = chunkhandler.GUIBGRenderer()
        """
        self.font = pygame.font.Font("./fonts/NanumGothicBold.ttf", 11)
        self.textRenderer = StaticTextRenderer(self.font)
        self.button1 = Button(self.textRenderer, u"타일찍기/제거", self.AddTile, 5, SH-128+5)
        self.button2 = Button(self.textRenderer, u"몹찍기/제거", self.AddMob, 30+55, SH-128+5)
        self.button2 = Button(self.textRenderer, u"문추가/제거", self.AddDoor, 30+55+45+25, SH-128+5)
        self.button2 = Button(self.textRenderer, u"보석추가/제거", self.AddGem, 30+55+45+45+45, SH-128+5)
        self.button3 = Button(self.textRenderer, u"게임모드", self.GameMode, 60+55+45+45+45+45, SH-128+5)
        self.button4 = Button(self.textRenderer, u"이전", self.PrevStage, 5, SH-128+5+32)
        self.button5 = Button(self.textRenderer, u"다음", self.NextStage, 5+32+32, SH-128+5+32)
        self.button6 = Button(self.textRenderer, u"추가", self.AddStage, 5+32+32+32, SH-128+5+32)
        self.hpText = self.textRenderer.NewTextObject(u"체력", (255,255,255), True, (50,50,50))
        self.mpText = self.textRenderer.NewTextObject(u"마력", (255,255,255), True, (50,50,50))
        self.atkText = self.textRenderer.NewTextObject(u"공격력", (255,255,255), True, (50,50,50))
        self.healText = self.textRenderer.NewTextObject(u"힐", (255,255,255), True, (50,50,50))
        self.slashText = self.textRenderer.NewTextObject(u"/", (255,255,255), True, (50,50,50))

        self.buttonGame1 = ButtonGame(self.textRenderer, u"에딧모드", self.EditMode, 5, SH-128+5)
        self.buttonGame1.enabled = False

        #self.button = Button(self.Print, 
        self.deads = []

        self.mode = self.ADDREMOVE_TILE
        self.emode = self.EDIT_MODE

        try:
            numS = pickle.load(open("./numstages.pkl", "r"))
        except:
            numS = 1
        self.stages = [Stage() for i in range(numS)]
        try:
            for i in range(numS):
                self.stages[i].doors = pickle.load(open("./stage%ddoors.pkl" % (i+1), "r"))
        except:
            pass
        try:
            for i in range(numS):
                self.stages[i].enemyDefs = pickle.load(open("./stage%denemies.pkl" % (i+1), "r"))
        except:
            pass
        try:
            for i in range(numS):
                self.stages[i].tiles = pickle.load(open("./stage%dtiles.pkl" % (i+1), "r"))
        except:
            pass
        try:
            for i in range(numS):
                self.stages[i].gems = pickle.load(open("./stage%dgems.pkl" % (i+1), "r"))
        except:
            pass
        try:
            self.curDoorIdx = pickle.load(open("./stage%ddoorIdx.pkl" % (i+1), "r"))
        except:
            self.curDoorIdx = 0
        self.curStageIdx = 1
        self.tileIdx = 0
        self.mobIdx = 0
        self.gemIdx = 0
        EMgrSt.BindMDown(self.DragStart)
        EMgrSt.BindMUp(self.DragEnd)
        self.dragStartPos = (0,0)
        self.scrStartPos = (0,0)
        self.dragging = False
        self.connects = [(0,7),(7,0),(1,8),(6,9),(9,6)]
        # 일단 0에서 2로 이도은 되나 2에서 0이 안되므로 0에서 2로 이동한 순간 2에서 0으로 이동할 수 있도록 (2,0)을 추가해야 한다.
    def GetConnectivity(self, door):
        for con in self.connects:
            if door == con[0]:
                return con

    def GetStageAndPos(self, doorNum):
        idx = 0
        for stage in self.stages:
            for door in stage.doors.iterkeys():
                num = stage.doors[door]
                if doorNum == num:
                    return idx, door
            idx += 1

    def PrevStage(self):
        self.curStageIdx -= 1
        if self.curStageIdx < 0:
            self.curStageIdx = 0
    def NextStage(self):
        self.curStageIdx += 1
        if self.curStageIdx >= len(self.stages):
            self.curStageIdx = len(self.stages)-1
    def AddStage(self):
        self.stages += [Stage()]
    def DragStart(self,t,m,k):
        self.dragging = True
        self.dragStartPos = (m.x,m.y)
        self.scrStartPos = (
            self.stages[self.curStageIdx].scrX,
            self.stages[self.curStageIdx].scrY)
    def DragEnd(self,t,m,k):
        self.dragging = False

    def AddGem(self):
        self.mode = self.ADD_GEM
    def AddDoor(self):
        self.mode = self.ADD_DOOR
    def AddTile(self):
        self.mode = self.ADDREMOVE_TILE
    def GameMode(self):
        self.button1.enabled = False
        self.button2.enabled = False
        self.button3.enabled = False
        self.button4.enabled = False
        self.button5.enabled = False
        self.button6.enabled = False
        self.buttonGame1.enabled = True
        self.emode = self.GAME_MODE
        self.stages[self.curStageIdx].StartGame()
    def EditMode(self):
        self.button1.enabled = True
        self.button2.enabled = True
        self.button3.enabled = True
        self.button4.enabled = True
        self.button5.enabled = True
        self.button6.enabled = True
        self.buttonGame1.enabled = False
        self.emode = self.EDIT_MODE
    def AddMob(self):
        self.mode = self.ADD_MOB
    def Regen(self):
        """
        self.tex = texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        teximg = pygame.image.tostring(self.botimg, "RGBA", 0) 
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1024, 256, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
        self.guiRenderer.Regen()
        """

    def Tick(self,t,m,k):

        if self.emode == self.EDIT_MODE:
            x = self.stages[self.curStageIdx].scrX+m.x
            y = self.stages[self.curStageIdx].scrY+m.y
            x,y = x-(x%64), y-(y%64)

            if self.mode == self.ADDREMOVE_TILE:
                if LMB in m.pressedButtons.iterkeys() and m.y < SH-128:
                    self.stages[self.curStageIdx].AddTile(x,y,self.tileIdx)
                elif RMB in m.pressedButtons.iterkeys() and m.y < SH-128:
                    self.stages[self.curStageIdx].DelTile(x,y)
                elif LMB in m.pressedButtons.iterkeys() and m.y >= SH-128:
                    x = 400
                    y = SH-128+5
                    for i in range(len(AppSt._2d_grndtiles)):
                        if InRect(x,y,64,64, m.x,m.y):
                            self.tileIdx = i
                            break
                        x += 64+5
            elif self.mode == self.ADD_DOOR:
                x,y = x-(x%64), y-(y%64)
                if LMB in m.pressedButtons.iterkeys() and m.y < SH-128:
                    if (x,y) not in self.stages[self.curStageIdx].doors:
                        self.stages[self.curStageIdx].AddDoor(x,y)
                elif RMB in m.pressedButtons.iterkeys() and m.y < SH-128:
                    self.stages[self.curStageIdx].DelDoor(x,y)
                    """
                elif LMB in m.pressedButtons.iterkeys() and m.y >= SH-128:
                    x = 400
                    y = SH-128
                    for i in range(len(AppSt._2d_enemy_tiles)):
                        if InRect(x,y,128,128, m.x,m.y):
                            self.tileIdx = i
                            break
                        x += 128+5
                    """
            elif self.mode == self.ADD_GEM:
                x,y = x-(x%64), y-(y%64)
                if LMB in m.pressedButtons.iterkeys() and m.y < SH-128:
                    self.stages[self.curStageIdx].AddGem(x,y,self.gemIdx)
                elif RMB in m.pressedButtons.iterkeys() and m.y < SH-128:
                    self.stages[self.curStageIdx].DelGem(x,y)
                elif LMB in m.pressedButtons.iterkeys() and m.y >= SH-128:
                    x = 400
                    y = SH-128+5
                    for i in range(len(AppSt._2d_gem_tiles)):
                        if InRect(x,y,64,64, m.x,m.y):
                            self.gemIdx = i
                            break
                        x += 64+5


            elif self.mode == self.ADD_MOB:
                x,y = x-(x%64), y-(y%64)
                if LMB in m.pressedButtons.iterkeys() and m.y < SH-128:
                    self.stages[self.curStageIdx].AddEnemy(EnemyDef(self.mobIdx, 'enemy', x+64,y+128, {"hp":100,"atk":30}))
                elif RMB in m.pressedButtons.iterkeys() and m.y < SH-128:
                    self.stages[self.curStageIdx].DelEnemy(x+64,y+128)
                elif LMB in m.pressedButtons.iterkeys() and m.y >= SH-128:
                    x = 400
                    y = SH-128
                    for i in range(len(AppSt._2d_enemy_tiles)):
                        if InRect(x,y,128,128, m.x,m.y):
                            self.mobIdx = i
                            break
                        x += 128+5
            if self.dragging:
                self.stages[self.curStageIdx].scrX = self.scrStartPos[0] + (self.dragStartPos[0]-m.x)
                self.stages[self.curStageIdx].scrY = self.scrStartPos[1] + (self.dragStartPos[1]-m.y)
                self.stages[self.curStageIdx].scrX = max(-1000, self.stages[self.curStageIdx].scrX)
                self.stages[self.curStageIdx].scrY = min(1000, self.stages[self.curStageIdx].scrY)
        elif self.emode == self.GAME_MODE:
            self.stages[self.curStageIdx].scrX = AppSt.player.pos[0]-SW/2
            self.stages[self.curStageIdx].scrY = AppSt.player.pos[1]-SH/2

    def Render(self):
        """
        glBindTexture(GL_TEXTURE_2D, AppSt.tvbg)
        DrawQuadTexTVBG(0,0,SW,SH)
        glBindTexture(GL_TEXTURE_2D, AppSt.bgbg)
        DrawQuadTex(0,0,SW,SH)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        self.guiRenderer.Render()

        
        DrawQuad(400,SH-256,SW-400,256,(128,128,128,128),(128,128,128,128))
        if AppSt.tileMode in [AppSt.TILECHANGE1, AppSt.TILECHANGE2]:
            x = 400+5
            y = SH-256
            y += 5
            for tile in AppSt.texTiles:
                glBindTexture(GL_TEXTURE_2D, tile[0])
                DrawQuadTex(x,y,32,32)
                x += 32 + 5
                if x+32+5 > SW:
                    x = 400+5
                    y += 32+5
        """
        """
        glBindTexture(GL_TEXTURE_2D, AppSt.tex2)
        DrawQuadTex(400+32,SH-256+5,32,32)
        glBindTexture(GL_TEXTURE_2D, AppSt.tex)
        DrawQuadTex(400+32+32,SH-256+5,32,64)
        """



        tiles = self.stages[self.curStageIdx].GetTiles()
        for tile_ in tiles:
            x,y,tile = tile_
            x -= self.stages[self.curStageIdx].scrX
            y -= self.stages[self.curStageIdx].scrY
            glBindTexture(GL_TEXTURE_2D, AppSt._2d_grndtiles[tile])
            DrawQuadTex(x,y,64,64)

        scrX = self.stages[self.curStageIdx].scrX
        scrY = self.stages[self.curStageIdx].scrY

        x = 400
        y = SH-128
        if self.emode == self.EDIT_MODE:
            for enemy in self.stages[self.curStageIdx].enemyDefs.itervalues():
                glBindTexture(GL_TEXTURE_2D, AppSt._2d_enemy_tiles[enemy.tileIdx][AppSt.ani[AppSt.aniIdx]])
                DrawQuadTex(enemy.pos[0]-scrX-64,enemy.pos[1]-scrY-128,128,128)

            for doorPos in self.stages[self.curStageIdx].doors.iterkeys():
                glBindTexture(GL_TEXTURE_2D, AppSt._2d_door)
                xx,yy = doorPos
                DrawQuadTex(xx-scrX,yy-scrY,128,128)
            for gem in self.stages[self.curStageIdx].gems.iterkeys():
                gemTile = self.stages[self.curStageIdx].gems[gem]
                glBindTexture(GL_TEXTURE_2D, AppSt._2d_gem_tiles[gemTile])
                DrawQuadTex(gem[0]-scrX,gem[1]-scrY, 64,64)

        else:
            for doorPos in self.stages[self.curStageIdx].doors.iterkeys():
                glBindTexture(GL_TEXTURE_2D, AppSt._2d_door)
                xx,yy = doorPos
                DrawQuadTex(xx-scrX,yy-scrY,128,128)

                num = self.stages[self.curStageIdx].doors[doorPos]

                openDoorFound = False
                closedDoorFound = False
                for con in self.connects:
                    a,b = con
                    if a == num:
                        openDoorFound = True
                    if b == num:
                        closedDoorFound = True

                if not openDoorFound and closedDoorFound:
                    AppSt.textRenderer.RenderText(AppSt.lockedText, (doorPos[0]+64-15-scrX, doorPos[1]-32-scrY))

            for gem in self.stages[self.curStageIdx].gameGems.iterkeys():
                gemTile = self.stages[self.curStageIdx].gameGems[gem]
                glBindTexture(GL_TEXTURE_2D, AppSt._2d_gem_tiles[gemTile])
                DrawQuadTex(gem[0]-scrX,gem[1]-scrY, 64,64)

            for dead in self.deads:
                glBindTexture(GL_TEXTURE_2D, AppSt._2d_tiles_dead)
                DrawQuadTex(dead.pos[0]-scrX,dead.pos[1]-scrY, 64,64)

            for enemy in self.stages[self.curStageIdx].enemies:
                glBindTexture(GL_TEXTURE_2D, AppSt._2d_enemy_tiles[enemy.tileIdx][AppSt.ani[AppSt.aniIdx]])
                if enemy.facing == enemy.LEFT:
                    DrawQuadTexFlipX(enemy.pos[0]-scrX-64,enemy.pos[1]-scrY-128,128,128)
                else:
                    DrawQuadTex(enemy.pos[0]-scrX-64,enemy.pos[1]-scrY-128,128,128)
                for beam in enemy.beams:
                    glBindTexture(GL_TEXTURE_2D, AppSt._2d_beam)
                    DrawQuadTex(beam.x-scrX,beam.y-scrY,128,64)


            for beam in AppSt.player.beams:
                glBindTexture(GL_TEXTURE_2D, AppSt._2d_beam)
                DrawQuadTex(beam.x-scrX,beam.y-scrY,128,64)
                

        DrawQuad(0,SH-128,SW,128,(128,128,128,255),(128,128,128,255))
        if self.emode == self.EDIT_MODE:
            AppSt.RenderNumber(self.curStageIdx, 32+5, SH-128+5+32)
            if self.mode == self.ADDREMOVE_TILE:
                for i in range(len(AppSt._2d_grndtiles)):
                    glBindTexture(GL_TEXTURE_2D, AppSt._2d_grndtiles[i])
                    DrawQuadTex(x,y,64,64)
                    x += 64+5
            elif self.mode == self.ADD_GEM:
                for i in range(len(AppSt._2d_gem_tiles)):
                    glBindTexture(GL_TEXTURE_2D, AppSt._2d_gem_tiles[i])
                    DrawQuadTex(x,y,64,64)
                    x += 64+5
            elif self.mode == self.ADD_MOB:
                for i in range(len(AppSt._2d_enemy_tiles)):
                    glBindTexture(GL_TEXTURE_2D, AppSt._2d_enemy_tiles[i][1])
                    DrawQuadTex(x,y,128,128)
                    x += 128+5
            for door in self.stages[self.curStageIdx].doors.iterkeys():
                num = self.stages[self.curStageIdx].doors[door]
                AppSt.RenderNumber(num, door[0]+64-scrX, door[1]+64-scrY)
        else:
            y = 32+SH-128
            self.textRenderer.RenderText(self.hpText, (5, y))
            AppSt.RenderNumber(AppSt.player.args["hp"], 40, y)
            self.textRenderer.RenderText(self.slashText, (90, y))
            AppSt.RenderNumber(AppSt.player.args["maxhp"], 100, y)
            self.textRenderer.RenderText(self.atkText, (5+200, y))
            AppSt.RenderNumber(AppSt.player.args["atk"], 40+200, y)

            y += 32
            self.textRenderer.RenderText(self.mpText, (5, y))
            AppSt.RenderNumber(AppSt.player.args["mana"], 40, y)
            self.textRenderer.RenderText(self.slashText, (90, y))
            AppSt.RenderNumber(AppSt.player.args["maxmana"], 100, y)
            self.textRenderer.RenderText(self.healText, (5+200, y))
            AppSt.RenderNumber(AppSt.player.args["heal"], 40+200, y)




# 이걸 GLQUAD랑 텍스쳐를 이용하도록 한다.
# 매번 blit할 필요가 없다.
# 글자만 pack 해서 0.5초당 한 번씩 블릿하면 된다!



class CustomIMEModule:
    def __init__(self, printFunc):
        EMgrSt.BindTick(self._OnTick)
        EMgrSt.BindKeyDown(self._OnKeyPressed)
        self.printFunc = printFunc

        self.cmdText = u""

        self.composingText = u""
        self.composing = False

        self.hangulMode = False
        self.chatMode = False

        self.keyPressedWaitedFor = 0
        self.keyRepeatStartWaitedFor = 0
        self.pressedDelay = 50
        self.repeatStartDelay = 250

        self.lastKey = 0
        self.lastText = 0
        self.lastTick = pygame.time.get_ticks()
        

        import hangul
        self.hangulComposer = hangul.HangulComposer()

    def ResetTexts(self):
        self._FinishChatMode()
        self.cmdText = u""
    def SetText(self, text):
        self._FinishChatMode()
        self.cmdText = unicode(text)
    def SetPrintFunc(self, func):
        self.printFunc = func
    def SetActive(self, mode):
        self.chatMode = mode
        if not mode:
            self._FinishChatMode()
        else:
            pass

    def _ToggleHangulMode(self):
        self.hangulMode = not self.hangulMode

    def _FinishChatMode(self):
        self._FinishHangulComposing()

    def _OnTick(self, tick, lastMouseState, lastKeyState):
        tick2 = tick - self.lastTick
        self.lastTick = tick
        def RepeatKeyEvent():
            if lastKeyState.GetPressedKey():
                # check if it's time to start to repeat
                if self.keyRepeatStartWaitedFor > self.repeatStartDelay and \
                        self.keyPressedWaitedFor > self.pressedDelay: # check if last repeat waiting is over
                    self.keyPressedWaitedFor = 0
                    if self.lastKey != K_RETURN:
                        self._ProcessKeyPressed(self.lastKey, self.lastText)
                self.keyPressedWaitedFor += tick2
                self.keyRepeatStartWaitedFor += tick2

        if self.chatMode:
            RepeatKeyEvent()

    def _OnKeyPressed(self, tick, m, k):
        if self.chatMode:
            def ResetRepeatKeyEvent():
                self.keyPressedWaitedFor = 0
                self.keyRepeatStartWaitedFor = 0
            ResetRepeatKeyEvent()
            self._ProcessKeyPressed(k.pressedKey, k.pressedChar)

    def _ProcessKeyPressed(self, key, text):
        self.lastKey = key
        self.lastText = text

        if key == K_RALT:
            self._ToggleHangulMode()

        elif key == K_BACKSPACE:
            if self.hangulComposer.iscomposing():
                self._DoHangulBackspace()
            else:
                if self.cmdText:
                    self.cmdText = self.cmdText[:-1]
            self._PrintCmd(self.cmdText + self.composingText)

        else:
            self._ProcessChar(text)
            self._PrintCmd(self.cmdText + self.composingText)

    def _DoHangulBackspace(self):
        bs = self.hangulComposer.backspace()
        if bs:
            uni, finished, finishedUni = bs
            if uni:
                self._StartHangulComposing(uni)
            else:
                self._FinishHangulComposing()
        else:
            self._FinishHangulComposing()

    def _StartHangulComposing(self, composingText):
        self.composing = True
        self.composingText = composingText
    def _FinishHangulComposing(self):
        self.hangulComposer.finish()
        if self.composing:
            self.cmdText += self.composingText
            self.composing = False
            self.composingText = u''

    def _ProcessChar(self, char):
        if len(self.cmdText) > 50:
            return
        alphabets = SpecialStrings.GetAlphabets()
        numerics = SpecialStrings.GetNumerics()
        specials = SpecialStrings.GetSpecials()
        #char = chr(char)

        if self.hangulMode and char in alphabets:
            uni, finished, finishedUni = self.hangulComposer.feed(char) # XXX: feel exotic to use huh?
            if finished:
                self.cmdText += finishedUni
                self._StartHangulComposing(uni[len(finishedUni):])
            else:
                self._StartHangulComposing(uni)

        elif char in numerics + alphabets + specials:
            self._FinishHangulComposing()
            self.cmdText += char
        else:
            self._FinishHangulComposing()

    def _PrintCmd(self, text):
        self.printFunc(text)


class TextArea(object):
    def __init__(self, x,y,w,h, letterW, lineH, color=(0,0,0), lineCut=True):
        self.lines = []
        self.rect = x,y,w,h
        self.letterW = letterW
        self.lineH = lineH
        self.color = color
        self.lineCut = lineCut
    def SetText(self, text):
        if text:
            lenn = len(self.lines)
            if self.lineCut:
                offset = self.rect[2]/self.letterW
                for textt in text.split("\n"):
                    leng = 0
                    while leng < len(textt):
                        newtext = textt[leng:leng+offset]
                        self.lines += [newtext]
                        leng += offset
            else:
                self.lines += text.split("\n")
        else:
            self.lines = []

    def Clear(self):
        self.lines = []
    def Update(self, renderer):
        y = 0
        for text in self.lines:
            renderer.NewTextObject(text, self.color, (self.rect[0], self.rect[1]+y), border=True, borderColor = (128,128,128))
            y += self.lineH
            if y > self.rect[3]:
                return

class TalkBox(object):
    def __init__(self):
        self.font3 = pygame.font.Font("./fonts/Fanwood.ttf", 15)
        self.textRendererArea = DynamicTextRenderer(self.font3)
        self.lines = []
        self.lines2 = []
        self.rect = (SW-500)/2,30,500,280
        self.letterW = 9
        self.lineH = 15
        self.color = (255,255,255)
        self.lineCut = True
        self.renderedLines = []
        self.renderedLines2 = []
        self.binds = {}
        self.mousePos = []
        self.selectedPos = None
        EMgrSt.BindMotion(self.Motion)
        EMgrSt.BindLDown(self.LDown)
        # 텍스트를 배경과 함께 출력하고
        # 텍스트, 클릭가능한 선택지
        # 다음화면으로 넘어가는거 등등을 해야한다.
        # 화면 넘어갈 때마다 텍스쳐를 업뎃하자
        self.active = False
    def AddText(self, text, color, bcolor): # 여기에 현재 텍스트를 추가하고 콜백을 추가하고
        # 선택지가 나오면 다시 클리어하고 현재텍스트를 추가하고 이런다
        lenn = len(self.lines)
        if self.lineCut:
            offset = self.rect[2]/self.letterW
            for textt in text.split("\n"):
                leng = 0
                while leng < len(textt):
                    newtext = textt[leng:leng+offset]
                    self.lines += [newtext]
                    leng += offset
        else:
            self.lines += text.split("\n")

        
        for text in self.lines[lenn:]:
            self.renderedLines += [self.textRendererArea.NewTextObject(text, color, (0, 0), border=False, borderColor = bcolor)]
    def AddSelection(self, text, bind, color, bcolor):
        lenn = len(self.lines2)
        self.lines2 += [text]

        
        for text in self.lines2[lenn:]:
            self.renderedLines2 += [self.textRendererArea.NewTextObject(text, color, (0, 0), border=False, borderColor = bcolor)]

        self.binds[lenn] = bind

    def Clear(self):
        self.lines = []
        self.lines2 = []
        self.renderedLines = []
        self.renderedLines2 = []
        self.textRendererArea.Clear()
        self.binds = {}

    def LDown(self, t, m, k):
        if self.selectedIdx != -1 and self.active:
            self.binds[self.selectedIdx]()
    def Motion(self, t, m, k):
        toDrawLines = self.rect[3]/self.lineH
        if len(self.renderedLines) >= toDrawLines:
            toDraw = self.renderedLines[-toDrawLines:]
        else:
            toDraw = self.renderedLines[:]

        if len(self.renderedLines2) >= toDrawLines:
            toDraw2 = self.renderedLines2[-toDrawLines:]
        else:
            toDraw2 = self.renderedLines2[:]

        y = self.lineH*(len(toDraw)+1)
        self.selectedPos = None
        self.selectedIdx = -1
        for i in range(len(toDraw2)):
            xx,yy = self.rect[0], self.rect[1]+y
            if InRect(xx,yy+5+2,self.rect[2], self.lineH, m.x, m.y):
                self.selectedPos = (xx,yy+5+2)
                self.selectedIdx = i
                break
            y += self.lineH

    def Render(self):
        DrawQuad(*(self.rect+((205,209,184,255), (205,209,184,255))))
        if self.selectedPos:
            DrawQuad(*(self.selectedPos+(self.rect[2], self.lineH)+((100,100,90,255), (100,100,90,255))))
        toDrawLines = self.rect[3]/self.lineH
        if len(self.renderedLines) >= toDrawLines:
            toDraw = self.renderedLines[-toDrawLines:]
        else:
            toDraw = self.renderedLines[:]

        if len(self.renderedLines2) >= toDrawLines:
            toDraw2 = self.renderedLines2[-toDrawLines:]
        else:
            toDraw2 = self.renderedLines2[:]

        y = 0
        for textid in toDraw:
            pos = self.rect[0]+5, self.rect[1]+y+5
            self.textRendererArea.RenderOne(textid, pos)
            y += self.lineH
            if y > self.rect[3]:
                break

        y += self.lineH
        for textid in toDraw2:
            pos = self.rect[0]+5, self.rect[1]+y+5
            self.textRendererArea.RenderOne(textid, pos)
            y += self.lineH
            if y > self.rect[3]:
                break

        # 다이나믹 렌더러를 가지고있고, AddNew로 텍스트가 추가될 때마다 추가하고
        # 한개씩 렌더링하고
        # 라인수가 일정 이상을 넘어서면 플러시
class MsgBox(object):
    def __init__(self):
        self.font3 = pygame.font.Font("./fonts/GoudyBookletter1911.ttf", 15)
        self.textRendererArea = DynamicTextRenderer(self.font3)
        self.lines = []
        self.rect = 0,SH-170,SW,100
        self.letterW = 9
        self.lineH = 15
        self.color = (255,255,255)
        self.lineCut = True
        self.renderedLines = []
    def AddText(self, text, color, bcolor):
        lenn = len(self.lines)
        if self.lineCut:
            offset = self.rect[2]/self.letterW
            for textt in text.split("\n"):
                leng = 0
                while leng < len(textt):
                    newtext = textt[leng:leng+offset]
                    self.lines += [newtext]
                    leng += offset
        else:
            self.lines += text.split("\n")

        
        for text in self.lines[lenn:]:
            self.renderedLines += [(self.textRendererArea.NewTextObject(text, color, (0, 0), border=True, borderColor = bcolor), color, bcolor)]

    def Clear(self):
        self.lines = []
    def Render(self):
        toDrawLines = self.rect[3]/self.lineH
        if len(self.renderedLines) > 120:
            self.textRendererArea.Clear()
            self.renderedLines = self.renderedLines[-toDrawLines:]
            idx  = 0
            for text in self.lines[-toDrawLines:]:
                old, color, bcolor = self.renderedLines[idx]
                self.renderedLines[idx] = [self.textRendererArea.NewTextObject(text, color, (0, 0), border=True, borderColor = bcolor)]
                idx += 1
            self.lines = self.lines[-toDrawLines:]

        if len(self.renderedLines) >= toDrawLines:
            toDraw = self.renderedLines[-toDrawLines:]
        else:
            toDraw = self.renderedLines[:]

        y = 0
        for textid in toDraw:
            pos = self.rect[0], self.rect[1]+y
            self.textRendererArea.RenderOne(textid[0], pos)
            y += self.lineH
            if y > self.rect[3]:
                break

        # 다이나믹 렌더러를 가지고있고, AddNew로 텍스트가 추가될 때마다 추가하고
        # 한개씩 렌더링하고
        # 라인수가 일정 이상을 넘어서면 플러시


class DynamicTextRenderer(object):
    # 한 씬에 렌더할 텍스트를 모아두고 한번에 렌더링을 하며
    # 0.25초당 한번씩 업데이트 된다.
    # 음....512짜리 4장 정도면 화면 꽉차니까 그거만 만들고 모자라면 더이상 추가하지 않는다.
    def __init__(self, font):
        self.font = font
        self.surfs = []
        for i in range(4):
            texid = glGenTextures(1)
            self.surfs += [[pygame.Surface((512,512), flags=SRCALPHA), texid, True]]
        self.surfIdx = 0
        self.texts = []
    def NewTextObject(self, text, color, pos, border=False, borderColor = (255,255,255)):
        if self.surfIdx >= 4:
            return
        if self.texts:
            prevsurfid, prevtextposList, prevpos = self.texts[-1]
            prevsurf = self.surfs[prevsurfid][0]
        else:
            prevsurfid = 0
            prevsurf, texid, updated = self.surfs[0]
            updated = True
            prevtextposList = [[0,0,0,0]]
        textsurf = Text.GetSurf(self.font, text, (0, 0), color, border, borderColor)[0]
        if textsurf.get_height()*((textsurf.get_width()/512)+1) >= 512:
            return None

        x,y,w,h = prevtextposList[-1]
        surf = prevsurf
        surfid = prevsurfid
        x = x+w
        w = textsurf.get_width()
        h = textsurf.get_height()
        
        availLen = 512-x
        needLen = w-availLen
        if needLen > 0:
            needYNum = (needLen/512)+2
            if y+needYNum*h >= 512:
                self.surfIdx += 1
                if self.surfIdx >= 4:
                    return
                surf = self.surfs[self.surfIdx][0]
                x,y = 0,0
                surfid = self.surfIdx
                availLen = 512
                needLen = w-availLen

        self.surfs[self.surfIdx][2] = True

        newtextposList = []
        xx = 0
        if needLen <= 0:
            surf.fill((0,0,0,0), pygame.Rect(x,y,w,h))
            surf.blit(textsurf, pygame.Rect(x,y,w,h), pygame.Rect(xx,0,w,h))
            newtextposList += [[x,y,w,h]]
        else:
            surf.fill((0,0,0,0), pygame.Rect(x,y,availLen,h))
            surf.blit(textsurf, pygame.Rect(x,y,availLen,h), pygame.Rect(xx,0,availLen,h))
            newtextposList += [[x,y,availLen,h]]
            curTextX = availLen
            xx += availLen
            x = 0
            y += h
            while True: 
                if needLen <= 512:
                    surf.fill((0,0,0,0), pygame.Rect(x,y,needLen,h))
                    surf.blit(textsurf, pygame.Rect(x,y,needLen,h), pygame.Rect(xx,0,needLen,h))
                    newtextposList += [[x,y,needLen,h]]
                    break
                else:
                    surf.fill((0,0,0,0), pygame.Rect(x,y,512,h))
                    surf.blit(textsurf, pygame.Rect(x,y,512,h), pygame.Rect(xx,0,512,h))
                    newtextposList += [[x,y,512,h]]
                    xx += 512
                    x = 0
                    y += h
                    needLen -= 512
        self.texts += [[surfid, newtextposList, pos]]
        return len(self.texts)-1

    def Clear(self): # 걍 무조건 1초에 4번 불린다. 아니면 3번 불리던가.
        self.texts = []
        self.surfIdx = 0
    def Render(self):
        textid = 0
        for text in self.texts:
            surfid, poslist, pos = text
            self.RenderText(textid, pos)
            textid += 1
    def RenderOne(self, textid, pos):
        self.RenderText(textid, pos)
    def RegenTex(self):
        for idx in range(len(self.surfs)):
            self.surfs[idx][1] = glGenTextures(1)
            self.surfs[idx][2] = True
    def GetDimension(self, textid):
        surfid, posList, pos_ = self.texts[textid]
        w = 0
        h = 0
        for imgpos in posList:
            w += imgpos[2]
            h += imgpos[3]
        return w,h
    def RenderText(self, textid, pos):
        surfid, posList, pos_ = self.texts[textid]
        surf, texid, updated = self.surfs[surfid]
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)


        if updated:
            teximg = pygame.image.tostring(surf, "RGBA", 0) 
            glBindTexture(GL_TEXTURE_2D, texid)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            self.surfs[surfid][2] = False

        glBegin(GL_QUADS)
        xx,yy = pos
        for imgpos in posList:
            x,y,w,h = imgpos
            glTexCoord2f(float(x)/512.0, float(y+h)/512.0)
            glVertex3f(float(xx), -float(yy+h), 100.0)

            glTexCoord2f(float(x+w)/512.0, float(y+h)/512.0)
            glVertex3f(float(xx+w), -float(yy+h), 100.0)

            glTexCoord2f(float(x+w)/512.0, float(y)/512.0)
            glVertex3f(float(xx+w), -float(yy), 100.0)

            glTexCoord2f(float(x)/512.0, float(y)/512.0)
            glVertex3f(float(xx), -float(yy), 100.0)
            xx += w

        glEnd()


class StaticTextRenderer(object):
    # 아이템 숫자 표시는.... 여기서 0~9를 렌더링 한 후에 그 숫자를 가지고 렌더링한다!
    def __init__(self, font):
        self.font = font
        texid = glGenTextures(1)
        self.surfs = [[pygame.Surface((512,512), flags=SRCALPHA), texid, True]]
        self.texts = []
    def GetDimension(self, textid):
        surfid, posList = self.texts[textid]
        w = 0
        h = 0
        for imgpos in posList:
            w += imgpos[2]
            h += imgpos[3]
        return w,h

    def NewTextObject(self, text, color, border=False, borderColor = (255,255,255)):
        if self.texts:
            prevsurfid, prevtextposList = self.texts[-1]
            prevsurf = self.surfs[prevsurfid][0]
        else:
            prevsurfid = 0
            prevsurf, texid, updated = self.surfs[0]
            prevtextposList = [[0,0,0,0]]

        textsurf = Text.GetSurf(self.font, text, (0, 0), color, border, borderColor)[0]
        if textsurf.get_height()*((textsurf.get_width()/512)+1) >= 512:
            return None

        x,y,w,h = prevtextposList[-1]
        surf = prevsurf
        surfid = prevsurfid
        x = x+w

        w = textsurf.get_width()
        h = textsurf.get_height()
        
        availLen = 512-x
        needLen = w-availLen
        if needLen > 0:
            needYNum = (needLen/512)+2
            if y+needYNum*h >= 512:
                texid = glGenTextures(1)
                self.surfs += [[pygame.Surface((512,512), flags=SRCALPHA), texid, True]]
                surf = self.surfs[-1][0]
                surfid = len(self.surfs)-1
                x,y = 0,0
                availLen = 512
                needLen = w-availLen
            else:
                self.surfs[prevsurfid][2] = True

        newtextposList = []
        xx = 0
        if needLen <= 0:
            surf.fill((0,0,0,0), pygame.Rect(x,y,w,h))
            surf.blit(textsurf, pygame.Rect(x,y,w,h), pygame.Rect(xx,0,w,h))
            newtextposList += [[x,y,w,h]]
        else:
            surf.fill((0,0,0,0), pygame.Rect(x,y,availLen,h))
            surf.blit(textsurf, pygame.Rect(x,y,availLen,h), pygame.Rect(xx,0,availLen,h))
            newtextposList += [[x,y,availLen,h]]
            curTextX = availLen
            xx += availLen
            x = 0
            y += h
            while True: 
                if needLen <= 512:
                    surf.fill((0,0,0,0), pygame.Rect(x,y,needLen,h))
                    surf.blit(textsurf, pygame.Rect(x,y,needLen,h), pygame.Rect(xx,0,needLen,h))
                    newtextposList += [[x,y,needLen,h]]
                    break
                else:
                    surf.fill((0,0,0,0), pygame.Rect(x,y,512,h))
                    surf.blit(textsurf, pygame.Rect(x,y,512,h), pygame.Rect(xx,0,512,h))
                    newtextposList += [[x,y,512,h]]
                    xx += 512
                    x = 0
                    y += h
                    needLen -= 512

        self.texts += [[surfid, newtextposList]]
        return len(self.texts)-1

    def RegenTex(self):
        for idx in range(len(self.surfs)):
            self.surfs[idx][1] = glGenTextures(1)
            self.surfs[idx][2] = True

    def RenderText(self, textid, pos):
        surfid, posList = self.texts[textid]
        surf, texid, updated = self.surfs[surfid]
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)


        if updated:
            glBindTexture(GL_TEXTURE_2D, texid)
            teximg = pygame.image.tostring(surf, "RGBA", 0) 
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            self.surfs[surfid][2] = False

        glBegin(GL_QUADS)
        xx,yy = pos
        for imgpos in posList:
            x,y,w,h = imgpos
            glTexCoord2f(float(x)/512.0, float(y+h)/512.0)
            glVertex3f(float(xx), -float(yy+h), 100.0)

            glTexCoord2f(float(x+w)/512.0, float(y+h)/512.0)
            glVertex3f(float(xx+w), -float(yy+h), 100.0)

            glTexCoord2f(float(x+w)/512.0, float(y)/512.0)
            glVertex3f(float(xx+w), -float(yy), 100.0)

            glTexCoord2f(float(x)/512.0, float(y)/512.0)
            glVertex3f(float(xx), -float(yy), 100.0)
            xx += w

        glEnd()

def RenderImg(texID, texupx, texupy, x, y, w, h):
    glBindTexture(GL_TEXTURE_2D, texID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glBegin(GL_QUADS)
    glTexCoord2f(texupx, texupy+float(h)/512.0)
    glVertex3f(float(x), -float(y+h), 100.0)

    glTexCoord2f(texupx+float(w)/512.0, texupy+float(h)/512.0)
    glVertex3f(float(x+w), -float(y+h), 100.0)

    glTexCoord2f(texupx+float(w)/512.0, texupy)
    glVertex3f(float(x+w), -float(y), 100.0)

    glTexCoord2f(texupx, texupy)
    glVertex3f(x, -float(y), 100.0)
    glEnd()

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


class SpecialStrings:
    def GetAlphabets(self):
        alphabets = [chr(i) for i in range(ord('a'),ord('z')+1)+range(ord('A'),ord('Z')+1)]
        return alphabets
    def GetNumerics(self):
        numerics = [chr(i) for i in range(ord('0'),ord('9')+1)]
        return numerics
    def GetSpecials(self):
        specialOrdsTup = [(32, 48), (58, 65), (91, 97), (123,127)]
        specialOrds = []
        for tup in specialOrdsTup:
            start, end = tup
            for i in range(start, end):
                specialOrds.append(i)
        specials = [chr(i) for i in specialOrds]
        return specials
SpecialStrings = SpecialStrings()


class Camera:
    def __init__(self):
        '''
        self.view = Vector(0, 0, 1.0).Normalized()
        self.rotX = 0
        self.rotY = ((math.pi/2)-0.1)
        self.posz = -3.0
        self.posx = 0
        self.posy = 0
        '''
        self.qPitch = Quaternion()
        self.qHeading = Quaternion()
        self.pitchDegrees = 0.0
        self.headingDegrees = 0.0
        self.directionVector = Vector()
        self.forwardVelocity = 1.0
        self.pos = Vector(0.0, 0.0, 0.0)
        self.xsens = 0.2
        self.ysens = 0.2

    def RotateVert(self, vert, angle, axis):
        axis = axis.Normalized()
        V = Quaternion(vert.x, vert.y, vert.z, 0)
        R = self.Rotation(angle, axis)
        W = R * V * R.Conjugate()
        return Vector(W.x, W.y, W.z)#.Normalized()

    def Rotation(self, angle, v):
        from math import sin, cos
        x = v.x * sin(float(angle)/2.0)
        y = v.y * sin(float(angle)/2.0)
        z = v.z * sin(float(angle)/2.0)
        w = cos(float(angle)/2.0)
        return Quaternion(x,y,z,w)


    def RotateByXY(self, xmoved, ymoved):
        '''
        if xmoved or ymoved:
            factor = 1000.0

            yMax = ((math.pi/2)-0.1)
            yMin = 0.1
            xmoved /= factor
            ymoved /= factor
    
            self.rotX += xmoved
            self.rotY += ymoved
            self.rotX = self.rotX % (2*math.pi)
            if self.rotY > yMax:
                self.rotY = yMax
            elif self.rotY < yMin:
                self.rotY = yMin

            view = self.view#Vector(0.0, 0.0, 1.0)
            pos = Vector(self.posx, self.posy, self.posz)
            axis = (view-pos).Cross(Vector(0.0,1.0,0.0)).Normalized()
            #view = self.RotateVert(view, -self.rotY, axis)
            #self.view = self.RotateVert(view, -self.rotX, Vector(0, 1.0, 0))
            view = self.RotateVert(view, -ymoved, axis)
            self.view = self.RotateVert(view, -xmoved, Vector(0, 1.0, 0))
        '''
        self.pitchDegrees += float(ymoved)*self.ysens
        if self.pitchDegrees >= 89.9:
            self.pitchDegrees = 89.9
        if self.pitchDegrees <= 10.0:#-89.9:
            self.pitchDegrees = 10.0#-89.9
        self.headingDegrees += float(xmoved)*self.xsens

    def ApplyCamera(self):
	self.qPitch.CreateFromAxisAngle(1.0, 0.0, 0.0, self.pitchDegrees)
	self.qHeading.CreateFromAxisAngle(0.0, 1.0, 0.0, self.headingDegrees)

	# Combine the pitch and heading rotations and store the results in q
	q = self.qPitch * self.qHeading
	matrix = q.CreateMatrix()

	# Let OpenGL set our new prespective on the world!
	glMultMatrixf(matrix)

	# Create a matrix from the pitch Quaternion and get the j vector
	# for our direction.
	matrix = self.qPitch.CreateMatrix()
	self.directionVector.y = matrix[9]

	# Combine the heading and pitch rotations and make a matrix to get
	# the i and j vectors for our direction.
	q = self.qHeading * self.qPitch
	matrix = q.CreateMatrix()
	self.directionVector.x = matrix[8]
	self.directionVector.z = matrix[10]

	# Scale the direction by our speed.
	self.directionVector.MultScalar(self.forwardVelocity)

	# Increment our position by the vector
	#self.pos.x += self.directionVector.x
	#self.pos.y += self.directionVector.y
	#self.pos.z += self.directionVector.z

	# Translate to our new position.
	glTranslatef(-self.pos.x, -(self.pos.y), self.pos.z) # 아 이게 왜 방향이 다 엉망인 이유였구만.... -z를 써야되는데-_-

        #glTranslatef(self.posx, self.posy, self.posz)
        #pos = Vector(self.posx, self.posy, self.posz).Normalized()
        #glpLookAt(pos, self.view,
        #        Vector(0.0, 1.0, 0.0).Normalized())
        dirV = self.GetDirV().Normalized().MultScalar(AppSt.camZoom)
        glTranslatef(dirV.x, dirV.y, -dirV.z) # Trackball implementation
    def GetInversedPos(self, vec):
        vec = vec+(1.0,)
        # glTranslatef(dirV.x, dirV.y, -dirV.z) inverse1*vec
	#glTranslatef(-self.pos.x, -(self.pos.y), self.pos.z) # inverse2*vec
	#glMultMatrixf(matrix) inverse3*vec 하면 최종 벡터가 나온다.
        #1 0 0 x 0 1 0 y 0 0 1 z 0 0 0 1 translate
	self.qPitch.CreateFromAxisAngle(1.0, 0.0, 0.0, self.pitchDegrees)
	self.qHeading.CreateFromAxisAngle(0.0, 1.0, 0.0, self.headingDegrees)

	# Combine the pitch and heading rotations and store the results in q
	q = self.qPitch * self.qHeading
	matrix3 = q.CreateMatrix()

	# Let OpenGL set our new prespective on the world!
	#glMultMatrixf(matrix)

	# Create a matrix from the pitch Quaternion and get the j vector
	# for our direction.
	matrix = self.qPitch.CreateMatrix()
	self.directionVector.y = matrix[9]

	# Combine the heading and pitch rotations and make a matrix to get
	# the i and j vectors for our direction.
	q = self.qHeading * self.qPitch
	matrix = q.CreateMatrix()
	self.directionVector.x = matrix[8]
	self.directionVector.z = matrix[10]

	# Scale the direction by our speed.
	self.directionVector.MultScalar(self.forwardVelocity)

	# Increment our position by the vector
	#self.pos.x += self.directionVector.x
	#self.pos.y += self.directionVector.y
	#self.pos.z += self.directionVector.z

	# Translate to our new position.
	#glTranslatef(-self.pos.x, -(self.pos.y), self.pos.z) # 아 이게 왜 방향이 다 엉망인 이유였구만.... -z를 써야되는데-_-
        matrix2 = [1, 0, 0, -self.pos.x,
                   0, 1, 0, -self.pos.y,
                   0, 0, 1, self.pos.z,
                   0, 0, 0, 1]
        #glTranslatef(self.posx, self.posy, self.posz)
        #pos = Vector(self.posx, self.posy, self.posz).Normalized()
        #glpLookAt(pos, self.view,
        #        Vector(0.0, 1.0, 0.0).Normalized())
        dirV = self.GetDirV().Normalized().MultScalar(14.0)
        #glTranslatef(dirV.x, dirV.y, -dirV.z) # Trackball implementation
        matrix1 = [1, 0, 0, dirV.x,
                   0, 1, 0, dirV.y,
                   0, 0, 1, -dirV.z,
                   0, 0, 0, 1]
        mat1 = AppSt.GetInverseMatrix(matrix1)
        mat2 = AppSt.GetInverseMatrix(matrix2)
        mat3 = AppSt.GetInverseMatrix(matrix3)
        vec = AppSt.MultMat4x4(mat1,vec)
        vec = AppSt.MultMat4x4(mat2,vec)
        vec = AppSt.MultMat4x4(mat3,vec)
        return vec

    def GetDirV(self):
	matrix = self.qPitch.CreateMatrix()
        dirV = Vector()
	dirV.y = matrix[9]
	q = self.qHeading * self.qPitch
	matrix = q.CreateMatrix()
	dirV.x = matrix[8]
	dirV.z = matrix[10]
	dirV.w = 1.0
        return dirV.Normalized()

    def Move(self, x, y, z, theT):
        # 이걸..... 음..... 현재 가리키는 방향 즉 현재 보는 방향을 알아내서
        # 그걸 기준으로 앞뒤좌우로 움직여야 한다.
        # 앞뒤벡터를 회전벡터로 회전시킨 후에 포지션에다 더하고 빼면 됨.
        #
        #
        # 자. 이제 여기서는 y값을 절대로 변경시키지 못한다!

        lrV = Vector(x/10.0, 0.0, 0.0, 1.0)
        fbV = Vector(0.0, 0.0, z/10.0, 1.0)
	self.qPitch.CreateFromAxisAngle(1.0, 0.0, 0.0, self.pitchDegrees)
	self.qHeading.CreateFromAxisAngle(0.0, 1.0, 0.0, self.headingDegrees)

	# Combine the pitch and heading rotations and store the results in q
	q = self.qPitch * self.qHeading
	matrix = q.CreateMatrix()
        lrV = lrV.MultMatrix(matrix)
        fbV = fbV.MultMatrix(matrix)


	# Combine the heading and pitch rotations and make a matrix to get
	# the i and j vectors for our direction.
        self.directionVector = self.GetDirV()
        factor = float(theT)*20/1000.0
        if factor < 0.0:
            factor = 0.0
        if factor*AppSt.speed > 1.0:
            factor = 1.0
        self.directionVector = self.directionVector.Normalized()
        if z and not x:
            factor *= 0.5
            upVector = Vector(0.0, 1.0, 0.0)
            leftVec = upVector.Cross(self.directionVector)
            leftVec = leftVec.MultScalar(-z).Normalized()
            forVector = upVector.Cross(leftVec)
            """
            if AppSt.chunks.InWater(self.pos.x, self.pos.y, -self.pos.z):
                forVector = self.GetDirV().Normalized().MultScalar(AppSt.speed*factor)
            else:
                forVector = forVector.Normalized().MultScalar(AppSt.speed*factor)
            """
            forVector = forVector.Normalized().MultScalar(AppSt.speed*factor)
            self.pos += forVector

        if x and not z:
            upVector = Vector(0.0, 1.0, 0.0)
            leftVec = upVector.Cross(self.directionVector).MultScalar(x)
            while factor > 1.0:
                leftVec = leftVec.Normalized().MultScalar(AppSt.speed)
                self.pos += leftVec
                factor -= 1.0
            leftVec = leftVec.Normalized().MultScalar(AppSt.speed*factor)
            self.pos += leftVec


        '''
        self.posx += x
        self.posy += y
        self.posz += z
        if self.posz > -0.15:
            self.posz = -0.15
        if self.posz < -10.0:
            self.posz = -10.0
        '''


def normalize(x, y, z):
    factor = 1.0/math.sqrt(x**2+y**2+z**2)
    return x*factor, y*factor, z*factor
def cross(x,y,z,x2,y2,z2):
    return ((y*z2-z*y2),(z*x2-x*z2),(x*y2-y*x2))
def dot(x,y,z,x2,y2,z2):
    return x*x2+y*y2+z*z2

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
def CatmullRomSpline(p0, p1, p2, p3, resolution=0.1):
    m0 = tangent(p1, p0)
    m1 = tangent(p2, p0)
    m2 = tangent(p3, p1)
    m3 = tangent(p3, p2)
    t = 0.0
    a = []
    b = []
    c = []
    while t < 1.0:
        t_2 = t * t
        _1_t = 1 - t
        _2t = 2 * t
        h00 =  (1 + _2t) * (_1_t) * (_1_t)
        h10 =  t  * (_1_t) * (_1_t)
        h01 =  t_2 * (3 - _2t)
        h11 =  t_2 * (t - 1)

        result = Vector2(0.0,0.0)
        result.x = h00 * p0.x + h10 * m0.x + h01 * p1.x + h11 * m1.x
        result.y = h00 * p0.y + h10 * m0.y + h01 * p1.y + h11 * m1.y
        a.append(result)
        result = Vector2(0.0,0.0)
        result.x = h00 * p1.x + h10 * m1.x + h01 * p2.x + h11 * m2.x
        result.y = h00 * p1.y + h10 * m1.y + h01 * p2.y + h11 * m2.y
        b.append(result)
        result = Vector2(0.0,0.0)
        result.x = h00 * p2.x + h10 * m2.x + h01 * p3.x + h11 * m3.x
        result.y = h00 * p2.y + h10 * m2.y + h01 * p3.y + h11 * m3.y
        c.append(result)
        t+=resolution
    out = []

    for point in b:
        out.append(point)
    return out

def IsClockwise(x0,x1,x2,y0,y1,y2):
    return ((x1-x0)*(y2-y0) - (x2-x0)*(y1-y0)) < 0

def MbyM44(m, n):
    m[0],m[4],m[8],m[12]
    m[1],m[5],m[9],m[13]
    m[2],m[6],m[10],m[14]
    m[3],m[7],m[11],m[15]

    n[0],n[4],n[8],n[12]
    n[1],n[5],n[9],n[13]
    n[2],n[6],n[10],n[14]
    n[3],n[7],n[11],n[15]

    l = [0 for i in range(16)]
    l[0] = m[0]*n[0] + m[1]*n[4] + m[2]*n[8] + m[3]*n[12]
    l[1] = m[0]*n[1] + m[1]*n[5] + m[2]*n[9] + m[3]*n[13]
    l[2] = m[0]*n[2] + m[1]*n[6] + m[2]*n[10] + m[3]*n[14]
    l[3] = m[0]*n[3] + m[1]*n[7] + m[2]*n[11] + m[3]*n[15]

    l[4] = m[4]*n[0] + m[5]*n[4] + m[6]*n[8] + m[7]*n[12]
    l[5] = m[4]*n[1] + m[5]*n[5] + m[6]*n[9] + m[7]*n[13]
    l[6] = m[4]*n[2] + m[5]*n[6] + m[6]*n[10] + m[7]*n[14]
    l[7] = m[4]*n[3] + m[5]*n[7] + m[6]*n[11] + m[7]*n[15]

    l[8] = m[8]*n[0] + m[9]*n[4] + m[10]*n[8] + m[11]*n[12]
    l[9] = m[8]*n[1] + m[9]*n[5] + m[10]*n[9] + m[11]*n[13]
    l[10] = m[8]*n[2] + m[9]*n[6] + m[10]*n[10] + m[11]*n[14]
    l[11] = m[8]*n[3] + m[9]*n[7] + m[10]*n[11] + m[11]*n[15]

    l[12] = m[12]*n[0] + m[13]*n[4] + m[14]*n[8] + m[15]*n[12]
    l[13] = m[12]*n[1] + m[13]*n[5] + m[14]*n[9] + m[15]*n[13]
    l[14] = m[12]*n[2] + m[13]*n[6] + m[14]*n[10] + m[15]*n[14]
    l[15] = m[12]*n[3] + m[13]*n[7] + m[14]*n[11] + m[15]*n[15]
    return l

def ViewingMatrix():
    projection = glGetDoublev( GL_PROJECTION_MATRIX)
    model = glGetDoublev( GL_MODELVIEW_MATRIX )
    # hmm, this will likely fail on 64-bit platforms :(
    if projection is None or model is None:
        if projection:
            return projection
        if model:
            return model
        return None
    else:
        m = model
        p = projection
        return numpy.dot(m,p)

def GetFrustum(matrix):
    frustum = numpy.zeros( (6, 4), 'd' )
    clip = numpy.ravel(matrix)
    # right
    frustum[0][0] = clip[ 3] - clip[ 0]
    frustum[0][1] = clip[ 7] - clip[ 4]
    frustum[0][2] = clip[11] - clip[ 8]
    frustum[0][3] = clip[15] - clip[12]
    # left
    frustum[1][0] = clip[ 3] + clip[ 0]
    frustum[1][1] = clip[ 7] + clip[ 4]
    frustum[1][2] = clip[11] + clip[ 8]
    frustum[1][3] = clip[15] + clip[12]
    # bottom
    frustum[2][0] = clip[ 3] + clip[ 1]
    frustum[2][1] = clip[ 7] + clip[ 5]
    frustum[2][2] = clip[11] + clip[ 9]
    frustum[2][3] = clip[15] + clip[13]
    # top
    frustum[3][0] = clip[ 3] - clip[ 1]
    frustum[3][1] = clip[ 7] - clip[ 5]
    frustum[3][2] = clip[11] - clip[ 9]
    frustum[3][3] = clip[15] - clip[13]
    # far
    frustum[4][0] = clip[ 3] - clip[ 2]
    frustum[4][1] = clip[ 7] - clip[ 6]
    frustum[4][2] = clip[11] - clip[10]
    frustum[4][3] = clip[15] - clip[14]
    # near
    frustum[5][0] = clip[ 3] + clip[ 2]
    frustum[5][1] = clip[ 7] + clip[ 6]
    frustum[5][2] = clip[11] + clip[10]
    frustum[5][3] = clip[15] + clip[14]
    return frustum
def NormalizeFrustum(frustum):
    magnitude = numpy.sqrt( 
        frustum[:,0] * frustum[:,0] + 
        frustum[:,1] * frustum[:,1] + 
        frustum[:,2] * frustum[:,2] 
    )
    # eliminate any planes which have 0-length vectors,
    # those planes can't be used for excluding anything anyway...
    frustum = numpy.compress( magnitude,frustum,0 )
    magnitude = numpy.compress( magnitude, magnitude,0 )
    magnitude = numpy.reshape(magnitude.astype('d'), (len(frustum),1))
    return frustum/magnitude


def resize(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(width)/height, .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init():
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glClearColor(1.0, 1.0, 1.0, 0.0)
    

def glpPerspective(fovy, aspect, zNear, zFar):
    top = math.tan(fovy * math.pi / 360.0) * zNear
    bottom = -top
    left = aspect * bottom
    right = aspect * top
    glFrustum(float(left), float(right), float(bottom), float(top), float(zNear), float(zFar))

def GUIDrawMode():
    glDisable(GL_CULL_FACE)
    glDisable(GL_DEPTH_TEST)
    #glViewport(0, 0, SW, SH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, float(SW), -float(SH), 0.0, -1000.0, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

G_FAR = 300.0
def GameDrawMode():
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    h = SH
    if SH == 0: h = 1
    aspect = float(SW) / float(h)
    fov = 45.0*2.0
    near = 0.1 # 이게 너무 작으면 Z버퍼가 정확도가 낮으면 글픽 깨짐
    far = G_FAR

    #glViewport(0, 0, SW, SH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glpPerspective(fov, aspect, near, far)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

class Quaternion:
    def __init__(self, x = 0, y = 0, z = 0, w = 1):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def Length(self):
        return sqrtf(self.x**2+self.y**2+self.z**2+self.w**2)

    def Normalized(self):
        len = self.Length()
        try:
            factor = 1.0/len
            x = self.x * factor
            y = self.y * factor
            z = self.z * factor
            w = self.w * factor
        except ZeroDivisionError:
            x = self.x
            y = self.y
            z = self.z
            w = self.w
        return Quaternion(x,y,z,w)


    def CreateFromAxisAngle(self, x, y, z, degrees):
        angle = (degrees / 180.0) * math.pi
        result = math.sin( angle / 2.0 )
        self.w = math.cos( angle / 2.0 )
        self.x = (x * result)
        self.y = (y * result)
        self.z = (z * result)

    def CreateMatrix(self):
        pMatrix = [0 for i in range(16)]
	
	# First row
	pMatrix[ 0] = 1.0 - 2.0 * ( self.y * self.y + self.z * self.z )
	pMatrix[ 1] = 2.0 * (self.x * self.y + self.z * self.w)
	pMatrix[ 2] = 2.0 * (self.x * self.z - self.y * self.w)
	pMatrix[ 3] = 0.0
	
	# Second row
	pMatrix[ 4] = 2.0 * ( self.x * self.y - self.z * self.w )
	pMatrix[ 5] = 1.0 - 2.0 * ( self.x * self.x + self.z * self.z )
	pMatrix[ 6] = 2.0 * (self.z * self.y + self.x * self.w )
	pMatrix[ 7] = 0.0

	# Third row
	pMatrix[ 8] = 2.0 * ( self.x * self.z + self.y * self.w )
	pMatrix[ 9] = 2.0 * ( self.y * self.z - self.x * self.w )
	pMatrix[10] = 1.0 - 2.0 * ( self.x * self.x + self.y * self.y )
	pMatrix[11] = 0.0

	# Fourth row
	pMatrix[12] = 0
	pMatrix[13] = 0
	pMatrix[14] = 0
	pMatrix[15] = 1.0
        return pMatrix


    def Conjugate(self):
        x = -self.x
        y = -self.y
        z = -self.z
        w = self.w
        return Quaternion(x,y,z,w)

    def __mul__(self, quat):
        x = self.w*quat.x + self.x*quat.w + self.y*quat.z - self.z*quat.y;
        y = self.w*quat.y - self.x*quat.z + self.y*quat.w + self.z*quat.x;
        z = self.w*quat.z + self.x*quat.y - self.y*quat.x + self.z*quat.w;
        w = self.w*quat.w - self.x*quat.x - self.y*quat.y - self.z*quat.z;
        return Quaternion(x,y,z,w)

    def __repr__(self):
        return str([self.w, [self.x,self.y,self.z]])
    
    def Dot(self, q):
        q = q.Normalized()
        self = self.Normalized()
        return self.x*q.x + self.y*q.y + self.z*q.z + self.w*q.w

    def Slerp(self, q, t):
        import math
        if t <= 0.0:
            return Quaternion(self.x, self.y, self.z, self.w)
        elif t >= 1.0:
            return Quaternion(q.x, q.y, q.z, q.w)

        cosOmega = self.Dot(q)
        if cosOmega < 0:
            cosOmega = -cosOmega
            q2 = Quaternion(-q.x, -q.y, -q.z, -q.w)
        else:
            q2 = Quaternion(q.x, q.y, q.z, q.w)
        
        if 1.0 - cosOmega > 0.00001:
            omega = math.acos(cosOmega)
            sinOmega = sin(omega)
            oneOverSinOmega = 1.0 / sinOmega

            k0 = sin((1.0 - t) * omega) / sinOmega
            k1 = sin(t * omega) / sinOmega
        else:
            k0 = 1.0 - t
            k1 = t
        return Quaternion(
                (k0 * self.x) + (k1 * q2.x),
                (k0 * self.y) + (k1 * q2.y),
                (k0 * self.z) + (k1 * q2.z),
                (k0 * self.w) + (k1 * q2.w))

class Vector:
    def __init__(self, x = 0, y = 0, z = 0, w=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def Length(self):
        import math
        return math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)

    def NormalizeByW(self):
        x,y,z,w = self.x,self.y,self.z,self.w
        w = float(w)
        if w == 0.0:
            w = 0.000001
        x /= w
        y /= w
        z /= w
        w = 1.0
        return Vector(x,y,z,w)

    def Normalized(self):
        try:
            newV = self.NormalizeByW()
            factor = 1.0/newV.Length()
            return newV.MultScalar(factor)
        except ZeroDivisionError:
            return Vector(self.x, self.y, self.z, self.w)

    def Cross(self, vector):
        newV = self.NormalizeByW()
        vector = vector.NormalizeByW()
        return Vector(*cross(newV.x,newV.y,newV.z,vector.x,vector.y,vector.z))

    def Dot(self, vector):
        newV = self.NormalizeByW()
        newV = newV.Normalized()
        vector = vector.NormalizeByW()
        vector = vector.Normalized()
        return newV.x*vector.x+newV.y*vector.y+newV.z*vector.z

    def __add__(self, vec):
        newV = self.NormalizeByW()
        vec = vec.NormalizeByW()
        a,b,c = newV.x,newV.y,newV.z
        x,y,z = vec.x,vec.y,vec.z
        return Vector(a+x,b+y,c+z)

    def __sub__(self, vec):
        newV = self.NormalizeByW()
        vec = vec.NormalizeByW()
        a,b,c = newV.x,newV.y,newV.z
        x,y,z = vec.x,vec.y,vec.z
        return Vector(a-x,b-y,c-z)

    def MultScalar(self, scalar):
        newV = self.NormalizeByW()
        return Vector(newV.x*scalar, newV.y*scalar, newV.z*scalar)
    def DivScalar(self, scalar):
        newV = self.NormalizeByW()
        return Vector(newV.x/scalar, newV.y/scalar, newV.z/scalar)
    def __repr__(self):
        return str([self.x, self.y, self.z, self.w])
    
    def MultMatrix(self, mat):
        tempVec = Vector()
        tempVec.x = self.x*mat[0] + self.y*mat[1] + self.z*mat[2] + self.w*mat[3]
        tempVec.y = self.x*mat[4] + self.y*mat[5] + self.z*mat[6] + self.w*mat[7]
        tempVec.z = self.x*mat[8] + self.y*mat[9] + self.z*mat[10] + self.w*mat[11]
        tempVec.w = self.x*mat[12] + self.y*mat[13] + self.z*mat[14] + self.w*mat[15]
        return tempVec




    
def glpLookAt(eye, center, up):
    m = [0.0 for i in range(16)]
    forward = center-eye
    forward = forward.Normalized()

    side = forward.Cross(up)
    side = side.Normalized()
    
    up = side.Cross(forward)

    m_ = [side.x, up.x, -forward.x, 0,
        side.y, up.y, -forward.y, 0,
        side.z, up.z, -forward.z, 0,
        0, 0, 0, 1]

    for i in range(16):
        m[i] = float(m_[i])

    glMultMatrixf(m)
    glTranslatef(-eye.x, -eye.y, -eye.z)


from OpenGL.GLUT import glutInit, glutSolidTeapot
AppSt = None

def DrawQuadTexTVBG(x,y,w,h):
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 12.0)
    glVertex3f(float(x), -float(y+h), 100.0)
    glTexCoord2f(16.0, 12.0)
    glVertex3f(float(x+w), -float(y+h), 100.0)
    glTexCoord2f(16.0, 0.0)
    glVertex3f(float(x+w), -float(y), 100.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(float(x), -float(y), 100.0)
    glEnd()
def DrawQuadTexFlipX(x,y,w,h):
    glBegin(GL_QUADS)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(float(x), -float(y+h), 100.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(float(x+w), -float(y+h), 100.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(float(x+w), -float(y), 100.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(float(x), -float(y), 100.0)
    glEnd()
def DrawQuadTex(x,y,w,h):
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(float(x), -float(y+h), 100.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(float(x+w), -float(y+h), 100.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(float(x+w), -float(y), 100.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(float(x), -float(y), 100.0)
    glEnd()
def DrawQuad(x,y,w,h, color1, color2):
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_TEXTURE_1D)
    glBegin(GL_QUADS)
    glColor4ub(*color1)
    glVertex3f(float(x), -float(y+h), 100.0)
    glVertex3f(float(x+w), -float(y+h), 100.0)
    glColor4ub(*color2)
    glVertex3f(float(x+w), -float(y), 100.0)
    glVertex3f(float(x), -float(y), 100.0)
    glEnd()
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_TEXTURE_1D)


def DrawCube(pos,bound, color, texture): # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)


    x,y,z = pos
    w,h,j = bound
    x -= w/2
    y -= h/2
    z -= j/2

    vidx = [ 
            (4, 5, 1, 0),  # bottom    
            (6,7,3, 2),  # top
            (3, 7, 4, 0),  # left
            (6,2,1, 5),  # right
            (7,6,5, 4),  # back
            (2,3,0, 1),  # front
            ]

    v = [   (0.0+x, 0.0+y, j+z),
            (w+x, 0.0+y, j+z),
            (w+x, h+y, j+z),
            (0.0+x, h+y, j+z),
            (0.0+x, 0.0+y, 0.0+z),
            (w+x, 0.0+y, 0.0+z),
            (w+x, h+y, 0.0+z),
            (0.0+x, h+y, 0.0+z) ]

    for face in range(6):
        v1, v2, v3, v4 = vidx[face]
        glBegin(GL_QUADS)
        glColor4ub(*color)
        glTexCoord2f(1.0, 0.0)
        glVertex( v[v1] )
        glTexCoord2f(0.0, 0.0)
        glVertex( v[v2] )
        glTexCoord2f(0.0, 1.0)
        glVertex( v[v3] )
        glTexCoord2f(1.0, 1.0)
        glVertex( v[v4] )            
        glEnd()
    glDisable(GL_TEXTURE_2D)


class Physics(object):
    def __init__(self):
# Create a world object
        world = ode.World()
        world.setGravity( (0,-9.81,0) )

# Create a body inside the world
        body = ode.Body(world)
        M = ode.Mass()
        M.setSphere(2500.0, 0.05)
        M.mass = 1.0
        body.setMass(M)

        body.setPosition( (0,2,0) )
        body.addForce( (0,200,0) )

# Do the simulation...
        total_time = 0.0
        dt = 0.04

    def Tick(self, t,m,k):
        x,y,z = body.getPosition()
        u,v,w = body.getLinearVel()
        print "%1.2fsec: pos=(%6.3f, %6.3f, %6.3f)  vel=(%6.3f, %6.3f, %6.3f)" % \
            (total_time, x, y, z, u,v,w)
        world.step(dt)
        total_time+=dt


class MenuScreen:
    def __init__(self):
        pass

def RectRectCollide2(rect1,rect2):
    x,y,w,h = rect1
    xx,yy,ww,hh = rect2
    if InRect(x,y,w,h,xx,yy):
        return True, 0
    if InRect(x,y,w,h,xx+ww,yy):
        return True, 1
    if InRect(x,y,w,h,xx,yy+hh):
        return True, 2
    if InRect(x,y,w,h,xx+ww,yy+hh):
        return True, 3

    return False
def RectRectCollide(rect1,rect2):
    x,y,w,h = rect1
    xx,yy,ww,hh = rect2
    if InRect(x,y,w,h,xx,yy):
        return True
    if InRect(x,y,w,h,xx+ww,yy):
        return True
    if InRect(x,y,w,h,xx+ww,yy+hh):
        return True
    if InRect(x,y,w,h,xx,yy+hh):
        return True

    if InRect(xx,yy,ww,hh,x,y):
        return True
    if InRect(xx,yy,ww,hh,x+w,y):
        return True
    if InRect(xx,yy,ww,hh,x+w,y+h):
        return True
    if InRect(xx,yy,ww,hh,x,y+h):
        return True


    return False
class DeadEnemy:
    def __init__(self,x,y):
        EMgrSt.BindTick(self.Tick)
        self.wait = pygame.time.get_ticks()
        self.delay = 500
        self.pos = x,y
    def Tick(self,t,m,k):
        if t-self.wait > self.delay:
            try:
                GUISt.deads.remove(self)
                EMgrSt.bindTick.remove(self.Tick)
            except:
                pass
class Beam:
    LEFT=0
    RIGHT=1
    def __init__(self,x,y,dir_, power, owner):
        self.owner = owner
        self.orgX = x
        self.orgY = y
        self.x = x
        self.y = y
        self.dir = dir_
        EMgrSt.BindTick(self.Tick)
        self.waitPrev = pygame.time.get_ticks()
        self.delay = 25
        self.speed = 30
        self.deleted = False
        self.power = power

    def Delete(self):
        try:
            self.owner.beams.remove(self)
            EMgrSt.bindTick.remove(self.Tick)
        except:
            pass
        self.deleted = True

    def Tick(self,t,m,k):
        if not self.deleted:
            if t-self.waitPrev > self.delay:
                self.waitPrev = t
                if self.dir == self.LEFT:
                    self.x -= self.speed
                if self.dir == self.RIGHT:
                    self.x += self.speed

                if self.owner == AppSt.player:
                    for enemy in GUISt.stages[GUISt.curStageIdx].enemies:
                        x,y = enemy.pos
                        x -= 32
                        y -= 128
                        w=64
                        h=128
                        xx = self.x
                        yy = self.y
                        ww = 128
                        hh = 64
                        if RectRectCollide((x,y,w,h), (xx,yy,ww,hh)):
                            enemy.hp -= AppSt.player.args["atk"]
                            GUISt.sounds["Hurt"].play()
                            self.Delete()
                else:
                    x,y = AppSt.player.pos
                    x -= 32
                    y -= 128
                    w=64
                    h=128
                    xx = self.x
                    yy = self.y
                    ww = 128
                    hh = 64
                    if RectRectCollide((x,y,w,h), (xx,yy,ww,hh)):
                        AppSt.player.args["hp"] -= self.power
                        GUISt.sounds["Hurt"].play()
                        self.Delete()
                if abs(self.x-self.orgX) > 1000:
                    self.Delete()
            
class Player:
    LEFT = 0
    RIGHT = 1
    def __init__(self, **args):
        self.hp = 1000
        self.args = args

        self.pos = [1100, SH-128-64]
        self.fallSpeed = 15
        self.fallWait = pygame.time.get_ticks()
        self.fallDelay = 25
        self.facing = self.RIGHT
        self.jumping = False
        self.jumpStart = 0
        self.jumpMax = 400
        self.jumpMin = 250
        self.grounded = False
        self.moving = False
        EMgrSt.BindTick(self.Tick)
        self.keyBinds = {
                "UP": K_w,
                "LEFT": K_a,
                "DOWN": K_s,
                "RIGHT": K_d,
                "ATK": K_j,
                "JUMP": K_k,
                "ACT": K_u,
                "ACT2": K_i,
                }
        self.beamDelay = 125
        self.prevBeam = pygame.time.get_ticks()
        self.beams = []

        EMgrSt.BindKeyDown(self.OnUPKey)
        EMgrSt.BindKeyDown(self.OnActKey)
    def OnActKey(self,t,m,k):
        if k.pressedKey == self.keyBinds["ACT"]:
            if self.args["mana"] >= 30:
                self.args["mana"] -= 30
                self.args["hp"] += self.args["heal"]
                if self.args["hp"] > self.args["maxhp"]:
                    self.args["hp"] = self.args["maxhp"]
    def OnUPKey(self,t,m,k):
        if k.pressedKey == self.keyBinds["UP"]:
            for door in GUISt.stages[GUISt.curStageIdx].doors.iterkeys():
                if RectRectCollide((self.pos[0]-64, self.pos[1]-128,128,128), (door[0],door[1],128,128)):
                    num = GUISt.stages[GUISt.curStageIdx].doors[door]
                    con = GUISt.GetConnectivity(num)
                    try:
                        a,b = con
                        if a == num:
                            stage, pos = GUISt.GetStageAndPos(b)
                            self.pos = [pos[0]+64, pos[1]+128]
                            GUISt.stages[GUISt.curStageIdx].EndGame()
                            GUISt.curStageIdx = stage
                            GUISt.stages[GUISt.curStageIdx].StartGame()
                            if (b,a) not in GUISt.connects:
                                GUISt.connects += [(b,a)]
                            break
                    except:
                        pass
    def Tick(self,t,m,k):
        if GUISt.emode == GUISt.GAME_MODE:
            if t-self.fallWait > self.fallDelay:
                self.fallWait = t
                tiles = GUISt.stages[GUISt.curStageIdx].GetTiles()
                self.moving = False

                if not self.jumping:
                    collide = False
                    collideY = 0
                    for tile in tiles:
                        x,y,tile_ = tile
                        w = 64
                        h = 64
                        px,py = self.pos
                        xx = px-32
                        yy = py-128+self.fallSpeed
                        ww = 64
                        hh = 128
                        if RectRectCollide((x+1,y+1,w-1,h-1),(xx+1,yy+1,ww-1,hh-1)):
                            collide = True
                            collideY = y
                    if not collide:
                        self.pos[1] += self.fallSpeed
                    else:
                        self.grounded = True
                        self.pos[1] = collideY
                else:
                    collide = False
                    collideY = 0
                    for tile in tiles:
                        x,y,t_ = tile
                        w = 64
                        h = 64
                        px,py = self.pos
                        xx = px-32
                        yy = py-128-self.fallSpeed
                        ww = 64
                        hh = 128
                        if RectRectCollide((x+1,y+1,w-1,h-1),(xx+1,yy+1,ww-1,hh-1)):
                            collide = True
                            collideY = y+h+128
                    if not collide:
                        self.pos[1] -= self.fallSpeed
                    else:
                        self.pos[1] = collideY

                if pygame.key.get_pressed()[self.keyBinds["LEFT"]]:
                    self.moving = True
                    self.facing = self.LEFT
                    collide = False
                    collideX = 0
                    for tile in tiles:
                        x,y,t_ = tile
                        w = 64
                        h = 64
                        px,py = self.pos
                        xx = px-32-self.fallSpeed
                        yy = py-128
                        ww = 64
                        hh = 128
                        if RectRectCollide((x+1,y+1,w-1,h-1),(xx+1,yy+1,ww-1,hh-1)):
                            collide = True
                            collideX = x+w+32
                    if not collide:
                        self.pos[0] -= self.fallSpeed
                    else:
                        self.pos[0] = collideX

                if pygame.key.get_pressed()[self.keyBinds["RIGHT"]]:
                    self.moving = True
                    self.facing = self.RIGHT
                    collide = False
                    collideX = 0
                    for tile in tiles:
                        x,y,t_ = tile
                        w = 64
                        h = 64
                        px,py = self.pos
                        xx = px-32+self.fallSpeed
                        yy = py-128
                        ww = 64
                        hh = 128
                        if RectRectCollide((x+1,y+1,w-1,h-1),(xx+1,yy+1,ww-1,hh-1)):
                            collide = True
                            collideX = x-32
                    if not collide:
                        self.pos[0] += self.fallSpeed
                    else:
                        self.pos[0] = collideX
                if pygame.key.get_pressed()[self.keyBinds["JUMP"]]:
                    if not self.jumping and self.grounded:
                        GUISt.sounds["Jump"].play()
                        self.jumping = True
                        self.jumpStart = t
                        self.grounded = False
                else:
                    if self.jumping and t-self.jumpStart > self.jumpMin:
                        self.jumping = False

                if pygame.key.get_pressed()[self.keyBinds["ATK"]]:
                    if t-self.prevBeam > self.beamDelay:
                        self.prevBeam = t
                        beamY = self.pos[1]-128
                        if self.facing == self.LEFT:
                            beamX = self.pos[0]-128-32
                        else:
                            beamX = self.pos[0]+32
                        GUISt.sounds["Beam"].play()
                        self.beams += [Beam(beamX,beamY,self.facing, self.args["atk"], self)]

            if t-self.jumpStart > self.jumpMax:
                self.jumping = False


    def Render(self):
        pass


class ConstructorApp:
    TILECHANGE1 = 0
    TILECHANGE2 = 1
    WALLCHANGE1 = 2
    WALLCHANGE2 = 3

    def __init__(self):
        global AppSt
        AppSt = self
        self.guiMode = False
        self.renderGUIs = []
        self.renderGameGUIs = []
        self.keyBinds = {
                "UP": K_w,
                "LEFT": K_a,
                "DOWN": K_s,
                "RIGHT": K_d,
                "ATK": K_j,
                "JUMP": K_SPACE,}
        self.prevTime = pygame.time.get_ticks()
        self.speed = 0.23
        glutInit()
        self.camMoveMode = False
        self.reload = True
        self.tr = -3.0
        self.camZoom = 8.0
        self.prevAniTime = pygame.time.get_ticks()
        self.prevAniDelay = 50
        self.aniOffset = 0.0
        self.aniOffset2 = 0.0
        self.aniOffset3 = 0.0
        
        self.tileMode = AppSt.TILECHANGE1

        self.delayAni = 250
        self.waitAni = pygame.time.get_ticks()
        self.aniIdx = 0

        self.delayBeam = 1000/20
        self.waitBeam = pygame.time.get_ticks()
        self.aniBeamX = 0
        self.ani = [0,1,2,1]



    def MultMat4x4(self, mat, vec):
        x = mat[0] *vec[0]+mat[1] *vec[1]+ mat[2]*vec[2]+ mat[3]*vec[3]
        y = mat[4] *vec[0]+mat[5] *vec[1]+ mat[6]*vec[2]+ mat[7]*vec[3]
        z = mat[8] *vec[0]+mat[9] *vec[1]+mat[10]*vec[2]+mat[11]*vec[3]
        w = mat[12]*vec[0]+mat[13]*vec[1]+mat[14]*vec[2]+mat[15]*vec[3]
        if w != 0:
            x /= w
            y /= w
            z /= w
            w /= w
            return [x,y,z,w]
        else:
            return [0,0,0,0]
    def Test(self):
        matrix1 = [1, 0, 0, 3.0,
                   0, 1, 0, 3.0,
                   0, 0, 1, 3.0,
                   0, 0, 0, 1]
        inv = self.GetInverseMatrix(matrix1)
        vec = [1.0,1.0,1.0,1.0]
        vec2 = self.MultMat4x4(matrix1, vec)
        vec3 = self.MultMat4x4(inv, vec2)


    def GetInverseMatrix(self, mat):
        det = mat[0]*mat[5]*mat[10]*mat[15] + mat[0]*mat[6]*mat[11]*mat[13] + mat[0]*mat[7]*mat[9]*mat[14] +\
                mat[1]*mat[4]*mat[11]*mat[14] + mat[1]*mat[6]*mat[8]*mat[15] + mat[1]*mat[7]*mat[10]*mat[12] +\
                mat[2]*mat[4]*mat[9]*mat[15] + mat[2]*mat[5]*mat[11]*mat[12] + mat[2]*mat[7]*mat[8]*mat[13] +\
                mat[3]*mat[4]*mat[10]*mat[13] + mat[3]*mat[5]*mat[8]*mat[14] + mat[3]*mat[6]*mat[9]*mat[12] -\
                mat[0]*mat[5]*mat[11]*mat[14] + mat[0]*mat[6]*mat[9]*mat[15] + mat[0]*mat[7]*mat[10]*mat[13] -\
                mat[1]*mat[4]*mat[10]*mat[15] + mat[1]*mat[6]*mat[11]*mat[12] + mat[1]*mat[7]*mat[8]*mat[14] -\
                mat[2]*mat[4]*mat[11]*mat[13] + mat[2]*mat[5]*mat[8]*mat[15] + mat[2]*mat[7]*mat[9]*mat[12] -\
                mat[3]*mat[4]*mat[9]*mat[14] + mat[3]*mat[5]*mat[10]*mat[12] + mat[3]*mat[6]*mat[8]*mat[13]
        result = [0 for i in range(16)]
        if det != 0:
            invDet = 1.0/det

            result[0] += invDet*mat[5]*mat[10]*mat[15]
            result[0] += invDet*mat[6]*mat[11]*mat[13]
            result[0] += invDet*mat[7]*mat[9]*mat[14]
            result[0] -= invDet*mat[5]*mat[11]*mat[14]
            result[0] -= invDet*mat[6]*mat[9]*mat[15]
            result[0] -= invDet*mat[7]*mat[10]*mat[13]

            result[1] += invDet*mat[1]*mat[11]*mat[14]
            result[1] += invDet*mat[2]*mat[9]*mat[15]
            result[1] += invDet*mat[3]*mat[10]*mat[13]
            result[1] -= invDet*mat[1]*mat[10]*mat[15]
            result[1] -= invDet*mat[2]*mat[11]*mat[13]
            result[1] -= invDet*mat[3]*mat[9]*mat[14]

            result[2] += invDet*mat[1]*mat[6]*mat[15]
            result[2] += invDet*mat[2]*mat[7]*mat[13]
            result[2] += invDet*mat[3]*mat[5]*mat[14]
            result[2] -= invDet*mat[1]*mat[7]*mat[14]
            result[2] -= invDet*mat[2]*mat[5]*mat[15]
            result[2] -= invDet*mat[3]*mat[6]*mat[13]

            result[3] += invDet*mat[1]*mat[7]*mat[10]
            result[3] += invDet*mat[2]*mat[5]*mat[11]
            result[3] += invDet*mat[3]*mat[6]*mat[9]
            result[3] -= invDet*mat[1]*mat[6]*mat[11]
            result[3] -= invDet*mat[2]*mat[7]*mat[9]
            result[3] -= invDet*mat[3]*mat[5]*mat[10]

            
            result[4] += invDet*mat[4]*mat[10]*mat[14]
            result[4] += invDet*mat[6]*mat[8]*mat[15]
            result[4] += invDet*mat[7]*mat[10]*mat[12]
            result[4] -= invDet*mat[4]*mat[10]*mat[15]
            result[4] -= invDet*mat[6]*mat[11]*mat[12]
            result[4] -= invDet*mat[7]*mat[8]*mat[14]

            result[5] += invDet*mat[0]*mat[10]*mat[15]
            result[5] += invDet*mat[2]*mat[11]*mat[12]
            result[5] += invDet*mat[3]*mat[8]*mat[14]
            result[5] -= invDet*mat[0]*mat[11]*mat[14]
            result[5] -= invDet*mat[2]*mat[8]*mat[15]
            result[5] -= invDet*mat[3]*mat[10]*mat[12]

            result[6] += invDet*mat[0]*mat[7]*mat[14]
            result[6] += invDet*mat[2]*mat[4]*mat[15]
            result[6] += invDet*mat[3]*mat[6]*mat[12]
            result[6] -= invDet*mat[0]*mat[6]*mat[15]
            result[6] -= invDet*mat[2]*mat[7]*mat[12]
            result[6] -= invDet*mat[3]*mat[4]*mat[14]

            result[7] += invDet*mat[0]*mat[6]*mat[11]
            result[7] += invDet*mat[2]*mat[7]*mat[8]
            result[7] += invDet*mat[3]*mat[4]*mat[10]
            result[7] -= invDet*mat[0]*mat[7]*mat[10]
            result[7] -= invDet*mat[2]*mat[4]*mat[11]
            result[7] -= invDet*mat[3]*mat[6]*mat[8]

            result[8] += invDet*mat[4]*mat[9]*mat[15]
            result[8] += invDet*mat[5]*mat[11]*mat[12]
            result[8] += invDet*mat[7]*mat[8]*mat[13]
            result[8] -= invDet*mat[4]*mat[11]*mat[13]
            result[8] -= invDet*mat[5]*mat[8]*mat[15]
            result[8] -= invDet*mat[7]*mat[9]*mat[12]

            result[9] += invDet*mat[0]*mat[11]*mat[13]
            result[9] += invDet*mat[1]*mat[8]*mat[15]
            result[9] += invDet*mat[3]*mat[9]*mat[12]
            result[9] -= invDet*mat[0]*mat[9]*mat[15]
            result[9] -= invDet*mat[1]*mat[11]*mat[12]
            result[9] -= invDet*mat[3]*mat[8]*mat[13]

            result[10] += invDet*mat[0]*mat[5]*mat[15]
            result[10] += invDet*mat[1]*mat[7]*mat[12]
            result[10] += invDet*mat[3]*mat[4]*mat[13]
            result[10] -= invDet*mat[0]*mat[7]*mat[13]
            result[10] -= invDet*mat[1]*mat[4]*mat[15]
            result[10] -= invDet*mat[3]*mat[5]*mat[12]

            result[11] += invDet*mat[0]*mat[7]*mat[9]
            result[11] += invDet*mat[1]*mat[4]*mat[11]
            result[11] += invDet*mat[3]*mat[5]*mat[8]
            result[11] -= invDet*mat[0]*mat[5]*mat[11]
            result[11] -= invDet*mat[1]*mat[7]*mat[8]
            result[11] -= invDet*mat[3]*mat[4]*mat[9]

            result[12] += invDet*mat[4]*mat[10]*mat[13]
            result[12] += invDet*mat[5]*mat[8]*mat[14]
            result[12] += invDet*mat[6]*mat[9]*mat[12]
            result[12] -= invDet*mat[4]*mat[9]*mat[14]
            result[12] -= invDet*mat[5]*mat[10]*mat[12]
            result[12] -= invDet*mat[6]*mat[8]*mat[13]

            result[13] += invDet*mat[0]*mat[9]*mat[14]
            result[13] += invDet*mat[1]*mat[10]*mat[12]
            result[13] += invDet*mat[2]*mat[8]*mat[13]
            result[13] -= invDet*mat[0]*mat[10]*mat[13]
            result[13] -= invDet*mat[1]*mat[8]*mat[14]
            result[13] -= invDet*mat[2]*mat[9]*mat[12]

            result[14] += invDet*mat[0]*mat[6]*mat[12]
            result[14] += invDet*mat[1]*mat[4]*mat[14]
            result[14] += invDet*mat[2]*mat[5]*mat[12]
            result[14] -= invDet*mat[0]*mat[5]*mat[14]
            result[14] -= invDet*mat[1]*mat[6]*mat[12]
            result[14] -= invDet*mat[2]*mat[4]*mat[13]

            result[15] += invDet*mat[0]*mat[5]*mat[10]
            result[15] += invDet*mat[1]*mat[6]*mat[8]
            result[15] += invDet*mat[2]*mat[4]*mat[9]
            result[15] -= invDet*mat[0]*mat[6]*mat[9]
            result[15] -= invDet*mat[1]*mat[4]*mat[10]
            result[15] -= invDet*mat[2]*mat[5]*mat[8]
        return result


    def Reload(self):
        if self.reload:
            resize(SW,SH)
            init()
        
            self.reload = False
            #self.model.Regen()
            #self.gui.Regen()
            self.textRenderer.RegenTex()
            self.textRendererSmall.RegenTex()
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_TEXTURE_1D)
            #glInitTextureFilterAnisotropicEXT( )
            """
            image = pygame.image.load("./img/sat3.png")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            self.sat3 = texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_1D, texture)
            glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

            image = pygame.image.load("./img/sat2.png")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            self.sat = texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_1D, texture)
            glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

            image = pygame.image.load("./img/sat.png")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            self.tex3 = texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_1D, texture)
            glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            """


            """
            tiles = ["water",
                    "grass",
                    "sand"]
            self.texTiles = []
            for tile in tiles:
                image = pygame.image.load("./img/tile_%s.png" % tile)
                # 타일의 top/left의 픽셀값을 읽어서 벽부분의 색으로 쓴다.
                teximg = pygame.image.tostring(image, "RGBA", 0) 
                texture = glGenTextures(1)
                self.texTiles += [(texture, image.get_at((0,0)))]
                glBindTexture(GL_TEXTURE_2D, texture)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 64, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 8.0)
                glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
                glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
            """


            imgs = ["walk1",
                    "walk2_4_idle",
                    "walk3"]
            self._2d_tiles = []
            for imgPath in imgs:
                image = pygame.image.load("./img/2d_%s.png" % imgPath)
                # 타일의 top/left의 픽셀값을 읽어서 벽부분의 색으로 쓴다.
                teximg = pygame.image.tostring(image, "RGBA", 0) 
                texture = glGenTextures(1)
                self._2d_tiles += [texture]
                glBindTexture(GL_TEXTURE_2D, texture)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 128, 128, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 8.0)
                glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
                glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)


            def LoadTex(path, w, h):
                image = pygame.image.load(path)
                teximg = pygame.image.tostring(image, "RGBA", 0) 
                texture = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, texture)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 8.0)
                glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
                glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
                return texture

            self._2d_door = LoadTex("./img/door.png", 128, 128)
            self._2d_enemy_tiles = []
            self._2d_gem_diamond = LoadTex("./img/2d_gem_diamond.png", 64,64)
            self._2d_gem_emerald = LoadTex("./img/2d_gem_emerald.png", 64,64)
            self._2d_gem_ruby = LoadTex("./img/2d_gem_ruby.png", 64,64)
            self._2d_gem_topaz = LoadTex("./img/2d_gem_topaz.png", 64,64)
            self._2d_gem_tiles = []
            self._2d_gem_tiles += [self._2d_gem_diamond]
            self._2d_gem_tiles += [self._2d_gem_ruby]
            self._2d_gem_tiles += [self._2d_gem_topaz]
            self._2d_gem_tiles += [self._2d_gem_emerald]

            self._2d_tiles_enemy = []
            for path in imgs:
                self._2d_tiles_enemy += [LoadTex("./img/2d_enemy1_%s.png" % path, 128, 128)]
            self._2d_enemy_tiles += [self._2d_tiles_enemy]

            self._2d_tiles_enemy = []
            for path in imgs:
                self._2d_tiles_enemy += [LoadTex("./img/2d_enemy2_%s.png" % path, 128, 128)]
            self._2d_enemy_tiles += [self._2d_tiles_enemy]

            tiles = [
                    "tile1",
                    "tile2",
                    "tile3",
                    "tile4",
                    ]
            self._2d_grndtiles = []
            for tile in tiles:
                self._2d_grndtiles += [LoadTex("./img/2d_%s.png" % tile, 64, 64)]

            self._2d_logo = LoadTex("./img/logo.png", 512, 512)
            self._2d_beam = LoadTex("./img/2d_beam.png", 128,64)
            self._2d_tiles_dead = LoadTex("./img/2d_enemy_dead.png", 64,64)


            """
            image = pygame.image.load("./img/tile_wall.png")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            self.tex = texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 128, 256, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 8.0)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
            #self.tiles = (self.water, (10,144,216,255)), (self.tex2, (13,92,7,255))
            self.map.Regen(*self.texTiles)

            image = pygame.image.load("./img/bgbg.png")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            self.bgbg = texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 64, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 8.0)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)

            image = pygame.image.load("./img/tvbg.png")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            self.tvbg = texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 64, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 8.0)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
            """

            """

            self.program3 = compile_program('''
            // Vertex program

#version 150 compatibility


varying vec3 vNormal;
varying vec3 vViewVec;
uniform vec4 view_position;

void main(void)
{
   gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;

   // World-space lighting
   vNormal = gl_Normal;
   vec4 pos = (gl_ModelViewProjectionMatrix*gl_Vertex);
   vec4 vp;
   vp.x=10.0;
   vp.y=0.0;
   vp.z=0.0;
   vp.w=0.0;

   vViewVec = vp.xyz - pos.xyz;

   
}
            ''', '''
#version 150 compatibility
#ifdef GL_FRAGMENT_PRECISION_HIGH
   // Default precision
   precision highp float;
#else
   precision mediump float;
#endif

uniform vec4 color;
varying vec3 vNormal;
varying vec3 vViewVec;

void main(void)
{
   float v = 0.5 * (1.0 + dot(normalize(vViewVec), vNormal));
   gl_FragColor = v * color;

}
            ''')
            self.program = compile_program('''
#version 150 compatibility
            // Vertex program
            varying vec3 pos; // 이걸 응용해서 텍스쳐 없이 그냥 프래그먼트로 쉐이딩만 잘해서 컬러링을 한다.
            varying vec3 vNorm;
            uniform vec4 eye;
            varying vec4 eyeWorld;
            void main() {
                pos = gl_Vertex.xyz;
                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                eyeWorld = eye;
                vNorm = gl_NormalMatrix  * gl_Normal;
            }
            ''', '''
#version 150 compatibility
#ifdef GL_FRAGMENT_PRECISION_HIGH
   // Default precision
   precision highp float;
#else
   precision mediump float;
#endif

            // Fragment program
            uniform sampler1D colorLookup;
            uniform sampler1D colorLookup2;
            uniform sampler1D colorLookup3;
            uniform float offset;
            uniform float offset2;
            uniform float offset3;
            uniform vec2 updown;
            uniform vec2 leftright;
            uniform vec2 frontback;
            varying vec3 pos;
            varying vec3 vNorm;
            varying vec4 eyeWorld;
            void main() {
                float base = updown.x;
                float high = updown.y;
                base *=1.4;
                high *=1.4;
                float cur = pos.z-base;
                float curCol = cur/(high-base);
                curCol += offset;
                if(curCol > 1.0)
                    curCol -= 1.0;

                base = leftright.x;
                high = leftright.y;
                base *=1.4;
                high *=1.4;
                cur = pos.x-base;
                float curCol2 = cur/(high-base);
                curCol2 += offset2;
                if(curCol2 > 1.0)
                    curCol2 -= 1.0;

                base = frontback.x;
                high = frontback.y;
                base *=1.4;
                high *=1.4;
                cur = pos.y-base;
                float curCol3 = cur/(high-base);
                curCol3 += offset3;
                if(curCol3 > 1.0)
                    curCol3 -= 1.0;

                vec3 light;
                light.x = 1000.0;
                light.y = 1000.0;
                light.z = 1000.0;
                light = normalize(light).xyz;
                vec3 norm = normalize(vNorm);
                float fac = (dot(light, norm)+0.0)/1.0;
                vec3 color = texture1D(colorLookup2, curCol*fac).rgb;
                //gl_FragColor.rgb = color*fac;
                gl_FragColor.rgb = (color + texture1D(colorLookup3, curCol3).rgb + texture1D(colorLookup, curCol2).rgb)/3.0;
            }
            ''')

            self.program2 = compile_program('''
#version 150 compatibility
            // Vertex program
            varying vec3 pos;
            varying vec2 texture_coordinate;
            void main() {
                pos = gl_Vertex.xyz;
                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                texture_coordinate = vec2(gl_MultiTexCoord0);
            }
            ''', '''
#version 150 compatibility
            // Fragment program
            varying vec2 texture_coordinate;
            uniform sampler2D my_color_texture;
            varying vec3 pos;
            void main() {
                //gl_FragColor.rgb = pos.xyz/2;
                gl_FragColor = texture2D(my_color_texture, texture_coordinate);

            }
            ''')
            """

    def GetWorldMouse(self, x_cursor, y_cursor):
        """이 코드는 꼭 피킹하려는 오브젝트를 렌더링한 직후에 다른 트랜스폼 없이 호출해야 한다."""
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)

        z_cursor = glReadPixels(x_cursor, viewport[3]-y_cursor, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
        x,y,z = gluUnProject(x_cursor, viewport[3]-y_cursor, z_cursor, modelview, projection, viewport)
        #x,y,z = gluUnProject(x_cursor, viewport[3]-y_cursor, 0.0, modelview, projection, viewport)
        #xx,yy, zz = gluUnProject(x_cursor, viewport[3]-y_cursor, 1.0, modelview, projection, viewport)
        return (x,y,z)


    def HandleMapTiling(self, t,m,k):
        # 타일체인지 모드에선 이렇게 하고
        # 높낮이 조절에서는 OnLDown써야됨
        if LMB in m.pressedButtons.iterkeys() and m.y < SH-256:
            LEFTTOP = 0
            RIGHTTOP = 1
            LEFTBOT = 2
            RIGHTBOT = 3
            x,y,z = self.GetWorldMouse(m.x, m.y)
            if x > 0.0:
                xTilePos1 = x-(x-math.floor(x))
                xTilePos2 = math.ceil(x)
            else:
                xTilePos1 = math.floor(x)
                xTilePos2 = x-(x-math.ceil(x))
            if z > 0.0:
                zTilePos1 = z-(z-math.floor(z))
                zTilePos2 = math.ceil(z)
            else:
                zTilePos1 = math.floor(z)
                zTilePos2 = z-(z-math.ceil(z))

            pos = LEFTTOP
            if xTilePos1 <= x < xTilePos1+0.5 and zTilePos1 <= z < zTilePos1+0.5:
                pos = LEFTTOP
            elif xTilePos1+0.5 <= x < xTilePos2 and zTilePos1 <= z < zTilePos1+0.5:
                pos = RIGHTTOP
            elif xTilePos1 <= x < xTilePos1+0.5 and zTilePos1+0.5 <= z < zTilePos2:
                pos = LEFTBOT
            elif xTilePos1+0.5 <= x < xTilePos2 and zTilePos1+0.5 <= z < zTilePos2:
                pos = RIGHTBOT
            self.map.ClickTile(self.tileMode, pos, (x,y,z))

        # 드래그드롭을 구현해서 여기에 잘 맵으로 전달하면 된다.
        #if LMB in m.pressedButtons.iterkeys():
        #    self.map.

    def Render(self, t, m, k):
        self.Reload()
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(132.0/255.0, 217.0/255.0, 212.0/255.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.DoMove(t,m,k)

        GameDrawMode()
        self.cam1.ApplyCamera()
        glUseProgram(0)
        #self.map.Render()
        #self.HandleMapTiling(t,m,k)
        #glUseProgram(self.program2)
        """
        for j in range(-4,1):
            for i in range(-4,1):
                DrawCube((float(i),0.0,float(j)*2.0),(1.0,2.0,1.0),(255,255,255,255), self.tex)
        for j in range(-4,1):
            for i in range(-4,1):
                DrawCube((float(i),1.0,float(j)),(1.0,1.0,1.0),(255,255,255,255), self.tex2)
        """
        """
        glTranslatef(5.0, 1.0, -5.0)
        glRotatef(270, 1.0, 0.0, 0.0)
        glRotatef(self.tr*200.0, 0.0, 0.0, 1.0)
        glScalef(0.2, 0.2, 0.2)
        self.tr += 0.001
        if self.tr >= 3.0:
            self.tr = -3.0

        if t-self.prevAniTime > self.prevAniDelay:
            self.aniOffset += (t-self.prevAniTime)/500.0
            self.aniOffset2 += (t-self.prevAniTime)/1000.0
            self.aniOffset3 += (t-self.prevAniTime)/1500.0
            self.prevAniTime = t
            if self.aniOffset > 1.0:
                self.aniOffset = 0.0
            if self.aniOffset2 > 1.0:
                self.aniOffset2 = 0.0
            if self.aniOffset3 > 1.0:
                self.aniOffset3 = 0.0
        glUseProgram(self.program)

        bounds = self.model.GetBounds()

        glUniform2f(glGetUniformLocation(self.program, "updown"), bounds[0][2],bounds[1][2])
        glUniform2f(glGetUniformLocation(self.program, "leftright"), bounds[0][0],bounds[1][0])
        glUniform2f(glGetUniformLocation(self.program, "frontback"), bounds[0][1],bounds[1][1])
        glUniform1f(glGetUniformLocation(self.program, "offset"), self.aniOffset)
        glUniform1f(glGetUniformLocation(self.program, "offset2"), self.aniOffset2)
        glUniform1f(glGetUniformLocation(self.program, "offset3"), self.aniOffset3)
        glUniform4f(glGetUniformLocation(self.program, "eye"), -self.cam1.pos.x, -self.cam1.pos.y, self.cam1.pos.z, 1.0)

        glEnable(GL_TEXTURE_1D)
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_1D, self.tex3)
        glUniform1i(glGetUniformLocation(self.program, "colorLookup"), 0)
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_1D, self.sat)
        glUniform1i(glGetUniformLocation(self.program, "colorLookup2"), 1)
        glActiveTexture(GL_TEXTURE0 + 2)
        glBindTexture(GL_TEXTURE_1D, self.sat3)
        glUniform1i(glGetUniformLocation(self.program, "colorLookup3"), 2)
        glActiveTexture(GL_TEXTURE0 + 0)


        self.model.Draw()
        """

        glUseProgram(0)

        GUIDrawMode()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.gui.Render()
        self.RenderNumber(int(self.fps.GetFPS()), 0,0)

        if t - self.waitAni > self.delayAni:
            self.waitAni = t
            self.aniIdx += 1
            if self.aniIdx >= 4:
                self.aniIdx = 0
        if GUISt.emode == GUISt.GAME_MODE:
            if self.player.moving:
                glBindTexture(GL_TEXTURE_2D, self._2d_tiles[self.ani[self.aniIdx]])
            else:
                glBindTexture(GL_TEXTURE_2D, self._2d_tiles[1])
            if self.player.facing == Player.LEFT:
                DrawQuadTexFlipX(SW/2-64,SH/2-128,128,128)
            if self.player.facing == Player.RIGHT:
                DrawQuadTex(SW/2-64,SH/2-128,128,128)

        """
        DrawQuadTexFlipX(32,32+128,128,128)
        glBindTexture(GL_TEXTURE_2D, self._2d_tiles_enemy[ani[self.aniIdx]])
        DrawQuadTex(32,32+128+128,128,128)
        DrawQuadTexFlipX(32,32+128+128+128,128,128)

        if t - self.waitBeam > self.delayBeam:
            self.waitBeam = t
            self.aniBeamX += 50
            if self.aniBeamX > SW:
                self.aniBeamX = 0
        glBindTexture(GL_TEXTURE_2D, self._2d_beam)
        DrawQuadTex(self.aniBeamX + 50+64,32+16,128,64)


        glBindTexture(GL_TEXTURE_2D, self._2d_logo)
        DrawQuadTex(SW/2-512/2,SH/2-512/2,512,512)
        """

        if self.gui.emode == ConstructorGUI.EDIT_MODE:
            for guiF in self.renderGUIs:
                guiF()
        elif self.gui.emode == ConstructorGUI.GAME_MODE:
            for guiF in self.renderGameGUIs:
                guiF()
        glDisable(GL_BLEND)
        pygame.display.flip()

    def UnCamMoveMode(self, t,m,k):
        self.camMoveMode = False
    def CamMoveMode(self, t,m,k):
        self.camMoveMode = True
    def DoCam(self, t, m, k):
        if not self.guiMode:
            pressedButtons = m.GetPressedButtons()
            if MMB in pressedButtons.iterkeys():
                self.cam1.RotateByXY(m.relX, m.relY)

    def DoMove(self, t, m, k):
        if not self.guiMode:
            pressed = pygame.key.get_pressed()
            oldPos = self.cam1.pos
            x,y,z = oldPos.x,oldPos.y,oldPos.z
            if pressed[self.keyBinds["LEFT"]]:
                self.cam1.Move(-1.0,0,0, t-self.prevTime)
            if pressed[self.keyBinds["RIGHT"]]:
                self.cam1.Move(1.0,0,0, t-self.prevTime)
            if pressed[self.keyBinds["UP"]]:
                self.cam1.Move(0,0,1.0, t-self.prevTime)
            if pressed[self.keyBinds["DOWN"]]:
                self.cam1.Move(0,0,-1.0, t-self.prevTime)

            """
            if pressed[self.keyBinds["JUMP"]]:
                if self.canJump and not self.jumping:
                    self.StartJump(t)
            """
            """
            #if t - self.prevTime > self.delay:
            xyz2 = self.cam1.pos#Vector(x,y,z)+((self.cam1.pos - Vector(x,y,z)).Normalized())
            x2,y2,z2 = xyz2.x, xyz2.y, xyz2.z

            #x3,y3,z3 = self.chunks.FixPos(Vector(x,y,-z), Vector(x2,y2,-z2), self.bound)
            x3,y3,z3 = x2,y2,z2
            self.cam1.pos = Vector(x3,y3,-z3)
            """

        self.prevTime = t
        #self.CheckJump(self.cam1.pos.y)


    def SetReload(self):
        self.reload = True
        pass
    def FartherCam(self,t,m,k):
        self.camZoom += 0.5
        if self.camZoom > 15.0:
            self.camZoom = 15.0
    def CloserCam(self,t,m,k):
        self.camZoom -= 0.5
        if self.camZoom < 0.5:
            self.camZoom = 0.5

    def RenderNumberS(self, num, x, y):
        count = str(num)
        x = x
        y = y
        for c in count:
            if c == "-":
                self.textRendererSmall.RenderText(self.numbersS[10], (x, y))
            else:
                self.textRendererSmall.RenderText(self.numbersS[int(c)], (x, y))
            x += 9
    def RenderNumber(self, num, x, y):
        count = str(num)
        x = x
        y = y
        for c in count:
            if c == "-":
                self.textRenderer.RenderText(self.numbers[10], (x, y))
            else:
                self.textRenderer.RenderText(self.numbers[int(c)], (x, y))
            x += 9
    def BindRenderGameGUI(self, func):
        self.renderGameGUIs += [func]

    def BindRenderGUI(self, func):
        self.renderGUIs += [func]
    def Run(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=2048)
        isFullScreen = FULLSCREEN#0

        screen = pygame.display.set_mode((SW,SH), HWSURFACE|OPENGL|DOUBLEBUF|isFullScreen)#|FULLSCREEN)
        done = False
        resize(SW,SH)
        init()



        self.cam1 = Camera()
        emgr = EventManager()
        emgr.BindTick(self.Render)
        #emgr.BindMotion(self.DoCam)
        #emgr.BindMDown(self.CamMoveMode)
        #emgr.BindMUp(self.UnCamMoveMode)
        #emgr.BindWUp(self.CloserCam)
        #emgr.BindWDn(self.FartherCam)
        #phy = Physics()
        #emgr.BindTick(phy.Tick)



        self.fps = fps = FPS()
        #self.model = chunkhandler.Model("./blend/humanoid.jrpg")
        #self.map = chunkhandler.Map()
        self.gui = ConstructorGUI()
        self.player = Player(hp=500, maxhp=500,atk=50, mana=500,maxmana=500, heal=125)
        self.player.pos = [64+32, SH-128]

        emgr.BindTick(self.gui.Tick)
        #self.Test()

        self.font = pygame.font.Font("./fonts/NanumGothicBold.ttf", 16)
        self.font2 = pygame.font.Font("./fonts/NanumGothicBold.ttf", 13)
        self.textRenderer = StaticTextRenderer(self.font)
        self.textRendererSmall = StaticTextRenderer(self.font2)
        self.lockedText = self.textRenderer.NewTextObject(u"잠김", (255,255,255), True, (50,50,50))
        self.numbers = [self.textRenderer.NewTextObject(`i`, (255,255,255), True, (50,50,50)) for i in range(10)]
        self.numbers += [self.textRenderer.NewTextObject("-", (255,255,255), True, (0,0,0))]
        self.numbersS = [self.textRendererSmall.NewTextObject(`i`, (0,0,0), False, (0,0,0)) for i in range(10)]
        self.numbersS += [self.textRendererSmall.NewTextObject("-", (0,0,0), False, (0,0,0))]

        # self.font3 = pygame.font.Font("./fonts/Fanwood.ttf", 15)
        while not done:
            fps.Start()
            for e in pygame.event.get():
                if e.type is QUIT: 
                    done = True
                elif e.type is KEYDOWN and e.mod & KMOD_LALT and e.key == K_F4:
                    done = True
                elif e.type is MOUSEMOTION:
                    pass
                elif e.type is MOUSEBUTTONDOWN:
                    pass
                elif e.type is MOUSEBUTTONUP:
                    pass
                elif e.type == ACTIVEEVENT and e.gain == 1:
                    screen = pygame.display.set_mode((SW,SH), HWSURFACE|OPENGL|DOUBLEBUF|isFullScreen)#|FULLSCREEN) # SDL의 제한 때문에 어쩔 수가 없다.
                    self.SetReload()

                emgr.Event(e)
            emgr.Tick()


            fps.End()
        pickle.dump(len(self.gui.stages), open("./numstages.pkl", "w"))
        for i in range(len(self.gui.stages)):
            pickle.dump(self.gui.stages[i].tiles, open("./stage%dtiles.pkl" % (i+1), "w"))
            pickle.dump(self.gui.stages[i].enemyDefs, open("./stage%denemies.pkl" % (i+1), "w"))
            pickle.dump(self.gui.stages[i].doors, open("./stage%ddoors.pkl" % (i+1), "w"))
            pickle.dump(self.gui.stages[i].gems, open("./stage%dgems.pkl" % (i+1), "w"))
            pickle.dump(self.gui.curDoorIdx, open("./stage%ddoorIdx.pkl" % (i+1), "w"))


if __name__ == '__main__':
    def run():
        app = ConstructorApp()
        app.Run()
    run()

"""
음 다른거 고민하지 말고 100% 타일구조의 3D 맵 에디터를 만든다.
의외로 DigDig랑 거의 비슷할지도 모르겠다.
----------------------------------------
타일이 꽉 차있지 않으므로 청크 구조는 아닌 반면, 옥트리의 파일구조는 남겨둬서 무한맵이 가능하도록? 맵 크기는 4096x4096x128이 최대로 잡자.
--------------------
lightmapping을 구현
---------
익스텐션에 대해:
    PyOpenGL은 그냥 익스텐션을 자유롭게 쓸 수 있다.
    ShaderModel 3.0에 맞는 익스텐션만 써서 만들자.
-------------
음악을 비롯해 모든 예술은 어떤 패턴을 만들고 패턴위에 패턴을 덮어씌우고 한 5단계의 패턴을 합쳐서 놓은 후에 그 패턴 위에 패턴과 어울리는 어떤
또다른 좀 더 큰 패턴을 만들고 그 다 합쳐진 패턴을 기준으로 또 그 위에 또다른 하나의 그림을 만드는 것이다.

패턴은 에너지를 준다. 그 패턴이 주는 에너지로 좀 더 복잡한 그림이나 멜로디를 보거나 듣고 즐길 수 있는 것이다.
또한 패턴 위에 패턴을 올리는 것도 있지만 안으로 들어가서 패턴안에 패턴을 넣는것도 있다.

heightmap을 쓰는게 아니라 일단 64x64크기의 맵을 만들어 렌더링한다.
마우스로 화면 이동 어케하지?
일단 맵의 중심점으로 pos를 옮긴다.
그다음에 회전을 한다.
그다음에 dir벡터의 반대방향으로 카메라를 옮긴다.
그러니까 pos의 X,Y는 변하지 않으면서 dirV만큼만 이동하면 
-------------------------
게임의 기본:
    물질의 얻음,잃음
    사람간의 상호관계 심리적 주고받음
    연출의 진행
--------------
64x64의 맵을 렌더링함. 큐브가 아닌 그냥 쿼드. 한 쿼드가 다른 쿼드보다 높을 때 그냥 단색의 어울리는 색의 색으로 FILL한다.
------
심시티2000과 캐피탈리즘과 울온의 게임방식을 섞자.
-----------------
타일이 무지막지하게 크므로 종류가 많으면 곤란?
-----------------
게임은 NP-Hard
-------------------
맵을 gimp로 그린 후에 픽셀대픽셀로 충돌처리를 한다?
그러지 말고 땅은 무조건 울퉁불퉁하지 않고 평평하게 한 다음에 그냥 대충 한다.

아 맵 에디터에서 점을 찍어서 맵을 울퉁불퉁하게 만들자. 높이만 결정 가능하고 x축 정점은 맘대로

지하가 필요하면? 지하던젼은 레이어를 찍어서 다른층을 따로 만든다.
-------
이제 "집"을 만들고 스테이지간의 통로를 만든다.

레벨업을 하고 레이져의 파워를 높이고 체력을 높이며 힐링 마법을 쓸 수 있게 하고 마나통을 키운다.
파워
체력
마나
힐파워
이렇게 4가지 속성만 있다.

4가지 색깔의 보석을 모아서 4가지 속성값을 올리고
경험치를 모아서 레벨을 올려서 속성포인트를 얻어 속성을 올린다.
돈을 벌어서 보석을 구입 가능
-------
음악연주법: 이전 노트를 치고 현재노트를 칠 때 이전노트의 끝자락을 잡고 연결해서 연주해야 한다.
드럼이건 뭐건간에. 이전노트를 연주하고 현재노트를 연주할 때 숨을 크게 쉰다던가 정신을 새롭게 가다듬는다던가 하면 연결성이 끊긴다.

기술적으로는, 노트의 길이 즉 16분음표 16비트라도 음의 길이가 16분음표 수준에서 끊기는게 아닌 324분음표라던지 하는 랜덤하게 보이는 정도의 수준에서 끊어져서 그 짧은 쉼표들이 리듬감이나 느낌을 만들게 된다.
"""
