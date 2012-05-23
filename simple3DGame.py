# License: AGPL 3.0
# -*- coding: utf-8 -*-
import os
os.environ['SDL_VIDEO_CENTERED'] = '1'
SW,SH = 1024,670
BGCOLOR = (0, 0, 0)

import sys
from ctypes import *
from math import radians 
from OpenGL import platform
from OpenGL.GL.EXT.texture_filter_anisotropic import *
import math
gl = platform.OpenGL
import copy
import cPickle

from OpenGL.GL import *
from OpenGL.GLU import *

import pygame
from pygame.locals import *
import chunkhandler
import legume
chunkhandler.SIZE_CHUNK = 24
chunkhandler.REGENX = 1
chunkhandler.REGENZ = 1
chunkhandler.OFFSETX = chunkhandler.SIZE_CHUNK/2-1
chunkhandler.OFFSETZ = chunkhandler.SIZE_CHUNK/2-1
chunkhandler.SW = SW
chunkhandler.SH = SH


import random
import math
import numpy
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
class ButtonInven(object):
    def __init__(self, ren, txt, func, x,y):
        self.rect = x,y
        self.func = func
        self.ren = ren
        self.txtID = ren.NewTextObject(txt, (0,0,0))
        EMgrSt.BindLDown(self.OnClick)
        self.enabled = True
        self.selected = False
    def OnClick(self, t,m,k):
        if self.enabled:
            w,h = self.ren.GetDimension(self.txtID)
            if InRect(self.rect[0],self.rect[1],w+10,h+10,m.x,m.y):
                self.func()
    def Render(self):
        if self.enabled:
            w,h = self.ren.GetDimension(self.txtID)
            DrawQuad(self.rect[0],self.rect[1],w+10,h+10,(143,128,99,200),(143,128,99,200))
            if self.selected:
                DrawQuad(self.rect[0]+2,self.rect[1]+2,w+6,h+6,(244,228,198,200),(244,228,198,200))
            else:
                DrawQuad(self.rect[0]+2,self.rect[1]+2,w+6,h+6,(144+50,128+50,98+50,200),(144+50,128+50,98+50,200))
            self.ren.RenderText(self.txtID, (self.rect[0]+5,self.rect[1]+5))
class Button(object):
    def __init__(self, ren, txt, func, x,y):
        self.rect = x,y
        self.func = func
        self.ren = ren
        self.txtID = ren.NewTextObject(txt, (0,0,0), (x,y))
        AppSt.BindRenderGUI(self.Render)
        EMgrSt.BindLDown(self.OnClick)
        self.enabled = True
    def OnClick(self, t,m,k):
        if self.enabled:
            w,h = self.ren.GetDimension(self.txtID)
            if InRect(self.rect[0],self.rect[1],w+10,h+10,m.x,m.y):
                self.func()
    def Render(self):
        if self.enabled:
            w,h = self.ren.GetDimension(self.txtID)
            DrawQuad(self.rect[0],self.rect[1],w+10,h+10,(164,164,164,200),(164,164,164,200))
            self.ren.RenderText(self.txtID, (self.rect[0]+5,self.rect[1]+5))



GUISt = None
class ConstructorGUI(object):
    def __init__(self):
        global GUISt
        GUISt = self

        self.tex = -1
        self.botimg = pygame.image.load("./img/guibottombg.png")
        self.guiRenderer = chunkhandler.GUIBGRenderer()
        self.msgBox = MsgBox()
        self.msgBox.AddText(u"안녕", (255,255,255), (64,64,64))
        self.inv = self.inventory = Inventory()
        self.itemMkr = ItemMaker()
        self.char = Char()
        self.inv.AddItem(Item(name=u"테스트아이템", itemgrp=1))
        self.inv.AddItem(Item(name=u"테스트아이템2", itemgrp=2))
        self.inv.AddItem(Item(name=u"테스트아이템3", itemgrp=11))
        self.inv.AddItem(Item(name=u"테스트아이템4", itemgrp=12))
        self.inv.AddItem(Item(name=u"테스트아이템4", itemgrp=12))
        self.inv.AddItem(Item(name=u"테스트아이템4", itemgrp=12))
        self.inv.AddItem(Item(name=u"테스트아이템4", itemgrp=12))
        self.inv.AddItem(Item(name=u"테스트아이템4", itemgrp=12))
        self.inv.AddItem(Item(name=u"테스트아이템4", itemgrp=12))
        self.inv.AddItem(Item(name=u"테스트아이템4", itemgrp=12))
        self.inv.items[24] = Item(name=u"테스트아이템4", itemgrp=12)


        self.inventoryOn = False
        self.charOn = False
        self.itemMakerOn = False
        EMgrSt.BindKeyDown(self.OnKeyDown)
    def OnKeyDown(self, t,m,k):
        if k.pressedKey == K_i:
            self.inventoryOn = not self.inventoryOn
            if self.inventoryOn:
                self.itemMakerOn = False
        elif k.pressedKey == K_j:
            self.itemMakerOn = not self.itemMakerOn
            if self.itemMakerOn:
                self.inventoryOn = False
        elif k.pressedKey == K_c:
            self.charOn = not self.charOn
        elif k.pressedKey == K_ESCAPE:
            self.inventoryOn = False
            self.charOn = False
            self.itemMakerOn = False
    def DragStart(self,t,m,k):
        self.dragging = True
        self.dragStartPos = (m.x,m.y)
        self.scrStartPos = (
            self.stages[self.curStageIdx].scrX,
            self.stages[self.curStageIdx].scrY)
    def DragEnd(self,t,m,k):
        self.dragging = False

    def Regen(self):
        self.msgBox.Regen()
        self.inventory.Regen()
        self.tex = texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        teximg = pygame.image.tostring(self.botimg, "RGBA", 0) 
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1024, 256, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
        self.guiRenderer.Regen()
        self.char.Regen()

    def Tick(self,t,m,k):
        if AppSt.tileMode in [AppSt.TILECHANGE1, AppSt.TILECHANGE2]:
            x = 400+5
            y = SH-96
            y += 5
            i = 0
            for tile in AppSt.texTiles:
                if InRect(x,y,32,32, m.x,m.y):
                    for map in AppSt.maps:
                        map.SetTile(i)
                    break
                x += 32 + 5
                i += 1
                if x+32+5 > SW:
                    x = 400+5
                    y += 32+5

    def Render(self):
        glBindTexture(GL_TEXTURE_2D, AppSt.tvbg)
        DrawQuadTexTVBG(0,0,SW,SH)
        glBindTexture(GL_TEXTURE_2D, AppSt.bgbg)
        DrawQuadTex(0,0,SW,SH)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        self.guiRenderer.Render()

        self.msgBox.Render()
        
        DrawQuad(0,0,SW,62,(128,200,140,255), (64,128,74,255))
        DrawQuad(0,62,SW,2,(32,32,32,255), (32,32,32,255))
        """
        if self.inventoryOn:
            lenItem = len(self.inv.items)
            startPos = self.inv.page*25
            offset = lenItem-startPos
            if offset >= 25:
                offset = 25

            y = 64 + self.inv.lineH*offset
            DrawQuad(SW/2+128,y,SW/2-128,SH-96-y,(168,168,168,200), (168,168,168,200))
            DrawQuad(SW/2+128,64,2,SH-64-96,(32,32,32,200), (32,32,32,200))
            DrawQuad(SW/2+128,SH-98,SW/2-128,2,(32,32,32,200), (32,32,32,200))
        """
        if self.charOn:
            DrawQuad(0,64,SW/2-128,SH-64-96,(168,168,168,200), (168,168,168,200))
            DrawQuad(SW/2-128,64,2,SH-64-96,(32,32,32,200), (32,32,32,200))
            DrawQuad(0,SH-98,SW/2-128,2,(32,32,32,200), (32,32,32,200))

        if AppSt.buttons[0].enabled:
            DrawQuad(400,SH-96,SW-400,128,(168,168,168,128),(168,168,168,128))
            if AppSt.tileMode in [AppSt.TILECHANGE1, AppSt.TILECHANGE2]:
                x = 400+5
                y = SH-96
                y += 5
                for tile in AppSt.texTiles:
                    glBindTexture(GL_TEXTURE_2D, tile[0])
                    DrawQuadTex(x,y,32,32)
                    x += 32 + 5
                    if x+32+5 > SW:
                        x = 400+5
                        y += 32+5

        if self.itemMakerOn:
            self.itemMkr.Render()

        if self.inventoryOn:
            self.inventory.Render()
            glPushMatrix()
            glTranslatef(850.0,-180.0,0.0)
            glRotatef(270, 1.0, 0.0, 0.0)
            glScale(18.0, 18.0, 18.0)
            glUseProgram(AppSt.program)

            glColor4f(0.3,0.3,0.9,1.0)
            AppSt.model.DrawOutline()
            AppSt.model.Draw()
            glUseProgram(0)
            glPopMatrix()
        if self.charOn:
            self.char.Render()

        if not AppSt.editMode:
            x = 5
            byFour = 96/3
            y = SH-96+byFour/2
            w = 300
            h = 96/3
            w2 = float(self.char.hp)*300.0/float(self.char.maxhp)
            if w2 < 0:
                w2 = 0

            DrawQuad(x,y,w,h, (0,0,0,128), (0,0,0,128))
            DrawQuad(x,y,w2,h, (64,0,0,255), (128,0,0,255))

            x = 5
            y = SH-96+byFour+byFour/2
            w2 = float(self.char.mp)*300.0/float(self.char.maxmp)
            if w2 < 0:
                w2 = 0

            DrawQuad(x,y,w,h, (0,0,0,128), (0,0,0,128))
            DrawQuad(x,y,w2,h, (0,0,64,255), (0,0,128,255))


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
            renderer.NewTextObject(text, self.color, (self.rect[0], self.rect[1]+y), border=False, borderColor = (168,168,168))
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
class Item:
    def __init__(self, **kwargs):
        self.a = kwargs
        self.imgIdx = 0


class ItemView:
    def __init__(self, x,y,item, tr):
        self.tr = tr
        self.x = x
        self.y = y
        self.item = item
        self.lineH = 20
        self.text = self.tr.NewTextObject(item.a["name"], (0,0,0), (0,0), border=False, borderColor=(64,64,64))
        self.texts = [self.tr.NewTextObject(item.a["name"], (0,0,0), (0,0), border=False, borderColor=(168,168,168)) for i in range(4)]

    def Render(self):
        x = self.x
        y = self.y
        w = 400
        h = 400
        DrawQuad(x,y,w,h,(200,200,200,255),(200,200,200,255))
        DrawQuad(x,y,w,2,(32,32,32,255),(32,32,32,255))
        DrawQuad(x,y+h-2,w,2,(32,32,32,255),(32,32,32,255))
        DrawQuad(x,y,2,h,(32,32,32,255),(32,32,32,255))
        DrawQuad(x+w-2,y,2,h,(32,32,32,255),(32,32,32,255))
        self.tr.RenderOne(self.text, (x+5,y+5))
        y += self.lineH*2
        for text in self.texts:
            self.tr.RenderOne(text, (x+5,y+5))
            y += self.lineH

class Enemy:
    def __init__(self, **kwargs):
        self.a = kwargs
        EMgrSt.BindTick(self.Tick)
        self.move = pygame.time.get_ticks()
        self.delay = 2500
        self.smoothD = self.delay/10.0
        self.maps = AppSt.maps
        self.inWar = False
        self.atkDelay = 2125
        self.atkWait = pygame.time.get_ticks()

    def GetDmg(self):
        return self.a["str"] * 5
    def GetDefense(self):
        return self.a["dex"]*5
    def GetAttacked(self, attacker):
        self.inWar = True
        self.a["hp"] -= attacker.GetDmg()-self.GetDefense()
        if self.a["hp"] <= 0:
            try:
                EMgrSt.bindTick.remove(self.Tick)
                for c in AppSt.spawnedEnemies:
                    for mob in AppSt.spawnedEnemies[c]:
                        if mob == self:
                            AppSt.spawnedEnemies[c].remove(self)
            except:
                pass
        
    def Tick(self,t,m,k):
        offset = t-self.move
        if offset >= self.smoothD:
            offset = self.smoothD
            self.a["prevcoord"] = self.a["coord"]
        factor = float(offset)/float(self.smoothD)
        posOffset = Vector(*self.a["coord"]) - Vector(*self.a["prevcoord"])
        curPos = Vector(*self.a["prevcoord"]) + (posOffset.MultScalar(factor))
        self.a["curPos"] = curPos.x,curPos.y,curPos.z

        xx,yy,zz = self.a["coord"]
        okToDo = False
        charPos = Vector2(*AppSt.GetCharCoord())
        mePos = Vector2(xx,zz)
        offsetPos = charPos-mePos

        if t-self.atkWait > self.atkDelay:
            self.atkWait = t
            if offsetPos.length() < 3 and self.inWar:
                GUISt.char.GetAttacked(self)
                if IsJong(self.a["name"][-1]):
                    jong = u"이"
                else:
                    jong = u"가"
                GUISt.msgBox.AddText(u"%s%s 당신을 공격했다! %d" % (self.a["name"], jong, self.GetDmg()-GUISt.char.GetDefense()), (255,255,255), (255,255,255))
        if offsetPos.length() > 12:
            self.inWar = False
        if self.inWar:
            if t-self.move > self.delay/4:
                okToDo = True
        else:
            if t-self.move > self.delay:
                okToDo = True
        if okToDo:
            self.move = t
            if self.inWar:

                x=0
                y=0
                if abs(offsetPos.x) >= 2 and offsetPos.x > 0:
                    x=1
                elif abs(offsetPos.x) >= 2  and offsetPos.x < 0:
                    x=-1
                if abs(offsetPos.y) >= 2 and offsetPos.y > 0:
                    y=1
                elif abs(offsetPos.y) >= 2 and offsetPos.y < 0:
                    y=-1
            else:
                x = random.randint(-1,1)
                y = random.randint(-1,1)
            zz = -zz


            wallFound = False

            def GetWallFound(xx,zz,facing_):
                wallFound_ = False
                walls = self.maps[0].GetWall(xx,-(zz))
                for wall in walls:
                    xxx,zzz,facing,tile = wall
                    if facing == facing_:
                        wallFound_ = True
                        break
                return wallFound_

            y=-y

            if x == 0 and y == -1:
                self.a["facing"] = 7
                wallFound = GetWallFound(xx,zz-1,0)
            elif x == 0 and y == 1:
                self.a["facing"] = 3
                wallFound = GetWallFound(xx,zz,0)
            elif x == 1 and y == 0:
                self.a["facing"] = 1
                wallFound = GetWallFound(xx+1,zz,1)
            elif x == -1 and y == 0:
                self.a["facing"] = 5
                wallFound = GetWallFound(xx,zz,1)
            elif x == 1 and y == 1:
                self.a["facing"] = 2
                # 위쪽
                if GetWallFound(xx+1,zz,1) or GetWallFound(xx,zz,0) or GetWallFound(xx+1,zz,0) or GetWallFound(xx+1,zz+1,1):
                    wallFound = True

                if wallFound and GetWallFound(xx+1,zz,1): # 포텐셜 z+1이동
                    if not GetWallFound(xx,zz,0):
                        wallFound = False
                        x = 0
                        y = 1
                elif wallFound and GetWallFound(xx,zz,0): # 포텐셜 x+1이동
                    if not GetWallFound(xx+1,zz,1):
                        wallFound = False
                        x = 1
                        y = 0
            elif x == -1 and y == -1:
                self.a["facing"] = 6
                # 아래쪽
                if GetWallFound(xx,zz,1) or GetWallFound(xx,zz-1,0) or GetWallFound(xx-1,zz-1,0) or GetWallFound(xx,zz-1,1):
                    wallFound = True

                if wallFound and GetWallFound(xx,zz,1): # 포텐셜 z-1이동
                    if not GetWallFound(xx,zz-1,0):
                        wallFound = False
                        x = 0
                        y = -1
                elif wallFound and GetWallFound(xx,zz-1,0): # 포텐션 x-1이동
                    if not GetWallFound(xx,zz,1):
                        wallFound = False
                        x = -1
                        y = 0
            elif x == -1 and y == 1:
                self.a["facing"] = 4
                # 왼쪽
                if GetWallFound(xx,zz,0)  or GetWallFound(xx,zz,1) or GetWallFound(xx-1,zz,0) or GetWallFound(xx,zz+1,1):
                    wallFound = True

                if wallFound and GetWallFound(xx,zz,0): # 포텐셜 x-1이동
                    if not GetWallFound(xx,zz,1):
                        wallFound = False
                        x = -1
                        y = 0
                elif wallFound and GetWallFound(xx,zz,1): # 포텐셜 y+1이동
                    if not GetWallFound(xx,zz,0):
                        wallFound = False
                        x = 0
                        y = 1
            elif x == 1 and y == -1:
                self.a["facing"] = 0
                # 오른쪽
                if GetWallFound(xx,zz-1,0) or GetWallFound(xx+1,zz,1) or GetWallFound(xx+1,zz-1,0) or GetWallFound(xx+1,zz-1,1):
                    wallFound = True


                if wallFound and GetWallFound(xx,zz-1,0): # x+1
                    if not GetWallFound(xx+1,zz,1):
                        wallFound = False
                        x = 1
                        y = 0
                elif wallFound and GetWallFound(xx+1,zz,1): # y-1
                    if not GetWallFound(xx,zz-1,0):
                        wallFound = False
                        x = 0
                        y = -1

            blocked = AppSt.blocked
            if not wallFound:
                if self.maps[0].GetTile(xx+x,-(zz-1+y)) not in blocked:
                    pass
                else:
                    if x == 1 and y == 1:
                        if self.maps[0].GetTile(xx+1,-(zz-1)) not in blocked:
                            x = 1
                            y = 0
                        elif self.maps[0].GetTile(xx,-(zz-1+1)) not in blocked:
                            x = 0
                            y = 1
                        else:
                            x=0
                            y=0
                    elif x == -1 and y == -1:
                        # 아래쪽
                        if self.maps[0].GetTile(xx,-(zz-1-1)) not in blocked:
                            x = 0
                            y = -1
                        elif self.maps[0].GetTile(xx-1,-(zz-1)) not in blocked:
                            x = -1
                            y = 0
                        else:
                            x=0
                            y=0
                    elif x == -1 and y == 1:
                        if self.maps[0].GetTile(xx-1,-(zz-1)) not in blocked:
                            x = -1
                            y = 0
                        elif self.maps[0].GetTile(xx,-(zz-1+1)) not in blocked:
                            x = 0
                            y = 1
                        else:
                            x=0
                            y=0
                        # 왼쪽
                    elif x == 1 and y == -1:
                        if self.maps[0].GetTile(xx+1,-(zz-1)) not in blocked:
                            x = 1
                            y = 0
                        elif self.maps[0].GetTile(xx,-(zz-1-1)) not in blocked:
                            x = 0
                            y = -1
                        else:
                            x=0
                            y=0
                    else:
                        x=0
                        y=0
                y=-y
                   
                self.a["prevcoord"] = self.a["coord"]
                zz = -zz
                self.a["coord"] = xx+x,yy,zz+y


class EnemySpawner:
    def __init__(self, **kwargs):
        self.a = kwargs
        EMgrSt.BindTick(self.Tick)
        self.spawnTime=pygame.time.get_ticks()
        self.spawnDelay=100
        self.maxEnemy = 3
    def Tick(self,t,m,k):
        if t-self.spawnTime > self.spawnDelay:
            self.spawnTime = t
            x,y,z = coord = self.a["coord"]
            x,z = AppSt.GetLocalItemCoord(x,z)
            if (x,z) not in AppSt.spawnedEnemies:
                AppSt.spawnedEnemies[(x,z)] = []

            if len(AppSt.spawnedEnemies[(x,z)]) < self.maxEnemy:
                GUISt.msgBox.AddText(u"적생성", (255,255,255),(255,255,255))
                AppSt.spawnedEnemies[(x,z)] += [Enemy(str=self.a["str"], dex=self.a["dex"], int=self.a["int"], hp=self.a["hp"],prevcoord=self.a["coord"],coord=self.a["coord"], name=self.a["name"], facing=0)]
                # 여기다 추가하면 렌더링할 때 곤란하므로 AppSt에다가 추가하고 대신 세이브를 하지 않는다.
                # 구조는 스포너나 아이템과 동일하다.
class Char:
    def __init__(self):
        self.name = u"플레이어"
        self.font3 = pygame.font.Font("./fonts/NanumGothicBold.ttf", 13)
        self.tr = DynamicTextRenderer(self.font3)
        self.tr2 = DynamicTextRenderer(self.font3)
        self.str = 60
        self.dex = 25
        self.int = 10
        self.nameT = self.tr.NewTextObject(self.name, (0,0,0), (0,0))
        self.lines = []
        self.itemsTXT = []
        self.itemUpdated = True
        self.itemNames = [
                u"왼손",
                u"오른손",
                u"머리",
                u"상체",
                u"하체",
                u"손가락",
                u"손가락",
                u"목걸이",
                u"장갑",
                u"신발",
                ]
        self.lines.append(self.tr.NewTextObject(u"STR: ", (0,0,0), (0,0)))
        self.lines.append(self.tr.NewTextObject(u"DEX: ", (0,0,0), (0,0)))
        self.lines.append(self.tr.NewTextObject(u"INT: ", (0,0,0), (0,0)))
        for name in self.itemNames:
            self.lines.append(self.tr.NewTextObject(name + u": ", (0,0,0), (0,0)))
        self.lineH = 20
        self.hp = 1500
        self.maxhp = 1500
        self.mp = 1500
        self.maxmp = 1500

    def GetDefense(self):
        return self.dex * 5
    def GetAttacked(self, mob):
        self.hp -= mob.GetDmg()-self.GetDefense()
        if self.hp <= 0:
            self.hp = 0
            self.Die()
    def Die(self):
        AppSt.cam1.curPos = AppSt.cam1.prevPos = AppSt.cam1.pos = Vector(0.5, 0.5, -4.5)
        self.hp = self.maxhp
    def GetDmg(self):
        return self.str*5
    def Regen(self):
        self.tr.RegenTex()

    def Render(self):
        x = 5
        y = 64+5
        lineH = self.lineH
        self.tr.RenderOne(self.nameT, (x, y))
        y += lineH*2

        i = 0
        self.tr.RenderOne(self.lines[i], (x, y))
        w,h = self.tr.GetDimension(self.lines[i])
        AppSt.RenderNumberS(self.str, x+w, y)
        y += lineH
        i += 1

        self.tr.RenderOne(self.lines[i], (x, y))
        w,h = self.tr.GetDimension(self.lines[i])
        AppSt.RenderNumberS(self.dex, x+w, y)
        y += lineH
        i += 1

        self.tr.RenderOne(self.lines[i], (x, y))
        w,h = self.tr.GetDimension(self.lines[i])
        AppSt.RenderNumberS(self.int, x+w, y)
        y += lineH
        i += 1

        if self.itemUpdated:
            self.itemUpdated = False
            self.tr2.Clear()
            self.itemsTXT = []
            for name in self.itemNames:
                self.itemsTXT.append(self.tr2.NewTextObject(name, (0,0,0), (0,0)))

        for j, name in enumerate(self.itemNames):
            self.tr.RenderOne(self.lines[i+j], (x, y))
            w,h = self.tr.GetDimension(self.lines[i+j])
            self.tr2.RenderOne(self.itemsTXT[j], (x+w, y))
            y += lineH



class ItemMaker:
    def __init__(self):
        self.font3 = pygame.font.Font("./fonts/NanumGothicBold.ttf", 13)
        self.tr = DynamicTextRenderer(self.font3)
        self.tr2 = StaticTextRenderer(self.font3)
        self.items = [None for i in range(6*4*6)]
        self.lines = []
        self.lineH = 20
        self.x = SW-350
        self.y = 64
        #EMgrSt.BindLDown(self.LDown)
        #EMgrSt.BindMotion(self.Motion)
        self.selected = -1
        self.itemView = None
        self.scrollW = 24
        self.page = 0
        self.buttons = []
        self.buttons += [ButtonInven(self.tr2, u"  1  ", self.On1, SW-350+27, 64+250)]
        w = 52
        self.buttons += [ButtonInven(self.tr2, u"  2  ", self.On2, SW-350+27+w, 64+250)]
        w += 52
        self.buttons += [ButtonInven(self.tr2, u"  3  ", self.On3, SW-350+27+w, 64+250)]
        w += 52
        self.buttons += [ButtonInven(self.tr2, u"  4  ", self.On4, SW-350+27+w, 64+250)]
        w += 52
        self.buttons += [ButtonInven(self.tr2, u"  5  ", self.On5, SW-350+27+w, 64+250)]
        w += 52
        self.buttons += [ButtonInven(self.tr2, u"  6  ", self.On6, SW-350+27+w, 64+250)]
        self.buttons[0].selected = True
        self.invenPage = 0
    #def __init__(self, ren, txt, func, x,y):
    def On1(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[0].selected = True
        self.invenPage = 0
    def On2(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[1].selected = True
        self.invenPage = 1
    def On3(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[2].selected = True
        self.invenPage = 2
    def On4(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[3].selected = True
        self.invenPage = 3
    def On5(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[4].selected = True
        self.invenPage = 4
    def On6(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[5].selected = True
        self.invenPage = 5
    """
    def Motion(self,t,m,k):
        if GUISt.inventoryOn:
            y = 0
            if self.itemView:
                self.tr2.Clear()
                del self.itemView
                self.itemView = None

            lenItem = len(self.items)
            startPos = self.page*25
            offset = lenItem-startPos
            if offset >= 25:
                offset = 25

            for i in range(startPos, startPos+offset):
                if InRect(self.x,self.y+y, SW/2-128-self.scrollW, self.lineH,m.x,m.y):
                    self.itemView = ItemView(SW/4-200, SH/2-200, self.items[i], self.tr2)
                    break
                y += self.lineH

    def LDown(self,t,m,k):
        if GUISt.inventoryOn:
            self.selected = -1
            y = 0
            i = 0

            lenItem = len(self.items)
            startPos = self.page*25
            offset = lenItem-startPos
            if offset >= 25:
                offset = 25

            for i in range(startPos, startPos+offset):
                if InRect(self.x,self.y+y, SW/2-128-self.scrollW, self.lineH,m.x,m.y):
                    self.selected = i
                    return
                y += self.lineH

            w = self.scrollW
            h = self.scrollW
            x = self.x+SW/2-128-w
            y1 = 64
            y2 = SH-96-h

            if InRect(x,y1,w,h,m.x,m.y):
                self.page -= 1
                if self.page < 0:
                    self.page = 0
                self.selected = -1
            if InRect(x,y2,w,h,m.x,m.y):
                self.page += 1
                maxPage = len(self.items)/25
                if self.page >= maxPage:
                    self.page = maxPage
                self.selected = -1

    """

    def AddItem(self, item):
        found = False
        for slotIdx in range(len(self.items)):
            if self.items[slotIdx] == None:
                self.items[slotIdx] = item
                found = True
                break
        return found
    def Render(self):
        glBindTexture(GL_TEXTURE_2D, AppSt.inven)
        DrawQuadTex2(self.x, self.y, 350, 510, 350, 510, 512, 512)
        for button in self.buttons:
            button.Render()

        xx = SW-350+21
        yy = 64+286
        idxxx = 0

        for item in self.items[self.invenPage*24:]:
            if item:
                idx = item.a["itemgrp"]
                idxLocal = idx%(11*11)
                pageNum = (idx-(idx%(11*11)))/(11*11)
                x = idxLocal % 11
                y = (idxLocal-(idxLocal%11))/11
                if pageNum == 0:
                    glBindTexture(GL_TEXTURE_2D, AppSt.items1)
                elif pageNum == 1:
                    glBindTexture(GL_TEXTURE_2D, AppSt.items2)
                elif pageNum == 2:
                    glBindTexture(GL_TEXTURE_2D, AppSt.items3)
                elif pageNum == 3:
                    glBindTexture(GL_TEXTURE_2D, AppSt.items4)
                DrawQuadTex3(xx, yy, 46, 46, x*46, y*46, 46,46,512, 512)
            xx += 48+4
            idxxx += 1
            if not (idxxx % 6):
                xx = SW-350+21
                yy += 48+4
            if idxxx >= 6*4:
                break
    """
    def Render(self):
        x = self.x
        y = self.y
        i = 0

        lenItem = len(self.items)
        startPos = self.page*25
        offset = lenItem-startPos
        if offset >= 25:
            offset = 25

        for i in range(startPos, startPos+offset):
            line = self.lines[i]
            if self.selected == i:
                DrawQuad(self.x+2,y,SW/2-128-2-self.scrollW,self.lineH,(19,66,192,200),(19,66,192,230))
            elif i%2:
                DrawQuad(self.x+2,y,SW/2-128-2-self.scrollW,self.lineH,(164,164,164,200),(164,164,164,230))
            else:
                DrawQuad(self.x+2,y,SW/2-128-2-self.scrollW,self.lineH,(120,120,120,200),(120,120,120,230))
            self.tr.RenderOne(line, (x+5,y+2))
            y += self.lineH

        if self.itemView:
            self.itemView.Render()

        w = self.scrollW
        h = self.scrollW
        x = self.x+SW/2-128-w
        y1 = 64
        y2 = SH-96-h
        DrawQuad(x,y1,w,SH-96-64,(32,32,32,200),(32,32,32,230))
        DrawQuad(x,y1,w,h,(0,0,0,200),(0,0,0,230))
        DrawQuad(x,y2,w,h,(0,0,0,200),(0,0,0,230))
    """

    def Regen(self):
        self.tr.RegenTex()
        self.tr2.RegenTex()

class Inventory:
    def __init__(self):
        self.font3 = pygame.font.Font("./fonts/NanumGothicBold.ttf", 13)
        self.tr = DynamicTextRenderer(self.font3)
        self.tr2 = StaticTextRenderer(self.font3)
        self.items = [None for i in range(6*4*6)]
        self.lines = []
        self.lineH = 20
        self.x = SW-350
        self.y = 64
        #EMgrSt.BindLDown(self.LDown)
        #EMgrSt.BindMotion(self.Motion)
        self.selected = -1
        self.itemView = None
        self.scrollW = 24
        self.page = 0
        self.buttons = []
        self.buttons += [ButtonInven(self.tr2, u"  1  ", self.On1, SW-350+27, 64+250)]
        w = 52
        self.buttons += [ButtonInven(self.tr2, u"  2  ", self.On2, SW-350+27+w, 64+250)]
        w += 52
        self.buttons += [ButtonInven(self.tr2, u"  3  ", self.On3, SW-350+27+w, 64+250)]
        w += 52
        self.buttons += [ButtonInven(self.tr2, u"  4  ", self.On4, SW-350+27+w, 64+250)]
        w += 52
        self.buttons += [ButtonInven(self.tr2, u"  5  ", self.On5, SW-350+27+w, 64+250)]
        w += 52
        self.buttons += [ButtonInven(self.tr2, u"  6  ", self.On6, SW-350+27+w, 64+250)]
        self.buttons[0].selected = True
        self.invenPage = 0
    #def __init__(self, ren, txt, func, x,y):
    def On1(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[0].selected = True
        self.invenPage = 0
    def On2(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[1].selected = True
        self.invenPage = 1
    def On3(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[2].selected = True
        self.invenPage = 2
    def On4(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[3].selected = True
        self.invenPage = 3
    def On5(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[4].selected = True
        self.invenPage = 4
    def On6(self):
        for button in self.buttons:
            button.selected = False
        self.buttons[5].selected = True
        self.invenPage = 5
    """
    def Motion(self,t,m,k):
        if GUISt.inventoryOn:
            y = 0
            if self.itemView:
                self.tr2.Clear()
                del self.itemView
                self.itemView = None

            lenItem = len(self.items)
            startPos = self.page*25
            offset = lenItem-startPos
            if offset >= 25:
                offset = 25

            for i in range(startPos, startPos+offset):
                if InRect(self.x,self.y+y, SW/2-128-self.scrollW, self.lineH,m.x,m.y):
                    self.itemView = ItemView(SW/4-200, SH/2-200, self.items[i], self.tr2)
                    break
                y += self.lineH

    def LDown(self,t,m,k):
        if GUISt.inventoryOn:
            self.selected = -1
            y = 0
            i = 0

            lenItem = len(self.items)
            startPos = self.page*25
            offset = lenItem-startPos
            if offset >= 25:
                offset = 25

            for i in range(startPos, startPos+offset):
                if InRect(self.x,self.y+y, SW/2-128-self.scrollW, self.lineH,m.x,m.y):
                    self.selected = i
                    return
                y += self.lineH

            w = self.scrollW
            h = self.scrollW
            x = self.x+SW/2-128-w
            y1 = 64
            y2 = SH-96-h

            if InRect(x,y1,w,h,m.x,m.y):
                self.page -= 1
                if self.page < 0:
                    self.page = 0
                self.selected = -1
            if InRect(x,y2,w,h,m.x,m.y):
                self.page += 1
                maxPage = len(self.items)/25
                if self.page >= maxPage:
                    self.page = maxPage
                self.selected = -1

    """

    def AddItem(self, item):
        found = False
        for slotIdx in range(len(self.items)):
            if self.items[slotIdx] == None:
                self.items[slotIdx] = item
                found = True
                break
        return found
    def Render(self):
        glBindTexture(GL_TEXTURE_2D, AppSt.inven)
        DrawQuadTex2(self.x, self.y, 350, 510, 350, 510, 512, 512)
        for button in self.buttons:
            button.Render()

        xx = SW-350+21
        yy = 64+286
        idxxx = 0

        for item in self.items[self.invenPage*24:]:
            if item:
                idx = item.a["itemgrp"]
                idxLocal = idx%(11*11)
                pageNum = (idx-(idx%(11*11)))/(11*11)
                x = idxLocal % 11
                y = (idxLocal-(idxLocal%11))/11
                if pageNum == 0:
                    glBindTexture(GL_TEXTURE_2D, AppSt.items1)
                elif pageNum == 1:
                    glBindTexture(GL_TEXTURE_2D, AppSt.items2)
                elif pageNum == 2:
                    glBindTexture(GL_TEXTURE_2D, AppSt.items3)
                elif pageNum == 3:
                    glBindTexture(GL_TEXTURE_2D, AppSt.items4)
                DrawQuadTex3(xx, yy, 46, 46, x*46, y*46, 46,46,512, 512)
            xx += 48+4
            idxxx += 1
            if not (idxxx % 6):
                xx = SW-350+21
                yy += 48+4
            if idxxx >= 6*4:
                break
    """
    def Render(self):
        x = self.x
        y = self.y
        i = 0

        lenItem = len(self.items)
        startPos = self.page*25
        offset = lenItem-startPos
        if offset >= 25:
            offset = 25

        for i in range(startPos, startPos+offset):
            line = self.lines[i]
            if self.selected == i:
                DrawQuad(self.x+2,y,SW/2-128-2-self.scrollW,self.lineH,(19,66,192,200),(19,66,192,230))
            elif i%2:
                DrawQuad(self.x+2,y,SW/2-128-2-self.scrollW,self.lineH,(164,164,164,200),(164,164,164,230))
            else:
                DrawQuad(self.x+2,y,SW/2-128-2-self.scrollW,self.lineH,(120,120,120,200),(120,120,120,230))
            self.tr.RenderOne(line, (x+5,y+2))
            y += self.lineH

        if self.itemView:
            self.itemView.Render()

        w = self.scrollW
        h = self.scrollW
        x = self.x+SW/2-128-w
        y1 = 64
        y2 = SH-96-h
        DrawQuad(x,y1,w,SH-96-64,(32,32,32,200),(32,32,32,230))
        DrawQuad(x,y1,w,h,(0,0,0,200),(0,0,0,230))
        DrawQuad(x,y2,w,h,(0,0,0,200),(0,0,0,230))
    """

    def Regen(self):
        self.tr.RegenTex()
        self.tr2.RegenTex()

class MsgBox(object):
    def __init__(self):
        self.font3 = pygame.font.Font("./fonts/NanumGothicBold.ttf", 14)
        self.textRendererArea = DynamicTextRenderer(self.font3)
        self.lines = []
        self.rect = 0,SH-96-96,SW,96
        self.letterW = 9
        self.lineH = 14
        self.color = (255,255,255)
        self.lineCut = True
        self.renderedLines = []
    def Regen(self):
        self.textRendererArea.RegenTex()
        """
        self.textRendererArea = DynamicTextRenderer(self.font3)
        self.renderedLines = []
        for text in self.lines:
            self.renderedLines += [(self.textRendererArea.NewTextObject(text[0], text[1], (0, 0), border=False, borderColor = text[2]), text[1], text[2])]
        """
    def AddText(self, text, color, bcolor):
        lenn = len(self.lines)
        if self.lineCut:
            offset = self.rect[2]/self.letterW
            for textt in text.split("\n"):
                leng = 0
                while leng < len(textt):
                    newtext = textt[leng:leng+offset]
                    self.lines += [(newtext, color, bcolor)]
                    leng += offset
        else:
            for text in text.split("\n"):
                self.lines += [(text,color,bcolor)]

        
        for text in self.lines[lenn:]:
            self.renderedLines += [(self.textRendererArea.NewTextObject(text[0], text[1], (0, 0), border=False, borderColor = text[2]), text[1], text[2])]

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
                self.renderedLines[idx] = [self.textRendererArea.NewTextObject(text[0], color, (0, 0), border=False, borderColor = bcolor)]
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
    def __del__(self):
        for surf in self.surfs:
            glDeleteTextures([1])
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
    def __del__(self):
        for surf in self.surfs:
            glDeleteTextures([1])

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
    def GetSurf(self, font, text, pos, color=(255,255,255), border=False, borderColor=(168,168,168)):
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
        self.prevPos = copy.copy(self.pos)
        self.xsens = 0.2
        self.ysens = 0.2
        self.curPos = self.pos

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

    def GetXYZ(self, t):
        return self.curPos.x, self.curPos.y, self.curPos.z
    def GetXZ(self, t):
        x,y,z = self.GetXYZ(t)
        return x,z
    def ApplyCamera(self, t):
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
        x,y,z = self.GetXYZ(t)
	glTranslatef(-x, -y, z) # 아 이게 왜 방향이 다 엉망인 이유였구만.... -z를 써야되는데-_-

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

G_FAR = 25.0
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
def DrawQuadTex3(x,y,w,h, x2,y2,w2,h2, dimw, dimh):
    glBegin(GL_QUADS)
    glTexCoord2f(float(x2)/float(dimw), float(y2+h2)/float(dimh))
    glVertex3f(float(x), -float(y+h), 100.0)
    glTexCoord2f(float(x2+w2)/float(dimw), float(y2+h2)/float(dimh))
    glVertex3f(float(x+w), -float(y+h), 100.0)
    glTexCoord2f(float(x2+w2)/float(dimw), float(y2)/float(dimh))
    glVertex3f(float(x+w), -float(y), 100.0)
    glTexCoord2f(float(x2)/float(dimw), float(y2)/float(dimh))
    glVertex3f(float(x), -float(y), 100.0)
    glEnd()
def DrawQuadTex2(x,y,w,h, w2,h2, dimw, dimh):
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, float(h2)/float(dimh))
    glVertex3f(float(x), -float(y+h), 100.0)
    glTexCoord2f(float(w2)/float(dimw), float(h2)/float(dimh))
    glVertex3f(float(x+w), -float(y+h), 100.0)
    glTexCoord2f(float(w2)/float(dimw), 0.0)
    glVertex3f(float(x+w), -float(y), 100.0)
    glTexCoord2f(0.0, 0.0)
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


def DrawCube2(pos,bound, color): # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_TEXTURE_1D)
    x,y,z = pos
    w,h,j = bound
    x -= w/2
    #y -= h/2
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
        glVertex( v[v1] )
        glVertex( v[v2] )
        glVertex( v[v3] )
        glVertex( v[v4] )            
        glEnd()
    glEnable(GL_TEXTURE_1D)
    glEnable(GL_TEXTURE_2D)


def DrawCube(pos,bound, color, texture): # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
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
            

def IsJong(chr):
    chr = ord(chr)
    c = chr - 0xAC00
    a = c / (21 * 28)
    c = c % (21 * 28)
    b = c / 28
    c = c % 28
    if c != 0:
        return True
    else:
        return False
class LSys:
    def __init__(self):
        self.sys = [1,-1,1, 1, 1]
        self.degree = 30
    def Render(self):
        glPushMatrix()
        glTranslatef(0.0, 0.0, -4.0)
        DrawCube2((0.0, 0.0, 0.0),(0.07,10.0,0.07),(255,255,255,255))
        def DoLoop(depth=0):
            z = 0.0
            if depth == 0:
                z = 1.0
            if depth == 1:
                z = 0.2
            if depth == 2:
                z = 0.03
            for pm in self.sys:
                glPushMatrix()
                glTranslatef(0.0, z, 0.0)
                lens = 0.0
                if depth == 0:
                    lens = 5.0
                if depth == 1:
                    lens = 2.0
                if depth == 2:
                    lens = 0.7
                if pm > 0:
                    glRotatef(30, 0.0, 0.0, 1.0)
                    DrawCube2((0.0, 0.0, 0.0),(0.01,lens,0.01),(255,255,255,255))

                    #glTranslatef(0.0, 0.3, 0.0)
                    #glRotatef(30, 0.0, 0.0, 1.0)
                    #DrawCube2((0.0, 0.0, 0.0),(0.01,0.5,0.01),(255,255,255,255))
                else:
                    glRotatef(-30, 0.0, 0.0, 1.0)
                    DrawCube2((0.0, 0.0, 0.0),(0.01,lens,0.01),(255,255,255,255))
                if depth < 3:
                    DoLoop(depth+1)
                glPopMatrix()
                if depth == 0:
                    z += 2.0
                if depth == 1:
                    z += 0.7
                if depth == 2:
                    z += 0.2

        DoLoop()
        glPopMatrix()

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
        self.camZoom = 6.5
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

        self.tilingDelay = 50
        self.tilingWait = pygame.time.get_ticks()


        self.degree = 0

        self.blocked = [0]
        self.lsys = LSys()


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
            self.model.Regen()
            self.model2.Regen()
            for model in self.models:
                model.Regen()
            self.gui.Regen()
            self.textRenderer.RegenTex()
            self.textRendererSmall.RegenTex()
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_TEXTURE_1D)




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
                glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
                glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
                return texture
            self.inven = LoadTex("./img/inven.png", 512, 512)
            self.items1 = LoadTex("./img/items.png", 512, 512)

            image = pygame.image.load("./img/tile_wall.png")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            self.tex = texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 128, 256, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
            #self.tiles = (self.water, (10,144,216,255)), (self.tex2, (13,92,7,255))

            idx = 0
            self.maps[0].Regen(self.texTiles, (self.tex,))

            image = pygame.image.load("./img/bgbg.png")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            self.bgbg = texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 64, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
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
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)


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
            uniform vec2 updown;
            uniform vec2 leftright;
            uniform vec2 frontback;
            varying vec4 min_;
            varying vec4 max_;
            void main() {
                min_.x = leftright.x;
                min_.y = updown.x;
                min_.z = frontback.x;
                min_.w = 1.0;
                max_.x = leftright.y;
                max_.y = updown.y;
                max_.z = frontback.y;
                max_.w = 1.0;
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
            varying vec4 min_;
            varying vec4 max_;
            varying vec3 pos;
            varying vec3 vNorm;
            varying vec4 eyeWorld;
            void main() {
                float base = min_.y;
                float high = max_.y;
                base *= 1.10;
                high *= 1.10;
                float cur = pos.z-base;
                float curCol = cur/(high-base);
                curCol += offset;
                if(curCol > 1.0)
                    curCol -= 1.0;

                base = min_.x;
                high = max_.x;
                base *= 1.10;
                high *= 1.10;
                cur = pos.x-base;
                float curCol2 = cur/(high-base);
                curCol2 += offset2;
                if(curCol2 > 1.0)
                    curCol2 -= 1.0;

                base = min_.z;
                high = max_.z;
                base *= 1.10;
                high *= 1.10;
                cur = pos.y-base;
                float curCol3 = cur/(high-base);
                curCol3 += offset3;
                if(curCol3 > 1.0)
                    curCol3 -= 1.0;

                vec3 light;
                light.x = 1.0;
                light.y = 1.0;
                light.z = 1.0;
                light = normalize(light).xyz;
                vec3 norm = normalize(vNorm);
                float fac = dot(light, norm)*0.5+0.5;
                fac = fac*fac;
                fac *=0.5;
                fac +=0.5;
                vec3 color222;
                color222.r = 0.0;
                color222.g = 0.0;
                color222.b = 1.0;

                vec3 color = texture1D(colorLookup2, fac).rgb;
                //gl_FragColor.rgb = (color + texture1D(colorLookup3, curCol3*fac).rgb + texture1D(colorLookup, curCol2*fac).rgb)*fac/3.0;
                gl_FragColor.rgb = color;
            }
            ''')

            self.programEnemy2 = compile_program(''' // 음 굉장히 멋진데?
#version 150 compatibility
            // Vertex program
            varying vec3 pos; // 이걸 응용해서 텍스쳐 없이 그냥 프래그먼트로 쉐이딩만 잘해서 컬러링을 한다.
            varying vec3 vNorm;
            uniform vec4 eye;
            varying vec4 eyeWorld;
            uniform vec2 updown;
            uniform vec2 leftright;
            uniform vec2 frontback;
            varying vec4 min_;
            varying vec4 max_;
            void main() {
                min_.x = leftright.x;
                min_.y = updown.x;
                min_.z = frontback.x;
                min_.w = 1.0;
                max_.x = leftright.y;
                max_.y = updown.y;
                max_.z = frontback.y;
                max_.w = 1.0;
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
            varying vec4 min_;
            varying vec4 max_;
            varying vec3 pos;
            varying vec3 vNorm;
            varying vec4 eyeWorld;
            void main() {
                float base = min_.y;
                float high = max_.y;
                base *= 1.10;
                high *= 1.10;
                float cur = pos.z-base;
                float curCol = cur/(high-base);
                curCol += offset;
                if(curCol > 1.0)
                    curCol -= 1.0;

                base = min_.x;
                high = max_.x;
                base *= 1.10;
                high *= 1.10;
                cur = pos.x-base;
                float curCol2 = cur/(high-base);
                curCol2 += offset2;
                if(curCol2 > 1.0)
                    curCol2 -= 1.0;

                base = min_.z;
                high = max_.z;
                base *= 1.10;
                high *= 1.10;
                cur = pos.y-base;
                float curCol3 = cur/(high-base);
                curCol3 += offset3;
                if(curCol3 > 1.0)
                    curCol3 -= 1.0;

                vec3 light;
                light.x = 1.0;
                light.y = 1.0;
                light.z = 1.0;
                light = normalize(light).xyz;
                vec3 norm = normalize(vNorm);
                float fac = (dot(light, norm)+1.0)/2.0;
                fac*=fac;
                fac*=fac;
                vec3 color = texture1D(colorLookup2, fac).rgb;
                vec3 color222;
                color222.r = 1.0;
                color222.g = 1.0;
                color222.b = 0.5;
                //gl_FragColor.rgb = color;
                gl_FragColor.rgb = ((color + texture1D(colorLookup3, fac).rgb + texture1D(colorLookup, fac).rgb)*fac/4.0
                    + color222.rgb)/2;
            }
            ''')
            self.programEnemy = compile_program(''' // 음 굉장히 멋진데?
#version 150 compatibility
            // Vertex program
            varying vec3 pos; // 이걸 응용해서 텍스쳐 없이 그냥 프래그먼트로 쉐이딩만 잘해서 컬러링을 한다.
            varying vec3 vNorm;
            uniform vec4 eye;
            varying vec4 eyeWorld;
            uniform vec2 updown;
            uniform vec2 leftright;
            uniform vec2 frontback;
            varying vec4 min_;
            varying vec4 max_;
            void main() {
                min_.x = leftright.x;
                min_.y = updown.x;
                min_.z = frontback.x;
                min_.w = 1.0;
                max_.x = leftright.y;
                max_.y = updown.y;
                max_.z = frontback.y;
                max_.w = 1.0;
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
            varying vec4 min_;
            varying vec4 max_;
            varying vec3 pos;
            varying vec3 vNorm;
            varying vec4 eyeWorld;
            void main() {
                float base = min_.y;
                float high = max_.y;
                base *= 1.10;
                high *= 1.10;
                float cur = pos.z-base;
                float curCol = cur/(high-base);
                curCol += offset;
                if(curCol > 1.0)
                    curCol -= 1.0;

                base = min_.x;
                high = max_.x;
                base *= 1.10;
                high *= 1.10;
                cur = pos.x-base;
                float curCol2 = cur/(high-base);
                curCol2 += offset2;
                if(curCol2 > 1.0)
                    curCol2 -= 1.0;

                base = min_.z;
                high = max_.z;
                base *= 1.10;
                high *= 1.10;
                cur = pos.y-base;
                float curCol3 = cur/(high-base);
                curCol3 += offset3;
                if(curCol3 > 1.0)
                    curCol3 -= 1.0;

                vec3 light;
                light.x = 1.0;
                light.y = 1.0;
                light.z = 1.0;
                light = normalize(light).xyz;
                vec3 norm = normalize(vNorm);
                float fac = (dot(light, norm)+1.0)/2.0;
                fac*=fac;
                fac*=fac;
                vec3 color = texture1D(colorLookup2, fac).rgb;
                vec3 color222;
                color222.r = 0.8;
                color222.g = 0.8;
                color222.b = 0.0;
                //gl_FragColor.rgb = color;
                vec3 color333;
                vec3 color334;
                color334 = (color + texture1D(colorLookup3, fac).rgb + texture1D(colorLookup, fac).rgb)*fac/4.0;
                if(fac < 0.25)
                {
                    color333.r = 0.25;
                    color333.g = 0.25;
                    color333.b = 0.25;
                }/*
                else if(fac < 0.3)
                {
                    color333.r = 0.35;
                    color333.g = 0.35;
                    color333.b = 0.35;
                }*/
                else if(fac < 0.3)
                {
                    color333.r = 0.55;
                    color333.g = 0.55;
                    color333.b = 0.55;
                }
                /*else if(fac < 0.62)
                {
                    color333.r = 0.65;
                    color333.g = 0.65;
                    color333.b = 0.65;
                }*/
                else if(fac < 0.55)
                {
                    color333.r = 0.75;
                    color333.g = 0.75;
                    color333.b = 0.75;
                }
                else
                {
                    color333.r = 1.0;
                    color333.g = 1.0;
                    color333.b = 1.0;
                }
                gl_FragColor.rgb = (color333 + color222.rgb + color334.rgb)/3;
            }
            ''')
            self.programItem = compile_program('''
#version 150 compatibility
            // Vertex program
            varying vec3 pos; // 이걸 응용해서 텍스쳐 없이 그냥 프래그먼트로 쉐이딩만 잘해서 컬러링을 한다.
            varying vec3 vNorm;
            uniform vec4 eye;
            varying vec4 eyeWorld;
            uniform vec2 updown;
            uniform vec2 leftright;
            uniform vec2 frontback;
            varying vec4 min_;
            varying vec4 max_;
            void main() {
                min_.x = leftright.x;
                min_.y = updown.x;
                min_.z = frontback.x;
                min_.w = 1.0;
                max_.x = leftright.y;
                max_.y = updown.y;
                max_.z = frontback.y;
                max_.w = 1.0;
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
            varying vec4 min_;
            varying vec4 max_;
            varying vec3 pos;
            varying vec3 vNorm;
            varying vec4 eyeWorld;
            void main() {
                float base = min_.y;
                float high = max_.y;
                base *= 1.10;
                high *= 1.10;
                float cur = pos.z-base;
                float curCol = cur/(high-base);
                curCol += offset;
                if(curCol > 1.0)
                    curCol -= 1.0;

                base = min_.x;
                high = max_.x;
                base *= 1.10;
                high *= 1.10;
                cur = pos.x-base;
                float curCol2 = cur/(high-base);
                curCol2 += offset2;
                if(curCol2 > 1.0)
                    curCol2 -= 1.0;

                base = min_.z;
                high = max_.z;
                base *= 1.10;
                high *= 1.10;
                cur = pos.y-base;
                float curCol3 = cur/(high-base);
                curCol3 += offset3;
                if(curCol3 > 1.0)
                    curCol3 -= 1.0;

                vec3 light;
                light.x = 1.0;
                light.y = 1.0;
                light.z = 1.0;
                light = normalize(light).xyz;
                vec3 norm = normalize(vNorm);
                float fac = (dot(light, norm)+1.0)/2.0;
                vec3 color = texture1D(colorLookup2, curCol*fac).rgb;
                vec3 color222;
                color222.r = 0.0;
                color222.g = 1.0;
                color222.b = 1.0;
                //gl_FragColor.rgb = color;
                gl_FragColor.rgb = ((color + texture1D(colorLookup3, curCol3*fac).rgb + texture1D(colorLookup, curCol2*fac).rgb)*fac/4.0
                    + color222.rgb)/2;
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


    def HandleMapWalling(self,t,m,k,map):
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
        #if 0.0 < x < 0.0+64.0 and -64.0 < z < 0.0:
        if x < 0.0:
            x -= 1
        if z > 0.0:
            z += 1
        x = int(x)
        z = int(z)
        DrawCube((float(x),0,float(z)-1.0),(0.25,0.25,0.25), (255,255,255,255), 0) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
        if LMB in m.pressedButtons.iterkeys() and 64 < m.y < SH-96 and k.pressedKey == K_q:
            if t-self.tilingWait > self.tilingDelay:
                self.tilingWait = t
                self.maps[0].DelWall(x,0,-(z-1),0,0)
        elif RMB in m.pressedButtons.iterkeys() and 64< m.y < SH-96 and k.pressedKey == K_q:
            if t-self.tilingWait > self.tilingDelay:
                self.tilingWait = t
                self.maps[0].DelWall(x,0,-(z-1),0,1)

        elif LMB in m.pressedButtons.iterkeys() and 64< m.y < SH-96:
            if t-self.tilingWait > self.tilingDelay:
                self.tilingWait = t
                self.maps[0].AddWall(x,0,-(z-1),0,0)
        elif RMB in m.pressedButtons.iterkeys() and 64< m.y < SH-96:
            if t-self.tilingWait > self.tilingDelay:
                self.tilingWait = t
                self.maps[0].AddWall(x,0,-(z-1),0,1)

    def HandleItemClicking(self, t,m,k, map):
        # 타일체인지 모드에선 이렇게 하고
        # 높낮이 조절에서는 OnLDown써야됨
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
        #if 0.0 < x < 0.0+64.0 and -64.0 < z < 0.0:
        if x < 0.0: x -= 1
        if z < 0.0:
            z -= 1
        x,z=int(x),int(z)
        if LMB in m.pressedButtons:
            xx,zz = self.GetLocalItemCoord(x,z)

            if (xx,zz) in self.worldItems:
                items = self.worldItems[(xx,zz)]
                for item in items[:]:
                    xxx,nonono,zzz = item.a["coord"]
                    if x == xxx and z == zzz:
                        charPos = Vector2(*self.GetCharCoord())
                        itemPos = Vector2(xxx,zzz)
                        if (itemPos-charPos).length() <= 3:
                            if GUISt.inv.AddItem(item):
                                items.remove(item)
                            break
            if t-self.attackTime > self.attackDelay:
                self.attackTime = t

                selectedMob = None
                for coord in self.spawnedEnemies:
                    items = self.spawnedEnemies[coord]
                    found = False
                    for item in items:
                        if "selected" in item.a and item.a["selected"]:
                            selectedMob = item
                            break

                if selectedMob:
                    charPos = Vector2(*self.GetCharCoord())
                    xxx,nonono,zzz = selectedMob.a["coord"]
                    itemPos = Vector2(xxx,zzz)
                    if (charPos-itemPos).length() < 5:
                        self.AttackMob(item, charPos, itemPos)
        # 걍 맵의 타일을 클릭하면 아이템이 선택되도록 하고 아이템은 클릭도 안됨 타일을 원클릭하면 집어짐.
        # 3타일 안에 있어야함
    def AttackMob(self, mob, charPos, mobPos):
        if IsJong(mob.a["name"][-1]):
            jong = u"을"
        else:
            jong = u"를"

        GUISt.msgBox.AddText(u"당신은 %s%s 공격했다 %d"% (mob.a["name"], jong,GUISt.char.GetDmg()-mob.GetDefense()), (0,0,0), (0,0,0))
        mob.GetAttacked(GUISt.char)
    def GetLocalItemCoord(self, x,z):
        return x-x%8,z-z%8
    def HandleMapTiling(self, t,m,k, map):
        # 타일체인지 모드에선 이렇게 하고
        # 높낮이 조절에서는 OnLDown써야됨
        if LMB in m.pressedButtons.iterkeys() and 64< m.y < SH-96:
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
            #if 0.0 < x < 0.0+64.0 and -64.0 < z < 0.0:
            if x < 0.0:
                x -= 1
            if z > 0.0:
                z += 1
            map.ClickTile(self.tileMode, pos, (x,y,-z))

        # 드래그드롭을 구현해서 여기에 잘 맵으로 전달하면 된다.
        #if LMB in m.pressedButtons.iterkeys():
        #    self.map.
    def MoveWithMouse(self, way):
        x = 0
        y = 0

        wallFound = False
        xx, zz = self.cam1.pos.x, self.cam1.pos.z
        if xx < 0:
            xx -= 1
        if zz > 0:
            zz += 1
        xx = int(xx)
        zz = int(zz)

        if way == 'n':
            x += 1
            y += 1
        if way == 'ne':
            x += 1

        if way == 'nw':
            y += 1
        if way == 's':
            x -= 1
            y -= 1
        if way == 'se':
            y -= 1
        if way == 'sw':
            x -= 1
        if way == 'e':
            x += 1
            y -= 1
        if way == 'w':
            x -= 1
            y += 1


        def GetWallFound(xx,zz,facing_):
            wallFound_ = False
            walls = self.maps[0].GetWall(xx,-(zz))
            for wall in walls:
                xxx,zzz,facing,tile = wall
                if facing == facing_:
                    wallFound_ = True
                    break
            return wallFound_

        if x == 0 and y == -1:
            wallFound = GetWallFound(xx,zz-1,0)
        elif x == 0 and y == 1:
            wallFound = GetWallFound(xx,zz,0)
        elif x == 1 and y == 0:
            wallFound = GetWallFound(xx+1,zz,1)
        elif x == -1 and y == 0:
            wallFound = GetWallFound(xx,zz,1)
        elif x == 1 and y == 1:
            # 위쪽
            if GetWallFound(xx+1,zz,1) or GetWallFound(xx,zz,0) or GetWallFound(xx+1,zz,0) or GetWallFound(xx+1,zz+1,1):
                wallFound = True

            if wallFound and GetWallFound(xx+1,zz,1): # 포텐셜 z+1이동
                if not GetWallFound(xx,zz,0):
                    wallFound = False
                    x = 0
                    y = 1
            elif wallFound and GetWallFound(xx,zz,0): # 포텐셜 x+1이동
                if not GetWallFound(xx+1,zz,1):
                    wallFound = False
                    x = 1
                    y = 0
        elif x == -1 and y == -1:
            # 아래쪽
            if GetWallFound(xx,zz,1) or GetWallFound(xx,zz-1,0) or GetWallFound(xx-1,zz-1,0) or GetWallFound(xx,zz-1,1):
                wallFound = True

            if wallFound and GetWallFound(xx,zz,1): # 포텐셜 z-1이동
                if not GetWallFound(xx,zz-1,0):
                    wallFound = False
                    x = 0
                    y = -1
            elif wallFound and GetWallFound(xx,zz-1,0): # 포텐션 x-1이동
                if not GetWallFound(xx,zz,1):
                    wallFound = False
                    x = -1
                    y = 0
        elif x == -1 and y == 1:
            # 왼쪽
            if GetWallFound(xx,zz,0)  or GetWallFound(xx,zz,1) or GetWallFound(xx-1,zz,0) or GetWallFound(xx,zz+1,1):
                wallFound = True

            if wallFound and GetWallFound(xx,zz,0): # 포텐셜 x-1이동
                if not GetWallFound(xx,zz,1):
                    wallFound = False
                    x = -1
                    y = 0
            elif wallFound and GetWallFound(xx,zz,1): # 포텐셜 y+1이동
                if not GetWallFound(xx,zz,0):
                    wallFound = False
                    x = 0
                    y = 1
        elif x == 1 and y == -1:
            # 오른쪽
            if GetWallFound(xx,zz-1,0) or GetWallFound(xx+1,zz,1) or GetWallFound(xx+1,zz-1,0) or GetWallFound(xx+1,zz-1,1):
                wallFound = True


            if wallFound and GetWallFound(xx,zz-1,0): # x+1
                if not GetWallFound(xx+1,zz,1):
                    wallFound = False
                    x = 1
                    y = 0
            elif wallFound and GetWallFound(xx+1,zz,1): # y-1
                if not GetWallFound(xx,zz-1,0):
                    wallFound = False
                    x = 0
                    y = -1

        blocked = self.blocked
        if not wallFound:
            if self.maps[0].GetTile(xx+x,-(zz-1+y)) not in blocked:
                pass
            else:
                
                if x == 1 and y == 1:
                    if self.maps[0].GetTile(xx+1,-(zz-1)) not in blocked:
                        x = 1
                        y = 0
                    elif self.maps[0].GetTile(xx,-(zz-1+1)) not in blocked:
                        x = 0
                        y = 1
                    else:
                        x=0
                        y=0
                elif x == -1 and y == -1:
                    # 아래쪽
                    if self.maps[0].GetTile(xx,-(zz-1-1)) not in blocked:
                        x = 0
                        y = -1
                    elif self.maps[0].GetTile(xx-1,-(zz-1)) not in blocked:
                        x = -1
                        y = 0
                    else:
                        x=0
                        y=0
                elif x == -1 and y == 1:
                    if self.maps[0].GetTile(xx-1,-(zz-1)) not in blocked:
                        x = -1
                        y = 0
                    elif self.maps[0].GetTile(xx,-(zz-1+1)) not in blocked:
                        x = 0
                        y = 1
                    else:
                        x=0
                        y=0
                    # 왼쪽
                elif x == 1 and y == -1:
                    if self.maps[0].GetTile(xx+1,-(zz-1)) not in blocked:
                        x = 1
                        y = 0
                    elif self.maps[0].GetTile(xx,-(zz-1-1)) not in blocked:
                        x = 0
                        y = -1
                    else:
                        x=0
                        y=0
                else:
                    x=0
                    y=0
            self.cam1.prevPos = copy.copy(self.cam1.pos)
            self.cam1.pos.x += x
            self.cam1.pos.z += y

    def GetCharCoord(self):
        x = (self.cam1.pos.x)
        z = -(self.cam1.pos.z)
        if x < 0.0:
            x -= 1
        if z < 0.0:
            z -= 1
        return int(x), int(z)
    def SetCharCoord(self, x,z,floor=1):
        x += 0.5
        z += 0.5
        self.cam1.pos.x = x
        self.cam1.pos.z = -z

    def GetDegree(self):
        return self.degree
    def Render(self, t, m, k):
        self.Reload()
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(132.0/255.0, 217.0/255.0, 212.0/255.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.DoMove(t,m,k)
        # 부드러운 이동을 구현하는데 전처럼 하지 말고 좀 정확도를 높이자. 125밀리세컨드동안 부드럽게 움직이는건데 이전->다음벡터를 125로 나누고
        # 틱마다 지난시간만큼을 이동하면 되는데 틱이 일정하지가 않다. t-self.moveWait이 125를 넘을 경우 그냥 125에서 클립하면 될 듯.
        offset = t-AppSt.moveWait
        if offset >= self.moveDelay/4.0:
            offset = self.moveDelay/4.0
            self.cam1.prevPos = copy.copy(self.cam1.pos)
        factor = float(offset)/float(self.moveDelay/4.0)
        posOffset = self.cam1.pos - self.cam1.prevPos
        curPos = self.cam1.prevPos + (posOffset.MultScalar(factor))
        self.cam1.curPos = curPos

        if RMB in m.pressedButtons:
            if (GUISt.charOn and m.x <= SW/2-128):
                pass
            elif ((GUISt.inventoryOn or GUISt.itemMakerOn) and m.x >= SW-350):
                pass
            else:
                degree = (m.GetScreenVectorDegree()-90-45/2.0)
                self.degree = degree = degree-(degree%45)
            if t-self.moveWait > self.moveDelay:
                self.moveWait = t
                if (GUISt.charOn and m.x <= SW/2-128):
                    pass
                elif ((GUISt.inventoryOn or GUISt.itemMakerOn) and m.x >= SW-350):
                    pass
                else:
                    self.MoveWithMouse(DegreeTo8WayDirection(m.GetScreenVectorDegree()))
        GameDrawMode()
        self.cam1.ApplyCamera(t)
        glUseProgram(0)
        # 이제 마우스로 이동을 구현한다.
        #
        self.PosUpdate(self.cam1.pos.x, self.cam1.pos.y, -self.cam1.pos.z)
        for map in self.maps:
            map.PosUpdate(self.cam1.pos.x, self.cam1.pos.y, -self.cam1.pos.z)
            x,z = map.GetXZ()
            #mat = ViewingMatrix()
            map.Render()
            self.HandleItemClicking(t,m,k, map)
            if self.buttons[0].enabled:
                if self.tileMode == self.TILECHANGE1:
                    self.HandleMapTiling(t,m,k, map)
                if self.tileMode == self.WALLCHANGE1:
                    self.HandleMapWalling(t,m,k, map)

            """
            if mat is not None:
                frustum = NormalizeFrustum(GetFrustum(mat))
                if chunkhandler.CubeInFrustum(x,-8.0,z-8.0,8.0, frustum):
                    glTranslatef(x,0.0,z)
                    glTranslatef(-x,0.0,-z)
            """
        glUseProgram(self.program2)
        """
        for j in range(-4,1):
            for i in range(-4,1):
                DrawCube((float(i),0.0,float(j)*2.0),(1.0,2.0,1.0),(255,255,255,255), self.tex)
        for j in range(-4,1):
            for i in range(-4,1):
                DrawCube((float(i),1.0,float(j)),(1.0,1.0,1.0),(255,255,255,255), self.tex2)
        """

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

        """glUniform2f(glGetUniformLocation(self.program, "updown"), bounds[0][2],bounds[1][2])
        glUniform2f(glGetUniformLocation(self.program, "leftright"), bounds[0][0],bounds[1][0])
        glUniform2f(glGetUniformLocation(self.program, "frontback"), bounds[0][1],bounds[1][1])
        glUniform1f(glGetUniformLocation(self.program, "offset"), self.aniOffset)
        glUniform1f(glGetUniformLocation(self.program, "offset2"), self.aniOffset2)
        glUniform1f(glGetUniformLocation(self.program, "offset3"), self.aniOffset3)"""
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


        glPushMatrix()
        x,z = self.cam1.GetXZ(t)
        glTranslatef(x, 1.0, -z)
        
        glRotatef(self.GetDegree(), 0.0, 1.0, 0.0)
        glRotatef(270, 1.0, 0.0, 0.0)
        #glRotatef(self.tr*200.0, 0.0, 0.0, 1.0)
        glScalef(0.2, 0.2, 0.2)
        self.tr += 0.001
        if self.tr >= 3.0:
            self.tr = -3.0
        glLineWidth(3.0)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT,  GL_NICEST)
        self.model.Draw()
        glUseProgram(0)
        glColor4f(0.3,0.3,0.9,1.0)
        #self.model.DrawOutline()
        glPopMatrix()

        bounds = self.model2.GetBounds()

        """
        glUniform2f(glGetUniformLocation(self.program, "updown"), bounds[0][2],bounds[1][2])
        glUniform2f(glGetUniformLocation(self.program, "leftright"), bounds[0][0],bounds[1][0])
        glUniform2f(glGetUniformLocation(self.program, "frontback"), bounds[0][1],bounds[1][1])
        glUniform1f(glGetUniformLocation(self.program, "offset"), self.aniOffset)
        glUniform1f(glGetUniformLocation(self.program, "offset2"), self.aniOffset2)
        glUniform1f(glGetUniformLocation(self.program, "offset3"), self.aniOffset3)
        """
        glUseProgram(self.program)
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


        glPushMatrix()
        glTranslatef(5.5, 0.35, -4.5)
        glRotatef(270, 1.0, 0.0, 0.0)
        #glRotatef(self.tr*200.0, 0.0, 0.0, 1.0)
        glScalef(0.4, 0.4, 0.4)
        self.tr += 0.001
        if self.tr >= 3.0:
            self.tr = -3.0
        self.model2.Draw()
        glUseProgram(0)
        glColor4f(0.3,0.3,0.9,1.0)
        #self.model2.DrawOutline()
        glUseProgram(self.program)
        glPopMatrix()


        bounds = self.models[0].GetBounds()
        """
        glUseProgram(self.program)
        glUniform2f(glGetUniformLocation(self.programItem, "updown"), bounds[0][2],bounds[1][2])
        glUniform2f(glGetUniformLocation(self.programItem, "leftright"), bounds[0][0],bounds[1][0])
        glUniform2f(glGetUniformLocation(self.programItem, "frontback"), bounds[0][1],bounds[1][1])
        glUniform1f(glGetUniformLocation(self.programItem, "offset"), self.aniOffset)
        glUniform1f(glGetUniformLocation(self.programItem, "offset2"), self.aniOffset2)
        glUniform1f(glGetUniformLocation(self.programItem, "offset3"), self.aniOffset3)
        glUniform4f(glGetUniformLocation(self.programItem, "eye"), -self.cam1.pos.x, -self.cam1.pos.y, self.cam1.pos.z, 1.0)

        glEnable(GL_TEXTURE_1D)
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_1D, self.tex3)
        glUniform1i(glGetUniformLocation(self.programItem, "colorLookup"), 0)
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_1D, self.sat)
        glUniform1i(glGetUniformLocation(self.programItem, "colorLookup2"), 1)
        glActiveTexture(GL_TEXTURE0 + 2)
        glBindTexture(GL_TEXTURE_1D, self.sat3)
        glUniform1i(glGetUniformLocation(self.programItem, "colorLookup3"), 2)
        glActiveTexture(GL_TEXTURE0 + 0)
        """
        self.RenderItems()


        bounds = self.models[1].GetBounds()
        glUseProgram(self.programEnemy)

        glUniform2f(glGetUniformLocation(self.programEnemy, "updown"), bounds[0][2],bounds[1][2])
        glUniform2f(glGetUniformLocation(self.programEnemy, "leftright"), bounds[0][0],bounds[1][0])
        glUniform2f(glGetUniformLocation(self.programEnemy, "frontback"), bounds[0][1],bounds[1][1])
        glUniform1f(glGetUniformLocation(self.programEnemy, "offset"), self.aniOffset)
        glUniform1f(glGetUniformLocation(self.programEnemy, "offset2"), self.aniOffset2)
        glUniform1f(glGetUniformLocation(self.programEnemy, "offset3"), self.aniOffset3)
        glUniform4f(glGetUniformLocation(self.programEnemy, "eye"), -self.cam1.pos.x, -self.cam1.pos.y, self.cam1.pos.z, 1.0)

        glEnable(GL_TEXTURE_1D)
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_1D, self.tex3)
        glUniform1i(glGetUniformLocation(self.programEnemy, "colorLookup"), 0)
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_1D, self.sat)
        glUniform1i(glGetUniformLocation(self.programEnemy, "colorLookup2"), 1)
        glActiveTexture(GL_TEXTURE0 + 2)
        glBindTexture(GL_TEXTURE_1D, self.sat3)
        glUniform1i(glGetUniformLocation(self.programEnemy, "colorLookup3"), 2)
        glActiveTexture(GL_TEXTURE0 + 0)
        self.RenderEnemies()
        self.RenderSpawnedEnemies()
        # XXX: 여기에 적 바운딩박스로 충돌하는걸 구현
        x,y,z = self.GetWorldMouse(m.x, m.y)
        ray1 = x,-9000, z
        for coord in self.spawnedEnemies:
            items = self.spawnedEnemies[coord]
            found = False
            for item in items:
                x,y,z = item.a["curPos"]
                item.a["drawHighlight"] = False
                item.a["selected"] = False
                if InRect(x-0.5,z-0.5,1.5,1.5,ray1[0],ray1[2]) and not found:
                    item.a["drawHighlight"] = True
                    item.a["selected"] = True
                    found = True


        """
        glPushMatrix()
        glTranslatef(5.5, 0.35, -5.5)
        glRotatef(270, 1.0, 0.0, 0.0)
        #glRotatef(self.tr*200.0, 0.0, 0.0, 1.0)
        glScalef(0.2, 0.2, 0.2)
        self.tr += 0.001
        if self.tr >= 3.0:
            self.tr = -3.0
        self.models[0].Draw()
        glPopMatrix()
        """




        glUseProgram(0)
        #self.lsys.Render()

        GUIDrawMode()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.gui.Render()
        self.RenderNumber(int(self.fps.GetFPS()), 0,0)
        for button in self.buttons:
            button.Render()
        self.editModeButton.Render()
        glDisable(GL_BLEND)
        pygame.display.flip()

    def UnCamMoveMode(self, t,m,k):
        if self.buttons[0].enabled:
            self.camMoveMode = False
    def CamMoveMode(self, t,m,k):
        if self.buttons[0].enabled:
            self.camMoveMode = True
    def DoCam(self, t, m, k):
        if self.buttons[0].enabled:
            if not self.guiMode:
                pressedButtons = m.GetPressedButtons()
                if MMB in pressedButtons.iterkeys():
                    self.cam1.RotateByXY(m.relX, m.relY)

    def DoMove(self, t, m, k):
        if self.buttons[0].enabled:
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
        if self.buttons[0].enabled:
            self.camZoom += 0.5
            if self.camZoom > 15.0:
                self.camZoom = 15.0
    def CloserCam(self,t,m,k):
        if self.buttons[0].enabled:
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

    def TileMode(self):
        self.tileMode = self.TILECHANGE1

    def WallMode(self):
        self.tileMode = self.WALLCHANGE1

    def ToggleEditMode(self):
        self.editMode = not self.editMode
        if self.editMode:
            self.camPos = copy.copy(self.cam1.pos)
            self.camPrevPos = copy.copy(self.cam1.prevPos)
            self.heading = copy.copy(self.cam1.headingDegrees)
            self.pitch = copy.copy(self.cam1.pitchDegrees)
        else:
            self.cam1.pos = copy.copy(self.camPos)
            self.cam1.prevPos = copy.copy(self.camPrevPos)
            self.cam1.headingDegrees = self.heading
            self.cam1.pitchDegrees = self.pitch
        for button in self.buttons:
            button.enabled = self.editMode

    def PosUpdate(self, x,y,z):
        RANGE = 24
        x = x-x%8
        z = z-z%8

        xx = x-RANGE/2
        zz = z-RANGE/2
        xx2 = x+RANGE/2
        zz2 = z+RANGE/2

        yesCoords = []
        while zz <= zz2:
            while xx <= xx2:
                xxx = xx-xx%8
                zzz = zz-zz%8
                yesCoords += [(xxx,zzz)]
                if (xxx,zzz) not in self.worldItems:
                    self.worldItems[(xxx,zzz)] = self.LoadItem(xxx,zzz)
                if (xxx,zzz) not in self.worldEnemies:
                    self.worldEnemies[(xxx,zzz)] = self.LoadEnemy(xxx,zzz)
                    for enemy in self.worldEnemies[(xxx,zzz)]:
                        enemy.__init__(**enemy.a)
                xx += 8
            zz += 8
            xx = x-RANGE/2

        keys = self.worldItems.keys()
        for coord in keys:
            if coord not in yesCoords:
                self.Save(self.worldItems[coord], self.GetWorldItemFileName(*coord))
                del self.worldItems[coord]

        keys = self.worldEnemies.keys()
        for coord in keys:
            if coord not in yesCoords:
                self.Save(self.worldEnemies[coord], self.GetWorldEnemyFileName(*coord))
                del self.worldEnemies[coord]

    def AddWorldEnemy(self,item):
        x,nonono,y = item.a["coord"]
        x = x-x%8
        y = y-y%8
        self.worldEnemies[(x,y)] = [item]
        #self.worldEnemies[(x,y)] += [item]

    def AddWorldItem(self,item):
        x,nonono,y = item.a["coord"]
        x = x-x%8
        y = y-y%8
        try:
            self.worldItems[(x,y)] += [item]
        except:
            self.worldItems[(x,y)] = [item]

    def RenderEnemies(self):
        for coord in self.worldEnemies:
            items = self.worldEnemies[coord]
            for item in items:
                x,y,z = item.a["coord"]
                itemc = Vector2(x,z)
                char = Vector2(*self.GetCharCoord())
                if (itemc-char).length() < 18:
                    glPushMatrix()
                    glTranslatef(x+0.5,y+0.5,z+0.5)
                    glRotatef(270, 1.0, 0.0, 0.0)
                    glScale(0.5,0.5,0.5)

                    self.models[1].Draw()

                    glUseProgram(0)
                    glColor4f(0.3,0.3,0.9,1.0)
                    #self.models[1].DrawOutline()
                    glUseProgram(AppSt.programEnemy)

                    glPopMatrix()

    def RenderSpawnedEnemies(self):
        for coord in self.spawnedEnemies:
            items = self.spawnedEnemies[coord]
            for item in items:
                x,y,z = item.a["curPos"]
                itemc = Vector2(x,z)
                char = Vector2(*self.GetCharCoord())
                if (itemc-char).length() < 18:
                    glPushMatrix()
                    glTranslatef(x+0.5,y+1.0,z+0.5)
                    degree = (45*item.a["facing"]-90-45/2.0)
                    degree = degree-(degree%45)
                    glRotatef(degree, 0.0, 1.0, 0.0)
                    glRotatef(270, 1.0, 0.0, 0.0)
                    glScale(0.2,0.2,0.2)
                    if "drawHighlight" in item.a and item.a["drawHighlight"]:
                        glUseProgram(AppSt.programEnemy2)
                    else:
                        glUseProgram(AppSt.programEnemy)
                    self.models[2].Draw()
                    glUseProgram(0)
                    glColor4f(0.8,0.8,0.2,1.0)
                    if not("drawHighlight" in item.a and item.a["drawHighlight"]):
                        self.models[2].DrawOutline()
                    glUseProgram(AppSt.programEnemy)
                    glPopMatrix()

    def RenderItems(self):
        for coord in self.worldItems:
            items = self.worldItems[coord]
            for item in items:
                x,y,z = item.a["coord"]
                itemc = Vector2(x,z)
                char = Vector2(*self.GetCharCoord())
                if (itemc-char).length() < 18:
                    glPushMatrix()
                    glTranslatef(x+0.5,y+0.5,z+0.5)
                    glRotatef(270, 1.0, 0.0, 0.0)
                    glScale(0.5,0.5,0.5)

                    glUseProgram(0)
                    glColor4f(0.3,0.3,0.9,1.0)
                    #self.models[0].DrawOutline()
                    glUseProgram(AppSt.program)

                    self.models[0].Draw()

                    glPopMatrix()
    def LoadEnemy(self, x, y):
        try:
            x = x-x%8
            y = y-y%8
            f = open(self.GetWorldEnemyFileName(x,y), "rb")
            items = cPickle.load(f)
            f.close()
            return items
        except:
            return []
    def LoadItem(self, x, y):
        try:
            x = x-x%8
            y = y-y%8
            f = open(self.GetWorldItemFileName(x,y), "rb")
            items = cPickle.load(f)
            f.close()
            return items
        except:
            return []
    def Save(self, item, fileName):
        f = open(fileName, "wb")
        cPickle.dump(item, f)
        f.close()
    def SaveEnemies(self):
        for coord in self.worldEnemies:
            f = open(self.GetWorldEnemyFileName(*coord), "wb")
            item = self.worldEnemies[coord]
            cPickle.dump(item, f)
            f.close()
    def SaveItems(self):
        for coord in self.worldItems:
            f = open(self.GetWorldItemFileName(*coord), "wb")
            item = self.worldItems[coord]
            cPickle.dump(item, f)
            f.close()

    def GetWorldEnemyFileName(self, x,y):
        x = x-x%8
        y = y-y%8
        return "./items/%d_%d.enemy" % (x,y)
    def GetWorldItemFileName(self, x,y):
        x = x-x%8
        y = y-y%8
        return "./items/%d_%d.item" % (x,y)

    def Run(self):
        pygame.init()
        pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS,1)
        pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES,8)

        pygame.display.set_caption("허수아비RPG")
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=2048)
        isFullScreen = 0#FULLSCREEN#0

        screen = pygame.display.set_mode((SW,SH), HWSURFACE|OPENGL|DOUBLEBUF|isFullScreen)#|FULLSCREEN)
        done = False
        resize(SW,SH)
        init()


        self.worldItems = {} # By 8x8 Coord
        self.worldEnemies = {} # Spawners
        self.spawnedEnemies = {}
        self.attackTime = pygame.time.get_ticks()
        self.attackDelay = 125

        self.cam1 = Camera()
        self.camPos = copy.copy(self.cam1.pos)
        self.camPrevPos = copy.copy(self.cam1.prevPos)
        self.heading = copy.copy(self.cam1.headingDegrees)
        self.pitch = copy.copy(self.cam1.pitchDegrees)

        self.moveWait = pygame.time.get_ticks()
        self.moveDelay = 150
        self.cam1.pos.x += 0.5
        self.cam1.pos.z += 0.5
        self.cam1.prevPos = copy.copy(self.cam1.pos)
        self.cam1.pitchDegrees = 85.9999
        self.cam1.headingDegrees = 45.0
        emgr = EventManager()
        emgr.BindTick(self.Render)

        emgr.BindMotion(self.DoCam)
        emgr.BindMDown(self.CamMoveMode)
        emgr.BindMUp(self.UnCamMoveMode)
        emgr.BindWUp(self.CloserCam)
        emgr.BindWDn(self.FartherCam)

        #phy = Physics()
        #emgr.BindTick(phy.Tick)



        self.fps = fps = FPS()
        self.model = chunkhandler.Model("./blend/humanoid.jrpg", 5)
        self.model2 = chunkhandler.Model("./blend/chest.jrpg", 1)
        self.models = [chunkhandler.Model("./blend/item.jrpg", 2)]
        self.models += [chunkhandler.Model("./blend/item.jrpg", 3)]
        self.models += [chunkhandler.Model("./blend/humanoid.jrpg", 4)]
        self.maps = []
        self.maps = [chunkhandler.Map(0)]

        idx = 0
        """
        self.map = chunkhandler.Map(0, (0,0))
        self.map2 = chunkhandler.Map(1, (0,1))
        """
        self.gui = ConstructorGUI()

        emgr.BindTick(self.gui.Tick)
        #self.Test()

        self.font = pygame.font.Font("./fonts/NanumGothicBold.ttf", 16)
        self.font2 = pygame.font.Font("./fonts/NanumGothicBold.ttf", 13)
        self.textRenderer = StaticTextRenderer(self.font)
        self.textRendererSmall = StaticTextRenderer(self.font2)
        self.lockedText = self.textRenderer.NewTextObject(u"잠김", (255,255,255), True, (50,50,50))
        self.numbers = [self.textRenderer.NewTextObject(`i`, (255,255,255), False, (50,50,50)) for i in range(10)]
        self.numbers += [self.textRenderer.NewTextObject("-", (255,255,255), False, (0,0,0))]
        self.numbersS = [self.textRendererSmall.NewTextObject(`i`, (0,0,0), False, (0,0,0)) for i in range(10)]
        self.numbersS += [self.textRendererSmall.NewTextObject("-", (0,0,0), False, (0,0,0))]

        self.editMode = False
        self.buttons = []
        self.button1 = Button(AppSt.textRendererSmall, u"타일모드", self.TileMode, 5, SH-96+5)
        self.buttons += [self.button1]
        self.button2 = Button(AppSt.textRendererSmall, u"벽모드", self.WallMode, 5+65, SH-96+5)
        self.buttons += [self.button2]
        for button in self.buttons:
            button.enabled = False
        item = Item(name=u"테스트월드아이템", coord=(-1,0,-1), itemgrp=0)
        #for i in range(125):
        #enemy = EnemySpawner(name=u"적", coord=(2,0,-30), mp=1020,maxmp=1020,maxhp=1050,hp=1050, str=60, dex=25, int=10)
        self.AddWorldItem(item)
        #self.AddWorldEnemy(enemy)
        self.SetCharCoord(-1,-1)
        #item = Item(name=u"테스트월드아이템", coord=(1,0,0))
        #self.AddWorldItem(item)

        self.editModeButton = Button(AppSt.textRendererSmall, u"에딧모드토글", self.ToggleEditMode, 105, 5)
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

        self.maps[0].SaveFiles()
        self.SaveItems()
        self.SaveEnemies()


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



VBO를 __del__에다가 glDeleteBuffer해줘야되ㅏㅁ
----------
그냥 위치에 따라 파일에서 로드해서 32x32맵을 로드한다.
저장은 16x16크기로 해서 4개의 맵을 로드하도록 한다. 왜냐면 맵이 겹쳐지므로
이동할 때마다 매번 로드해야하네..... 48x48로 하면 될 듯
12칸 이동할 때마다 한번씩 로드될 것 같다.
---------------
파일 하나에 256x256칸을 넣고
좌표에 따라 파일을 연다. 파일이 이미 열렸다면 열린 파일을 쓴다.
리젠할 때 파일을 연다.
타일 저장은 언로드시에 저장한다.
Save버튼을 만들어서 매뉴얼 저장을 하게 한다.
---------
심즈처럼 경계선 사이에서 클릭해서 벽만들게 한다.
2층 3층 4층까지 가능한데 각 층의 높이는 무조건 +2.0이다.
---------------------
맵상의 오브젝트 클릭시 반응 어떻게 하나?
이미 오브젝트가 떨어진 곳에는 못 떨어뜨리므로 걍 맵을 클릭하면 아이템이 집어진다.
---------------------
XXX XXX XXX XXX XXX 2층 구현:  벽 주면에 2층짜리 사각형을 2개 투명하게 그리고 거기 클릭해서 타일을 그린다.
---------------
이제 벽으로 막기를 구현
--------------
이제 인벤토리, 캐릭터창등을 구현
----------------
캐릭터 데페니션과 모델을 정의
몬스터의 수는 25종
몬스터 스포너의 수는 100개(재탕 4번씩)
맵은 아일랜드의 연결로 이어져있는데 아일랜드는 당연히 스포너의 수만큼 100개 정도
아이템의 종류는 20종정도
20종의 아이템으로 속성을 서로 다르게 드랍함
마법의 종류는 10종
한번에 싸워야 하는 몬스터는 많아야 100마리
울온의 공격범위 마법처럼 사각형 범위에 AOE드랍, 일렬로 드랍하기 정도만 구현한다.


타일처럼 몬스터의 그림을 그려두고 그걸 클릭해서 땅에다 클릭하면 스포너가 생긴다.
---------
황병기씨 가야금의 비밀:
    그냥 신디사이져로 7개 옥타브의 도음을 한번에 누르면 가야금 1개 소리가 난다. 즉, 걍 여러 음이 한 음에 합쳐져있어서 풍성한 소리가 남.
    게임에 응용하면 한 연출이나 액션, 게임무브에 여러개의 액션이 있으면 재밌다?
-------
게임 디자인:
    게임은 서비스다. 할거리, 볼거리를 제공해줘야한다.
--------------------
음악 작곡할 때 좀 이해가 잘 안되는 멜로디는 볼륨을 줄여서 백그라운드로 넣으면 이해가 된다.
----------
바운딩 박스로 적 클릭하는걸 구현해야한다.
언프로젝트하고 모든 적의 바운딩박스와 언프로젝트된 포지션을 Y축으로 길게 늘려서 만든 레이와 충돌검사
------------
음 이제 아이템 장비하고 스킬도 쓰며 적을 잡아보자.
-------------
현재 레벨과 장비로 몹을 잡을 수 있느냐 없느냐가 중요
퍼즐처럼 해서 여러가지 패턴(스킬셋과 장비셋과 스탯셋)으로 어떤 몹을 잡을 수 있고 어떤 몹을 못잡는지를 결정한다.
아 레벨은 없고 스킬이 올라가는 것만 있다. 그리고 무제한이라서 노가다를 뛰면 결국 못잡는 몹이 없게 하고
몹의 종류를 계속 만들어 올려서 한참동안 플레이할 수 있게 한다.


여러 리듬을 겹쳐서 음악을 작곡한다.
4분음표 8분음표로만 나누는게 아니라 서로 다른 8분음표 패턴을 섞으면 된다. 낮은도 높은도만 있는게 아니라 그 사이에 1도레미파가 있듯이 리듬도 나눠진다.
---------
음악의 한 멜로디라인은 게임의 던젼의 스릴을 표현하고 다른 멜로디라인은 주인공이 던젼을 탐험하고 깨는 통쾌함을 표현.
------------
영어 책을 읽을 때 내가 아는 문법에 맞춰서 읽지말고 그대로 일거야 한다..
----------------
RPG크래프트
적이나 스펠 아이템등을 유져가 모두 다 제작한다.
더 센 적을 만들수록 드랍하는 골드라던가 경험치가 더 높아짐
-----------
적 제작 메뉴
아이템 제작 메뉴
마법및 기술 제작 메뉴

아이템 제작은 일단 울온같은 메뉴에서 아이템을 제작한다.
그 다음 인챈팅을 하는데 오블리비언에서 마법을 만드는 창을 띄우게 하고 보유중인 마법으로 마법을 만들어 장비에 바르면 인챈팅이 된다.
인챈트가 끝난 아이템에 추가적으로 이미 있는 옵션을 빼거나 없는 옵션을 넣거나 옵션치를 변경할 수 있다.

마법:
불데미지
얼음데미지
번개데미지
불저항업다운
얼음저항업다운
번개저항업다운
스턴
속도업다운
물리데미지업버프/다운저주
물리방어업다운
마법데미지업다운
STR업다운
DEX업다운
INT업다운
체력흡수
마나흡수
마나쉴드
최대체력깎기
최대마나깎기
남은 체력 퍼센티지로 깎기
남은 마나 퍼센티지로 깎기
체력/마나 퍼센테지로 회복
공격속도 증가/감소
체력/마나리젠 업/다운
소환
스킬 업다운

인챈트에만 존재하는것:
    무기의 기본 공격력 증가(물리및 각 속성별)
    방어구의 기본 방어력 증가(물리및 각 속성별)
    얻는 경험치 증가
    골드 증가

모든 마법은 밀리가 아니라 레인지드이며 지속시간과 범위가 있다.
공격마법이나 체력깎기라던가 하는 것들은 지속시간이 길면 길수록 초단위로 데미지를 입힌다.
예를들어 데미지 50 5초면 총합 250의 데미지를 입힌다.
스턴이나 슬로우같은 깎기 종류가 아닌것은 그냥 지속만 된다.

지식:
    파괴마법
    소환마법
    저주마법
    증폭마법
    웨폰리
    아머

포션류는 모든 마법을 포션으로 바꿈
포션이랑 버프는 중복됨 하지만 버프+버프 또는 포션+포션은 중복이 안됨


3D신디사이져. 자갈을 랜덤하게 생성한다.
나무도 랜덤하게 생성해 본다.
지형도 랜덤하게 생성해 본다.

돌기둥이나 바위도 랜덤하게 생성해 본다.

이외에 여러가지 랜덤하게 생성 가능한 자연물을 생성해 본다.


인간이 만든 물체는 다만 랜덤하게 생성하기가 어렵겠지만 랜덤하게 생성된 물체를 조합하면 인간이 만든 조형물도 생성이 가능?



파티장을 이쁘게 꾸미듯 맵도 이쁘게 꾸며야 한다.


그 이외에 프랙탈 조형물은 랜덤하게 생성해서 나무처럼 또는 나무 대신 장식물로 쓸 수 있다.
L-System을 이용/확장하여 나무가 아닌 여러가지 물체를 만들어 본다.
"""
