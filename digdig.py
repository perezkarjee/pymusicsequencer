# -*- coding: utf-8 -*-
"""
DigDigRPG
Copyright (C) 2011 Jin Ju Yu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
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
g_Textures = []
def glGenTexturesDebug(texnum):
    global g_Textures
    tex = glGenTextures(texnum)
    if tex in g_Textures:
        print 'Error!'
    g_Textures += [tex]
    return tex
def GenId():
    global g_id
    newid = g_id
    g_id += 1
    return newid

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


def DrawQuad(x,y,w,h, color1, color2):
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glColor4ub(*color1)
    glVertex3f(float(x), -float(y+h), 100.0)
    glVertex3f(float(x+w), -float(y+h), 100.0)
    glColor4ub(*color2)
    glVertex3f(float(x+w), -float(y), 100.0)
    glVertex3f(float(x), -float(y), 100.0)
    glEnd()
    glEnable(GL_TEXTURE_2D)


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


class SpawnerGUI(object): # XXX: 스포너를 이용해 건물을 복사하는 기능을 넣자! 스포너 2개로 min,max바운딩 박스 또는 스포너 2개로 x,z의 min max그리고 높이값으로
    # 정해서 최대 128x128x128크기의 오브젝트를 저장하고 다른곳에 복사할 수 있는 기능을 넣자.
    # 스포너 2개로 x,z값을 정하고 그 위치부터 위쪽으로 Y값 몇칸, 아래쪽으로 Y값 몇칸을 정하는게 가장 현실적일 것 같다.
    # 아니면...스포너 2개로 min/max를 정하고 Y값은 그냥 무한으로 0~128까지를 다 저장하도록 만들던지. 선택적으로 일부분만 할 수도 있게 하자. 오버행
    # 같은게 걸리면 골치아프니까.
    # 저장하면 건물 스포너라는 아이템으로 불러올 수 있다.
    # 또한 개인 소유지를 만들 수 있게 하는데 2개 스포너로 x,z를 minmax정하고 위아래로 Y값을 모두 자기 개인 소유지로 정한다.
    # 넓이가 넓을수록 많은 돈이 필요.
    # 개인 소유지에서만 땅을 파서 광물을 얻을 수 있도록 해보자.
    def __init__(self, x,y,w,h, letterW, color=(0,0,0)):
        self.text = ''
        self.rect = x,y,w,h
        self.letterW = letterW
        self.color = color
        self.active = False
        def A():
            pass
        self.func = A
        self.destroyFunc = A
        EMgrSt.BindLDown(self.LDown)
    def LDown(self, t,m,k):
        x,y,w,h = self.rect
        self.active = False
        if AppSt.gui.invShown and AppSt.gui.toolMode == TM_SPAWN:
            if InRect(x,y,30,30, m.x,m.y):
                if self.text:
                    self.func(self.text)
                AppSt.gui.toolMode = TM_TOOL
                AppSt.gui.ShowInventory(False)
                AppSt.guiMode = False
            if InRect(x+30,y,30,30, m.x,m.y):
                AppSt.gui.toolMode = TM_TOOL
                AppSt.gui.ShowInventory(False)
                AppSt.guiMode = False
            if InRect(x+60,y,30,30, m.x,m.y):
                AppSt.gui.toolMode = TM_TOOL
                AppSt.gui.ShowInventory(False)
                AppSt.guiMode = False
                self.destroyFunc()
            if InRect(x,y+30,w,h-30, m.x,m.y):
                self.active = True
                AppSt.gui.ime.SetPrintFunc(self.SetText)
                AppSt.gui.ime.SetText(self.text)
                AppSt.gui.ime.SetActive(self.active)

    def BindDestroy(self, func):
        self.destroyFunc = func
    def Bind(self, func):
        self.func = func
    def SetText(self, text):
        if text:
            leng = 0
            offset = self.rect[2]/self.letterW
            self.text = text[0:offset]
        else:
            self.text = ''

    def Clear(self):
        self.text = ''
    def Update(self, renderer):
        renderer.NewTextObject(self.text, self.color, (self.rect[0], self.rect[1]+30))

    def Render(self):
        # 선택한 텍스트는 하이라이트 DrawQuad로
        if AppSt.gui.invShown and AppSt.gui.toolMode == TM_SPAWN:
            DrawQuad(*self.rect+((40,40,40,220), (40,40,40,220)))
            x,y,w,h = self.rect
            DrawQuad(x,y+30,w,h-30,(230,230,230,220), (230,230,230,220))

            texupx = (3*30.0) / 512.0
            texupy = (11*30.0) / 512.0
            RenderImg(AppSt.gui.tooltex, texupx, texupy, x+0, y, 30, 30)
            texupx = (3*30.0) / 512.0
            texupy = (12*30.0) / 512.0
            RenderImg(AppSt.gui.tooltex, texupx, texupy, x+30, y, 30, 30)
            texupx = (3*30.0) / 512.0
            texupy = (13*30.0) / 512.0
            RenderImg(AppSt.gui.tooltex, texupx, texupy, x+60, y, 30, 30)

        # ok버튼을 넣고 스포너에 이름을 붙일 수 있도록 한다.
        # 스포너를 좌측 버튼으로 hit 하면 OnSpawnerHit이벤트가 발생하고
        # 코드블럭을 좌측버튼으로 hit하면 OnCodeHit이벤트가 발생한다.

class FileSelector(object):
    def __init__(self, scriptPath):
        self.path = scriptPath
        self.rect = (SW-400)/2, (SH-300)/2, 400, 300
        x,y,w,h = self.rect
        self.lineH = 14
        self.textArea = TextArea(x,y+30,w,h,14,self.lineH,color=(255,255,255),lineCut=False)
        self.textArea.SetText("fileName.py")
        EMgrSt.BindMotion(self.Motion)
        EMgrSt.BindLDown(self.LDown)
        self.selectedFile = -1
        self.pageIdx = 0
        self.dirs = []

        def a(fileN):
            print fileN
        def b():
            pass
        self.func = a
        self.destroyFunc = b

        paths = []
        files = []
        dirs = os.listdir(self.path)
        self.fileLen = (300-30)/self.lineH
        self.pageLen = len(dirs)/(self.fileLen)+1
        self.selectedFileName = None
        self.pageIdx = 0


    def BindDestroy(self, func):
        self.destroyFunc = func
    def Bind(self, func):
        self.func = func

    def LDown(self, t, m, k):
        if AppSt.gui.invShown and AppSt.gui.toolMode == TM_CODE:
            x,y,w,h = self.rect
            if InRect(x,y,w,h,m.x,m.y):
                if InRect(x,y,30,30,m.x,m.y): # prev
                    self.pageIdx -= 1
                    if self.pageIdx < 0:
                        self.pageIdx = 0
                elif InRect(x+30,y,30,30,m.x,m.y): # next
                    self.pageIdx += 1
                    if self.pageIdx >= self.pageLen:
                        self.pageIdx = self.pageLen-1
                elif InRect(x+60,y,30,30,m.x,m.y): # up
                    if self.dirs:
                        del self.dirs[-1]
                    thepath = self.path
                    for path in self.dirs:
                        thepath += "/"+path
                    dirs = os.listdir(thepath)
                    self.pageLen = len(dirs)/(self.fileLen)+1
                    self.pageIdx = 0
                elif InRect(x+90,y,30,30,m.x,m.y): # ok
                    self.func(self.selectedFileName)
                    AppSt.gui.toolMode = TM_TOOL
                    AppSt.gui.ShowInventory(False)
                    AppSt.guiMode = False
                elif InRect(x+120,y,30,30,m.x,m.y): # cancel
                    AppSt.gui.toolMode = TM_TOOL
                    AppSt.gui.ShowInventory(False)
                    AppSt.guiMode = False
                elif InRect(x+150,y,30,30,m.x,m.y): # destroy
                    AppSt.gui.toolMode = TM_TOOL
                    AppSt.gui.ShowInventory(False)
                    AppSt.guiMode = False
                    self.destroyFunc()
                elif self.selectedFile != -1:
                    paths = []
                    files = []
                    thepath = self.path
                    for path in self.dirs:
                        thepath += "/"+path
                    dirs = os.listdir(thepath)
                    paths = []
                    files = []
                    for path in dirs:
                        if os.path.isdir(self.path+"/"+path):
                            paths += [path]
                        elif path.endswith(".py"):
                            files += [path]
                    if self.selectedFile < len(paths+files):


                        selected = (paths+files)[self.pageIdx*(self.fileLen):self.pageIdx*(self.fileLen)+self.fileLen][self.selectedFile]
                        if os.path.isdir(thepath+"/"+selected):
                            self.dirs += [selected]
                            self.pageIdx = 0
                            dirs = os.listdir(thepath+"/"+selected)
                            self.pageLen = len(dirs)/(self.fileLen)+1
                        else:
                            self.selectedFileName = thepath+"/"+selected

    def Motion(self, t, m, k):
        if AppSt.gui.invShown and AppSt.gui.toolMode == TM_CODE:
            self.selectedFile = -1
            x,y,w,h = self.rect
            if InRect(x,y,w,h,m.x,m.y):
                yy = y+30
                idx = 0
                while idx < self.fileLen:
                    if InRect(x,yy+3,w,self.lineH, m.x, m.y):
                        self.selectedFile = idx
                        break
                    idx += 1
                    yy += self.lineH

    def Update(self, renderer):
        paths = []
        files = []
        thepath = self.path
        for path in self.dirs:
            thepath += "/"+path
        dirs = os.listdir(thepath)
        for path in dirs:
            if os.path.isdir(self.path+"/"+path):
                paths += ["[%s]" % path]
            elif path.endswith(".py"):
                files += [path]

        self.textArea.SetText('\n'.join((paths+files)[self.pageIdx*(self.fileLen):self.pageIdx*(self.fileLen)+self.fileLen]))
        self.textArea.Update(renderer)
        renderer.NewTextObject(str(self.selectedFileName), (200,200,200), (self.rect[0]+180, self.rect[1]+0))

    def Render(self):
        # 선택한 텍스트는 하이라이트 DrawQuad로
        DrawQuad(*self.rect+((40,40,40,220), (40,40,40,220)))
        x,y,w,h = self.rect
        if self.selectedFile != -1:
            DrawQuad(x,y+30+3+self.lineH*self.selectedFile,w,self.lineH,(0,0,0,220), (0,0,0,220))

        texupx = (3*30.0) / 512.0
        texupy = (8*30.0) / 512.0
        RenderImg(AppSt.gui.tooltex, texupx, texupy, x, y, 30, 30)
        texupx = (3*30.0) / 512.0
        texupy = (9*30.0) / 512.0
        RenderImg(AppSt.gui.tooltex, texupx, texupy, x+30, y, 30, 30)
        texupx = (3*30.0) / 512.0
        texupy = (10*30.0) / 512.0
        RenderImg(AppSt.gui.tooltex, texupx, texupy, x+60, y, 30, 30)
        texupx = (3*30.0) / 512.0
        texupy = (11*30.0) / 512.0
        RenderImg(AppSt.gui.tooltex, texupx, texupy, x+90, y, 30, 30)
        texupx = (3*30.0) / 512.0
        texupy = (12*30.0) / 512.0
        RenderImg(AppSt.gui.tooltex, texupx, texupy, x+120, y, 30, 30)
        texupx = (3*30.0) / 512.0
        texupy = (13*30.0) / 512.0
        RenderImg(AppSt.gui.tooltex, texupx, texupy, x+150, y, 30, 30)

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
            texid = glGenTexturesDebug(1)
            self.surfs += [[pygame.Surface((512,512), flags=SRCALPHA), texid, True]]
        self.surfIdx = 0
        self.texts = []
        EMgrSt.BindTick(self.RegenTex)
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
    def RegenTex(self, t,m,k):
        if AppSt.regenTex:
            for idx in range(len(self.surfs)):
                self.surfs[idx][1] = glGenTexturesDebug(1)
                self.surfs[idx][2] = True
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
        texid = glGenTexturesDebug(1)
        self.surfs = [[pygame.Surface((512,512), flags=SRCALPHA), texid, True]]
        self.texts = []
        EMgrSt.BindTick(self.RegenTex)
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
                texid = glGenTexturesDebug(1)
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

    def RegenTex(self, t,m,k):
        if AppSt.regenTex:
            for idx in range(len(self.surfs)):
                self.surfs[idx][1] = glGenTexturesDebug(1)
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

g_id = 0
ITEM_PICKAXE = GenId()
ITEM_AXE = GenId()
ITEM_SHOVEL = GenId()
ITEM_TORCH = GenId()
ITEM_CHARCOAL = GenId()
ITEM_COAL = GenId()
ITEM_STICK = GenId()
ITEM_CHEST = GenId()
ITEM_GOLD = GenId()
ITEM_SILVER = GenId()
ITEM_IRON = GenId()
ITEM_DIAMOND = GenId()
ITEM_STAIR = GenId()
ITEM_WOODENSTAIR = GenId()
ITEM_SWORD = GenId()
ITEM_SPEAR = GenId()
ITEM_MACE = GenId()
ITEM_KNUCKLE = GenId()
ITEM_SHIELD = GenId()
ITEM_GLOVES = GenId()
ITEM_BOOTS = GenId()
ITEM_GOLDRING = GenId()
ITEM_GOLDNECLACE = GenId()
ITEM_HELM = GenId()
ITEM_ARMOR = GenId()
ITEM_SILVERRING = GenId()
ITEM_SILVERNECLACE = GenId()
ITEM_DIAMONDRING = GenId()
ITEM_DIAMONDNECLACE = GenId()
ITEM_SCROLL = GenId()
ITEM_SENCHANTSCROLL = GenId()
ITEM_GENCHANTSCROLL = GenId()
ITEM_DENCHANTSCROLL = GenId()
ITEM_SKILL = GenId()
ITEM_NONE = 0
TOOL_TEX_COORDS = [
        0,0,
        1,0,
        2,0,
        4,0,
        6,0,
        6,0,
        5,0,
        3,5,
        6,0,
        6,0,
        6,0,
        6,0,
        4,1,
        4,1,
        0,1,
        0,2,
        0,3,
        0,4,
        0,5,
        1,1,
        1,2,
        1,3,
        1,4,
        1,5,
        2,1,
        1,3,
        1,4,
        2,2,
        2,3,
        0,6,
        0,7,
        0,7,
        0,7,
        ]

TYPE_BLOCK = "Block"
TYPE_ITEM = "Item"

"""
무기
방패
모자
몸통
장갑
신발
목걸이
반지
"""
g_id = 0
EQ_RIGHTHAND = GenId()
EQ_LEFTHAND = GenId()
EQ_HEAD = GenId()
EQ_BODY = GenId()
EQ_GLOVES = GenId()
EQ_BOOTS = GenId()
EQ_NECKLACE = GenId()
EQ_RING = GenId()
g_id = 0
WEAPON_ONEHANDED = GenId()
WEAPON_TWOHANDED = GenId()


g_id = 0
TM_TOOL = GenId()
TM_EQ = GenId()
TM_BOX = GenId()
TM_CODE = GenId()
TM_SPAWN = GenId()
TM_CHAR = GenId()
TM_TALK = GenId()
TM_EXCHANGE = GenId()


g_id = 0
QUEST_REQUIREDQUEST = GenId()
QUEST_GATHER = GenId()
QUEST_KILLMOB = GenId()
class MakeTool(object):
    def __init__(self, name, desc, color, needs, returns, textRenderer, textRendererSmall):
        self.name = name
        self.desc = desc
        self.color = color
        self.needs = needs
        self.returns = returns
        self.textidName = [textRenderer.NewTextObject(text, (0,0,0)) for text in self.name.split("\n")]
        self.textidDesc = [textRendererSmall.NewTextObject(text, (0,0,0)) for text in self.desc.split("\n")]
class DigDigGUI(object):
    def __init__(self):
        self.invPos = (SW-306)/2, 430-186-20
        self.qbarPos = (SW-308)/2, 430
        self.makePos = (SW-306)/2, 20-3
        self.invRealPos = (SW-300)/2, 430-186-20+3
        self.qbarRealPos = (SW-300)/2, 430+4
        self.makeRealPos = (SW-300)/2, 20

        self.inventex = texture = glGenTexturesDebug(1)
        self.invenimg = pygame.image.load("./images/digdig/inven.png")
        glBindTexture(GL_TEXTURE_2D, self.inventex)
        teximg = pygame.image.tostring(self.invenimg, "RGBA", 0) 
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)

        self.tooltex = texture = glGenTexturesDebug(1)
        self.toolimg = pygame.image.load("./images/digdig/tools.png")
        glBindTexture(GL_TEXTURE_2D, self.tooltex)
        teximg = pygame.image.tostring(self.toolimg, "RGBA", 0) 
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)


        self.invShown = False
        self.setInvShown = False
        self.toolMode = TM_TOOL # 장비창이냐 제작창이냐 상자창이냐 등등
        self.font = pygame.font.Font("./fonts/Fanwood.ttf", 18)
        self.font2 = pygame.font.Font("./fonts/FanwoodText-Italic.ttf", 13)
        self.font3 = pygame.font.Font("./fonts/Fanwood.ttf", 14)
        
        self.textRenderer = StaticTextRenderer(self.font)
        self.textRendererSmall = StaticTextRenderer(self.font2)
        self.textRendererArea = DynamicTextRenderer(self.font3)
        self.textRendererItemTitle = DynamicTextRenderer(self.font)
        self.textRendererItemSmall = DynamicTextRenderer(self.font2)
        self.msgBox = MsgBox()
        self.talkBox = TalkBox()
        self.talkBox.AddText("aaaa", (68,248,93), (8,29,1))
        def ppp():
            print 'aaaa'
        self.talkBox.AddSelection("aaaa", ppp, (68,248,93), (8,29,1))
        #self.testText = TextArea(0,SH-190,SW,100, 9, 14)
        self.testFile = FileSelector("./scripts")
        self.testEdit = SpawnerGUI((SW-400)/2,(SH-50)/2,400,50,14)
        #self.testText.SetText(u"asdhoihhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhrrㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱrrㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱㄱ가가가가\nadsasd")
        self.prevAreaT = 0
        self.prevDescT = 0
        self.areaDelay = 500
        self.numbers = [self.textRenderer.NewTextObject(`i`, (255,255,255), True, (50,50,50)) for i in range(10)]
        self.numbers += [self.textRenderer.NewTextObject("-", (255,255,255), True, (0,0,0))]
        self.numbersS = [self.textRendererSmall.NewTextObject(`i`, (0,0,0), False, (0,0,0)) for i in range(10)]
        self.numbersS += [self.textRendererSmall.NewTextObject("-", (0,0,0), False, (0,0,0))]



        self.draggingItem = None
        self.dragging = False
        self.dragPos = None
        self.dragCont = None
        self.otherPoints = [] # 땅에 떨굴 때 사용하는 영역
        self.selectedItem = 0
        self.selectedMakeTool = -1
        self.selectedContItem = ITEM_NONE
        self.qbMode2 = False

        EMgrSt.BindTick(self.Tick)
        EMgrSt.BindMotion(self.Motion)
        EMgrSt.BindLDown(self.LDown)
        EMgrSt.BindRDown(self.RDown)
        EMgrSt.BindLUp(self.LUp)
        EMgrSt.BindRUp(self.RUp)
        EMgrSt.BindKeyDown(self.KDown)
        EMgrSt.BindWUp(self.WUp)
        EMgrSt.BindWDn(self.WDn)
        self.ime = CustomIMEModule(self.OnIME)
        self.slotSize = slotSize = 30

        try:
            self.inventory = pickle.load(open("./map/inv.pkl", "r"))
        except:
            self.inventory = [ITEM_NONE for i in range(60)]
        try:
            self.qbar1 = pickle.load(open("./map/qb.pkl", "r"))
        except:
            self.qbar1 = [ITEM_NONE for i in range(10)]

        self.qbar = self.qbar1
        try:
            self.qbar2 = pickle.load(open("./map/qb2.pkl", "r"))
        except:
            self.qbar2 = [ITEM_NONE for i in range(10)]

        try:
            self.boxes = pickle.load(open("./map/chests.pkl", "r"))
        except:
            self.boxes = {}
        try:
            self.codes = pickle.load(open("./map/codes.pkl", "r"))
        except:
            self.codes = {}
        try:
            self.spawns = pickle.load(open("./map/spawns.pkl", "r"))
        except:
            self.spawns = {}
        try:
            self.eqs = pickle.load(open("./map/eqs.pkl", "r"))
        except:
            self.eqs = [ITEM_NONE for i in range(8)]

        self.skills = [ITEM_NONE for i in range(10*6)]


        
        eqTexts = [
        u"RightHand",
        u"LeftHand",
        u"Head",
        u"Body",
        u"Gloves",
        u"Boots",
        u"Necklace",
        u"Ring",]
        self.eqTexts = []
        for t in eqTexts:
            self.eqTexts += [self.textRendererSmall.NewTextObject(t, (0,0,0))]
        

        self.makes1 = self.makes = [ITEM_NONE for i in range(60)]
        self.makes[0] = MakeTool(u"Wood", u"A wood block.", (116,100,46), [(BLOCK_LOG, 1, TYPE_BLOCK)], (BLOCK_WOOD, [], [], 4, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes[1] = MakeTool(u"Stick", u"Multi purpose stick", (255,255,255), [(BLOCK_WOOD, 1, TYPE_BLOCK)], (ITEM_STICK, [], [], 4, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[2] = MakeTool(u"Charcoal", u"A charcoal", (60,60,60), [(BLOCK_LOG, 1, TYPE_BLOCK)], (ITEM_COAL, [], [], 1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[3] = MakeTool(u"Glass", u"A glass", (255,255,255), [(BLOCK_SAND, 4, TYPE_BLOCK), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (BLOCK_GLASS, [], [], 4, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes[4] = MakeTool(u"Stone", u"A stone block", (255,255,255), [(BLOCK_COBBLESTONE, 1, TYPE_BLOCK)], (BLOCK_STONE, [], [], 1, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes[5] = MakeTool(u"Brick", u"A brick block", (255,255,255), [(BLOCK_COBBLESTONE, 1, TYPE_BLOCK)], (BLOCK_BRICK, [], [], 1, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes[6] = MakeTool(u"Wall", u"A wall block", (255,255,255), [(BLOCK_COBBLESTONE, 1, TYPE_BLOCK)], (BLOCK_WALL, [], [], 1, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes[7] = MakeTool(u"TNT", u"Kaboom!\n- Machine -", (255,255,255), [(BLOCK_GRAVEL, 1, TYPE_BLOCK)], (BLOCK_TNT, [], [], 1, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes[13] = MakeTool(u"Wooden stair", u"A wooden stair", (116,100,46), [(BLOCK_WOOD, 1, TYPE_BLOCK)], (ITEM_WOODENSTAIR, [], [], 1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[14] = MakeTool(u"Stair", u"A stair", (30,30,30), [(BLOCK_COBBLESTONE, 1, TYPE_BLOCK)], (ITEM_STAIR, [], [], 1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[15] = MakeTool(u"Slotmachine", u"Select silver, gold, diamond\nin the quickbar and \nright click to opeate.\nIf you use silver\nit will yield 1x of result.\nGold 1.5x, Diamond 2x.\n25% chance to win 2 silver\n15% for golds, 10% for diamonds.\n1% to win 64 silvers,\n64 golds, 64 diamonds.\n0.0001% to win\nten chest full of diamonds", (255,255,255), [(ITEM_DIAMOND, 9, TYPE_ITEM, (80,212,217))], (BLOCK_DIAMONDSLOT, [], [], 1, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes[20] = MakeTool(u"Wooden pickaxe", u"Used to pick stones, ores", (116,100,46), [(BLOCK_WOOD, 5, TYPE_BLOCK)], (ITEM_PICKAXE, [15,20], (BLOCK_IRONORE, BLOCK_SILVERORE, BLOCK_GOLDORE, BLOCK_DIAMONDORE), 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        # returns: 아이템, 체력깎는 정도, 못파는 광물목록
        self.makes[21] = MakeTool(u"Wooden axe", u"Wood cutting wooden axe", (116,100,46), [(BLOCK_WOOD, 5, TYPE_BLOCK)], (ITEM_AXE, [15,20], [], 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[22] = MakeTool(u"Wooden shovel", u"Digs up dirts or sands", (116,100,46), [(BLOCK_WOOD, 5, TYPE_BLOCK)], (ITEM_SHOVEL, [15,20], [], 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[23] = MakeTool(u"Stone pickaxe", u"Used to pick stones, ores", (47,43,43), [(BLOCK_COBBLESTONE, 5, TYPE_BLOCK)], (ITEM_PICKAXE, [20,10], (BLOCK_IRONORE, BLOCK_SILVERORE, BLOCK_GOLDORE, BLOCK_DIAMONDORE), 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        # returns: 아이템, 체력깎는 정도, 못파는 광물목록
        self.makes[24] = MakeTool(u"Stone axe", u"Used to cut trees", (47,43,43), [(BLOCK_COBBLESTONE, 5, TYPE_BLOCK)], (ITEM_AXE, [20,10], [], 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[25] = MakeTool(u"Stone shovel", u"Digs up dirts or sands", (47,43,43), [(BLOCK_COBBLESTONE, 5, TYPE_BLOCK)], (ITEM_SHOVEL, [20,10], [], 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[26] = MakeTool(u"Iron pickaxe", u"Used to pick stones, ores", (107,107,107), [(ITEM_IRON, 5, TYPE_ITEM, (107,107,107))], (ITEM_PICKAXE, [40,5], (BLOCK_IRONORE, BLOCK_SILVERORE, BLOCK_GOLDORE, BLOCK_DIAMONDORE), 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        # returns: 아이템, 체력깎는 정도, 못파는 광물목록
        self.makes[27] = MakeTool(u"Iron axe", u"Used to cut trees", (107,107,107), [(ITEM_IRON, 5, TYPE_ITEM, (107,107,107))], (ITEM_AXE, [40,5], [], 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[28] = MakeTool(u"Iron shovel", u"Digs up dirts or sands", (107,107,107), [(ITEM_IRON, 5, TYPE_ITEM, (107,107,107))], (ITEM_SHOVEL, [40,5], [], 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[32] = MakeTool(u"Diamond pickaxe", u"Used to pick stones, ores", (80,212,217), [(ITEM_DIAMOND, 5, TYPE_ITEM, (80,212,217))], (ITEM_PICKAXE, [100,1], (BLOCK_IRONORE, BLOCK_SILVERORE, BLOCK_GOLDORE, BLOCK_DIAMONDORE), 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        # returns: 아이템, 체력깎는 정도, 못파는 광물목록
        self.makes[33] = MakeTool(u"Diamond axe", u"Used to cut trees", (80,212,217), [(ITEM_DIAMOND, 5, TYPE_ITEM, (80,212,217))], (ITEM_AXE, [100,1], [], 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[34] = MakeTool(u"Diamond shovel", u"Digs up dirts or sands", (80,212,217), [(ITEM_DIAMOND, 5, TYPE_ITEM, (80,212,217))], (ITEM_SHOVEL, [100,1], [], 0, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[35] = MakeTool(u"Silver Enchant Scroll", u"Used to enchant an item\n(Right click on target item\nwhile holding it)", (255,255,255), [(ITEM_SENCHANTSCROLL, 2, TYPE_ITEM, (255,255,255))], (ITEM_SENCHANTSCROLL, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[36] = MakeTool(u"Gold Enchant Scroll", u"Used to enchant an item\n(Right click on target item\nwhile holding it)", (207,207,101), [(ITEM_GENCHANTSCROLL, 2, TYPE_ITEM, (207,207,101))], (ITEM_GENCHANTSCROLL, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[37] = MakeTool(u"Diamond\nEnchant Scroll", u"Used to enchant an item\n(Right click on target item\nwhile holding it)", (80,212,217), [(ITEM_DENCHANTSCROLL, 2, TYPE_ITEM, (80,212,217))], (ITEM_DENCHANTSCROLL, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)

        self.makes[11] = MakeTool(u"Torch", u"Lights up dark places", (255,255,255), [(ITEM_STICK, 1, TYPE_ITEM, (255,255,255)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_TORCH, [], [], 1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[12] = MakeTool(u"Chest", u"Can hold items and blocks", (255,255,255), [(BLOCK_WOOD, 8, TYPE_BLOCK)], (ITEM_CHEST, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[30] = MakeTool(u"Code", u"Runs python code.\nUsed to launch commands\nor spawn an object\n(Put scripts in scripts directory)", (255,255,255), [(ITEM_GOLD, 4, TYPE_ITEM, (207,207,101)), (ITEM_SILVER, 4, TYPE_ITEM, (201,201,201))], (BLOCK_CODE, [], [], 1, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes[31] = MakeTool(u"Spawner", u"Spawning spot\n- Machine -", (255,255,255), [(ITEM_GOLD, 4, TYPE_ITEM, (207,207,101)), (ITEM_SILVER, 4, TYPE_ITEM, (201,201,201))], (BLOCK_SPAWNER, [], [], 1, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes[40] = MakeTool(u"Sword", u"A sword\n- Weapon -", (107,107,107), [(ITEM_IRON, 8, TYPE_ITEM, (107,107,107)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_SWORD, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[41] = MakeTool(u"Spear", u"A spear\n- Two Handed Weapon -", (107,107,107), [(ITEM_IRON, 16, TYPE_ITEM, (107,107,107)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_SPEAR, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[42] = MakeTool(u"Mace", u"A mace\n- Weapon -", (107,107,107), [(ITEM_IRON, 8, TYPE_ITEM, (107,107,107)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_MACE, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[43] = MakeTool(u"Brass Knuckle", u"A brass knuckle\n- Weapon -", (107,107,107), [(ITEM_IRON, 8, TYPE_ITEM, (107,107,107)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_KNUCKLE, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[44] = MakeTool(u"Shield", u"A shield\n- Shield -", (107,107,107), [(ITEM_IRON, 16, TYPE_ITEM, (107,107,107)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_SHIELD, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[45] = MakeTool(u"Helm", u"A Helm\n- Helm -", (107,107,107), [(ITEM_IRON, 8, TYPE_ITEM, (107,107,107)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_HELM, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[46] = MakeTool(u"Armor", u"A body armor\n- Armor -", (107,107,107), [(ITEM_IRON, 16, TYPE_ITEM, (107,107,107)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_ARMOR, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[47] = MakeTool(u"Gloves", u"A pair of gloves\n- Gloves -", (107,107,107), [(ITEM_IRON, 8, TYPE_ITEM, (107,107,107)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_GLOVES, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[48] = MakeTool(u"Boots", u"A pair of boots\n- Boots -", (107,107,107), [(ITEM_IRON, 8, TYPE_ITEM, (107,107,107)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_BOOTS, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[50] = MakeTool(u"Silver Ring", u"A silver ring\n- Ring -", (201,201,201), [(ITEM_SILVER, 1, TYPE_ITEM, (201,201,201)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_SILVERRING, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[51] = MakeTool(u"Silver Necklace", u"A silver necklace\n- Necklace -", (201,201,201), [(ITEM_SILVER, 1, TYPE_ITEM, (201,201,201)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_SILVERNECLACE, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[52] = MakeTool(u"Gold Ring", u"A gold ring\n- Ring -", (207,207,101), [(ITEM_GOLD, 1, TYPE_ITEM, (207,207,101)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_GOLDRING, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[53] = MakeTool(u"Gold Necklace", u"A gold necklace\n- Necklace -", (207,207,101), [(ITEM_GOLD, 1, TYPE_ITEM, (207,207,101)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_GOLDNECLACE, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[54] = MakeTool(u"Diamond Ring", u"A diamond ring\n- Ring -", (80,212,217), [(ITEM_DIAMOND, 1, TYPE_ITEM, (80,212,217)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_DIAMONDRING, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[55] = MakeTool(u"Diamond Necklace", u"A diamond necklace\n- Necklace -", (80,212,217), [(ITEM_DIAMOND, 1, TYPE_ITEM, (80,212,217)), (ITEM_COAL, 1, TYPE_ITEM, (60,60,60))], (ITEM_DIAMONDNECLACE, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[56] = MakeTool(u"Blank Scroll", u"Used to make enchant scrolls", (255,255,255), [(BLOCK_WOOD, 1, TYPE_BLOCK)], (ITEM_SCROLL, [], [], 64, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[57] = MakeTool(u"Silver Enchant Scroll", u"Used to enchant an item\n(Right click on target item\nwhile holding it)", (255,255,255), [(ITEM_SILVER, 5, TYPE_ITEM, (201,201,201)), (ITEM_SCROLL, 1, TYPE_ITEM, (201,201,201))], (ITEM_SENCHANTSCROLL, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[58] = MakeTool(u"Gold Enchant Scroll", u"Used to enchant an item\n(Right click on target item\nwhile holding it)", (207,207,101), [(ITEM_GOLD, 5, TYPE_ITEM, (207,207,101)), (ITEM_SCROLL, 1, TYPE_ITEM, (201,201,201))], (ITEM_GENCHANTSCROLL, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes[59] = MakeTool(u"Diamond\nEnchant Scroll", u"Used to enchant an item\n(Right click on target item\nwhile holding it)", (80,212,217), [(ITEM_DIAMOND, 5, TYPE_ITEM, (80,212,217)), (ITEM_SCROLL, 1, TYPE_ITEM, (201,201,201))], (ITEM_DENCHANTSCROLL, [], [], -1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)

        self.makes2 = [ITEM_NONE for i in range(60)] # 환전
        self.makes3 = [ITEM_NONE for i in range(60)] # 컬러블럭. 128컬러만 지원. 인덱스를 가지고 있을 뿐이다. 그 중 60컬러
        self.makes4 = [ITEM_NONE for i in range(60)] # 컬러블럭. 또다른 60컬러. 120컬러까지만 하자.
        # 실제 구현은 음.....실제 컬러 버퍼 자체도 128컬러만 지원하도록 하자. 청크 버퍼와 똑같은 컬러버퍼를 둔다. 컬러의 인덱스만 저장하고 있다.
        # 120개의 컬러를 어떻게 할까? 
        # GIMP에서 가장 튀어보이는 컬러 11개를 골라 10단계로 나누고, 나머지 1개의 10단계를 그레이스케일.
        # 컬러블럭은 렌더링도 다르게 해야한다.
        #
        # HSV로 S 3단계, V3단계를 하고
        # H 11단계
        # 나머지는 그레이스케일 10단계로 한다.
        # 그냥 360을 12로 나눠서 쓰고
        # S,V는 25부터 100을 3으로 나눠저 25, 50, 75, 25, 50, 75, (100, 100)
        # 이렇게 한 후에 RGB로 변환한 표를 만들자.
        #
        # 그래도 되고.... 그냥 RGB의 조합을 
        # R,G,B를 각각 5단계로 나누면 125컬러가 나오는데 여기서 5컬러만 빼면 된다.
        # 뭘빼지? R,G,B가 약한 51,0,0 0,51,0  0,0,51 빼고 51,51,0, 0,51,51 51,0,51 빼면 될 듯. 119컬러! 검은색인지 빨간색인지 구별이 안감 ㅇㅇ?
        # 51대신 153? 102를 빼도록 하자. 음....
        # 으 다 좋은데?;;; 51을 빼자. 아니. 255가 들어가는 게 제일 별로다. 255가 들어가는 걸 빼자.

        self.colors = [
                ]
        for b in range(5):
            for g in range(5):
                for r in range(5):
                    if r == 0 and b == 0 and g == 0:
                        self.colors += [[r*51, g*51, b*51]]
                    elif r == 4 and b == 4 and g == 4:
                        self.colors += [[r*51, g*51, b*51]]
                    elif r in [4,0] and b in [4,0] and g in [4,0]:
                        pass
                    else:
                        self.colors += [[r*51, g*51, b*51]]








        self.recipeTextID = self.textRenderer.NewTextObject(u"Recipe:", (0,0,0))
        self.enchantTextID = self.textRendererSmall.NewTextObject(u"Enchant Count", (0,0,0))
        self.enchantSlashTextID = self.textRenderer.NewTextObject(u"/", (0,0,0))
        self.charTabID = self.textRendererSmall.NewTextObject(u"Char", (0,0,0))
        self.strID = self.textRendererSmall.NewTextObject(u"Str:", (0,0,0))
        self.dexID = self.textRendererSmall.NewTextObject(u"Dex:", (0,0,0))
        self.intID = self.textRendererSmall.NewTextObject(u"Int:", (0,0,0))
        self.skillTabID = self.textRendererSmall.NewTextObject(u"Skills", (0,0,0))
        self.swordID = self.textRendererSmall.NewTextObject(u"Sword:", (0,0,0))
        self.maceID = self.textRendererSmall.NewTextObject(u"Mace:", (0,0,0))
        self.spearID = self.textRendererSmall.NewTextObject(u"Spear:", (0,0,0))
        self.knuckleID = self.textRendererSmall.NewTextObject(u"Knuckle:", (0,0,0))
        self.armorID = self.textRendererSmall.NewTextObject(u"Armor:", (0,0,0))
        self.magicID = self.textRendererSmall.NewTextObject(u"Magic:", (0,0,0))
        self.atkID = self.textRendererSmall.NewTextObject(u"Melee:", (0,0,0))
        self.dfnID = self.textRendererSmall.NewTextObject(u"Defense:", (0,0,0))
        self.patkID = self.textRendererSmall.NewTextObject(u"Poison:", (0,0,0))
        self.iatkID = self.textRendererSmall.NewTextObject(u"Ice:", (0,0,0))
        self.fatkID = self.textRendererSmall.NewTextObject(u"Fire:", (0,0,0))
        self.eatkID = self.textRendererSmall.NewTextObject(u"Electric:", (0,0,0))
        self.resID = self.textRendererSmall.NewTextObject(u"- Resist -", (0,0,0))

        
        # 컬러를 저장해야한다. ok
        # invModeIdx = 0
        # modeIdx += 1
        # if modeIdx >= 4
            # modeIDx = 0
        # makes3을 만들 때에는 컬러를 잘 넣고, toolStrength있는데다가 컬러 인덱스를 넣어 저장하게 한다.
        # DoMake를 할 때에는 BLOCK_COLOR인지를 보고 컬러라는 속성을 아이템에 넣는다.
        self.invModeIdx = 0

        for i in range(60):
            self.makes3[i] = MakeTool(u"Color Block", u"A color block", tuple(self.colors[i]), [(ITEM_SILVER, 1, TYPE_ITEM, (201,201,201))], (BLOCK_COLOR, [i], [], 1, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        for i in range(59):
            self.makes4[i] = MakeTool(u"Color Block", u"A color block", tuple(self.colors[i+60]), [(ITEM_SILVER, 1, TYPE_ITEM, (201,201,201))], (BLOCK_COLOR, [i+60], [], 1, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)


        self.makes2[0] = MakeTool(u"Buy silvers", u"Buy 3 silvers with 2 golds", (201,201,201), [(ITEM_GOLD, 2, TYPE_ITEM, (207,207,101))], (ITEM_SILVER, [], [], 3, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes2[1] = MakeTool(u"Buy silvers", u"Buy 2 silvers with 1 diamond", (201,201,201), [(ITEM_DIAMOND, 1, TYPE_ITEM,  (80,212,217))], (ITEM_SILVER, [], [], 2, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes2[2] = MakeTool(u"Buy golds", u"Buy 2 golds with 3 silvers",(207,207,101), [(ITEM_SILVER, 3, TYPE_ITEM,  (201,201,201))], (ITEM_GOLD, [], [], 2, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes2[3] = MakeTool(u"Buy golds", u"Buy 4 golds with 3 diamonds",(207,207,101), [(ITEM_DIAMOND, 3, TYPE_ITEM,  (80,212,217))], (ITEM_GOLD, [], [], 4, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes2[4] = MakeTool(u"Buy diamonds", u"Buy 1 diamond with 2 silvers",(80,212,217), [(ITEM_SILVER, 2, TYPE_ITEM,  (201,201,201))], (ITEM_DIAMOND, [], [], 1, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes2[5] = MakeTool(u"Buy diamonds", u"Buy 3 diamond with 4 golds",(80,212,217), [(ITEM_GOLD, 4, TYPE_ITEM,  (207,207,101))], (ITEM_DIAMOND, [], [], 3, TYPE_ITEM), self.textRenderer, self.textRendererSmall)
        self.makes2[6] = MakeTool(u"Buy cobblestones", u"Buy 64 cobblestones\nfor 16 silver",(80,212,217), [(ITEM_SILVER, 16, TYPE_ITEM,  (201,201,201))], (BLOCK_COBBLESTONE, [], [], 64, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes2[7] = MakeTool(u"Buy woods", u"Buy 64 woords\nfor 16 silver",(80,212,217), [(ITEM_SILVER, 16, TYPE_ITEM,  (201,201,201))], (BLOCK_WOOD, [], [], 64, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes2[8] = MakeTool(u"Buy glasses", u"Buy 64 glasses\nfor 32 silver",(80,212,217), [(ITEM_SILVER, 32, TYPE_ITEM,  (201,201,201))], (BLOCK_GLASS, [], [], 64, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes2[9] = MakeTool(u"Buy grasses", u"Buy 64 grasses\nfor 16 silver",(80,212,217), [(ITEM_SILVER, 16, TYPE_ITEM,  (201,201,201))], (BLOCK_GRASS, [], [], 64, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)
        self.makes2[10] = MakeTool(u"Buy dirts", u"Buy 64 dirts\nfor 16 silver",(80,212,217), [(ITEM_SILVER, 16, TYPE_ITEM,  (201,201,201))], (BLOCK_DIRT, [], [], 64, TYPE_BLOCK), self.textRenderer, self.textRendererSmall)

        self.invSlotPos = []
        invX, invY = self.invRealPos
        for y in range(6):
            for x in range(10):
                self.invSlotPos += [(invX+x*30, invY+y*30)]

        self.qbSlotPos = []
        invX, invY = self.qbarRealPos
        y=0
        for x in range(10):
            self.qbSlotPos += [(invX+x*30, invY+y*30)]

        self.makeSlotPos = []
        invX, invY = self.makeRealPos
        for y in range(6):
            for x in range(10):
                self.makeSlotPos += [(invX+x*30, invY+y*30)]

        self.eqSlotPos = []
        self.charTab = True

        """
        무기
        방패
        모자
        몸통
        장갑
        신발
        목걸이
        반지

        0, 200

        26,228
        26,262
        26,296
        26,330

        250,228
        250,262
        250,296
        250,330

        """
        for i in range(4):
            self.eqSlotPos += [(self.makeRealPos[0]+23, self.makeRealPos[1]+25+i*34)]
        for i in range(4):
            self.eqSlotPos += [(self.makeRealPos[0]+247, self.makeRealPos[1]+25+i*34)]

        """
        self.PutItemInInventory(Item(ITEM_GOLD, 64, color = (207,207,101), stackable=True))
        self.PutItemInInventory(Item(ITEM_SILVER, 64, color = (201,201,201), stackable=True))
        self.PutItemInInventory(Block(BLOCK_CODE, 64))
        self.PutItemInInventory(Block(BLOCK_CPU, 64))
        self.PutItemInInventory(Block(BLOCK_ENERGY, 64))
        self.PutItemInInventory(Item(ITEM_IRON, 64, color = (107,107,107), stackable=True))
        self.PutItemInInventory(Item(ITEM_IRON, 64, color = (107,107,107), stackable=True))
        self.PutItemInInventory(Item(ITEM_GOLD, 64, color = (207,207,101), stackable=True))
        self.PutItemInInventory(Item(ITEM_SILVER, 64, color = (201,201,201), stackable=True))
        self.PutItemInInventory(Item(ITEM_DIAMOND, 64, color = (80,212,217), stackable=True))
        self.PutItemInInventory(Block(BLOCK_LOG, 64))
        self.PutItemInInventory(Item(ITEM_IRON, 64, color = (107,107,107), stackable=True))
        self.PutItemInInventory(Item(ITEM_GOLD, 64, color = (207,207,101), stackable=True))
        self.PutItemInInventory(Item(ITEM_SILVER, 64, color = (201,201,201), stackable=True))
        self.PutItemInInventory(Item(ITEM_DIAMOND, 64, color = (80,212,217), stackable=True))
        """
        """
        self.PutItemInInventory(Item(ITEM_CHEST, 1, color=(255,255,255), stackable=False, inv=[Item(ITEM_DIAMOND, 64, color = (80,212,217), stackable=True) for i in range(60)]))
        self.PutItemInInventory(Item(ITEM_CHEST, 1, color=(255,255,255), stackable=False, inv=[Item(ITEM_GOLD, 64, color = (207,207,80), stackable=True) for i in range(60)]))
        self.PutItemInInventory(Item(ITEM_CHEST, 1, color=(255,255,255), stackable=False, inv=[Item(ITEM_SILVER, 64, color = (201,201,201), stackable=True) for i in range(60)]))
        """
        #self.PutItemInInventory(Block(BLOCK_COBBLESTONE, 64))
        #self.PutItemInInventory(Block(BLOCK_DIRT, 64))


        # 여기서 텍스쳐를 생성한다.
    def OnIME(self, text):
        pass
    def CanPutItemInInventory(self, item):
        for invItem in self.qbar+self.inventory:
            if not invItem:
                continue
            if invItem.type_ == item.type_ and invItem.count+item.count < invItem.maxLen and invItem.name == item.name and invItem.stackable:
                return True

        idx = 0
        for item_ in self.qbar[:]:
            if item_ == ITEM_NONE:
                return True
            idx += 1

        idx = 0
        for item_ in self.inventory[:]:
            if item_ == ITEM_NONE:
                return True
            idx += 1
        return False

    def PutItemInInventory(self, item):
        for invItem in self.qbar+self.inventory:
            if invItem == ITEM_NONE:
                continue
            if invItem.type_ == item.type_ and invItem.count+item.count <= invItem.maxLen and invItem.name == item.name and invItem.stackable and invItem.colorIdx == item.colorIdx:
                invItem.count += item.count
                return True

        idx = 0
        for item_ in self.qbar[:]:
            if item_ == ITEM_NONE:
                self.qbar[idx] = item
                return True
            idx += 1

        idx = 0
        for item_ in self.inventory[:]:
            if item_ == ITEM_NONE:
                self.inventory[idx] = item
                return True
            idx += 1
        return False
    def ShowInventory(self, show):
        # 끌 떄: 아이템을 들고 있는 경우 제자리에 돌려놓음 XXX:
        # 아닌경우 걍 끔
        #
        #
        # 이제 아이템 반으로 나누기
        # 아이템 반 나눈 거 드랍하기
        # 아이템 합치기
        # 아이템 들고있던거 제자리에 못넣을 경우 빈자리에 넣거나 빈공간에 합치기
        if show == False:
            pygame.mouse.set_visible(False)
            pygame.mouse.set_pos(SW/2, SH/2)
        else:
            pygame.mouse.set_visible(True)
        if show == False and self.dragging:
            self.dragging = False
            x,y = self.dragPos
            if not self.dragCont[y*10+x]:
                self.dragCont[y*10+x] = self.draggingItem
            else:
                if self.CanPutItemInInventory(self.draggingItem):
                    self.PutItemInInventory(self.draggingItem)
                else:
                    AppSt.DropItem(self.draggingItem)

        self.setInvShown = show

    def Tick(self, t, m, k):
        pass
    def Motion(self, t, m, k):
        self.selectedMakeTool = -1
        if self.invShown:
            if self.toolMode == TM_TOOL:
                idx = 0
                foundIdx = -1
                for pos in self.makeSlotPos:
                    x,y = pos
                    if InRect(x,y,30,30,m.x,m.y):
                        foundIdx = idx
                        break
                    idx += 1

                if foundIdx != -1:
                    x = foundIdx % 10
                    y = (foundIdx - x) / 10
                    self.selectedMakeTool = foundIdx


            idx = 0
            foundIdx = -1
            self.selectedContItem = ITEM_NONE
            for pos in self.invSlotPos:
                x,y = pos
                if InRect(x,y,30,30,m.x,m.y):
                    foundIdx = idx
                    break
                idx += 1
            if foundIdx != -1:
                self.selectedContItem = self.inventory[foundIdx]

            idx = 0
            foundIdx = -1
            for pos in self.qbSlotPos:
                x,y = pos
                if InRect(x,y,30,30,m.x,m.y):
                    foundIdx = idx
                    break
                idx += 1

            if foundIdx != -1:
                self.selectedContItem = self.qbar[foundIdx]

            if self.toolMode == TM_BOX:
                idx = 0
                foundIdx = -1
                for pos in self.makeSlotPos:
                    x,y = pos
                    if InRect(x,y,30,30,m.x,m.y):
                        foundIdx = idx
                        break
                    idx += 1

                if foundIdx != -1:
                    self.selectedContItem = self.selectedBox[foundIdx]
            elif self.toolMode == TM_EQ:
                idx = 0
                foundIdx = -1
                for pos in self.eqSlotPos:
                    x,y = pos
                    if InRect(x,y,30,30,m.x,m.y):
                        foundIdx = idx
                        break
                    idx += 1

                if foundIdx != -1:
                    self.selectedContItem = self.eqs[foundIdx]

            elif self.toolMode == TM_CHAR and not self.charTab:
                idx = 0
                foundIdx = -1
                for pos in self.makeSlotPos:
                    x,y = pos
                    if InRect(x,y,30,30,m.x,m.y):
                        foundIdx = idx
                        break
                    idx += 1

                if foundIdx != -1:
                    skills = self.skills
                    
                    if idx < len(skills):
                        self.selectedContItem = skills[idx]

    def LDown(self, t, m, k):
        if self.toolMode == TM_CHAR:
            pass # XXX:#
        if self.toolMode in [TM_BOX, TM_TOOL, TM_EQ, TM_CHAR]:
            self.OnDown(t,m,k,False)


 
    def DoCont(self,x,y,cont, rmb = False):
        if self.dragging:
            #drop or swap
            # real crazy nested if elses
            def Drop():
                self.dragging = False
                cont[y*10+x] = self.draggingItem
                self.draggingItem = None
                self.dragPos = None
                self.dragCont = None
            def Swap():
                if self.draggingItem.type_ == cont[y*10+x].type_ and self.draggingItem.name == cont[y*10+x].name and self.draggingItem.stackable and self.draggingItem.colorIdx == cont[y*10+x].colorIdx:
                    if self.draggingItem.count+cont[y*10+x].count <= cont[y*10+x].maxLen:
                        cont[y*10+x].count += self.draggingItem.count 
                        self.dragging = False
                    else:
                        temp = self.draggingItem.count + cont[y*10+x].count
                        cont[y*10+x].count = 64
                        self.draggingItem.count = temp-64
                else:
                    self.draggingItem, cont[y*10+x] = cont[y*10+x], self.draggingItem
                # swap or combine

            if cont[y*10+x]:
                if not rmb:
                    Swap()
                else:
                    if self.draggingItem.type_ in [ITEM_SENCHANTSCROLL, ITEM_GENCHANTSCROLL, ITEM_DENCHANTSCROLL] and cont[y*10+x].type_ in [ITEM_SWORD, ITEM_SPEAR, ITEM_MACE, ITEM_KNUCKLE, ITEM_SHIELD,ITEM_HELM,ITEM_ARMOR,ITEM_BOOTS,ITEM_GLOVES,ITEM_SILVERNECLACE, ITEM_GOLDNECLACE, ITEM_DIAMONDNECLACE,ITEM_SILVERRING, ITEM_GOLDRING, ITEM_DIAMONDRING]:
                        item = cont[y*10+x]
                        if item.enchantCount < item.maxEnchant:
                            self.ApplyEnchantScroll(cont[y*10+x], self.draggingItem)
                            self.dragging = False
                            self.draggingItem = None
                            self.dragPos = None
                            self.dragCont = None
                    elif self.draggingItem.type_ == cont[y*10+x].type_ and self.draggingItem.name == cont[y*10+x].name and self.draggingItem.stackable and self.draggingItem.colorIdx == cont[y*10+x].colorIdx:
                        if self.draggingItem.count > 1:
                            half = self.draggingItem.count / 2
                            self.draggingItem.count -= half

                            if half+cont[y*10+x].count <= cont[y*10+x].maxLen:
                                cont[y*10+x].count += half
                            else:
                                temp = half + cont[y*10+x].count
                                cont[y*10+x].count = 64
                                self.draggingItem.count += temp-64
                        else:
                            Swap()
                    else:
                        Swap()
            else:
                if not rmb:
                    Drop()
                else:
                    if self.draggingItem.stackable and self.draggingItem.count > 1:
                        half = self.draggingItem.count / 2
                        self.draggingItem.count -= half
                        if self.draggingItem.name == TYPE_BLOCK:
                            cont[y*10+x] = Block(self.draggingItem.type_, half)
                        elif self.draggingItem.name == TYPE_ITEM:
                            cont[y*10+x] = Item(self.draggingItem.type_, half, color=self.draggingItem.color, stackable=True)
                    else:
                        Drop()
        else:
            # pick
            if cont[y*10+x]:
                def Pick():
                    self.dragging = True
                    self.draggingItem = cont[y*10+x]
                    self.dragPos = (x,y)
                    self.dragCont = cont
                    cont[y*10+x] = ITEM_NONE

                if not rmb:
                    Pick()
                else:
                    if cont[y*10+x].count > 1 and cont[y*10+x].stackable:
                        half = cont[y*10+x].count / 2
                        cont[y*10+x].count -= half
                        self.dragging = True
                        item = cont[y*10+x]
                        if item.name == TYPE_BLOCK:
                            self.draggingItem = Block(cont[y*10+x].type_, half)
                        elif item.name == TYPE_ITEM:
                            self.draggingItem = Item(item.type_, half, color=item.color, stackable=True)

                        self.dragPos = (x,y)
                        self.dragCont = cont
                    else:
                        Pick()

            # start dragging
 
    def RDown(self, t, m, k):
        if self.toolMode in [TM_BOX, TM_TOOL, TM_EQ]:
            self.OnDown(t,m,k,True)


    def ApplyEnchantScroll(self, item, scroll):
        if not item.element:
            item.element = FightingElements("Item", (0,0,0), {})
        item.element.ApplyEnchantScroll(item.type_, scroll)
        item.enchantCount += 1
    def DoEquip(self, idx):
        # dragging이 있으면 그걸 입을수있는지 검사
        # 없으면 언이큅
        """
        u"RightHand",
        u"LeftHand",
        u"Head",
        u"Body",
        u"Gloves",
        u"Boots",
        u"Necklace",
        u"Ring",]
        """

        if self.draggingItem and self.draggingItem.name == "Item" and self.draggingItem.type_ in [ITEM_SWORD, ITEM_SPEAR, ITEM_MACE, ITEM_KNUCKLE, ITEM_SHIELD, ITEM_GLOVES, ITEM_BOOTS, ITEM_GOLDRING, ITEM_GOLDNECLACE, ITEM_HELM, ITEM_ARMOR, ITEM_SILVERRING, ITEM_SILVERNECLACE, ITEM_DIAMONDRING, ITEM_DIAMONDNECLACE]:
            item = self.draggingItem
            def Drop():
                self.dragging = False
                self.eqs[idx] = self.draggingItem
                self.draggingItem = None
                self.dragPos = None
                self.dragCont = None
            def Swap():
                self.draggingItem, self.eqs[idx] = self.eqs[idx], self.draggingItem

            idxToTypes = [
                    [ITEM_SWORD, ITEM_SPEAR, ITEM_MACE, ITEM_KNUCKLE, ITEM_SHIELD],
                    [ITEM_SWORD, ITEM_SPEAR, ITEM_MACE, ITEM_KNUCKLE, ITEM_SHIELD],
                    [ITEM_HELM],
                    [ITEM_ARMOR],
                    [ITEM_GLOVES],
                    [ITEM_BOOTS],
                    [ITEM_SILVERNECLACE, ITEM_GOLDNECLACE, ITEM_DIAMONDNECLACE],
                    [ITEM_SILVERRING, ITEM_GOLDRING, ITEM_DIAMONDRING]
                    ]
            idx2 = 0
            for types in idxToTypes:
                if idx == idx2:
                    if item.type_ in types:
                        if not self.eqs[1] and self.eqs[0] and idx2 == 1 and self.eqs[0].type_ == ITEM_SPEAR:
                            self.draggingItem, self.eqs[idx2] = self.eqs[0], self.draggingItem
                            self.eqs[0] = ITEM_NONE
                        elif not self.eqs[0] and self.eqs[1] and idx2 == 0 and self.eqs[1].type_ == ITEM_SPEAR:
                            self.draggingItem, self.eqs[idx2] = self.eqs[1], self.draggingItem
                            self.eqs[1] = ITEM_NONE
                        elif not self.eqs[1] and self.eqs[0] and idx2 == 1 and self.draggingItem.type_ != self.eqs[0].type_ and not ((self.eqs[0].type_ != ITEM_SHIELD and self.draggingItem.type_ == ITEM_SHIELD) or (self.eqs[0].type_ == ITEM_SHIELD and self.draggingItem.type_ != ITEM_SHIELD)):
                            self.draggingItem, self.eqs[idx2] = self.eqs[0], self.draggingItem
                            self.eqs[0] = ITEM_NONE
                        elif not self.eqs[0] and self.eqs[1] and idx2 == 0 and self.draggingItem.type_ != self.eqs[1].type_ and not ((self.eqs[1].type_ != ITEM_SHIELD and self.draggingItem.type_ == ITEM_SHIELD) or (self.eqs[1].type_ == ITEM_SHIELD and self.draggingItem.type_ != ITEM_SHIELD)):
                            self.draggingItem, self.eqs[idx2] = self.eqs[1], self.draggingItem
                            self.eqs[1] = ITEM_NONE
                        elif self.eqs[idx]:
                            Swap()
                        else:
                            Drop()
                    break
                idx2 += 1
        elif not self.dragging and self.eqs[idx]:
            def Pick():
                self.dragging = True
                self.draggingItem = self.eqs[idx]
                self.dragPos = (idx,0)
                self.dragCont = self.eqs
                self.eqs[idx] = ITEM_NONE
            Pick()

    def OnDown(self, t, m, k, rmb=False):
        if self.invShown:
            idx = 0
            foundIdx = -1
            for pos in self.invSlotPos:
                x,y = pos
                if InRect(x,y,30,30,m.x,m.y):
                    foundIdx = idx
                    break
                idx += 1
            if foundIdx != -1:
                x = foundIdx % 10
                y = (foundIdx - x) / 10
                if not self.dragging:
                    self.DoCont(x,y, self.inventory, rmb)
                elif self.dragging and self.draggingItem.name != "Skill":
                    self.DoCont(x,y, self.inventory, rmb)

            idx = 0
            foundIdx = -1
            for pos in self.qbSlotPos:
                x,y = pos
                if InRect(x,y,30,30,m.x,m.y):
                    foundIdx = idx
                    break
                idx += 1

            if foundIdx != -1:
                x = foundIdx % 10
                y = (foundIdx - x) / 10
                self.DoCont(x,y, self.qbar, rmb)

            if self.toolMode == TM_TOOL:
                idx = 0
                foundIdx = -1
                for pos in self.makeSlotPos:
                    x,y = pos
                    if InRect(x,y,30,30,m.x,m.y):
                        foundIdx = idx
                        break
                    idx += 1

                if foundIdx != -1:
                    x = foundIdx % 10
                    y = (foundIdx - x) / 10
                    self.DoMake(foundIdx)


            elif self.toolMode == TM_BOX:
                idx = 0
                foundIdx = -1
                for pos in self.makeSlotPos:
                    x,y = pos
                    if InRect(x,y,30,30,m.x,m.y):
                        foundIdx = idx
                        break
                    idx += 1

                if foundIdx != -1:
                    x = foundIdx % 10
                    y = (foundIdx - x) / 10

                    if self.dragging and self.draggingItem.name != "Skill":
                        self.DoCont(x,y,self.selectedBox, rmb)
                    elif not self.dragging:
                        self.DoCont(x,y,self.selectedBox, rmb)

            elif self.toolMode == TM_EQ:
                idx = 0
                foundIdx = -1
                for pos in self.eqSlotPos:
                    x,y = pos
                    if InRect(x,y,30,30,m.x,m.y):
                        foundIdx = idx
                        break
                    idx += 1

                if foundIdx != -1:
                    x = foundIdx % 10
                    y = (foundIdx - x) / 10
                    self.DoEquip(foundIdx)

            elif self.toolMode == TM_CHAR and not self.charTab:
                idx = 0
                foundIdx = -1
                for pos in self.makeSlotPos:
                    x,y = pos
                    if InRect(x,y,30,30,m.x,m.y):
                        foundIdx = idx
                        break
                    idx += 1

                if foundIdx != -1:
                    x = foundIdx % 10
                    y = (foundIdx - x) / 10
                    if self.dragging and self.draggingItem.name == "Skill":
                        self.DoCont(x,y,self.skills, rmb)
                    elif not self.dragging:
                        self.DoCont(x,y,self.skills, rmb)


    def GenElement(self, gentype): # 스킬 레벨이 높을수록 보너스도 더 높은게 나온다.
        # 최대 현재 스킬 레벨과 같은 수준의 인챈트 스크롤이 나올 수 있다. 간단함
        # 음 스킬이 더럽게 안오르니까 몹을 캐릭터의 수준에 맞춰서 생성하고 그러자....
        # 굴곡이 좀 있어서 한 번 생성된 몹 중 강한놈 못잡으면 나중에 잡을 수 있도록 하고 강한 몹이라면 더 좋은 걸 줘야겠지....
        # 울온엔 장식용 아이템이 참 많다. 심즈처럼 많지는 않지만 그정도 수준이다. 음...........
        #
        # 아 여러 지역을 두고 그 지역에는 어떤 특정한 몹이 나오도록 뭐 그렇게 해볼까.
        # 무한 맵이라고 해서 맵을 넓게 쓸 필요가 없음;
        # 미니맵이나 전체지도 만들어야함 XXX:


        # 나머지는 +1~5
        # 1/10확률로 +10
        # 1/100 확률로 +20 -- 보통 이걸 뽑을 듯.
        # 1/1000 확률로 +100 -- 대박, 보스급 몹이 나온다. 일정 확률로 +1000 스크롤을 드랍한다 - 한 100마리 잡으면 나오게 한다. 이 쯤 되면 뽑기가 더 쉬울 정도로 돈을 벌테니까. 실버 골드 다이아 5000개 정도는 껌으로 얻게 한다.
        # 1/10000 확률로 +1000 -- 나오긴 하나. 특이한 몹이 나온다. 일정 확률로 +5000 스크롤을 드랍한다. 한 1000마리 잡으면 나오게 한다.
        # 1/100000 확률로 +5000 -- 이게 나오면 진짜 대박.. 숨겨진 최종보스가 나온다.
        def GenPlus():
            rand = random.randint(0,100000)
            if rand == 50000:
                return 5000
            elif 60000 <= rand <= 70000:
                return 10
            elif 70001 <= rand <= 71000:
                return 20
            elif 80001 <= rand <= 80100:
                return 100
            elif 90001 <= rand <= 90010:
                return 1000
            else:
                return random.randint(1,5)
        if gentype == ITEM_SENCHANTSCROLL:
            skills = [skill.skill for skill in AppSt.entity.magics.itervalues()]
            skills += [skill.skill for skill in AppSt.entity.swordSkills.itervalues()]
            skills += [skill.skill for skill in AppSt.entity.maceSkills.itervalues()]
            skills += [skill.skill for skill in AppSt.entity.spearSkills.itervalues()]
            skills += [skill.skill for skill in AppSt.entity.knuckleSkills.itervalues()]
            bonusSkills = {}
            plus = GenPlus()
            for skill in skills:
                bonusSkills[skill.name] = plus

            selected = [bonusSkills.keys()[random.randint(0, len(bonusSkills.values())-1)] for i in range(3)]
            params = {}
            for selectedKey in selected:
                if selectedKey in params:
                    params[selectedKey] += bonusSkills[selectedKey]
                else:
                    params[selectedKey] = bonusSkills[selectedKey]
            element = FightingElements("Silver", (0,0,0), params) # 여기서 아이템을 제작하는 코드가 다있다. XXX:
        if gentype == ITEM_GENCHANTSCROLL:
            plus = GenPlus()
            basehp = plus
            basemp = plus
            str = plus
            dex = plus
            int_ = plus
            atk = plus
            dfn = plus
            fatk = plus
            eatk = plus
            iatk = plus
            patk = plus
            fres = plus
            eres = plus
            ires = plus
            pres = plus
            stats = {
                    "HP": basehp,
                    "MP": basemp,
                    "Str":str,
                    "Dex":dex,
                    "Int":int_,
                    "Melee Damage":atk,
                    "Defense":dfn,
                    "Fire Damage":fatk,
                    "Electric Damage":eatk,
                    "Ice Damage":iatk,
                    "Poison Damage":patk,
                    "Fire Resist":fres,
                    "Electric Resist":eres,
                    "Ice Resist":ires,
                    "Poison Resist":pres}
            selected = [stats.keys()[random.randint(0, len(stats.values())-1)] for i in range(3)]
            params = {}
            for selectedKey in selected:
                if selectedKey in params:
                    params[selectedKey] += stats[selectedKey]
                else:
                    params[selectedKey] = stats[selectedKey]

            element = FightingElements("Gold", (0,0,0), params)

        if gentype == ITEM_DENCHANTSCROLL:
            plus = GenPlus()
            sword = plus
            mace = plus
            spear = plus
            knuckle = plus
            armor = plus
            magic = plus
            skills = {"Sword Skill": sword, "Mace Skill": mace, "Spear Skill": spear, "Knuckle Skill": knuckle, "Armor Skill": armor, "Magic Skill": magic}
            selected = [skills.keys()[random.randint(0, len(skills.values())-1)] for i in range(3)]
            params = {}
            for selectedKey in selected:
                if selectedKey in params:
                    params[selectedKey] += skills[selectedKey]
                else:
                    params[selectedKey] = skills[selectedKey]
            element = FightingElements("Diamond", (0,0,0), params)
        return element
        # 음..... maxenchant횟수를 5번으로 적용하고
        # 만약 스크롤에 maxenchant횟수를 늘리는 게 있다면 그만큼 늘려주고 뭐 이런다.
        # 맥스인챈트 늘려수는 횟수가 가끔씩 랜덤하게 나온다.
        # 아이템의 max atk이런건 없고 무제한. 맥스 인챈트 횟수랑
        # 인챈트 스크롤의 퀄리티가 현재 전투 스킬에 따라 다르게 나오게 한다.
        # 뭐 SWORD스킬이 좋으면 SWORD스킬 관련 스탯이 좀 더 좋게 나온다던가 이런다.
        # 마법 스킬이 높으면 방어구나 무기에 마법 관련 스탯이 좋게 나오고 뭐 이런다.
        # 한 개의 인챈트 스크롤에 나올 수 있는 스탯의 숫자는 정해져있다.
        # 실버에서는 밀리 전투 스킬관련, 골드에서는 마법 관련 스킬, 다이아에서는 스탯 관련 
        #
        # 음......... 어떤 마법 스킬에 따라서 더 좋은 결과가 나온다.
        # 몬스터도 인챈트 스크롤을 드랍한다. 아이템 대신!
    def DoMake(self, makeIdx):
        tool = self.makes[makeIdx]
        if not tool:
            return

        type_, stats, disallowed, count, name = tool.returns
        if name == TYPE_BLOCK:
            returneditem = Block(type_, count)
            if type_ == BLOCK_COLOR:
                returneditem.colorIdx = stats[0]
                returneditem.color = tool.color
        elif name == TYPE_ITEM:
            if type_ in [ITEM_SENCHANTSCROLL, ITEM_GENCHANTSCROLL, ITEM_DENCHANTSCROLL]:
                #인챈트 스크롤 복사하는 아이템이 고급 몬스터에게서 떨어진다. XXX:
                element = self.GenElement(type_)
                returneditem = Item(type_, 1, color=tool.color, element=element)
                returneditem.maxEnchant = 0
            elif type_ in [ITEM_GOLDRING, ITEM_GOLDNECLACE, ITEM_HELM, ITEM_ARMOR, ITEM_SILVERRING, ITEM_SILVERNECLACE, ITEM_DIAMONDRING, ITEM_DIAMONDNECLACE]:
                returneditem = Item(type_, 1, color=tool.color, stats=stats)
                if type_ in [ITEM_SILVERNECLACE, ITEM_SILVERRING]:
                    returneditem.maxEnchant += 2
                if type_ in [ITEM_GOLDNECLACE, ITEM_GOLDRING]:
                    returneditem.maxEnchant += 4
                if type_ in [ITEM_DIAMONDNECLACE, ITEM_DIAMONDRING]:
                    returneditem.maxEnchant += 6
            elif type_ in [ITEM_SWORD, ITEM_SPEAR, ITEM_MACE, ITEM_KNUCKLE]:
                returneditem = Item(type_, 1, color=tool.color, stats=stats)
                if type_ == ITEM_SPEAR:
                    returneditem.element = FightingElements("Weapon", (0,0,0), {"Melee Damage":20})
                else:
                    returneditem.element = FightingElements("Weapon", (0,0,0), {"Melee Damage":10})
            elif type_ in [ITEM_SHIELD]:
                returneditem = Item(type_, 1, color=tool.color, stats=stats)
                returneditem.element = FightingElements("Shield", (0,0,0), {"Defense":10})
            elif type_ in [ITEM_HELM]:
                returneditem = Item(type_, 1, color=tool.color, stats=stats)
                returneditem.element = FightingElements("Helm", (0,0,0), {"Defense":5})
            elif type_ in [ITEM_ARMOR]:
                returneditem = Item(type_, 1, color=tool.color, stats=stats)
                returneditem.element = FightingElements("Armor", (0,0,0), {"Defense":10})
            elif type_ in [ITEM_BOOTS]:
                returneditem = Item(type_, 1, color=tool.color, stats=stats)
                returneditem.element = FightingElements("Boots", (0,0,0), {"Defense":5})
            elif type_ in [ITEM_GLOVES]:
                returneditem = Item(type_, 1, color=tool.color, stats=stats)
                returneditem.element = FightingElements("Gloves", (0,0,0), {"Defense":5})

            # 무기나 방어구에 알맞는 기본 atk, dfn등을 넣어야 한다.
            # 이용자의 스킬에 따라 더 높은 속성을 넣을 수도 있다?
            else:
                if count == 0:
                    returneditem = Item(type_, 999, color=tool.color, stats=stats)
                    returneditem.maxEnchant = 0
                elif count == -1:
                    returneditem = Item(type_, 1, color=tool.color, stats=stats)
                    returneditem.maxEnchant = 0
                else:
                    returneditem = Item(type_, count, color=tool.color, stackable=True, stats=stats)
                    returneditem.maxEnchant = 0
        if not self.CanPutItemInInventory(returneditem):
            return

        def Make(nDict):
            for need in tool.needs:
                count = need[1]
                makeList = nDict[need]
                for item, cont in makeList:
                    if item.count > count:
                        item.count -= count
                        count = 0
                    elif item.count == count:
                        count = 0
                        cont[cont.index(item)] = ITEM_NONE
                    else:
                        count -= item.count
                        cont[cont.index(item)] = ITEM_NONE
            self.PutItemInInventory(returneditem)

        needDict = {}
        def DoPass(mList, type_, count, name, cont):
            countNeeds = count
            for item in cont:
                if item and item.type_ == type_ and item.name == name:
                    if item.count >= countNeeds:
                        mList += [(item, cont)]
                        return True, countNeeds
                    else:
                        mList += [(item, cont)]
                        countNeeds -= item.count
            return False, countNeeds

        for need in tool.needs:
            if len(need) == 3:
                type_, count, name = need
            elif len(need) == 4:
                type_, count, name, color = need
            cont = self.inventory
            needDict[need] = []
            found, count = DoPass(needDict[need], type_, count, name, cont)
            if not found:
                cont = self.qbar
                found, count = DoPass(needDict[need], type_, count, name, cont)
                if not found:
                    return

        Make(needDict)




    def LUp(self, t, m, k):
        pass
    def RUp(self, t, m, k):
        pass
    def WDn(self, t, m, k):
        self.selectedItem -= 1
        if self.selectedItem < 0:
            self.selectedItem = 9

    def WUp(self, t, m, k):
        self.selectedItem += 1
        if self.selectedItem > 9:
            self.selectedItem = 0

    def KDown(self, t, m, k):
        if k.pressedKey == K_1:
            self.selectedItem = 0
        if k.pressedKey == K_2:
            self.selectedItem = 1
        if k.pressedKey == K_3:
            self.selectedItem = 2
        if k.pressedKey == K_4:
            self.selectedItem = 3
        if k.pressedKey == K_5:
            self.selectedItem = 4
        if k.pressedKey == K_6:
            self.selectedItem = 5
        if k.pressedKey == K_7:
            self.selectedItem = 6
        if k.pressedKey == K_8:
            self.selectedItem = 7
        if k.pressedKey == K_9:
            self.selectedItem = 8
        if k.pressedKey == K_0:
            self.selectedItem = 9

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

    def Render(self, t, m, k):
        if t - self.prevAreaT >= self.areaDelay:
            if self.invShown:
                self.textRendererArea.Clear()
                self.prevAreaT = t
                if self.toolMode == TM_CODE:
                    self.testFile.Update(self.textRendererArea)
                elif self.toolMode == TM_SPAWN:
                    self.testEdit.Update(self.textRendererArea)
        if self.invShown and self.toolMode == TM_CODE:
            self.testFile.Render()
        elif self.invShown and self.toolMode == TM_SPAWN:
            self.testEdit.Render()
        if self.invShown:
            self.textRendererArea.Render()
        self.talkBox.active = False
        if self.invShown and self.toolMode == TM_TALK:
            self.talkBox.active = True
            self.talkBox.Render()
        self.msgBox.Render()
            # XXX: 이거를 음....텍스트 에어리어에 텍스트가 꽉 찼을 때만 업뎃하게 하고 나머지는 그냥
            # 위로 한칸씩 올리면서 추가하기만 한다.

        glBindTexture(GL_TEXTURE_2D, self.inventex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

    
        glBegin(GL_QUADS)
        if self.invShown and self.toolMode in [TM_EQ]:
            x,y = self.invPos
            glTexCoord2f(0.0, float(186)/512.0)
            glVertex3f(float(x), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, float(186)/512.0)
            glVertex3f(float(x+306), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, 0.0)
            glVertex3f(float(x+306), -float(y), 100.0)

            glTexCoord2f(0.0, 0.0)
            glVertex3f(x, -float(y), 100.0)

            x,y = self.makePos
            glTexCoord2f(0.0, float(186+200)/512.0)
            glVertex3f(float(x), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, float(186+200)/512.0)
            glVertex3f(float(x+306), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, 0.0+200.0/512.0)
            glVertex3f(float(x+306), -float(y), 100.0)

            glTexCoord2f(0.0, 200.0/512.0)
            glVertex3f(x, -float(y), 100.0)

        if self.invShown and self.toolMode in [TM_BOX, TM_TOOL]:
            x,y = self.invPos
            glTexCoord2f(0.0, float(186)/512.0)
            glVertex3f(float(x), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, float(186)/512.0)
            glVertex3f(float(x+306), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, 0.0)
            glVertex3f(float(x+306), -float(y), 100.0)

            glTexCoord2f(0.0, 0.0)
            glVertex3f(x, -float(y), 100.0)

            x,y = self.makePos
            glTexCoord2f(0.0, float(186)/512.0)
            glVertex3f(float(x), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, float(186)/512.0)
            glVertex3f(float(x+306), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, 0.0)
            glVertex3f(float(x+306), -float(y), 100.0)

            glTexCoord2f(0.0, 0.0)
            glVertex3f(x, -float(y), 100.0)


        if self.invShown and self.toolMode == TM_CHAR and not self.charTab:
            x,y = self.invPos
            glTexCoord2f(0.0, float(186)/512.0)
            glVertex3f(float(x), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, float(186)/512.0)
            glVertex3f(float(x+306), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, 0.0)
            glVertex3f(float(x+306), -float(y), 100.0)

            glTexCoord2f(0.0, 0.0)
            glVertex3f(x, -float(y), 100.0)

            x,y = self.makePos
            glTexCoord2f(0.0, float(186)/512.0)
            glVertex3f(float(x), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, float(186)/512.0)
            glVertex3f(float(x+306), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, 0.0)
            glVertex3f(float(x+306), -float(y), 100.0)

            glTexCoord2f(0.0, 0.0)
            glVertex3f(x, -float(y), 100.0)



        x,y = self.qbarPos
        glTexCoord2f(0.0, float(410+38)/512.0)
        glVertex3f(float(x), -float(y+38), 100.0)

        glTexCoord2f(float(308)/512.0, float(410+38)/512.0)
        glVertex3f(float(x+308), -float(y+38), 100.0)

        glTexCoord2f(float(308)/512.0, float(410)/512.0)
        glVertex3f(float(x+308), -float(y), 100.0)

        glTexCoord2f(0.0, float(410)/512.0)
        glVertex3f(x, -float(y), 100.0)

        glEnd()
            # XXX: 여기다가 출력
            # 출력은 어찌하나.스탯이 오를 때마다 업뎃?
            # 켤 때마다 업뎃하게 하면 된다. 켠 상태에서 스킬이 올라도 걍 표시하지 않는다?
            # 아...숫자니까 글자는 스태틱, 숫자는 숫자 렌더러로..
            # 소수점자리는 표시하지 않음.
        if self.invShown and self.toolMode == TM_CHAR and self.charTab:
            glBegin(GL_QUADS)
            x,y = self.invPos
            glTexCoord2f(0.0, float(186)/512.0)
            glVertex3f(float(x), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, float(186)/512.0)
            glVertex3f(float(x+306), -float(y+186), 100.0)

            glTexCoord2f(float(306)/512.0, 0.0)
            glVertex3f(float(x+306), -float(y), 100.0)

            glTexCoord2f(0.0, 0.0)
            glVertex3f(x, -float(y), 100.0)
            glEnd()


            x,y = self.makePos
            DrawQuad(x,y,306,186, (205,209,184,255), (205,209,184,255))
            x += 3
            orgx = x
            y += 3
            self.textRendererSmall.RenderText(self.strID, (x,y))
            x += 25
            self.RenderNumberS(int(AppSt.entity.str), x,y)
            x += 30
            self.textRendererSmall.RenderText(self.dexID, (x,y))
            x += 25
            self.RenderNumberS(int(AppSt.entity.dex), x,y)
            x += 30
            self.textRendererSmall.RenderText(self.intID, (x,y))
            x += 25
            self.RenderNumberS(int(AppSt.entity.int), x,y)

            x = orgx
            y += 20
            self.textRendererSmall.RenderText(self.atkID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.atk), x,y)
            x += 100
            self.textRendererSmall.RenderText(self.dfnID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.dfn), x,y)


            x = orgx
            y += 15
            self.textRendererSmall.RenderText(self.swordID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.sword), x,y)
            x += 100
            self.textRendererSmall.RenderText(self.maceID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.mace), x,y)


            x = orgx
            y += 15
            self.textRendererSmall.RenderText(self.spearID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.spear), x,y)
            x += 100
            self.textRendererSmall.RenderText(self.knuckleID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.knuckle), x,y)


            x = orgx
            y += 15
            self.textRendererSmall.RenderText(self.armorID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.armor), x,y)
            x += 100
            self.textRendererSmall.RenderText(self.magicID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.magic), x,y)


            x = orgx
            y += 20
            self.textRendererSmall.RenderText(self.patkID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.patk), x,y)
            x += 100
            self.textRendererSmall.RenderText(self.iatkID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.iatk), x,y)


            x = orgx
            y += 15
            self.textRendererSmall.RenderText(self.eatkID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.eatk), x,y)
            x += 100
            self.textRendererSmall.RenderText(self.fatkID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.fatk), x,y)

            x = orgx
            y += 20
            self.textRendererSmall.RenderText(self.resID, (x,y))


            x = orgx
            y += 15
            self.textRendererSmall.RenderText(self.patkID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.pres), x,y)
            x += 100
            self.textRendererSmall.RenderText(self.iatkID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.ires), x,y)


            x = orgx
            y += 15
            self.textRendererSmall.RenderText(self.eatkID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.eres), x,y)
            x += 100
            self.textRendererSmall.RenderText(self.fatkID, (x,y))
            x += 50
            self.RenderNumberS(int(AppSt.entity.fres), x,y)



        if self.invShown and self.toolMode == TM_EQ:
            idx = 0
            for pos in self.eqSlotPos[:4]:
                x,y = pos
                x += 32
                y += 3
                self.textRendererSmall.RenderText(self.eqTexts[idx], (x,y))
                idx += 1
            for pos in self.eqSlotPos[4:]:
                x,y = pos
                x -= 56
                y += 3
                self.textRendererSmall.RenderText(self.eqTexts[idx], (x,y))
                idx += 1



        def RenderItemEq(item, posx, posy, text=True):
            x = posx
            y = posy
            b = item.type_
            if item.name == TYPE_BLOCK:
                glBindTexture(GL_TEXTURE_2D, AppSt.tex)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
                texupx = (BLOCK_TEX_COORDS[b*2*3 + 0]*32.0) / 512.0
                texupy = (BLOCK_TEX_COORDS[b*2*3 + 1]*32.0) / 512.0
                glBegin(GL_QUADS)
                glTexCoord2f(texupx, texupy+float(32)/512.0)
                glVertex3f(float(x), -float(y+30), 100.0)

                glTexCoord2f(texupx+float(32)/512.0, texupy+float(32)/512.0)
                glVertex3f(float(x+30), -float(y+30), 100.0)

                glTexCoord2f(texupx+float(32)/512.0, texupy)
                glVertex3f(float(x+30), -float(y), 100.0)

                glTexCoord2f(texupx, texupy)
                glVertex3f(x, -float(y), 100.0)
                glEnd()
            elif item.name == TYPE_ITEM:
                glBindTexture(GL_TEXTURE_2D, self.tooltex)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                if item.color:
                    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
                else:
                    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
                texupx = (TOOL_TEX_COORDS[b*2 + 0]*30.0) / 512.0
                texupy = (TOOL_TEX_COORDS[b*2 + 1]*30.0) / 512.0
                glBegin(GL_QUADS)
                if item.color:
                    glColor4ub(*(item.color+(255,)))
                glTexCoord2f(texupx, texupy+float(30)/512.0)
                glVertex3f(float(x), -float(y+30), 100.0)

                glTexCoord2f(texupx+float(30)/512.0, texupy+float(30)/512.0)
                glVertex3f(float(x+30), -float(y+30), 100.0)

                glTexCoord2f(texupx+float(30)/512.0, texupy)
                glVertex3f(float(x+30), -float(y), 100.0)

                glTexCoord2f(texupx, texupy)
                glVertex3f(x, -float(y), 100.0)
                glEnd()

            """
            texmidx = (BLOCK_TEX_COORDS[b*2*3 + 2]*32.0) / 512.0
            texmidy = (BLOCK_TEX_COORDS[b*2*3 + 3]*32.0) / 512.0
            texbotx = (BLOCK_TEX_COORDS[b*2*3 + 4]*32.0) / 512.0
            texboty = (BLOCK_TEX_COORDS[b*2*3 + 5]*32.0) / 512.0
            """
            if text:
                self.RenderNumber(item.count, x, y)
        def RenderSkill(skill, idx, posx, posy, text=True):
            x = idx%10
            y = (idx-x)/10
            x*=30
            y*=30
            x += posx
            y += posy
            glBindTexture(GL_TEXTURE_2D, self.tooltex)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            texupx = (skill.texcoord[0]*30.0) / 512.0
            texupy = (skill.texcoord[1]*30.0) / 512.0
            glBegin(GL_QUADS)
            glTexCoord2f(texupx, texupy+float(30)/512.0)
            glVertex3f(float(x), -float(y+30), 100.0)

            glTexCoord2f(texupx+float(30)/512.0, texupy+float(30)/512.0)
            glVertex3f(float(x+30), -float(y+30), 100.0)

            glTexCoord2f(texupx+float(30)/512.0, texupy)
            glVertex3f(float(x+30), -float(y), 100.0)

            glTexCoord2f(texupx, texupy)
            glVertex3f(x, -float(y), 100.0)
            glEnd()

            """
            texmidx = (BLOCK_TEX_COORDS[b*2*3 + 2]*32.0) / 512.0
            texmidy = (BLOCK_TEX_COORDS[b*2*3 + 3]*32.0) / 512.0
            texbotx = (BLOCK_TEX_COORDS[b*2*3 + 4]*32.0) / 512.0
            texboty = (BLOCK_TEX_COORDS[b*2*3 + 5]*32.0) / 512.0
            """
            if text:
                self.RenderNumber(int(skill.skillPoint), x, y)
        def RenderItem(item, idx, posx, posy, text=True):
            x = idx%10
            y = (idx-x)/10
            x*=30
            y*=30
            x += posx
            y += posy
            b = item.type_
            if item.name == TYPE_BLOCK:
                glBindTexture(GL_TEXTURE_2D, AppSt.tex)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                if item.type_ == BLOCK_COLOR:
                    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
                else:
                    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
                texupx = (BLOCK_TEX_COORDS[b*2*3 + 0]*32.0) / 512.0
                texupy = (BLOCK_TEX_COORDS[b*2*3 + 1]*32.0) / 512.0
                glBegin(GL_QUADS)
                if item.type_ == BLOCK_COLOR:
                    glColor4ub(*(tuple(item.color)+(255,)))
                else:
                    pass
                glTexCoord2f(texupx, texupy+float(32)/512.0)
                glVertex3f(float(x), -float(y+30), 100.0)

                glTexCoord2f(texupx+float(32)/512.0, texupy+float(32)/512.0)
                glVertex3f(float(x+30), -float(y+30), 100.0)

                glTexCoord2f(texupx+float(32)/512.0, texupy)
                glVertex3f(float(x+30), -float(y), 100.0)

                glTexCoord2f(texupx, texupy)
                glVertex3f(x, -float(y), 100.0)
                glEnd()
                w = 29
                h = 29
                y+=1
                glDisable(GL_TEXTURE_2D)

                glLineWidth(1.0)
                glBegin(GL_LINES)
                glColor4f(0.0,0.0,0.0,1.0)
                glVertex3f(float(x), -float(y+h), 100.0)
                glVertex3f(float(x+w), -float(y+h), 100.0)
                
                glVertex3f(float(x+w), -float(y+h), 100.0)
                glVertex3f(float(x+w), -float(y), 100.0)

                glVertex3f(float(x+w), -float(y), 100.0)
                glVertex3f(x, -float(y), 100.0)

                glVertex3f(x, -float(y), 100.0)
                glVertex3f(float(x), -float(y+h), 100.0)
                glEnd()
                glEnable(GL_TEXTURE_2D)

            elif item.name == TYPE_ITEM:
                glBindTexture(GL_TEXTURE_2D, self.tooltex)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                if item.color:
                    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
                else:
                    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
                texupx = (TOOL_TEX_COORDS[b*2 + 0]*30.0) / 512.0
                texupy = (TOOL_TEX_COORDS[b*2 + 1]*30.0) / 512.0
                glBegin(GL_QUADS)
                if item.color:
                    glColor4ub(*(item.color+(255,)))
                glTexCoord2f(texupx, texupy+float(30)/512.0)
                glVertex3f(float(x), -float(y+30), 100.0)

                glTexCoord2f(texupx+float(30)/512.0, texupy+float(30)/512.0)
                glVertex3f(float(x+30), -float(y+30), 100.0)

                glTexCoord2f(texupx+float(30)/512.0, texupy)
                glVertex3f(float(x+30), -float(y), 100.0)

                glTexCoord2f(texupx, texupy)
                glVertex3f(x, -float(y), 100.0)
                glEnd()

            """
            texmidx = (BLOCK_TEX_COORDS[b*2*3 + 2]*32.0) / 512.0
            texmidy = (BLOCK_TEX_COORDS[b*2*3 + 3]*32.0) / 512.0
            texbotx = (BLOCK_TEX_COORDS[b*2*3 + 4]*32.0) / 512.0
            texboty = (BLOCK_TEX_COORDS[b*2*3 + 5]*32.0) / 512.0
            """
            if text:
                self.RenderNumber(item.count, x, y)

        if self.invShown:
            if self.toolMode in [TM_EQ]:
                idx = 0
                for item in self.eqs:
                    if not item:
                        pass
                    else:
                        RenderItemEq(item, self.eqSlotPos[idx][0], self.eqSlotPos[idx][1])
                    idx += 1

            if self.toolMode in [TM_BOX, TM_TOOL, TM_EQ, TM_CHAR]:
                idx = 0
                for item in self.inventory:
                    if not item:
                        idx += 1
                        continue

                    RenderItem(item, idx, self.invRealPos[0], self.invRealPos[1])
                    idx += 1

            if self.toolMode == TM_CHAR and not self.charTab:
                idx = 0
                for skill in self.skills:
                    if skill:
                        RenderSkill(skill.skill, idx, self.makeRealPos[0], self.makeRealPos[1])
                    idx += 1
                cleared = False


            if self.toolMode == TM_BOX:
                idx = 0
                for item in self.selectedBox:
                    if not item:
                        idx += 1
                        continue

                    RenderItem(item, idx, self.makeRealPos[0], self.makeRealPos[1])
                    idx += 1
            if self.toolMode == TM_TOOL:
                idx = 0
                for item in self.makes:
                    if not item:
                        idx += 1
                        continue
                    type_, stats, disallowed, count, name = item.returns
                    if name == TYPE_ITEM:
                        glBindTexture(GL_TEXTURE_2D, self.tooltex)
                        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

                        x = idx%10
                        y = (idx-x)/10
                        x*=30
                        y*=30
                        x += self.makeRealPos[0]
                        y += self.makeRealPos[1]
                        b = item.returns[0]
                        texupx = (TOOL_TEX_COORDS[b*2 + 0]*30.0) / 512.0
                        texupy = (TOOL_TEX_COORDS[b*2 + 1]*30.0) / 512.0
                        """
                        texmidx = (BLOCK_TEX_COORDS[b*2*3 + 2]*32.0) / 512.0
                        texmidy = (BLOCK_TEX_COORDS[b*2*3 + 3]*32.0) / 512.0
                        texbotx = (BLOCK_TEX_COORDS[b*2*3 + 4]*32.0) / 512.0
                        texboty = (BLOCK_TEX_COORDS[b*2*3 + 5]*32.0) / 512.0
                        """

                        # XXX: 재료가 없으면 배경을 빨간색으로 표시
                        """
                        glDisable(GL_TEXTURE_2D)
                        glBegin(GL_QUADS)
                        glColor4ub(200,0,0,200)
                        glVertex3f(float(x), -float(y+30), 100.0)
                        glVertex3f(float(x+30), -float(y+30), 100.0)
                        glVertex3f(float(x+30), -float(y), 100.0)
                        glVertex3f(x, -float(y), 100.0)
                        glEnd()
                        glEnable(GL_TEXTURE_2D)
                        """

                        glBegin(GL_QUADS)
                        glColor4ub(*item.color + (255,))
                        glTexCoord2f(texupx, texupy+float(30)/512.0)
                        glVertex3f(float(x), -float(y+30), 100.0)

                        glTexCoord2f(texupx+float(30)/512.0, texupy+float(30)/512.0)
                        glVertex3f(float(x+30), -float(y+30), 100.0)

                        glTexCoord2f(texupx+float(30)/512.0, texupy)
                        glVertex3f(float(x+30), -float(y), 100.0)

                        glTexCoord2f(texupx, texupy)
                        glVertex3f(x, -float(y), 100.0)
                        glEnd()
                        idx += 1
                    elif name == TYPE_BLOCK:
                        glBindTexture(GL_TEXTURE_2D, AppSt.tex)
                        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                        if item.returns[0] == BLOCK_COLOR:
                            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
                        else:
                            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

                        x = idx%10
                        y = (idx-x)/10
                        x*=30
                        y*=30
                        x += self.makeRealPos[0]
                        y += self.makeRealPos[1]
                        b = item.returns[0]
                        texupx = (BLOCK_TEX_COORDS[b*2*3 + 0]*32.0) / 512.0
                        texupy = (BLOCK_TEX_COORDS[b*2*3 + 1]*32.0) / 512.0
                        """
                        texmidx = (BLOCK_TEX_COORDS[b*2*3 + 2]*32.0) / 512.0
                        texmidy = (BLOCK_TEX_COORDS[b*2*3 + 3]*32.0) / 512.0
                        texbotx = (BLOCK_TEX_COORDS[b*2*3 + 4]*32.0) / 512.0
                        texboty = (BLOCK_TEX_COORDS[b*2*3 + 5]*32.0) / 512.0
                        """

                        # XXX: 재료가 없으면 배경을 빨간색으로 표시
                        """
                        glDisable(GL_TEXTURE_2D)
                        glBegin(GL_QUADS)
                        glColor4ub(200,0,0,200)
                        glVertex3f(float(x), -float(y+30), 100.0)
                        glVertex3f(float(x+30), -float(y+30), 100.0)
                        glVertex3f(float(x+30), -float(y), 100.0)
                        glVertex3f(x, -float(y), 100.0)
                        glEnd()
                        glEnable(GL_TEXTURE_2D)
                        """

                        glBegin(GL_QUADS)
                        glColor4ub(*item.color + (255,))
                        glTexCoord2f(texupx, texupy+float(32)/512.0)
                        glVertex3f(float(x), -float(y+30), 100.0)

                        glTexCoord2f(texupx+float(32)/512.0, texupy+float(32)/512.0)
                        glVertex3f(float(x+30), -float(y+30), 100.0)

                        glTexCoord2f(texupx+float(32)/512.0, texupy)
                        glVertex3f(float(x+30), -float(y), 100.0)

                        glTexCoord2f(texupx, texupy)
                        glVertex3f(x, -float(y), 100.0)
                        glEnd()

                        w=29
                        h=29
                        y+=1
                        glDisable(GL_TEXTURE_2D)
                        glLineWidth(1.0)
                        glBegin(GL_LINES)
                        glColor4f(0.0,0.0,0.0,1.0)
                        glVertex3f(float(x), -float(y+h), 100.0)
                        glVertex3f(float(x+w), -float(y+h), 100.0)
                        
                        glVertex3f(float(x+w), -float(y+h), 100.0)
                        glVertex3f(float(x+w), -float(y), 100.0)

                        glVertex3f(float(x+w), -float(y), 100.0)
                        glVertex3f(x, -float(y), 100.0)

                        glVertex3f(x, -float(y), 100.0)
                        glVertex3f(float(x), -float(y+h), 100.0)
                        glEnd()
                        glEnable(GL_TEXTURE_2D)

                        idx += 1

                if self.selectedMakeTool != -1 and self.makes[self.selectedMakeTool]:
                    x,y,w,h = 5, 20, 165, 380
                    glDisable(GL_TEXTURE_2D)
                    glBegin(GL_QUADS)
                    glColor4f(1.0,1.0,1.0,0.85)
                    glVertex3f(float(x), -float(y+h), 100.0)
                    glVertex3f(float(x+w), -float(y+h), 100.0)
                    glVertex3f(float(x+w), -float(y), 100.0)
                    glVertex3f(x, -float(y), 100.0)
                    glEnd()

                    glLineWidth(3.0)
                    glBegin(GL_LINES)
                    glColor4f(0.0,0.0,0.0,1.0)
                    glVertex3f(float(x), -float(y+h), 100.0)
                    glVertex3f(float(x+w), -float(y+h), 100.0)
                    
                    glVertex3f(float(x+w), -float(y+h), 100.0)
                    glVertex3f(float(x+w), -float(y), 100.0)

                    glVertex3f(float(x+w), -float(y), 100.0)
                    glVertex3f(x, -float(y), 100.0)

                    glVertex3f(x, -float(y), 100.0)
                    glVertex3f(float(x), -float(y+h), 100.0)
                    glEnd()
                    glEnable(GL_TEXTURE_2D)

                    tool = self.makes[self.selectedMakeTool]
                    y = 0
                    for textid in tool.textidName:
                        self.textRenderer.RenderText(textid, (10, 25+y))
                        y += 20
                    y += 10
                    for textid in tool.textidDesc:
                        self.textRendererSmall.RenderText(textid, (10, 25+y))
                        y += 15
                    y += 10
                    self.textRenderer.RenderText(self.recipeTextID, (10, 25+y))
                    y += 20+25

                    x = 10
                    for need in tool.needs:
                        if len(need) == 3:
                            item, count, textype = need
                            color=(255,255,255)
                        elif len(need) == 4:
                            item, count, textype, color = need
                        if textype == TYPE_BLOCK:
                            glBindTexture(GL_TEXTURE_2D, AppSt.tex)
                            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
                            texupx = (BLOCK_TEX_COORDS[item*2*3 + 0]*32.0) / 512.0
                            texupy = (BLOCK_TEX_COORDS[item*2*3 + 1]*32.0) / 512.0
                            glBegin(GL_QUADS)
                            glTexCoord2f(texupx, texupy+float(32)/512.0)
                            glVertex3f(float(x), -float(y+30), 100.0)

                            glTexCoord2f(texupx+float(32)/512.0, texupy+float(32)/512.0)
                            glVertex3f(float(x+30), -float(y+30), 100.0)

                            glTexCoord2f(texupx+float(32)/512.0, texupy)
                            glVertex3f(float(x+30), -float(y), 100.0)

                            glTexCoord2f(texupx, texupy)
                            glVertex3f(x, -float(y), 100.0)
                            glEnd()
                            self.RenderNumber(count, x, y)
                        elif textype == TYPE_ITEM:
                            glBindTexture(GL_TEXTURE_2D, self.tooltex)
                            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
                            texupx = (TOOL_TEX_COORDS[item*2 + 0]*30.0) / 512.0
                            texupy = (TOOL_TEX_COORDS[item*2 + 1]*30.0) / 512.0
                            glBegin(GL_QUADS)
                            glColor3ub(*color)
                            glTexCoord2f(texupx, texupy+float(30)/512.0)
                            glVertex3f(float(x), -float(y+30), 100.0)

                            glTexCoord2f(texupx+float(30)/512.0, texupy+float(30)/512.0)
                            glVertex3f(float(x+30), -float(y+30), 100.0)

                            glTexCoord2f(texupx+float(30)/512.0, texupy)
                            glVertex3f(float(x+30), -float(y), 100.0)

                            glTexCoord2f(texupx, texupy)
                            glVertex3f(x, -float(y), 100.0)
                            glEnd()
                            self.RenderNumber(count, x, y)
                        x += 35
                        if x+35 >= 160:
                            x = 10
                            y += 35





            def GenItemName(item):
                textTitle = ["Item"]
                if item.type_ == ITEM_SENCHANTSCROLL:
                    textTitle = [u"Silver Enchant Scroll"]
                # 여기서 text width에 맞게 적당히 split을 하고
                # 접두사 접미사를 붙인다.
                # param에 뭐가 있느냐에 따라 접두사 접미사를..
                # 굉장히 귀찮을 듯.
                # 음.....아이템 생성에 대해서도 디아처럼 생성하면 되겠네 구조를 아니까...
                # 데이지서버 할 때 처럼 스탯 맞추면 될 듯.
                return textTitle
            def GenItemDesc(item):
                textDesc = ["Enchant"]
                if item.type_ == ITEM_SENCHANTSCROLL:
                    textDesc = [u"Individual Skills"]
                if item.type_ == ITEM_GENCHANTSCROLL:
                    textDesc = [u"Stats"]
                if item.type_ == ITEM_DENCHANTSCROLL:
                    textDesc = [u"Skill Levels"]
                return textDesc
            def GenItemParams(item):
                textParams = str(item.element.params).replace("{","").replace("}","").split(', ')
                return textParams

            cleared = False
            if t - self.prevDescT >= self.areaDelay:
                self.prevDescT = t
                self.textRendererItemTitle.Clear()
                self.textRendererItemSmall.Clear()
                cleared = True
            

            def RenderItemDesc(item):
                if not item.element:
                    return
                x,y,w,h = 5, 20, 165, 380
                glDisable(GL_TEXTURE_2D)
                glBegin(GL_QUADS)
                glColor4f(1.0,1.0,1.0,0.85)
                glVertex3f(float(x), -float(y+h), 100.0)
                glVertex3f(float(x+w), -float(y+h), 100.0)
                glVertex3f(float(x+w), -float(y), 100.0)
                glVertex3f(x, -float(y), 100.0)
                glEnd()

                glLineWidth(3.0)
                glBegin(GL_LINES)
                glColor4f(0.0,0.0,0.0,1.0)
                glVertex3f(float(x), -float(y+h), 100.0)
                glVertex3f(float(x+w), -float(y+h), 100.0)
                
                glVertex3f(float(x+w), -float(y+h), 100.0)
                glVertex3f(float(x+w), -float(y), 100.0)

                glVertex3f(float(x+w), -float(y), 100.0)
                glVertex3f(x, -float(y), 100.0)

                glVertex3f(x, -float(y), 100.0)
                glVertex3f(float(x), -float(y+h), 100.0)
                glEnd()
                glEnable(GL_TEXTURE_2D)

                y = 0
                textTitle = GenItemName(item)
                if not item.textTitleIdx or cleared:
                    item.textTitleIdx = [self.textRendererItemTitle.NewTextObject(text, (0,0,0), (10, 25+y)) for text in textTitle]

                try:
                    for idx in item.textTitleIdx:
                        self.textRendererItemTitle.RenderOne(idx, (10, 25+y))
                        y += 20
                except:
                    pass
                y += 10

                textDesc = GenItemDesc(item)
                paramText = GenItemParams(item)
                if not item.textDescIdx or cleared:
                    item.textDescIdx = [self.textRendererItemSmall.NewTextObject(text, (0,0,0), (10, 25+y)) for text in textDesc]
                    item.textDescIdx += [self.textRendererItemSmall.NewTextObject(text, (0,0,0), (10, 25+y)) for text in paramText]


                try:
                    for textid in item.textDescIdx:
                        self.textRendererItemSmall.RenderOne(textid, (10, 25+y))
                        y += 15
                except:
                    pass
                y += 10
                if item.maxEnchant:
                    self.textRendererSmall.RenderText(self.enchantTextID, (10, 25+y))
                    y += 10
                    self.RenderNumber(item.enchantCount, 10, 25+y)
                    self.textRenderer.RenderText(self.enchantSlashTextID, (25, 25+y))
                    self.RenderNumber(item.maxEnchant, 40, 25+y)


            def RenderSkillDesc(skill):
                x,y,w,h = 5, 20, 165, 380
                glDisable(GL_TEXTURE_2D)
                glBegin(GL_QUADS)
                glColor4f(1.0,1.0,1.0,0.85)
                glVertex3f(float(x), -float(y+h), 100.0)
                glVertex3f(float(x+w), -float(y+h), 100.0)
                glVertex3f(float(x+w), -float(y), 100.0)
                glVertex3f(x, -float(y), 100.0)
                glEnd()

                glLineWidth(3.0)
                glBegin(GL_LINES)
                glColor4f(0.0,0.0,0.0,1.0)
                glVertex3f(float(x), -float(y+h), 100.0)
                glVertex3f(float(x+w), -float(y+h), 100.0)
                
                glVertex3f(float(x+w), -float(y+h), 100.0)
                glVertex3f(float(x+w), -float(y), 100.0)

                glVertex3f(float(x+w), -float(y), 100.0)
                glVertex3f(x, -float(y), 100.0)

                glVertex3f(x, -float(y), 100.0)
                glVertex3f(float(x), -float(y+h), 100.0)
                glEnd()
                glEnable(GL_TEXTURE_2D)

                y = 0
                textTitle = [skill.name]
                if not skill.textTitleIdx or cleared:
                    skill.textTitleIdx = [self.textRendererItemTitle.NewTextObject(text, (0,0,0), (10, 25+y)) for text in textTitle]

                try:
                    for idx in skill.textTitleIdx:
                        self.textRendererItemTitle.RenderOne(idx, (10, 25+y))
                        y += 20
                except:
                    pass
                y += 10

                textDesc = ["Level: %d" % skill.skillPoint, "Range: %d" % skill.range]
                textDesc += ["Cost: %d" % (skill.cost*(skill.skillPoint*0.5))]
                for raw in skill.raws:
                    typetexts = {SKILL_PHYSICAL: "Physical",
                            SKILL_FIRE: "Fire",
                            SKILL_ICE: "Ice",
                            SKILL_ELECTRIC: "Electric",
                            SKILL_POISON: "Poison",
                            SKILL_HEAL: "Heal",
                            SKILL_CURE: "Cure Poison",
                            SKILL_STR: "Increse Strength",
                            SKILL_DEX: "Increase Dexterity",
                            SKILL_INT: "Increase Intelligence",
                            SKILL_BASEHP: "Increase Max HP",
                            SKILL_BASEMP: "Increase Max MP",
                            SKILL_SKILL: "Increase %s" % raw.targetskillname,}
                    if raw.skilltype == SKILL_FIRE:
                        textDesc += ["Point: %d" % (((AppSt.entity.fatk+raw.value*(skill.skillPoint*raw.incFactor)))*(AppSt.entity.int**1.8/AppSt.entity.int))]
                    elif raw.skilltype == SKILL_PHYSICAL:
                        textDesc += ["Point: %d" % (((AppSt.entity.atk+raw.value*(skill.skillPoint*raw.incFactor)))*(AppSt.entity.int**1.8/AppSt.entity.int))]
                    elif raw.skilltype == SKILL_ICE:
                        textDesc += ["Point: %d" % (((AppSt.entity.iatk+raw.value*(skill.skillPoint*raw.incFactor)))*(AppSt.entity.int**1.8/AppSt.entity.int))]
                    elif raw.skilltype == SKILL_POISON:
                        textDesc += ["Point: %d" % (((AppSt.entity.patk+raw.value*(skill.skillPoint*raw.incFactor)))*(AppSt.entity.int**1.8/AppSt.entity.int))]
                    elif raw.skilltype == SKILL_ELECTRIC:
                        textDesc += ["Point: %d" % (((AppSt.entity.eatk+raw.value*(skill.skillPoint*raw.incFactor)))*(AppSt.entity.int**1.8/AppSt.entity.int))]
                    else:
                        textDesc += ["Point: %d" % (((raw.value*(skill.skillPoint*raw.incFactor)))*(AppSt.entity.int**1.8/AppSt.entity.int))]
                    textDesc += ["Type: %s" % typetexts[raw.skilltype]]
                    if raw.targettype == TARGET_SELF:
                        textDesc += ["Target: Self"]
                    if raw.targettype == TARGET_OTHER:
                        textDesc += ["Target: Enemy"]
                    if raw.duration == 0:
                        textDesc += ["Duration: Instant"]
                    else:
                        textDesc += ["Duration: %s sec." % raw.duration]
                #paramText = GenItemParams(skill)
                if not skill.textDescIdx or cleared:
                    skill.textDescIdx = [self.textRendererItemSmall.NewTextObject(text, (0,0,0), (10, 25+y)) for text in textDesc]
                    #skill.textDescIdx += [self.textRendererItemSmall.NewTextObject(text, (0,0,0), (10, 25+y)) for text in paramText]


                try:
                    for textid in skill.textDescIdx:
                        self.textRendererItemSmall.RenderOne(textid, (10, 25+y))
                        y += 15
                except:
                    pass
                y += 10




            if self.selectedContItem and self.selectedContItem.name == "Skill" and self.selectedContItem.skill:
                RenderSkillDesc(self.selectedContItem.skill)
            elif self.selectedContItem:
                if self.selectedContItem.name == "Item":
                    RenderItemDesc(self.selectedContItem)







        idx = 0
        for item in self.qbar:
            if not item:
                idx += 1
                continue

            if item.name == "Skill":
                RenderSkill(item.skill, idx, self.qbarRealPos[0], self.qbarRealPos[1])
            else:
                RenderItem(item, idx, self.qbarRealPos[0], self.qbarRealPos[1])
            idx += 1

        x = self.selectedItem%10
        y = (self.selectedItem-x)/10
        x*=30
        y*=30
        x += self.qbarRealPos[0]
        y += self.qbarRealPos[1]
        glDisable(GL_TEXTURE_2D)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glColor4f(0.0,0.0,0.0,1.0)
        glVertex3f(float(x), -float(y+30), 100.0)
        glVertex3f(float(x+30), -float(y+30), 100.0)
        
        glVertex3f(float(x+30), -float(y+30), 100.0)
        glVertex3f(float(x+30), -float(y), 100.0)

        glVertex3f(float(x+30), -float(y), 100.0)
        glVertex3f(x, -float(y), 100.0)

        glVertex3f(x, -float(y), 100.0)
        glVertex3f(float(x), -float(y+30), 100.0)
        glEnd()
        glEnable(GL_TEXTURE_2D)

        if self.invShown and self.dragging:
            if self.draggingItem.name == "Skill":
                RenderSkill(self.draggingItem.skill, 0, m.x-15,m.y-15)
            else:
                RenderItem(self.draggingItem, 0, m.x-15,m.y-15)




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
        self.eventDelay = 50

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
        self.bindMUp += [func]
    def BindMDown(self, func):
        self.bindMDown += [func]
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
            for func in self.bindMDown:
                self.tick = pygame.time.get_ticks()
                func(self.tick, self.lastMouseState, self.lastKeyState)

            dic = {LMB: self.ldown, MMB: self.mdown, RMB: self.rdown, WUP: self.wup, WDN: self.wdn}
            for button in dic:
                if e.button == button:
                    for func in dic[button]:
                        self.tick = pygame.time.get_ticks()
                        func(self.tick, self.lastMouseState, self.lastKeyState)
                
        elif e.type is MOUSEBUTTONUP:
            x,y = e.pos
            self.lastMouseState.OnMouseReleased(x,y,SW,SH, e.button)
            for func in self.bindMUp:
                self.tick = pygame.time.get_ticks()
                func(self.tick, self.lastMouseState, self.lastKeyState)

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
            """
    KEYDOWN	     unicode, key, mod
    KEYUP	     key, mod
            """

def emptyfunc(pos):
    pass
class MouseEventHandler(object):
    def __init__(self, rect):
        self.rect = rect
        self.ldown = emptyfunc
        self.rdown = emptyfunc

    def BindLDown(self, func):
        self.ldown = func
    def BindRDown(self, func):
        self.rdown = func

    def Event(self, e):
        self.OnLDown(e)
        self.OnRDown(e)

    def OnRDown(self, e):
        if e.type is MOUSEBUTTONDOWN:
            if e.button == RMB:
                x, y = e.pos
                x2,y2,w,h = self.rect
                if InRect(x2,y2,w,h,x,y):
                    self.rdown(e.pos)

    def OnLDown(self, e):
        if e.type is MOUSEBUTTONDOWN:
            if e.button == LMB:
                x, y = e.pos
                x2,y2,w,h = self.rect
                if InRect(x2,y2,w,h,x,y):
                    self.ldown(e.pos)


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
"""

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
"""

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


"""
class Frustum (node.Node):
    ""Holder for frustum specification for intersection tests

    Note:
        the Frustum can include an arbitrary number of
        clipping planes, though the most common usage
        is to define 6 clipping planes from the OpenGL
        model-view matrices.
    ""
    ARRAY_TYPE = 'd'
    planes = fieldtypes.MFVec4f( 'planes', 1, [])
    normalized = fieldtypes.SFBool( 'normalized', 0, 1)
    def fromViewingMatrix(cls, matrix= None, normalize=1):
        ""Extract and calculate frustum clipping planes from OpenGL

        The default initializer allows you to create
        Frustum objects with arbitrary clipping planes,
        while this alternate initializer provides
        automatic clipping-plane extraction from the
        model-view matrix.

        matrix -- the combined model-view matrix
        normalize -- whether to normalize the plane equations
            to allow for sphere bounding-volumes and use of
            distance equations for LOD-style operations.
        ""
        if matrix is None:
            matrix = viewingMatrix( )
        clip = ravel(matrix)
        frustum = zeros( (6, 4), cls.ARRAY_TYPE )
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
        if normalize:
            frustum = cls.normalize( frustum )
        return cls( planes = frustum, normalized = normalize )
    fromViewingMatrix = classmethod(fromViewingMatrix)
    def normalize(cls, frustum):
        ""Normalize clipping plane equations""
        magnitude = sqrt( 
            frustum[:,0] * frustum[:,0] + 
            frustum[:,1] * frustum[:,1] + 
            frustum[:,2] * frustum[:,2] 
        )
        # eliminate any planes which have 0-length vectors,
        # those planes can't be used for excluding anything anyway...
        frustum = compress( magnitude,frustum,0 )
        magnitude = compress( magnitude, magnitude,0 )
        magnitude=reshape(magnitude.astype(cls.ARRAY_TYPE), (len(frustum),1))
        return frustum/magnitude
    normalize = classmethod(normalize)
"""

def resize(width, height):
    glViewport(0, 0, width, height)
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
    fov = 90.0
    near = 0.1 # 이게 너무 작으면 Z버퍼가 정확도가 낮으면 글픽 깨짐
    far = G_FAR

    #glViewport(0, 0, SW, SH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glpPerspective(90.0, aspect, near, far)
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

class Camera:
    def __init__(self):
        """
        self.view = Vector(0, 0, 1.0).Normalized()
        self.rotX = 0
        self.rotY = ((math.pi/2)-0.1)
        self.posz = -3.0
        self.posx = 0
        self.posy = 0
        """
        self.qPitch = Quaternion()
        self.qHeading = Quaternion()
        self.pitchDegrees = 0.0
        self.headingDegrees = 0.0
        self.directionVector = Vector()
        self.forwardVelocity = 1.0
        self.pos = Vector(0.0, 0.0, 0.0)

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
        """
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
        """
        self.pitchDegrees += float(ymoved)/10.0
        if self.pitchDegrees >= 89.9:
            self.pitchDegrees = 89.9
        if self.pitchDegrees <= -89.9:
            self.pitchDegrees = -89.9
        self.headingDegrees += float(xmoved)/10.0

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
            if AppSt.chunks.InWater(self.pos.x, self.pos.y, -self.pos.z):
                forVector = self.GetDirV().Normalized().MultScalar(AppSt.speed*factor)
            else:
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


        """
        self.posx += x
        self.posy += y
        self.posz += z
        if self.posz > -0.15:
            self.posz = -0.15
        if self.posz < -10.0:
            self.posz = -10.0
        """


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

g_id = 0
BLOCK_EMPTY = GenId()
BLOCK_WATER = GenId()
BLOCK_GLASS = GenId()
BLOCK_LAVA = GenId()
BLOCK_COBBLESTONE = GenId()
BLOCK_LOG = GenId()
BLOCK_WALL = GenId()
BLOCK_BRICK = GenId()
BLOCK_TNT = GenId()
BLOCK_STONE = GenId()

BLOCK_SAND = GenId()
BLOCK_GRAVEL = GenId()
BLOCK_WOOD = GenId()
BLOCK_LEAVES = GenId()
BLOCK_SILVER = GenId()
BLOCK_GOLD = GenId()
BLOCK_COALORE = GenId()
BLOCK_IRONORE = GenId()
BLOCK_DIAMONDORE = GenId()
BLOCK_IRON = GenId()

BLOCK_DIAMOND = GenId()
BLOCK_CPU = GenId()
BLOCK_CODE = GenId()
BLOCK_ENERGY = GenId()
BLOCK_KEYBIND = GenId()
BLOCK_PANELSWITCH = GenId()
BLOCK_LEVER = GenId()
BLOCK_WALLSWITCH = GenId()
BLOCK_NUMPAD = GenId()
BLOCK_TELEPORT = GenId()

BLOCK_JUMPER = GenId()
BLOCK_ELEVATOR = GenId()
BLOCK_ENGINECORE = GenId()
BLOCK_CONSTRUCTIONSITE = GenId()
BLOCK_AREASELECTOR = GenId()
BLOCK_GOLDORE = GenId()
BLOCK_SILVERORE = GenId()
BLOCK_WOOL = GenId()
BLOCK_GRASS = GenId()
BLOCK_DIRT = GenId()
BLOCK_INDESTRUCTABLE = GenId()
BLOCK_CHEST = GenId()
BLOCK_SPAWNER = GenId()
BLOCK_SILVERSLOT = GenId()
BLOCK_GOLDSLOT = GenId()
BLOCK_DIAMONDSLOT = GenId()
BLOCK_COLOR = GenId()



class Item(object):
    def __init__(self, type_, count, stackable = False, name="Item", color=None, inv=None, element=None, stats=[], skill=None):
        self.type_ = type_
        self.maxLen = 64
        self.stackable = stackable
        self.name = name
        self.count = count
        self.color = color
        self.colorIdx = 0
        self.optionalInventory = inv
        self.element = element
        self.stats = stats
        self.textTitleIdx = []
        self.textDescIdx = []
        self.skill = skill
        self.enchantCount = 0
        self.maxEnchant = 3

class Skill(Item):
    def __init__(self, skill):
        Item.__init__(self, ITEM_SKILL, 1, False, "Skill", skill=skill)

class Block(Item):
    def __init__(self, type_, count):
        Item.__init__(self, type_, count, True, "Block")

class Inventory(object):
    def __init__(self):
        self.items = [None for i in range(60)]
        self.quickItems = [None for i in range(10)]

class WorldObject(object):
    def __init__(self, time_, type_, pos):
        self.t = time_
        self.type_ 
        self.pos = pos

BLOCK_TEX_COORDS = [0,0, 0,0, 0,0,
        14,0, 14,0, 14,0,
        1,3, 1,3, 1,3,
        1,5, 1,5, 1,5,
        1,0, 1,0, 1,0,
        5,1, 4,1, 5,1,
        3,5, 3,5, 3,5,
        7,0, 7,0, 7,0,
        9,0, 8,0, 10,0,
        0,1, 0,1, 0,1,

        2,1, 2,1, 2,1,
        3,1, 3,1, 3,1,
        4,0, 4,0, 4,0,
        6,1, 6,1, 6,1,
        7,1, 7,2, 7,3,
        8,1, 8,2, 8,3,
        2,2, 2,2, 2,2,
        0,2, 0,2, 0,2,
        1,6, 1,6, 1,6,
        0,0, 0,0, 0,0,

        0,0, 0,0, 0,0,
        9,4, 9,4, 9,4,
        7,4, 7,4, 7,4,
        10,4, 10,4, 10,4,
        11,4, 11,4, 11,4,
        0,0, 0,0, 0,0,
        0,0, 0,0, 0,0,
        0,0, 0,0, 0,0,
        0,0, 0,0, 0,0,
        0,0, 0,0, 0,0,
        0,0, 0,0, 0,0,

        0,0, 0,0, 0,0,
        0,0, 0,0, 0,0,
        0,0, 0,0, 0,0,
        0,0, 0,0, 0,0,
        12,6, 12,6, 12,6,
        13,6, 13,6, 13,6,
        0,0, 0,0, 0,0,
        0,0, 3,0, 2,0,
        2,0, 2,0, 2,0,
        2,7,2,7,2,7,
        11,0,11,0,11,0,
        8,4, 8,4, 8,4,

        4,4, 4,4, 4,4,
        5,4, 5,4, 5,4,
        6,4, 6,4, 6,4,
        0,4,0,4,0,4,
    ]


def DrawCubeArm(pos,bound, color, tex1,tex2,tex3,tex4,tex5,tex6, texid, flipX = False, offset=64.0): # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
    x,y,z = pos
    w,h,j = bound
    x -= w/2
    y -= 0#h/2
    z -= j/2

    vidx = [ 
            (4, 5, 1, 0),  # bottom    
            (6,7,3, 2),  # top
            (3, 7, 4, 0),  # left
            (6,2,1, 5),  # right
            (7,6,5, 4),  # back
            (2,3,0, 1),  # front
            ]

    v = [   (0.0+x, 0.0+y-h, j+z),
            (w+x, 0.0+y-h, j+z),
            (w+x, y, j+z),
            (0.0+x, y, j+z),
            (0.0+x, 0.0+y-h, 0.0+z),
            (w+x, 0.0+y-h, 0.0+z),
            (w+x, y, 0.0+z),
            (0.0+x, y, 0.0+z) ]

    offset = offset/512.0
    for face in range(6):
        if face == 0:
            texc = [
                    (tex1[0]+offset, tex1[1]),
                    (tex1[0], tex1[1]),
                    (tex1[0], tex1[1]+offset),
                    (tex1[0]+offset, tex1[1]+offset),
                    ]
        elif face == 1:
            texc = [
                    (tex2[0]+offset, tex2[1]),
                    (tex2[0], tex2[1]),
                    (tex2[0], tex2[1]+offset),
                    (tex2[0]+offset, tex2[1]+offset),
                    ]

        elif face == 2:
            texc = [
                    (tex3[0]+offset, tex3[1]),
                    (tex3[0], tex3[1]),
                    (tex3[0], tex3[1]+offset),
                    (tex3[0]+offset, tex3[1]+offset),
                    ]

        elif face == 3:
            texc = [
                    (tex4[0]+offset, tex4[1]),
                    (tex4[0], tex4[1]),
                    (tex4[0], tex4[1]+offset),
                    (tex4[0]+offset, tex4[1]+offset),
                    ]

        elif face == 4:
            if flipX:
                texc = [
                        (tex5[0], tex5[1]),
                        (tex5[0]+offset, tex5[1]),
                        (tex5[0]+offset, tex5[1]+offset),
                        (tex5[0], tex5[1]+offset),
                        ]

            else:
                texc = [
                        (tex5[0]+offset, tex5[1]),
                        (tex5[0], tex5[1]),
                        (tex5[0], tex5[1]+offset),
                        (tex5[0]+offset, tex5[1]+offset),
                        ]

        elif face == 5:
            if flipX:
                texc = [
                        (tex6[0], tex6[1]),
                        (tex6[0]+offset, tex6[1]),
                        (tex6[0]+offset, tex6[1]+offset),
                        (tex6[0], tex6[1]+offset),
                        ]

            else:
                texc = [
                        (tex6[0]+offset, tex6[1]),
                        (tex6[0], tex6[1]),
                        (tex6[0], tex6[1]+offset),
                        (tex6[0]+offset, tex6[1]+offset),
                        ]

        v1, v2, v3, v4 = vidx[face]
        glBegin(GL_QUADS)
        glColor4ub(*color)
        glTexCoord2f(*texc[0])
        glVertex( v[v1] )
        glTexCoord2f(*texc[1])
        glVertex( v[v2] )
        glTexCoord2f(*texc[2])
        glVertex( v[v3] )
        glTexCoord2f(*texc[3])
        glVertex( v[v4] )            
        glEnd()
        """
        glDisable(GL_TEXTURE_2D)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glVertex( v[v1] )
        glVertex( v[v2] )
        glVertex( v[v2] )
        glVertex( v[v3] )
        glVertex( v[v3] )
        glVertex( v[v4] )            
        glVertex( v[v4] )            
        glVertex( v[v1] )
        glEnd()
        glEnable(GL_TEXTURE_2D)
        """
def DrawCubeStair(pos,bound, color, tex1,tex2,tex3,tex4,tex5,tex6, texid, flipX = False, offset=32.0): # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
    x,y,z = pos
    w,h,j = bound
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

    offset = offset/512.0
    for face in range(6):
        if face == 0:
            texc = [
                    (tex1[0]+offset, tex1[1]),
                    (tex1[0], tex1[1]),
                    (tex1[0], tex1[1]+offset),
                    (tex1[0]+offset, tex1[1]+offset),
                    ]
        elif face == 1:
            texc = [
                    (tex2[0]+offset, tex2[1]),
                    (tex2[0], tex2[1]),
                    (tex2[0], tex2[1]+offset),
                    (tex2[0]+offset, tex2[1]+offset),
                    ]

        elif face == 2:
            texc = [
                    (tex3[0]+offset, tex3[1]),
                    (tex3[0], tex3[1]),
                    (tex3[0], tex3[1]+offset),
                    (tex3[0]+offset, tex3[1]+offset),
                    ]

        elif face == 3:
            texc = [
                    (tex4[0]+offset, tex4[1]),
                    (tex4[0], tex4[1]),
                    (tex4[0], tex4[1]+offset),
                    (tex4[0]+offset, tex4[1]+offset),
                    ]

        elif face == 4:
            if flipX:
                texc = [
                        (tex5[0], tex5[1]),
                        (tex5[0]+offset, tex5[1]),
                        (tex5[0]+offset, tex5[1]+offset),
                        (tex5[0], tex5[1]+offset),
                        ]

            else:
                texc = [
                        (tex5[0]+offset, tex5[1]),
                        (tex5[0], tex5[1]),
                        (tex5[0], tex5[1]+offset),
                        (tex5[0]+offset, tex5[1]+offset),
                        ]

        elif face == 5:
            if flipX:
                texc = [
                        (tex6[0], tex6[1]),
                        (tex6[0]+offset, tex6[1]),
                        (tex6[0]+offset, tex6[1]+offset),
                        (tex6[0], tex6[1]+offset),
                        ]

            else:
                texc = [
                        (tex6[0]+offset, tex6[1]),
                        (tex6[0], tex6[1]),
                        (tex6[0], tex6[1]+offset),
                        (tex6[0]+offset, tex6[1]+offset),
                        ]

        v1, v2, v3, v4 = vidx[face]
        glBegin(GL_QUADS)
        glColor4ub(*color)
        glTexCoord2f(*texc[0])
        glVertex( v[v1] )
        glTexCoord2f(*texc[1])
        glVertex( v[v2] )
        glTexCoord2f(*texc[2])
        glVertex( v[v3] )
        glTexCoord2f(*texc[3])
        glVertex( v[v4] )            
        glEnd()
def DrawCube(pos,bound, color, tex1,tex2,tex3,tex4,tex5,tex6, texid, flipX = False, offset=64.0): # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
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

    offset = offset/512.0
    for face in range(6):
        if face == 0:
            texc = [
                    (tex1[0]+offset, tex1[1]),
                    (tex1[0], tex1[1]),
                    (tex1[0], tex1[1]+offset),
                    (tex1[0]+offset, tex1[1]+offset),
                    ]
        elif face == 1:
            texc = [
                    (tex2[0]+offset, tex2[1]),
                    (tex2[0], tex2[1]),
                    (tex2[0], tex2[1]+offset),
                    (tex2[0]+offset, tex2[1]+offset),
                    ]

        elif face == 2:
            texc = [
                    (tex3[0]+offset, tex3[1]),
                    (tex3[0], tex3[1]),
                    (tex3[0], tex3[1]+offset),
                    (tex3[0]+offset, tex3[1]+offset),
                    ]

        elif face == 3:
            texc = [
                    (tex4[0]+offset, tex4[1]),
                    (tex4[0], tex4[1]),
                    (tex4[0], tex4[1]+offset),
                    (tex4[0]+offset, tex4[1]+offset),
                    ]

        elif face == 4:
            if flipX:
                texc = [
                        (tex5[0], tex5[1]),
                        (tex5[0]+offset, tex5[1]),
                        (tex5[0]+offset, tex5[1]+offset),
                        (tex5[0], tex5[1]+offset),
                        ]

            else:
                texc = [
                        (tex5[0]+offset, tex5[1]),
                        (tex5[0], tex5[1]),
                        (tex5[0], tex5[1]+offset),
                        (tex5[0]+offset, tex5[1]+offset),
                        ]

        elif face == 5:
            if flipX:
                texc = [
                        (tex6[0], tex6[1]),
                        (tex6[0]+offset, tex6[1]),
                        (tex6[0]+offset, tex6[1]+offset),
                        (tex6[0], tex6[1]+offset),
                        ]

            else:
                texc = [
                        (tex6[0]+offset, tex6[1]),
                        (tex6[0], tex6[1]),
                        (tex6[0], tex6[1]+offset),
                        (tex6[0]+offset, tex6[1]+offset),
                        ]

        v1, v2, v3, v4 = vidx[face]
        glBegin(GL_QUADS)
        glColor4ub(*color)
        glTexCoord2f(*texc[0])
        glVertex( v[v1] )
        glTexCoord2f(*texc[1])
        glVertex( v[v2] )
        glTexCoord2f(*texc[2])
        glVertex( v[v3] )
        glTexCoord2f(*texc[3])
        glVertex( v[v4] )            
        glEnd()
        """
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glVertex( v[v1] )
        glVertex( v[v2] )
        glVertex( v[v2] )
        glVertex( v[v3] )
        glVertex( v[v3] )
        glVertex( v[v4] )            
        glVertex( v[v4] )            
        glVertex( v[v1] )
        glEnd()
        """

g_id = 0
ANIM_IDLE = GenId()
ANIM_WALK = GenId()
ANIM_ATTACK = GenId()
ANIM_HIT = GenId()

g_id = 0
MOB_SKELETON = GenId()
MOB_NPC = GenId()


MobRSt = None
class MobRenderer(object):
    def __init__(self, skins):
        global MobRSt
        MobRSt = self
        self.dLists = {}
        self.skins = skins
    def RenderMob(self, mobType, pos, bound, angle, frame, anim):
        x,y,z = pos
        y -= bound[1]
        glPushMatrix()
        glTranslatef(x,y,z)
        glRotatef(-angle+90, 0.0, 1.0, 0.0)
        glCallList(self.dLists[mobType][anim][frame])
        glPopMatrix()
    def RebuildMobs(self, bound):
        """
        factor = self.animIdx/self.animMax
        """

        w,h,l = bound
        self.color = (255,255,255,255)
        for mob in self.skins:
            self.dLists[mob] = [[glGenLists(1) for j in range(60)] for k in range(4)]
            animstate = 0
            while animstate < 4:
                animIdx = -30
                while animIdx < 30:
                    factor = float(animIdx)/30.0
                    tex1,tex2,tex3,tex4,tex5,tex6 = self.skins[mob][0]
                    glNewList(self.dLists[mob][animstate][animIdx+30], GL_COMPILE)
                    glPushMatrix()
                    h = 1.5
                    top = h-(0.25)+0.5
                    glTranslatef(0,top,0)
                    if animstate == ANIM_HIT:
                        glRotatef(-30, 1.0, 0.0, 0.0)
                    DrawCube((0,0,0), (0.25, 0.25, 0.15), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
                    glPopMatrix()

                    tex1,tex2,tex3,tex4,tex5,tex6 = self.skins[mob][1]
                    glPushMatrix()
                    mid = h-(0.25)+0.25/2-(0.5)+0.5
                    glTranslatef(0,0+mid,0)
                    glRotatef(0, 0.0, 1.0, 0.0)
                    DrawCube((0,0,0),(0.4, 0.5, 0.25), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
                    glPopMatrix()

                    tex1,tex2,tex3,tex4,tex5,tex6 = self.skins[mob][2]
                    glPushMatrix()
                    glTranslatef(0-0.25,0+mid+0.25,0)
                    if animstate == ANIM_WALK:
                        glRotatef(factor*45, 1.0, 0.0, 0.0)
                    elif animstate == ANIM_IDLE:
                        pass
                    elif animstate == ANIM_ATTACK:
                        glRotatef(-90, 1.0, 0.0, 0.0)
                        glRotatef(factor*45, 1.0, 0.0, 0.0)
                        glRotatef(factor*45, 0.0, 0.0, 1.0)
                    elif animstate == ANIM_HIT:
                        glRotatef(-30, 1.0, 0.0, 0.0)

                    DrawCubeArm((0,0,0),(0.1, 0.5, 0.1), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
                    glPopMatrix() # 오른팔

                    tex1,tex2,tex3,tex4,tex5,tex6 = self.skins[mob][3]
                    glPushMatrix()
                    glTranslatef(0+0.25,0+mid+0.25,0)
                    if animstate == ANIM_WALK:
                        glRotatef(-factor*45, 1.0, 0.0, 0.0)
                    elif animstate == ANIM_IDLE:
                        pass
                    elif animstate == ANIM_HIT:
                        glRotatef(-30, 1.0, 0.0, 0.0)
                    DrawCubeArm((0,0,0),(0.1, 0.5, 0.1), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
                    glPopMatrix() # 왼팔

                    tex1,tex2,tex3,tex4,tex5,tex6 = self.skins[mob][4]
                    glPushMatrix()
                    glTranslatef(0-0.075,0+mid-0.5+0.25,0)
                    if animstate == ANIM_WALK:
                        glRotatef(-factor*45, 1.0, 0.0, 0.0)
                    elif animstate == ANIM_IDLE:
                        pass
                    DrawCubeArm((0,0,0),(0.15, 0.5, 0.15), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
                    glPopMatrix() # 오른발

                    tex1,tex2,tex3,tex4,tex5,tex6 = self.skins[mob][5]
                    glPushMatrix()
                    glTranslatef(0+0.075,0+mid-0.5+0.25,0)
                    if animstate == ANIM_WALK:
                        glRotatef(factor*45, 1.0, 0.0, 0.0)
                    elif animstate == ANIM_IDLE:
                        pass
                    DrawCubeArm((0,0,0),(0.15, 0.5, 0.15), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex, True) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
                    glPopMatrix() # 왼발
                    glEndList()

                    animIdx += 1

                animstate += 1

class MobGL(object):
    def __init__(self, pos, bound, skin, type_, color, entity, name=None):
        self.pos = pos
        self.bound = bound
        self.skin = skin
        self.name = name


        self.type_ = type_
        self.color = color
        self.entity = entity

        self.animstate = ANIM_IDLE
        self.animMax = 30.0
        self.animIdx = -self.animMax
        self.t = 0
        self.fps = 15.0/6.0
        self.flip = False

        self.dList = None
        self.genDone = False


        self.prevY = 0.0
        self.jumpStartT = 0
        self.jumping = False
        self.canJump = False
        self.jumpTime = 350
        self.jumpHeight = 1.9
        self.prevFactor = 0.0
        self.prevFall = -1

        self.prevJump = 0
        self.jumpDelay = 700
        self.prevJumpY = 0.0
        self.speed = 0.15
        self.angle = 0.0
        # 방향이동, 점프등을 구현한다.
        # 이동하는 방향으로 dir벡터를 구하고
        # dir벡터의 각도를 구해서 회전을 한다.
        # 점프를 하면서 막 플레이어의 위치로 이동하면 됨
        self.attackDelay = 3000
        self.prevAtk = 0
        self.prevWalk = 0
        if self.type_ == MOB_SKELETON:
            self.entity.BindHit(self.OnHit)
            self.entity.BindDead(self.OnDead)
        self.prevHit = 0
        self.hitRecovery = 250



    def OnDead(self, attacker):
        if self.type_ == MOB_SKELETON:
            AppSt.mobs.remove(self)
            AppSt.gui.msgBox.AddText("Mob is dead.", (68,248,93), (8,29,1))
            if not self.type_ in AppSt.mobKillLog:
                AppSt.mobKillLog[self.type_] = 0
            AppSt.mobKillLog[self.type_] += 1
    def OnHit(self, attacker):
        self.animstate = ANIM_HIT
        self.prevHit = pygame.time.get_ticks()
    def Tick(self,t,m,k):
        def AIAttacker():
            if self.PlayerInSpot():
                if self.Range() > 1.2:
                    if t-self.prevJump > self.jumpDelay:
                        self.prevJump = t
                        if self.canJump and not self.jumping:
                            self.StartJump(t)
                    self.WalkToPlayer(t-self.prevWalk)
                    self.UpdateDirection()
                else:
                    if t - self.prevAtk > self.attackDelay:
                        self.prevAtk = t
                        self.UpdateDirection()
                        self.AttackPlayer()
                    elif t - self.prevAtk > self.attackDelay/6:
                        self.animIdx = -self.animMax
                        self.flip = False
                        self.animstate = ANIM_IDLE
            else:
                self.animIdx = -self.animMax
                self.flip = False
                self.animstate = ANIM_IDLE
        if self.type_ == MOB_SKELETON:
            if t - self.prevHit > self.hitRecovery:
                AIAttacker()
            self.prevWalk = t
        self.FallOrJump(t)

    def AttackPlayer(self):
        self.entity.Attack(AppSt.entity)
        AppSt.sounds["Hit2"].play()
        self.animIdx = -self.animMax
        self.flip = False
        self.animstate = ANIM_ATTACK
    def Range(self):
        pos = AppSt.cam1.pos
        pos = Vector(pos.x,0,-pos.z)
        mypos = Vector(self.pos[0], 0, self.pos[2])
        return (mypos-pos).Length()
    def PlayerInSpot(self):
        pos = AppSt.cam1.pos
        pos = Vector(pos.x,pos.y,-pos.z)
        mypos = Vector(*self.pos)
        if (mypos-pos).Length() < 10.0:
            return True
        else:
            return False

    def UpdateDirection(self):
        pos = AppSt.cam1.pos
        pos = Vector(pos.x,pos.y,-pos.z)
        mypos = Vector(*self.pos)
        dirV = pos-mypos
        dirV.y = 0
        dirV = dirV.Normalized()
        self.angle = Vector2ToAngle(dirV.x, dirV.z)
    def WalkToPlayer(self, theT):
        self.animstate = ANIM_WALK
        pos = AppSt.cam1.pos
        pos = Vector(pos.x,pos.y,-pos.z)
        mypos = Vector(*self.pos)
        dirV = pos-mypos
        dirV.y = 0
        factor = float(theT)*20.0/1000.0

        if factor < 0.0:
            factor = 0.0
        while factor >= 1.0:
            dirV = dirV.Normalized().MultScalar(self.speed)
            self.pos = x,y,z = AppSt.chunks.FixPos(mypos, mypos+dirV, self.bound)
            factor -= 1.0
        dirV = dirV.Normalized().MultScalar(self.speed*factor)
        self.pos = x,y,z = AppSt.chunks.FixPos(mypos, mypos+dirV, self.bound)


    def CheckJump(self, y):
        if self.prevY - 0.15 <= y <= self.prevY + 0.15:
            self.canJump = True
        else:
            self.canJump = False
        self.prevY = y

    def StartJump(self, t):
        self.jumpStartT = t
        self.jumping = True
        self.canJump = False
    def DoJump(self, t):
        if t-self.jumpStartT < self.jumpTime:
            x,y,z = self.pos
            factor = (float(t)-float(self.jumpStartT))/float(self.jumpTime)
            jump = (factor-self.prevFactor)*self.jumpHeight
            self.prevFactor = factor
            
            x,y,z = AppSt.chunks.FixPos(Vector(x,y,z), Vector(x,y+jump,z), self.bound)
            self.pos = x,y,z
            if y == self.prevJumpY:
                self.prevFactor = 0.0
                self.jumping = False
            self.prevJumpY = y
        else:
            self.prevFactor = 0.0
            self.jumping = False

    def FallOrJump(self, t):
        if self.jumping:
            self.DoJump(t)
            self.prevFall = t
        else:
            x,y,z = self.pos
            if not AppSt.chunks.InWater(x,y,z) and not AppSt.chunks.InWater(x,y-1.0,z):
                factor = (t-self.prevFall)*35.0/1000.0
                if factor < 0.0:
                    factor = 0.0
                while factor >= 1.0:
                    x,y,z = AppSt.chunks.FixPos(Vector(x,y,z), Vector(x,y-(self.speed),z), self.bound)
                    factor -= 1.0
                x,y,z = AppSt.chunks.FixPos(Vector(x,y,z), Vector(x,y-(self.speed*factor),z), self.bound)
                if x >= 0:
                    xx = int(x)
                else:
                    xx = int(x-1.0)

                yy = int(y-1.19)
                if z >= 0:
                    zz = int(z)
                else:
                    zz = int(z-1.0)
                xxx = xx-(xx%32)
                yyy = yy-(yy%32)
                zzz = zz-(zz%32)
                if (xxx,yyy,zzz) in AppSt.stairs:
                    for stair in AppSt.stairs[(xxx,yyy,zzz)]:
                        x1,y1,z1,f,b = stair
                        if x1 <= x <= x1+1.0 and z1 <= z <= z1+1.0 and y1+1.19 <= y <= y1+2.20:
                            plus = 0
                            if f == 2:
                                x2 = x
                                plus = (x2-math.floor(x2))
                            if f == 3:
                                x2 = x
                                plus = 1.0-(x2-math.floor(x2))
                            if f == 4:
                                z2 = z
                                plus = (z2-math.floor(z2))
                            if f == 5:
                                z2 = z
                                plus = 1.0-(z2-math.floor(z2))
                            plus *= 2
                            if plus > 1.0:
                                plus = 1.0
                            x,y,z = AppSt.chunks.FixPos(Vector(x,y,z), Vector(x,float(y1)+1.20+plus,z), self.bound)

                self.pos = x,y,z
                self.CheckJump(y)
            self.prevFall = t

    def SetAnimState(self, s):
        self.animstate = s
    def Render2(self, nameRenderer, cam, t):
        """
        if not self.genDone or AppSt.regenTex:
            self.dList = [glGenLists(1) for i in range(6)]
        """
        glBindTexture(GL_TEXTURE_2D, AppSt.mobtex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        idx = int(self.animIdx)+30
        if idx > 59:
            idx = 59
        if idx < 0:
            idx = 0
        MobRSt.RenderMob(self.type_, self.pos, self.bound, self.angle, idx, self.animstate)

        if self.t and self.flip:
            self.animIdx -= (t-self.t)/float(self.fps)
        elif self.t:
            self.animIdx += (t-self.t)/float(self.fps)
        if self.animIdx > self.animMax:
            self.animIdx = self.animMax
            self.flip = True
        elif self.animIdx < -self.animMax:
            self.animIdx = -self.animMax
            self.flip = False
        self.t = t


        """

        x,y,z = self.pos
        y -= self.bound[1]
        w,h,l = self.bound

        factor = self.animIdx/self.animMax
        glPushMatrix()
        glTranslatef(x,y,z)
        glRotatef(-self.angle+90, 0.0, 1.0, 0.0)

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[0]
        glPushMatrix()
        h = 1.5
        top = h-(0.25)+0.5
        glTranslatef(0,top,0)
        if self.animstate == ANIM_HIT:
            glRotatef(-30, 1.0, 0.0, 0.0)
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[0], GL_COMPILE)
            DrawCube((0,0,0), (0.25, 0.25, 0.15), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[0])
        glPopMatrix()

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[1]
        glPushMatrix()
        mid = h-(0.25)+0.25/2-(0.5)+0.5
        glTranslatef(0,0+mid,0)
        glRotatef(0, 0.0, 1.0, 0.0)
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[1], GL_COMPILE)
            DrawCube((0,0,0),(0.4, 0.5, 0.25), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[1])

        glPopMatrix()

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[2]
        glPushMatrix()
        glTranslatef(0-0.25,0+mid+0.25,0)
        if self.animstate == ANIM_WALK:
            glRotatef(factor*45, 1.0, 0.0, 0.0)
        elif self.animstate == ANIM_IDLE:
            pass
        elif self.animstate == ANIM_ATTACK:
            glRotatef(-90, 1.0, 0.0, 0.0)
            glRotatef(factor*45, 1.0, 0.0, 0.0)
            glRotatef(factor*45, 0.0, 0.0, 1.0)
        elif self.animstate == ANIM_HIT:
            glRotatef(-30, 1.0, 0.0, 0.0)

        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[2], GL_COMPILE)
            DrawCubeArm((0,0,0),(0.1, 0.5, 0.1), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[2])
        glPopMatrix() # 오른팔

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[3]
        glPushMatrix()
        glTranslatef(0+0.25,0+mid+0.25,0)
        if self.animstate == ANIM_WALK:
            glRotatef(-factor*45, 1.0, 0.0, 0.0)
        elif self.animstate == ANIM_IDLE:
            pass
        elif self.animstate == ANIM_HIT:
            glRotatef(-30, 1.0, 0.0, 0.0)
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[3], GL_COMPILE)
            DrawCubeArm((0,0,0),(0.1, 0.5, 0.1), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[3])
        glPopMatrix() # 왼팔

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[4]
        glPushMatrix()
        glTranslatef(0-0.075,0+mid-0.5+0.25,0)
        if self.animstate == ANIM_WALK:
            glRotatef(-factor*45, 1.0, 0.0, 0.0)
        elif self.animstate == ANIM_IDLE:
            pass
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[4], GL_COMPILE)
            DrawCubeArm((0,0,0),(0.15, 0.5, 0.15), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[4])
        glPopMatrix() # 오른발

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[5]
        glPushMatrix()
        glTranslatef(0+0.075,0+mid-0.5+0.25,0)
        if self.animstate == ANIM_WALK:
            glRotatef(factor*45, 1.0, 0.0, 0.0)
        elif self.animstate == ANIM_IDLE:
            pass
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[5], GL_COMPILE)
            DrawCubeArm((0,0,0),(0.15, 0.5, 0.15), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex, True) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[5])
        glPopMatrix() # 왼발


        self.genDone = True
        if self.t and self.flip:
            self.animIdx -= (t-self.t)/float(self.fps)
        elif self.t:
            self.animIdx += (t-self.t)/float(self.fps)
        if self.animIdx > self.animMax:
            self.animIdx = self.animMax
            self.flip = True
        elif self.animIdx < -self.animMax:
            self.animIdx = -self.animMax
            self.flip = False
        self.t = t

        glPopMatrix()
        """
    def Render(self, nameRenderer, cam, t):
        if not self.genDone or AppSt.regenTex:
            self.dList = [glGenLists(1) for i in range(6)]
        glBindTexture(GL_TEXTURE_2D, AppSt.mobtex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)



        x,y,z = self.pos
        y -= self.bound[1]
        w,h,l = self.bound

        factor = self.animIdx/self.animMax
        glPushMatrix()
        glTranslatef(x,y,z)
        glRotatef(-self.angle+90, 0.0, 1.0, 0.0)

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[0]
        glPushMatrix()
        h = 1.5
        top = h-(0.25)+0.5
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[0], GL_COMPILE)
            glTranslatef(0,top,0)
            if self.animstate == ANIM_HIT:
                glRotatef(-30, 1.0, 0.0, 0.0)
            DrawCube((0,0,0), (0.25, 0.25, 0.15), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[0])
        glPopMatrix()

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[1]
        glPushMatrix()
        mid = h-(0.25)+0.25/2-(0.5)+0.5
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[1], GL_COMPILE)
            glTranslatef(0,0+mid,0)
            glRotatef(0, 0.0, 1.0, 0.0)
            DrawCube((0,0,0),(0.4, 0.5, 0.25), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[1])

        glPopMatrix()

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[2]
        glPushMatrix()
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[2], GL_COMPILE)
            glTranslatef(0-0.25,0+mid+0.25,0)
            if self.animstate == ANIM_WALK:
                glRotatef(factor*45, 1.0, 0.0, 0.0)
            elif self.animstate == ANIM_IDLE:
                pass
            elif self.animstate == ANIM_ATTACK:
                glRotatef(-90, 1.0, 0.0, 0.0)
                glRotatef(factor*45, 1.0, 0.0, 0.0)
                glRotatef(factor*45, 0.0, 0.0, 1.0)
            elif self.animstate == ANIM_HIT:
                glRotatef(-30, 1.0, 0.0, 0.0)

            DrawCubeArm((0,0,0),(0.1, 0.5, 0.1), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[2])
        glPopMatrix() # 오른팔

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[3]
        glPushMatrix()
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[3], GL_COMPILE)
            glTranslatef(0+0.25,0+mid+0.25,0)
            if self.animstate == ANIM_WALK:
                glRotatef(-factor*45, 1.0, 0.0, 0.0)
            elif self.animstate == ANIM_IDLE:
                pass
            elif self.animstate == ANIM_HIT:
                glRotatef(-30, 1.0, 0.0, 0.0)
            DrawCubeArm((0,0,0),(0.1, 0.5, 0.1), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[3])
        glPopMatrix() # 왼팔

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[4]
        glPushMatrix()
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[4], GL_COMPILE)
            glTranslatef(0-0.075,0+mid-0.5+0.25,0)
            if self.animstate == ANIM_WALK:
                glRotatef(-factor*45, 1.0, 0.0, 0.0)
            elif self.animstate == ANIM_IDLE:
                pass
            DrawCubeArm((0,0,0),(0.15, 0.5, 0.15), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[4])
        glPopMatrix() # 오른발

        tex1,tex2,tex3,tex4,tex5,tex6 = self.skin[5]
        glPushMatrix()
        if not self.genDone or AppSt.regenTex:
            glNewList(self.dList[5], GL_COMPILE)
            glTranslatef(0+0.075,0+mid-0.5+0.25,0)
            if self.animstate == ANIM_WALK:
                glRotatef(factor*45, 1.0, 0.0, 0.0)
            elif self.animstate == ANIM_IDLE:
                pass
            DrawCubeArm((0,0,0),(0.15, 0.5, 0.15), self.color, tex1,tex2,tex3,tex4,tex5,tex6, AppSt.mobtex, True) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
            glEndList()
        else:
            glCallList(self.dList[5])
        glPopMatrix() # 왼발


        self.genDone = True
        if self.t and self.flip:
            self.animIdx -= (t-self.t)/float(self.fps)
        elif self.t:
            self.animIdx += (t-self.t)/float(self.fps)
        if self.animIdx > self.animMax:
            self.animIdx = self.animMax
            self.flip = True
        elif self.animIdx < -self.animMax:
            self.animIdx = -self.animMax
            self.flip = False
        self.t = t

        glPopMatrix()

class FightingElements(object):
    def __init__(self, name, pos, params):
        self.name = name
        self.pos = pos
        self.params = params

    def OnAttack(self, attacker, defenders):
        # 이렇게 하지 말고 일단 전투를 구현한 다음에 하나하나 유틸라이즈하자.
        pass
    def ApplyEnchantScroll(self, type_, scroll):
        for param in scroll.element.params:
            if param == "Melee Damage" and type_ == ITEM_SPEAR:
                scroll.element.params[param] *= 2
            if param in self.params:
                self.params[param] += scroll.element.params[param]
            else:
                self.params[param] = scroll.element.params[param]

g_id = 0
SKILL_PHYSICAL = GenId()
SKILL_FIRE = GenId()
SKILL_ICE = GenId()
SKILL_ELECTRIC = GenId()
SKILL_POISON = GenId()
SKILL_HEAL = GenId()
SKILL_CURE = GenId()
SKILL_STR = GenId()
SKILL_DEX = GenId()
SKILL_INT = GenId()
SKILL_BASEHP = GenId()
SKILL_BASEMP = GenId()
SKILL_SKILL = GenId()
g_id = 0
TARGET_SELF = GenId()
TARGET_OTHER = GenId()
class RawSkill(object):
    def __init__(self, name, params):
        self.value = params["value"]
        self.incFactor = params["incFactor"]  # 데미지는 sword스킬일경우 sword스킬레벨이 올라갈 때마다 증가한다. 여기서 정한 퍼센티지로 선형적으로 증가한다
        self.skilltype = params["stype"] # 공격이냐 버프냐 힐이냐, 공격이면 물리냐 4속성이냐 등등
        self.targettype = params["ttype"] # self나 other
        self.targetskillname = "" # CombinedSkill의 이름
        self.name = name
        self.duration = params["dur"] # 0이면 순간적용, 0 초과면 그만금의 초동안 적용

    def SetSkillName(self, name):
        self.targetskillname = name

    def CalculateMagicDefense(self, target, stype):
        dfn = 0
        if stype == SKILL_PHYSICAL:
            dfn = target.dfn
        if stype == SKILL_ICE:
            dfn = target.ires
        if stype == SKILL_FIRE:
            dfn = target.fres
        if stype == SKILL_POISON:
            dfn = target.pres
        if stype == SKILL_ELECTRIC:
            dfn = target.eres
        for item in target.eqs:
            if item:
                if "Defense" in item.element.params:
                    if stype == SKILL_PHYSICAL:
                        dfn += item.element.params["Defense"]
                if "Ice Resist" in item.element.params:
                    if stype == SKILL_ICE:
                        dfn += item.element.params["Ice Resist"]
                if "Fire Resist" in item.element.params:
                    if stype == SKILL_FIRE:
                        dfn += item.element.params["Fire Resist"]
                if "Poison Resist" in item.element.params:
                    if stype == SKILL_POISON:
                        dfn += item.element.params["Poison Resist"]
                if "Electric Resist" in item.element.params:
                    if stype == SKILL_ELECTRIC:
                        dfn += item.element.params["Electric Resist"]
        dfn *= (target.int**1.8/target.int)
        return dfn

    def Apply(self, user, target, skill, skillBonus):
        intBonus = 0
        for item in user.eqs:
            if item and item.element and "Int" in item.element.params:
                intBonus += item.element.params["Int"]
        magicBonus = 0
        for item in user.eqs:
            if item and item.element and "Magic Skill" in item.element.params:
                magicBonus += item.element.params["Magic Skill"]

        if self.targettype == TARGET_SELF:
            if self.skilltype == SKILL_HEAL:
                heal = (self.value*((skill.skillPoint+skillBonus)*self.incFactor))*((intBonus+user.int)**1.8/(user.int+intBonus))
                heal *= (magicBonus+user.magic)**1.2/(magicBonus+user.magic)
                user.curhp += heal
                if user.curhp > user.CalcMaxHP():
                    user.curhp = user.CalcMaxHP()
                return heal


        elif self.targettype == TARGET_OTHER and target:
            if self.skilltype == SKILL_PHYSICAL:
                atkBonus = 0
                for item in user.eqs:
                    if item and item.element and "Melee Damage" in item.element.params:
                        atkBonus += item.element.params["Melee Damage"]

                dmg = ((atkBonus+user.atk+self.value*((skill.skillPoint+skillBonus)*self.incFactor)))*((intBonus+user.int)**1.8/(user.int+intBonus))
                user.atk += ((user.atk)**1.5/(user.atk))/100.0
                target.dfn += (target.dfn**1.5/target.dfn)/100.0 # 타겟은 기본적으로 정의되어있지 아이템이 입은게 아니므로 그냥 한다.
            if self.skilltype == SKILL_FIRE:
                fatkBonus = 0
                for item in user.eqs:
                    if item and item.element and "Fire Damage" in item.element.params:
                        fatkBonus += item.element.params["Fire Damage"]
                dmg = ((fatkBonus+user.fatk+self.value*((skill.skillPoint+skillBonus)*self.incFactor)))*((intBonus+user.int)**1.8/(user.int+intBonus))
                user.fatk += ((user.fatk)**1.5/(user.fatk))/100.0
                target.fres += (target.fres**1.5/target.fres)/100.0
            if self.skilltype == SKILL_ICE:
                fatkBonus = 0
                for item in user.eqs:
                    if item and item.element and "Ice Damage" in item.element.params:
                        fatkBonus += item.element.params["Ice Damage"]
                dmg = ((fatkBonus+user.iatk+self.value*((skill.skillPoint+skillBonus)*self.incFactor)))*((intBonus+user.int)**1.8/(user.int+intBonus))
                user.iatk += (user.iatk**1.5/user.iatk)/100.0
                target.ires += (user.fres**1.5/user.ires)/100.0
            if self.skilltype == SKILL_ELECTRIC:
                fatkBonus = 0
                for item in user.eqs:
                    if item and item.element and "Electric Damage" in item.element.params:
                        fatkBonus += item.element.params["Electric Damage"]
                dmg = ((fatkBonus+user.eatk+self.value*((skill.skillPoint+skillBonus)*self.incFactor)))*((intBonus+user.int)**1.8/(user.int+intBonus))
                user.eatk += (user.eatk**1.5/user.eatk)/100.0
                target.eres += (target.eres**1.5/target.eres)/100.0
            if self.skilltype == SKILL_POISON:
                fatkBonus = 0
                for item in user.eqs:
                    if item and item.element and "Poison Damage" in item.element.params:
                        fatkBonus += item.element.params["Poison Damage"]
                dmg = ((fatkBonus+user.patk+self.value*((skill.skillPoint+skillBonus)*self.incFactor)))*((intBonus+user.int)**1.8/(user.int+intBonus))
                user.patk += (user.patk**1.5/user.patk)/100.0
                target.pres += (target.pres**1.5/target.pres)/100.0


            dmg *= (magicBonus+user.magic)**1.2/(magicBonus+user.magic)
            target.curhp -= dmg
            if target.curhp > target.CalcMaxHP():
                target.curhp = target.CalcMaxHP()
            target.onhit(user)
            if target.curhp < 0:
                target.ondead(user)
                if AppSt.curAttackingMob == target:
                    AppSt.curAttackingMob = None
            return dmg
        return 0



class CombinedSkill(object): # 위의 생스킬을 합쳐서 스킬하나를 만든다.
    def __init__(self, name, raws, texcoord, params):
        self.raws = raws
        self.name = name
        self.minreq = params["minreq"] # 스킬을 사용할 수 있는 sword스킬레벨 제한
        self.range = params["range"]
        self.cost = params["cost"]
        self.texcoord = texcoord
        self.skillPoint = 1.0
        self.textTitleIdx = []
        self.textDescIdx = []
    def Apply(self, user, target): # 레인지 검사는 MobGL이나 DIgDigApp에서
        mpcost = (self.cost*(self.skillPoint*0.5))
        if user.curmp > mpcost:
            user.curmp -= mpcost
            dmg = 0
            skillBonus = 0
            for item in user.eqs:
                if item and item.element and self.name in item.element.params:
                    skillBonus += item.element.params[self.name]

            for raw in self.raws:
                dmg += raw.Apply(user, target, self, skillBonus)
            self.skillPoint += (self.skillPoint/self.skillPoint**1.5)/100.0
            user.magic += (user.magic/user.magic**1.5)/100.0
            user.int += (user.int/user.int**1.5)/100.0
            if self.name == "Heal":
                if user == AppSt.entity:
                    AppSt.gui.msgBox.AddText("You heal yourself: %d" % dmg, (68,248,93), (8,29,1))
                else:
                    AppSt.gui.msgBox.AddText("Mob uses heal: %d" % dmg, (248,98,68), (73,16,5))
            else:
                magicT = self.name
                if user == AppSt.entity:
                    AppSt.gui.msgBox.AddText("You use %s: %d" % (magicT, dmg), (68,248,93), (8,29,1))
                else:
                    AppSt.gui.msgBox.AddText("Mob uses %s: %d" % (magicT, dmg), (248,98,68), (73,16,5))


class FightingEntity(object):
    def __init__(self, name, params):
        # 복잡하게 str이 체력을 올려주고 이러지 말고
        # str은 밀리무기 공격력
        # dex는 레인지 무기 공격력
        # int는 마법파워 이렇게 올리고
        # 여러가지를 둔다.
        # 연사력은 그냥 다 똑같음?
        # 멀티는 하지 말고 싱글만 만들자.
        self.name = name
        self.basehp = params["HP"]
        self.basemp = params["MP"]
        self.str = params["Str"]
        self.dex = params["Dex"]
        self.int = params["Int"]
        self.atk = params["Melee Damage"]
        self.dfn = params["Defense"]
        self.patk = params["Poison Damage"]
        self.eatk = params["Electric Damage"]
        self.iatk = params["Ice Damage"]
        self.fatk = params["Fire Damage"]
        self.pres = params["Poison Resist"]
        self.eres = params["Electric Resist"]
        self.ires = params["Ice Resist"]
        self.fres = params["Fire Resist"]
        self.sword = params["Sword Skill"] # 스트렝스, 무기는 다 스트렝스
        self.mace = params["Mace Skill"] 
        self.spear = params["Spear Skill"]
        self.knuckle = params["Knuckle Skill"]
        self.armor = params["Armor Skill"] # 덱스를 올림
        self.magic = params["Magic Skill"]
        self.swordSkills = {}
        self.maceSkills = {}
        self.spearSkills = {}
        self.knuckleSkills = {}
        self.armorSkills = {}
        fireEle = RawSkill("Fire", {"value": 5, "incFactor": 1.2, "stype": SKILL_FIRE, "ttype": TARGET_OTHER, "dur": 0})
        iceEle = RawSkill("Ice", {"value": 5, "incFactor": 1.2, "stype": SKILL_ICE, "ttype": TARGET_OTHER, "dur": 0})
        elecEle = RawSkill("Electric", {"value": 5, "incFactor": 1.2, "stype": SKILL_ELECTRIC, "ttype": TARGET_OTHER, "dur": 0})
        poisonEle = RawSkill("Poison", {"value": 5, "incFactor": 1.2, "stype": SKILL_POISON, "ttype": TARGET_OTHER, "dur": 0})
        healEle = RawSkill("Heal", {"value": 5, "incFactor": 1.2, "stype": SKILL_HEAL, "ttype": TARGET_SELF, "dur": 5})
        self.magics = {"Fireball": Skill(CombinedSkill("Fireball", [fireEle], [4,2], {"minreq": 0, "range": 10, "cost": 2})), "Lightning": Skill(CombinedSkill("Lightning", [elecEle], [4,3], {"minreq": 0, "range": 10, "cost": 2})), "Poison": Skill(CombinedSkill("Poison", [poisonEle], [4,4], {"minreq": 0, "range": 10, "cost": 2})), "Snowball": Skill(CombinedSkill("Snowball", [iceEle], [4,5], {"minreq": 0, "range": 10, "cost": 2})), "Heal": Skill(CombinedSkill("Heal", [healEle], [4,6], {"minreq": 0, "range": 0, "cost": 2}))}
        self.eqs = [] # 몹일경우 여기에 담고
        self.inventory = [] # 플레이어일경우 그냥 링크일 뿐
        self.curhp = self.CalcMaxHP()
        self.curmp = self.CalcMaxMP()
        # 순수하게 element만 담으면 뭔가 퍼즐이 맞을 거 같지만 아이템 자체를 담아야함.
        # 아이템의 속성에 texture뭘쓸건지도 나중에 넣어줘야함. 종류가 많아지면 후덜덜...XXX:
        # 하여간에 그리하여 공격 방어는 entity끼리 싸우게 된다.
        # 음...아니면 걍 텍스쳐 종류는 적은 수로 유지하고 컬러만 바꾸도록 해보자. 컬러가 달라도 다른 품질일 수도 있고말이지.
        # 블럭들은 마우스를 댔을때 설명이 필요없다.
        # 하지만 토치 상자등이나 코드블럭 스포너 아이템등은 설명이 필요하다.
        # 코드와 스포너를 잘써서 타워디펜스를 만들 수도 있을 것이고 상점을 만들 수도 있을 것이고 뭐....
        # NPC는 또다른 코드블럭이다. 단지, npc는 스포너가 없고 메뉴 인터랙션으로 출력을 하는 정도?
        self.ondead = self.OnDead
        self.onhit = self.OnDead
        self.karma = 0 # 성향에 따라 Evil, Good, Neutral의 여러 중간단계로 나뉨? 음.... 카르마가 게임에 미치는 영향은 어떨까

    def OnDead(self, other):
        pass
    def CalcMaxHP(self):
        strBonus = 0
        for item in self.eqs:
            if item and item.element and "Str" in item.element.params:
                strBonus += item.element.params["Str"]
        return self.basehp + ((self.str+strBonus)**1.5/(self.str+strBonus))*25
    def CalcMaxMP(self):
        intBonus = 0
        for item in self.eqs:
            if item and item.element and "Int" in item.element.params:
                intBonus += item.element.params["Int"]
        return self.basemp + ((self.int+intBonus)**1.5/(self.int+intBonus))*25
    def BindDead(self, func):
        self.ondead = func

    def BindHit(self, func):
        self.onhit = func

    def CalculateAttack(self):
        atk = self.atk
        for item in self.eqs:
            if item and item.element and "Melee Damage" in item.element.params:
                atk += item.element.params["Melee Damage"] # 보너스로 웨폰 스킬로 데미지 퍼센티지로 추가

        for item in self.eqs[:2]:
            if not item:
                continue
            if item.type_ == ITEM_SWORD:
                swordBonus = 0
                for item in self.eqs:
                    if item and item.element and "Sword Skill" in item.element.params:
                        swordBonus += item.element.params["Sword Skill"] # 보너스로 웨폰 스킬로 데미지 퍼센티지로 추가
                atk *= (self.sword+swordBonus)**1.2/(self.sword+swordBonus)
                break
            elif item.type_ == ITEM_SPEAR:
                spearBonus = 0
                for item in self.eqs:
                    if item and item.element and "Spear Skill" in item.element.params:
                        spearBonus += item.element.params["Spear Skill"] # 보너스로 웨폰 스킬로 데미지 퍼센티지로 추가
                atk *= (self.spear+spearBonus)**1.2/(self.spear+spearBonus)
                break
            elif item.type_ == ITEM_MACE:
                maceBonus = 0
                for item in self.eqs:
                    if item and item.element and "Mace Skill" in item.element.params:
                        maceBonus += item.element.params["Mace Skill"] # 보너스로 웨폰 스킬로 데미지 퍼센티지로 추가
                atk *= (self.mace+maceBonus)**1.2/(self.mace+maceBonus)
                break
            elif item.type_ == ITEM_KNUCKLE:
                knuckleBonus = 0
                for item in self.eqs:
                    if item and item.element and "Knuckle Skill" in item.element.params:
                        knuckleBonus += item.element.params["Knuckle Skill"] # 보너스로 웨폰 스킬로 데미지 퍼센티지로 추가
                atk *= (self.knuckle+knuckleBonus)**1.2/(self.knuckle+knuckleBonus)
                break
        strBonus = 0
        for item in self.eqs:
            if item and item.element and "Str" in item.element.params:
                strBonus += item.element.params["Str"]

        atk *= (self.str+strBonus)**1.2/(self.str+strBonus)
        self.str += (self.str/self.str**1.5)/100.0
        self.atk += (self.atk/self.atk**1.5)/100.0
        return atk

    def CalculateDmg(self, dfn):
        atk = self.CalculateAttack()
        return atk - dfn

    def CalculateDefense(self):
        dfn = self.dfn
        armorBonus = 0
        for item in self.eqs:
            if item and item.element and "Defense" in item.element.params:
                dfn += item.element.params["Defense"]
            if item and item.element and "Armor Skill" in item.element.params:
                armorBonus += item.element.params["Armor Skill"]
        found = False
        for item in self.eqs:
            if item and item.type_ in [ITEM_SHIELD,ITEM_HELM,ITEM_ARMOR,ITEM_BOOTS,ITEM_GLOVES]:
                found = True
                break
        if found:
            dfn *= ((armorBonus+self.armor)**1.2/(armorBonus+self.armor))
            self.armor += (self.armor/self.armor**1.5)/100.0

        dexBonus = 0
        for item in self.eqs:
            if item and item.element and "Dex" in item.element.params:
                dexBonus += item.element.params["Dex"]

        dfn *= (self.dex+dexBonus)**1.2/(self.dex+dexBonus)
        self.dex += (self.dex/self.dex**1.5)/100.0
        self.dfn += (self.dfn/self.dfn**1.5)/100.0
        return dfn

    def Attack(self, other):
        for item in self.eqs[:1]:
            if not item:
                continue
            if item.type_ == ITEM_SWORD:
                self.sword += (self.sword/self.sword**1.5)/100.0
                break
            elif item.type_ == ITEM_SPEAR:
                self.spear += (self.spear/self.spear**1.5)/100.0
                break
            elif item.type_ == ITEM_MACE:
                self.mace += (self.mace/self.mace**1.5)/100.0
                break
            elif item.type_ == ITEM_KNUCKLE:
                self.knuckle += (self.knuckle/self.knuckle**1.5)/100.0
                break

        dmg = self.CalculateDmg(other.CalculateDefense())
        if other == AppSt.entity:
            AppSt.gui.msgBox.AddText("Mob attacks you: %d" % dmg, (248,98,68), (73,16,5))
        else:
            AppSt.gui.msgBox.AddText("You attack mob: %d" % dmg, (68,248,93), (8,29,1))

        other.curhp -= dmg
        if other.curhp > other.CalcMaxHP():
            other.curhp = other.CalcMaxHP()
        other.onhit(self)
        if other.IsDead():
            other.ondead(self)
            if AppSt.curAttackingMob == other:
                AppSt.curAttackingMob = None

    def IsDead(self):
        if self.curhp <= 0:
            return True
        else:
            return False


AppSt = None

from threading import Thread
import copy

class DigDigScript(object):
    def __init__(self):
        pass

    def SaveRegion(self, name_, min, max, ymin, ymax):
        assert type(min) in [str, unicode]
        assert type(max) in [str, unicode]
        spawners = {}
        for coord in AppSt.gui.spawns:
            name = AppSt.gui.spawns[coord]
            spawners[name] = coord
        min, max = spawners[min], spawners[max]
        min = list(min)
        max = list(max)
        if min[0] > max[0]:
            max[0], min[0] = min[0], max[0]
        if min[2] > max[2]:
            max[2], min[2] = min[2], max[2]
        if ymin > ymax:
            ymax, ymin = ymin, ymax
        AppSt.chunks.SaveRegion(name_, (min[0], ymin, min[2]), (max[0], ymax, max[2]))

    def LoadRegion(self, name_, pos):
        assert type(pos) in [str, unicode]
        spawners = {}
        for coord in AppSt.gui.spawns:
            name = AppSt.gui.spawns[coord]
            spawners[name] = coord
        pos = spawners[pos]
        AppSt.chunks.LoadRegion(name_, pos)
        del AppSt.gui.spawns[pos]
        # 스포너 뿐만이 아니라, 덮어씌울때 모든 아이템이나 상자등을 다 어떻게 처리한다? 아예, 그곳에 상자나 아이템이 있으면 로드하지 못하게
        # 막아야 할 것 같다. XXX:
        # 또한 복사할 때 스포너나 아이템이 복사되지 않도록 해야한다.(상자, 스포너, 코드블락)?
        # 음......여러가지 장치를 해둔 경우 그것도 복사하고 싶겠지만 그건 걍 포기??
        # 그것도 다 복사되게 해야하는 듯. 특히 복사하는 용도의 스포너는 복사하지 않고, 그 외의 스포너는 복사를 하되
        # 만약 스포너의 이름이 중복되는 경....음.................
        #
        # 아예 어드민의 용도로만 사용하게 하도록 하자 그냥;;
        # XXX: 이제 부수지 못하도록 스포너 2개로 Lockdown거는 것을 구현하자. 락다운을 걸면 땅의 주인만 락다운을 풀 수가 있음
        # 땅의 소유지를 결정하는 것도 스포너 2개로.

    def QuestDoneCheck(self, *args):
        # 각각의 arg는 함수, 파라메터의 2개짜리 튜플이나 리스트
        pass
    def CheckKillMob(self, mobid, number):
        pass
    def CheckGatherItem(self, itemtype, itemid, number):
        pass
    def CheckQuestFlag(self, questid, npcname):
        pass
    def SpawnNPC(self, name, pos, quest):
        # 같은 이름의 npc가 없다면 스폰 있으면 스킵
        pass
    def SpawnMob(self, pos):
        assert type(pos) in [str, unicode]
        spawners = {}
        for coord in AppSt.gui.spawns:
            name = AppSt.gui.spawns[coord]
            spawners[name] = coord
        pos = spawners[pos]
        skin = [
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 0*64.0/512.0)],
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (1*64.0/512.0, 0*64.0/512.0),
            (1*64.0/512.0, 0*64.0/512.0)],
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0)],
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0)],
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (1*64.0/512.0, 1*64.0/512.0),
            (1*64.0/512.0, 1*64.0/512.0)],
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (1*64.0/512.0, 1*64.0/512.0),
            (1*64.0/512.0, 1*64.0/512.0)]]

        entity = FightingEntity("Mob1", {"HP": 100, "MP": 100, "Str": 5, "Dex": 5, "Int": 5, "Melee Damage":5,"Defense":5,"Poison Damage":5,"Poison Resist":5,"Electric Damage":5,"Electric Resist":5,"Ice Damage":5,"Ice Resist":5,"Fire Damage":5,"Fire Resist":5,"Sword Skill":5,"Mace Skill":5,"Spear Skill":5,"Knuckle Skill":5,"Armor Skill":5,"Magic Skill":5})
        entity.curhp = entity.CalcMaxHP()
        entity.curmp = entity.CalcMaxMP()
        AppSt.mobs += [MobGL((pos[0]+0.5, pos[1]+3.0+0.5, pos[2]+0.5), [0.8,1.7,0.8], skin, MOB_SKELETON, (200,200,200,255), entity)]
class ScriptLauncher(object):
    def __init__(self, coord):
        self.code = ''
        self.lastError = ''
        self.coord = coord
        # 일정 시간이 지나면 강제종료하는 루틴도 넣는다?
        # 서버에 랙이 있다면?
        from RestrictedPython.Guards import full_write_guard
        def getmyitem(obj, name):
            if name in AppSt.gui.spawns.itervalues():
                return obj[name]
            else:
                return None

        def getmyattr(obj, name):
            assert name in ["SpawnMob", "SaveRegion", "LoadRegion"], "Cannot access that attribute"
            return getattr(obj,name)
        self.r = dict(__builtins__ = {'digdig': DigDigScript(), 'None': None, 'True': True, 'False': False, '_getitem_':getmyitem, '_write_':full_write_guard, '_getattr_':getmyattr})


    def run(self):
        if not self.code:
            return
        self.code = self.code.replace("while", "while not supported")
        self.code = self.code.replace("for", "for not supported")
        self.code = self.code.replace("def", "def not supported")
        self.code = self.code.replace("class", "class not supported")
        self.code = self.code.replace("print", "print not supported")
        self.code = self.code.replace("exec", "exec not supported")
        self.code = self.code.replace("lambda", "lambda not supported")
        self.code = self.code.replace("import", "import not supported")
        self.code = self.code.replace("del", "del not supported")
        # XXX: while이나 for같은 루프는 함수 수준에서 간략하게 지원한다.
        spawners = {}
        for coord in AppSt.gui.spawns:
            name = AppSt.gui.spawns[coord]
            spawners[name] = coord
        self.r["spawners"] = spawners

        from RestrictedPython import compile_restricted
        code = compile_restricted(self.code, 'CodeBlock (%d, %d, %d)' % self.coord, 'exec')

        try:
            exec(code) in self.r
        except:
            import traceback
            self.lastError = traceback.format_exc()
            print self.lastError

class DigDigApp(object):
    def __init__(self):
        global AppSt
        AppSt = self
        self.keyBinds = {
                "UP": K_w,
                "LEFT": K_a,
                "DOWN": K_s,
                "RIGHT": K_d,
                "ATK": K_j,
                "JUMP": K_SPACE,}
        self.delay = 50
        self.renderDelay = 1000/15
        self.prevTime = 0
        self.renderPrevTime = 0
        self.soundPrevTime = 0
        self.soundDelay = 1000/4
        self.bound = (0.5,1.7,0.5)
        self.prevY = 0.0
        self.jumpStartT = 0
        self.jumping = False
        self.canJump = False
        self.jumpTime = 350
        self.jumpHeight = 1.9
        self.prevFactor = 0.0
        self.prevFall = -1
        self.prevJumpY = 0.0
        self.speed = 0.23
        self.guiMode = False
        self.guiPrevTime = 0
        self.guiRenderDelay = 500
        self.show = True
        self.prevDig = 0
        self.digDelay = 80
        self.prevBlock = None
        self.lastBlock = None
        self.blockHP = -1
        self.maxBlockHP = -1
        self.blockItems = []
        self.digging = False
        
        self.attackDelay = 1000
        self.prevAttack = 0


        self.surf = pygame.Surface((512,512), flags =SRCALPHA)


    def DropItem(self, item):
        print 'DropItem'
    def DoCam(self, t, m, k):
        if not self.guiMode:
            self.cam1.RotateByXY(m.x-SW/2, m.y-SH/2)
            pygame.mouse.set_pos(SW/2, SH/2)
    def StartJump(self, t):
        self.jumpStartT = t
        self.jumping = True
        self.canJump = False
    def DoJump(self, t):
        if t-self.jumpStartT < self.jumpTime:
            x = self.cam1.pos.x
            y = self.cam1.pos.y
            z = -self.cam1.pos.z
            factor = (float(t)-float(self.jumpStartT))/float(self.jumpTime)
            jump = (factor-self.prevFactor)*self.jumpHeight
            self.prevFactor = factor
            
            x,y,z = self.chunks.FixPos(Vector(x,y,z), Vector(x,y+jump,z), self.bound)
            self.cam1.pos = Vector(x,y,-z)
            if y == self.prevJumpY:
                self.prevFactor = 0.0
                self.jumping = False
            self.prevJumpY = y
        else:
            self.prevFactor = 0.0
            self.jumping = False

    def FallOrJump(self, t):
        if self.jumping:
            self.DoJump(t)
            self.prevFall = t
        else:
            if not self.chunks.InWater(self.cam1.pos.x, self.cam1.pos.y, -self.cam1.pos.z) and not self.chunks.InWater(self.cam1.pos.x, self.cam1.pos.y-1.0, -self.cam1.pos.z):
                x = self.cam1.pos.x
                y = self.cam1.pos.y
                z = -self.cam1.pos.z
                factor = (t-self.prevFall)*35.0/1000.0
                if factor < 0.0:
                    factor = 0.0
                while factor >= 1.0:
                    x,y,z = self.chunks.FixPos(Vector(x,y,z), Vector(x,y-(self.speed),z), self.bound)
                    factor -= 1.0
                x,y,z = self.chunks.FixPos(Vector(x,y,z), Vector(x,y-(self.speed*factor),z), self.bound)

                # 여기서 계단위에 있으면 그만큼 좌표를 올려준다.
                if x >= 0:
                    xx = int(x)
                else:
                    xx = int(x-1.0)

                yy = int(y-1.19)
                if z >= 0:
                    zz = int(z)
                else:
                    zz = int(z-1.0)
                xxx = xx-(xx%32)
                yyy = yy-(yy%32)
                zzz = zz-(zz%32)
                if (xxx,yyy,zzz) in self.stairs:
                    for stair in self.stairs[(xxx,yyy,zzz)]:
                        x1,y1,z1,f,b = stair
                        if x1 <= x <= x1+1.0 and z1 <= z <= z1+1.0 and y1+1.19 <= y <= y1+2.20:
                            plus = 0
                            if f == 2:
                                x2 = x
                                plus = (x2-math.floor(x2))
                            if f == 3:
                                x2 = x
                                plus = 1.0-(x2-math.floor(x2))
                            if f == 4:
                                z2 = z
                                plus = (z2-math.floor(z2))
                            if f == 5:
                                z2 = z
                                plus = 1.0-(z2-math.floor(z2))
                            plus *= 2
                            if plus > 1.0:
                                plus = 1.0
                            x,y,z = self.chunks.FixPos(Vector(x,y,z), Vector(x,float(y1)+1.20+plus,z), self.bound)

                self.cam1.pos = Vector(x,y,-z)

                self.CheckJump(y)
            self.prevFall = t

    def RenderStairs(self, frustum):
        for xyz in self.stairs:
            stairs = self.stairs[xyz]
            if xyz not in self.stairsDL:
                self.stairsDL[xyz] = {}
            for stair in stairs:
                x,y,z,f,b = stair
                if (x,y,z) not in self.stairsDL[xyz] or self.regenTex:
                    self.stairsDL[xyz][(x,y,z)] = dList = glGenLists(1)
                    glNewList(dList, GL_COMPILE)
                    if b == ITEM_STAIR:
                        b = BLOCK_STONE
                    elif b == ITEM_WOODENSTAIR:
                        b = BLOCK_WOOD

                    texupx = (BLOCK_TEX_COORDS[b*2*3 + 0]*32.0) / 512.0
                    texupy = (BLOCK_TEX_COORDS[b*2*3 + 1]*32.0) / 512.0
                    texmidx = (BLOCK_TEX_COORDS[b*2*3 + 2]*32.0) / 512.0
                    texmidy = (BLOCK_TEX_COORDS[b*2*3 + 3]*32.0) / 512.0
                    texbotx = (BLOCK_TEX_COORDS[b*2*3 + 4]*32.0) / 512.0
                    texboty = (BLOCK_TEX_COORDS[b*2*3 + 5]*32.0) / 512.0

                    tex1 = texupx,texupy
                    tex2 = texbotx,texboty
                    tex3 = texmidx,texmidy
                    tex4 = texmidx,texmidy
                    tex5 = texmidx,texmidy
                    tex6 = texmidx,texmidy
                    if f == 2: # 왼쪽을 향한 계단
                        DrawCubeStair((x,y,z), (1.0,0.33,1.0), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                        DrawCubeStair((x+0.33,y+0.33,z), (0.66,0.33,1.0), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                        DrawCubeStair((x+0.66,y+0.66,z), (0.33,0.33,1.0), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                    elif f == 3:
                        DrawCubeStair((x,y,z), (1.0,0.33,1.0), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                        DrawCubeStair((x,y+0.33,z), (0.66,0.33,1.0), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                        DrawCubeStair((x,y+0.66,z), (0.33,0.33,1.0), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                    elif f == 4:
                        DrawCubeStair((x,y,z), (1.0,0.33,1.0), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                        DrawCubeStair((x,y+0.33,z+0.33), (1.0,0.33,0.66), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                        DrawCubeStair((x,y+0.66,z+0.66), (1.0,0.33,0.33), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                    elif f == 5:
                        DrawCubeStair((x,y,z), (1.0,0.33,1.0), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                        DrawCubeStair((x,y+0.33,z), (1.0,0.33,0.66), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                        DrawCubeStair((x,y+0.66,z), (1.0,0.33,0.33), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, AppSt.tex)
                    glEndList()


                if self.chunks.CubeInFrustumPy(x+0.5,y+0.5,z+0.5,0.5,frustum):
                    glBindTexture(GL_TEXTURE_2D, self.tex)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
                    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
                    glCallList(self.stairsDL[xyz][(x,y,z)])

                # 큐브 3개로 계단을 만든다. 스톤 텍스쳐를 이용하면 된다.
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

            if pressed[self.keyBinds["JUMP"]]:
                if self.canJump and not self.jumping:
                    self.StartJump(t)
            #if t - self.prevTime > self.delay:
            xyz2 = self.cam1.pos#Vector(x,y,z)+((self.cam1.pos - Vector(x,y,z)).Normalized())
            x2,y2,z2 = xyz2.x, xyz2.y, xyz2.z

            x3,y3,z3 = self.chunks.FixPos(Vector(x,y,-z), Vector(x2,y2,-z2), self.bound)
            self.cam1.pos = Vector(x3,y3,-z3)

        self.prevTime = t
        self.CheckJump(self.cam1.pos.y)

    def RPressing(self,t,m,k):
        if not self.gui.invShown:
            mob = self.GetMob()
            if mob:
                self.OnMobRHit(mob, t)
                self.chColor = self.BLUE_CH
                return
    def RUp(self,t,m,k):
        self.chColor = self.WHITE_CH

    def DoSlot(self, b):
        item = self.gui.qbar[self.gui.selectedItem]
        if item and item.name == "Item" and item.type_ in [ITEM_SILVER, ITEM_GOLD, ITEM_DIAMOND]:
            item.count -= 1
            if item.count == 0:
                self.gui.qbar[self.gui.selectedItem] = ITEM_NONE
        else:
            self.gui.msgBox.AddText("You need silver or gold or diamond to operate a slotmachine.", (68,248,93), (8,29,1))
            return
        self.gui.msgBox.AddText("Spinning...", (0,0,0), (8,29,1))
        rand = random.randint(0,200000)
        if 0 <= rand <= 50000:
            if item.name == "Item" and item.type_ == ITEM_SILVER:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % (2), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_SILVER, 2, color = (201,201,201), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_GOLD:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % (3), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_SILVER, 3, color = (201,201,201), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_DIAMOND:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % (4), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_SILVER, 4, color = (201,201,201), stackable=True))
        elif 50001 <= rand <= 80000:
            if item.name == "Item" and item.type_ == ITEM_SILVER:
                self.gui.msgBox.AddText("Result: You've earned %d golds" % (2), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_GOLD, 2, color = (207,207,101), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_GOLD:
                self.gui.msgBox.AddText("Result: You've earned %d golds" % (3), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_GOLD, 3, color = (207,207,101), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_DIAMOND:
                self.gui.msgBox.AddText("Result: You've earned %d golds" % (4), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_GOLD, 4, color = (207,207,101), stackable=True))
        elif 80001 <= rand <= 100000:
            if item.name == "Item" and item.type_ == ITEM_SILVER:
                self.gui.msgBox.AddText("Result: You've earned %d diamonds" % (2), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_DIAMOND, 2, color = (80,212,217), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_GOLD:
                self.gui.msgBox.AddText("Result: You've earned %d diamonds" % (3), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_DIAMOND, 3, color = (80,212,217), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_DIAMOND:
                self.gui.msgBox.AddText("Result: You've earned %d diamonds" % (4), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_DIAMOND, 4, color = (80,212,217), stackable=True))
        elif 100001 <= rand <= 100666:
            if item.name == "Item" and item.type_ == ITEM_SILVER:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % (64), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_SILVER, 64, color = (201,201,201), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_GOLD:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % int(64*1.5), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_SILVER, 64, color = (201,201,201), stackable=True))
                self.gui.PutItemInInventory(Item(ITEM_SILVER, 32, color = (201,201,201), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_DIAMOND:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % (64*2), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_SILVER, 64, color = (201,201,201), stackable=True))
                self.gui.PutItemInInventory(Item(ITEM_SILVER, 64, color = (201,201,201), stackable=True))
        elif 100667 <= rand <= 101332:
            if item.name == "Item" and item.type_ == ITEM_SILVER:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % (64), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_GOLD, 64, color = (207,207,101), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_GOLD:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % int(64*1.5), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_GOLD, 64, color = (207,207,101), stackable=True))
                self.gui.PutItemInInventory(Item(ITEM_GOLD, 32, color = (207,207,101), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_DIAMOND:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % (64*2), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_GOLD, 64, color = (207,207,101), stackable=True))
                self.gui.PutItemInInventory(Item(ITEM_GOLD, 64, color = (207,207,101), stackable=True))
        elif 101333 <= rand <= 102000:
            if item.name == "Item" and item.type_ == ITEM_SILVER:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % (64), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_DIAMOND, 64, color = (80,212,217), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_GOLD:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % int(64*1.5), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_DIAMOND, 64, color = (80,212,217), stackable=True))
                self.gui.PutItemInInventory(Item(ITEM_DIAMOND, 32, color = (80,212,217), stackable=True))
            elif item.name == "Item" and item.type_ == ITEM_DIAMOND:
                self.gui.msgBox.AddText("Result: You've earned %d silvers" % (64*2), (68,248,93), (8,29,1))
                self.gui.PutItemInInventory(Item(ITEM_DIAMOND, 64, color = (80,212,217), stackable=True))
                self.gui.PutItemInInventory(Item(ITEM_DIAMOND, 64, color = (80,212,217), stackable=True))
        elif 102001 <= rand <= 102011:
            # XXX: 여기에 엔딩을 넣고 인벤이 꽉찼을 경우 나중에 이 박스를 인벤 비우고 다시 얻을 수 있게 저장한다.
            if item.name == "Item" and item.type_ == ITEM_SILVER:
                self.gui.msgBox.AddText("Jackpot! You've earned 10 chest full of diamonds", (68,248,93), (8,29,1))
                for i in range(10):
                    self.gui.PutItemInInventory(Item(ITEM_CHEST, 1, color=(255,255,255), stackable=False, inv=[Item(ITEM_DIAMOND, 64, color = (80,212,217), stackable=True) for i in range(60)]))
            elif item.name == "Item" and item.type_ == ITEM_GOLD:
                self.gui.msgBox.AddText("Jackpot! You've earned 15 chests full of diamonds", (68,248,93), (8,29,1))
                for i in range(15):
                    self.gui.PutItemInInventory(Item(ITEM_CHEST, 1, color=(255,255,255), stackable=False, inv=[Item(ITEM_DIAMOND, 64, color = (80,212,217), stackable=True) for i in range(60)]))
            elif item.name == "Item" and item.type_ == ITEM_DIAMOND:
                self.gui.msgBox.AddText("Jackpot! You've earned 20 chests full of diamonds", (68,248,93), (8,29,1))
                for i in range(20):
                    self.gui.PutItemInInventory(Item(ITEM_CHEST, 1, color=(255,255,255), stackable=False, inv=[Item(ITEM_DIAMOND, 64, color = (80,212,217), stackable=True) for i in range(60)]))
        else:
            self.gui.msgBox.AddText("Result: You've earned nothing", (0,0,0), (8,29,1))
        

    def RDown(self, t, m, k):
        # 이제 여기서 가지고있는 블럭을 쌓도록 한다.
        # 아이템 스폰할 때 오어를 스폰하고 블럭은 스폰하지 않도록도 한다. XXX:
        # 아 그런데 이제 박스같은거 클릭하면 그거 열고 그래야하네
        # 상자 동서남북은 어떻게 할까. extra block flag가 있어서 블럭이 그거면
        # 다른 버퍼에서 읽어온다는....

        # 음....아이템을 넣으면 거기에 BLOCK_ITEM을 넣어서
        # 그 블럭을 해체하면 아이템도 해체할 수 있도록 해야겠다.
        # 만약 오른클릭한게 슬롯머신이라면 슬롯머신 코드를 실행한다.
        if not self.gui.invShown:
            mob = self.GetMob()
            if mob:
                self.OnMobRHit(mob, t)
                self.chColor = self.BLUE_CH
                return
        if not self.gui.invShown:
            npc = self.GetNPC()
            if npc:
                self.OnNPCRHit(npc, t)
                self.chColor = self.BLUE_CH
                return

        item = self.gui.qbar[self.gui.selectedItem]
        if item and item.name == "Skill":
            if t - self.prevAttack > self.attackDelay:
                self.prevAttack = t
                item.skill.Apply(self.entity, None)
            return
        if not self.lastBlock:
            return
        x,y,z,f,b = self.lastBlock
        if b in [BLOCK_SILVERSLOT, BLOCK_GOLDSLOT, BLOCK_DIAMONDSLOT]:
            self.DoSlot(b)
            return
        pos = self.cam1.pos
        pos = Vector(pos.x, pos.y, -pos.z)
        dir_ = self.cam1.GetDirV()
        dir_ = Vector(dir_.x, dir_.y, -dir_.z)
        dir_ = dir_.Normalized()
        dir_ = dir_.MultScalar(math.sqrt(2)*9.0)
        dir_ += pos

        if self.IsStairThere(x,y,z):
            return
        if not self.gui.invShown:
            if (x,y,z) in self.gui.boxes:
                self.gui.selectedBox = self.gui.boxes[(x,y,z)]
                self.gui.toolMode = TM_BOX
                self.guiMode = True
                self.gui.ShowInventory(True)
                return
            if (x,y,z) in self.gui.spawns:
                def Delete():
                    block, items, color = self.chunks.DigBlock(x,y,z)
                    if block:
                        self.SpawnBlockItems(x,y,z, block, color)
                    del self.gui.spawns[(x,y,z)]

                def SetName(name):
                    if name not in self.gui.spawns.values():
                        self.gui.spawns[(x,y,z)] = name

                self.gui.toolMode = TM_SPAWN
                self.guiMode = True
                self.gui.ShowInventory(True)
                self.gui.testEdit.Bind(SetName)
                self.gui.testEdit.BindDestroy(Delete)
                self.gui.testEdit.text = self.gui.spawns[(x,y,z)]
                return

            if (x,y,z) in self.gui.codes:
                def Delete():
                    block, items, color = self.chunks.DigBlock(x,y,z)
                    if block:
                        self.SpawnBlockItems(x,y,z, block, color)
                    del self.gui.codes[(x,y,z)]
                def SetCode(fileN):
                    self.gui.codes[(x,y,z)] = fileN
                    self.scripts[(x,y,z)] = ScriptLauncher((x,y,z))
                self.gui.toolMode = TM_CODE
                self.guiMode = True
                self.gui.ShowInventory(True)
                self.gui.testFile.Bind(SetCode)
                self.gui.testFile.BindDestroy(Delete)
                self.gui.testFile.selectedFileName = self.gui.codes[(x,y,z)]
                return

            item = self.gui.qbar[self.gui.selectedItem]
            for mob in self.npcs:
                if self.chunks.CheckCollide(x,y,z,Vector(mob.pos[0], mob.pos[1]-mob.bound[1], mob.pos[2]),mob.bound):
                    # 몹과 충돌을 한다면 바로 return한다.
                    return
            for mob in self.mobs:
                if self.chunks.CheckCollide(x,y,z,Vector(mob.pos[0], mob.pos[1]-mob.bound[1], mob.pos[2]),mob.bound):
                    # 몹과 충돌을 한다면 바로 return한다.
                    return

            if item and item.name == "Block":

                mat = ViewingMatrix()
                if mat is not None:
                    if self.chunks.ModBlock(pos, dir_, 9, item.type_, self.bound, 0, mat, item.colorIdx) == -1:
                        self.sounds["Put"].play()
                        if item.type_ == BLOCK_SPAWNER:
                            if f == 0:
                                xyz = x,y-1,z
                            elif f == 1:
                                xyz = x,y+1,z
                            elif f == 2:
                                xyz = x-1,y,z
                            elif f == 3:
                                xyz = x+1,y,z
                            elif f == 4:
                                xyz = x,y,z-1
                            elif f == 5:
                                xyz = x,y,z+1

                            self.gui.spawns[xyz] = 'Spawner_'+`len(self.gui.spawns.keys())`
                        if item.type_ == BLOCK_CODE:
                            if f == 0:
                                xyz = x,y-1,z
                            elif f == 1:
                                xyz = x,y+1,z
                            elif f == 2:
                                xyz = x-1,y,z
                            elif f == 3:
                                xyz = x+1,y,z
                            elif f == 4:
                                xyz = x,y,z-1
                            elif f == 5:
                                xyz = x,y,z+1

                            self.gui.codes[xyz] = None
                        item.count -= 1
                        if item.count == 0:
                            self.gui.qbar[self.gui.selectedItem] = ITEM_NONE


            elif item and item.name == "Item":

                if item.type_ == ITEM_CHEST:
                    dirV = self.cam1.GetDirV().Normalized()
                    dx,dz = dirV.x,-dirV.z
                    if abs(dx) > abs(dz):
                        if dx < 0:
                            facing = 3
                        else:
                            facing = 2
                    else:
                        if dz < 0:
                            facing = 5
                        else:
                            facing = 4
                    installed = False

                    if f == 0:
                        pass
                    elif f == 1:
                        xyz = x,y+1,z
                    elif f == 2:
                        xyz = x-1,y,z
                    elif f == 3:
                        xyz = x+1,y,z
                    elif f == 4:
                        xyz = x,y,z-1
                    elif f == 5:
                        xyz = x,y,z+1
                    mat = ViewingMatrix()
                    if mat is not None:
                        if self.chunks.ModBlock(pos, dir_, 9, BLOCK_CHEST, self.bound, 0, mat, item.colorIdx) == -1:
                            installed = self.chunks.AddChest(xyz[0],xyz[1],xyz[2],facing)
                            if installed:
                                if item.optionalInventory:
                                    self.gui.boxes[xyz] = item.optionalInventory
                                else:
                                    self.gui.boxes[xyz] = [ITEM_NONE for i in range(60)]
                                item.count -= 1
                                if item.count == 0:
                                    self.gui.qbar[self.gui.selectedItem] = ITEM_NONE

                if item.type_ == ITEM_TORCH and self.chunks.AddTorch(x,y,z,f):
                    item.count -= 1
                    if item.count == 0:
                        self.gui.qbar[self.gui.selectedItem] = ITEM_NONE
                if item.type_ in [ITEM_STAIR, ITEM_WOODENSTAIR]:
                    dirV = self.cam1.GetDirV().Normalized()
                    dx,dz = dirV.x,-dirV.z
                    if abs(dx) > abs(dz):
                        if dx < 0:
                            facing = 3
                        else:
                            facing = 2
                    else:
                        if dz < 0:
                            facing = 5
                        else:
                            facing = 4

                    if f == 0:
                        return
                    elif f == 1:
                        xyz = x,y+1,z
                    elif f == 2:
                        xyz = x-1,y,z
                    elif f == 3:
                        xyz = x+1,y,z
                    elif f == 4:
                        xyz = x,y,z-1
                    elif f == 5:
                        xyz = x,y,z+1

                    xx = xyz[0]-(xyz[0]%32)
                    yy = xyz[1]-(xyz[1]%32)
                    zz = xyz[2]-(xyz[2]%32)
                    if self.chunks.IsBlockThere(*xyz):
                        return
                    if (xx,yy,zz) not in self.stairs:
                        self.stairs[(xx,yy,zz)] = []
                    for stair in self.stairs[(xx,yy,zz)]:
                        if xyz == stair[:3]:
                            return
                    else:
                        self.stairs[(xx,yy,zz)] += [xyz+(facing,item.type_)]
                        item.count -= 1
                        if item.count == 0:
                            self.gui.qbar[self.gui.selectedItem] = ITEM_NONE

                        

        pos = self.cam1.pos
        x,y,z = pos.x, pos.y, -pos.z
        if y > 127.0:
            for zz in range(7):
                for yy in range(7):
                    for xx in range(7):
                        block, items, color = self.chunks.DigBlock(int(x-3+xx), int(y-3+yy), int(z-3+zz))
                        if block:
                            self.SpawnBlockItems(int(x-3+xx), int(y-3+yy), int(z-3+zz), block, color)
                        if items:
                            for item in items:
                                if item == ITEM_TORCH:
                                    self.gui.PutItemInInventory(Item(item, 1, color=(255,255,255), stackable=True))
                                if item == ITEM_CHEST:
                                    self.gui.PutItemInInventory(Item(item, 1, color=(255,255,255), stackable=False, inv=self.gui.boxes[(x,y,z)]))
                                    del self.gui.boxes[(x,y,z)]


    def RenderWeapon(self, x,y, color, rotate=False):
        glPushMatrix()
        texupx = (x*30.0) / 512.0
        texupy = (y*30.0) / 512.0
        x = SW-SW/3-50
        y = SH-SH/3-50
        w = 200
        h = 200
        glTranslatef(x,-y,0)
        if rotate:
            glRotatef(45, 0.0, 1.0, 1.0)
        else:
            glRotatef(45, 0.0,1.0,0.0)
        glBindTexture(GL_TEXTURE_2D, self.gui.tooltex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glBegin(GL_QUADS)
        glColor4ub(*color)

        glTexCoord2f(texupx, texupy+float(30)/512.0)
        glVertex3f(float(0), -float(0+h), 100.0)

        glTexCoord2f(texupx+float(30)/512.0, texupy+float(30)/512.0)
        glVertex3f(float(0+w), -float(0+h), 100.0)

        glTexCoord2f(texupx+float(30)/512.0, texupy)
        glVertex3f(float(0+w), -float(0), 100.0)

        glTexCoord2f(texupx, texupy)
        glVertex3f(float(0), -float(0), 100.0)
        glEnd()
        glPopMatrix()

    def RenderCrossHair(self):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_CULL_FACE)
        glLineWidth(2.0)
        w = 15.0
        h = 15.0
        x = float((SW-w)/2.0)
        y = float((SH-h)/2.0)
        glBegin(GL_QUADS)
        glColor4ub(*self.chColor)
        glVertex3f(float(x), -float(y+h), 100.0)
        glVertex3f(float(x+w), -float(y+h), 100.0)
        glVertex3f(float(x+w), -float(y), 100.0)
        glVertex3f(float(x), -float(y), 100.0)
        glEnd()

        glBegin(GL_LINES)
        glColor4f(0.0,0.0,0.0,1.0)
        glVertex3f(x, -(y+h/2), 145.0)
        glVertex3f(x+w, -(y+h/2), 145.0)

        glVertex3f(x+w/2, -y, 145.0)
        glVertex3f(x+w/2, -(y+h), 145.0)
        glEnd()

        glEnable(GL_TEXTURE_2D)

    def RenderMobHP(self):
        if self.curAttackingMob:
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_CULL_FACE)
            glLineWidth(4.0)
            x = float((SW-145)/2.0)
            y = 30
            width = (float(self.curAttackingMob.curhp)/float(self.curAttackingMob.CalcMaxHP()))*145
            if width < 0.0:
                width = 0.0

            glBegin(GL_LINES)
            w = 145.0
            glColor4f(0.0,0.0,0.0,1.0)
            glVertex3f(x-2, -y, 145.0)
            glVertex3f(x+w+2, -y, 145.0)

            glVertex3f(x+w, -y, 145.0)
            glVertex3f(x+w, -(y+15.0), 145.0)

            glVertex3f(x+w+2, -(y+15.0), 145.0)
            glVertex3f(x-2, -(y+15.0), 145.0)

            glVertex3f(x, -(y+15.0), 145.0)
            glVertex3f(x, -y, 145.0)
            glEnd()
            glBegin(GL_QUADS)
            glColor4ub(189,45,6,255)
            glVertex3f(x, -y, 145.0)
            glVertex3f(x+width, -y, 145.0)
            glVertex3f(x+width, -(y+15.0), 145.0)
            glVertex3f(x, -(y+15.0), 145.0)
            glEnd()


            glEnable(GL_TEXTURE_2D)

    def RenderHPMP(self):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_CULL_FACE)
        glLineWidth(4.0)
        x = float((SW-300)/2.0)
        y = SH-67
        width = float(self.entity.curhp)/float(self.entity.CalcMaxHP())*145
        if width < 0.0:
            width = 0.0

        glBegin(GL_LINES)
        w = 145.0
        glColor4f(0.0,0.0,0.0,1.0)
        glVertex3f(x-2, -y, 145.0)
        glVertex3f(x+w+2, -y, 145.0)

        glVertex3f(x+w, -y, 145.0)
        glVertex3f(x+w, -(y+15.0), 145.0)

        glVertex3f(x+w+2, -(y+15.0), 145.0)
        glVertex3f(x-2, -(y+15.0), 145.0)

        glVertex3f(x, -(y+15.0), 145.0)
        glVertex3f(x, -y, 145.0)
        glEnd()
        glBegin(GL_QUADS)
        glColor4ub(189,45,6,255)
        glVertex3f(x, -y, 145.0)
        glVertex3f(x+width, -y, 145.0)
        glVertex3f(x+width, -(y+15.0), 145.0)
        glVertex3f(x, -(y+15.0), 145.0)
        glEnd()

        x = x + 155
        width = float(self.entity.curmp)/float(self.entity.CalcMaxMP())*145
        if width < 0.0:
            width = 0.0
        w = 145.0
        glBegin(GL_LINES)
        glColor4f(0.0,0.0,0.0,1.0)
        glVertex3f(x-2, -y, 145.0)
        glVertex3f(x+w+2, -y, 145.0)

        glVertex3f(x+w, -y, 145.0)
        glVertex3f(x+w, -(y+15.0), 145.0)

        glVertex3f(x+w+2, -(y+15.0), 145.0)
        glVertex3f(x-2, -(y+15.0), 145.0)

        glVertex3f(x, -(y+15.0), 145.0)
        glVertex3f(x, -y, 145.0)
        glEnd()
        glBegin(GL_QUADS)
        glColor4ub(6,118,189,255)
        glVertex3f(x, -y, 145.0)
        glVertex3f(x+width, -y, 145.0)
        glVertex3f(x+width, -(y+15.0), 145.0)
        glVertex3f(x, -(y+15.0), 145.0)
        glEnd()


        glEnable(GL_TEXTURE_2D)

    def RenderBlockHP(self):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_CULL_FACE)
        glLineWidth(3.0)
        x = float((SW-100)/2.0)
        y = float((SH-25)/2.0)
        width = float(self.blockHP/self.maxBlockHP)*100.0
        if width < 0.0:
            width = 0.0

        glBegin(GL_LINES)
        glColor4f(0.0,0.0,0.0,1.0)
        glVertex3f(x, -y, 100.0)
        glVertex3f(x+100.0, -y, 100.0)

        glVertex3f(x+100.0, -y, 100.0)
        glVertex3f(x+100.0, -(y+25.0), 100.0)

        glVertex3f(x+100.0, -(y+25.0), 100.0)
        glVertex3f(x, -(y+25.0), 100.0)

        glVertex3f(x, -(y+25.0), 100.0)
        glVertex3f(x, -y, 100.0)
        glEnd()
        glBegin(GL_QUADS)
        glColor4f(1.0,1.0,1.0,1.0)
        glVertex3f(x, -y, 100.0)
        glVertex3f(x+width, -y, 100.0)
        glVertex3f(x+width, -(y+25.0), 100.0)
        glVertex3f(x, -(y+25.0), 100.0)
        glEnd()
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

    def GetNPC(self):
        mobIntersects = []
        for mob in self.npcs:
            pos = self.cam1.pos
            pos = (pos.x, pos.y, -pos.z)
            dir_ = self.cam1.GetDirV().Normalized().MultScalar(3.0)
            dir_ = (dir_.x, dir_.y, -dir_.z)
            x,y,z = mob.pos
            min = x-mob.bound[0]/2,y-mob.bound[1],z-mob.bound[2]/2
            max = x+mob.bound[0]/2,y,z+mob.bound[2]/2
            intersects, coord = self.chunks.HitBoundingBox(min,max,pos,dir_)
            if intersects:
                mobIntersects += [(mob, coord)]

        if mobIntersects:
            pos = self.cam1.pos
            pos = Vector(pos.x, pos.y, -pos.z)
            lowest = mobIntersects[0]
            for mobcoord in mobIntersects[1:]:
                mob, coord = mobcoord
                c = Vector(*coord)
                if (c-pos).Length() < (Vector(*lowest[1])-pos).Length():
                    lowest = mobcoord
            return lowest
        return None
    def GetMob(self):
        mobIntersects = []
        for mob in self.mobs:
            pos = self.cam1.pos
            pos = (pos.x, pos.y, -pos.z)
            dir_ = self.cam1.GetDirV().Normalized().MultScalar(3.0)
            dir_ = (dir_.x, dir_.y, -dir_.z)
            x,y,z = mob.pos
            min = x-mob.bound[0]/2,y-mob.bound[1],z-mob.bound[2]/2
            max = x+mob.bound[0]/2,y,z+mob.bound[2]/2
            intersects, coord = self.chunks.HitBoundingBox(min,max,pos,dir_)
            if intersects:
                mobIntersects += [(mob, coord)]
        if mobIntersects:
            pos = self.cam1.pos
            pos = Vector(pos.x, pos.y, -pos.z)
            lowest = mobIntersects[0]
            for mobcoord in mobIntersects[1:]:
                mob, coord = mobcoord
                c = Vector(*coord)
                if (c-pos).Length() < (Vector(*lowest[1])-pos).Length():
                    lowest = mobcoord
            return lowest
        return None

    def LDown(self,t,m,k):
        # 여러가지 액션 또는 땅파기 XXX
        if not self.gui.invShown:
            mob = self.GetMob()
            if mob:
                self.OnMobHit(mob, t)
                self.chColor = self.RED_CH
                return

            if self.lastBlock:
                x,y,z,f,b = self.lastBlock
                hp = 100.0
                if b == BLOCK_COALORE:
                    hp = 120.0
                if b == BLOCK_IRONORE:
                    hp = 150.0
                if b == BLOCK_SILVERORE:
                    hp = 180.0
                if b == BLOCK_GOLDORE:
                    hp = 250.0
                if b == BLOCK_DIAMONDORE:
                    hp = 500.0

                self.blockHP = hp
                self.maxBlockHP = hp
                self.prevDig = t
                self.digging = False

            self.RunScript()
    def RunScript(self):
        if self.lastBlock:
            x,y,z,f,b = self.lastBlock
            if b in [BLOCK_CODE]:
                if (x,y,z) in self.gui.codes:
                    name = self.gui.codes[(x,y,z)]
                    if name:
                        scr = self.scripts[(x,y,z)]
                        scr.code = open(name, "r").read()
                        try:
                            scr.run()
                        except:
                            import traceback
                            self.lastError = traceback.format_exc()
                            print self.lastError


    def LUp(self, t, m, k):
        self.blockHP = 100.0
        self.prevDig = t
        self.digging = False
        self.chColor = self.WHITE_CH

    def OnMobHit(self, mob, t):
        self.curAttackingMob = mob[0].entity
        # 여기서 대화 또는 공격 XXX
        if t - self.prevAttack > self.attackDelay:
            self.prevAttack = t
            pos = self.cam1.pos
            pos = Vector(pos.x, pos.y, -pos.z)
            mpos = Vector(*mob[0].pos)
            if (mpos-pos).Length() < 1.2:
                self.entity.Attack(mob[0].entity)
                self.sounds["Hit"].play()

    def OnNPCRHit(self, mob, t):
        pos = self.cam1.pos
        pos = Vector(pos.x, pos.y, -pos.z)
        mpos = Vector(*mob[0].pos)
        mob[0].UpdateDirection()
        if (mpos-pos).Length() < 3:
            # 퀘스트 받을 수 있는 조건이 맞으면 퀘스트를 여기서 주고
            # 퀘스트를 이미 받았고 퀘스트를 완료했다면 퀘스트 완료를 하고 idx += 1을 하고 리워드를 준다.

            self.gui.talkBox.Clear()
            if not(len(self.quests[mob[0].name])-1 >= self.questIdxes[mob[0].name]):
                self.gui.talkBox.AddText("Hi", (30,30,30), (8,29,1))
                def Close2():
                    self.guiMode = False
                    self.gui.ShowInventory(self.guiMode)
                self.gui.talkBox.AddSelection("OK", Close2, (8,29,1), (8,29,1))

                self.guiMode = True
                self.gui.toolMode = TM_TALK
                self.gui.ShowInventory(self.guiMode)
                return
            curQuest = self.quests[mob[0].name][self.questIdxes[mob[0].name]]
            checkOK = curQuest["CheckOKToGiveQuest"]
            questDone = curQuest["CheckQuestDone"]
            requestQ = curQuest["OnRequestQuest"]
            qDone = curQuest["OnQuestDone"]
            
            oktext, notoktext = requestQ
            notfound = False
            for check in checkOK:
                if check not in self.questLog[mob[0].name]:
                    notfound = True

            if notfound:
                self.gui.talkBox.AddText(notoktext, (30,30,30), (8,29,1))
            else:
                # 인벤토리를 체크, 몹 킬 로그를 체크
                def CheckQuestDone():
                    curCounts = []
                    for quest in questDone:
                        if quest[1] == QUEST_GATHER:
                            curCount = 0
                            for item in self.gui.inventory:
                                if item and item.name == quest[4] and item.type_ == quest[3]:
                                    curCount += item.count

                            for item in self.gui.qbar1:
                                if item and item.name == quest[4] and item.type_ == quest[3]:
                                    curCount += item.count

                            for item in self.gui.qbar2:
                                if item and item.name == quest[4] and item.type_ == quest[3]:
                                    curCount += item.count

                            if curCount < quest[2]:
                                return False
                            else:
                                curCounts += [(quest[3], quest[4], quest[2])]

                        elif quest[1] == QUEST_KILLMOB:
                            if not(self.mobKillLog[quest[3]] >= quest[2]):
                                return False
                        elif quest[1] == QUEST_REQUIREDQUEST:
                            if quest[2] not in self.questLog[quest[3]]:
                                return False

                    if curCounts:
                        for count in curCounts:
                            curCount = count[2]
                            idx = 0
                            for item in self.gui.inventory[:]:
                                if item and item.name == count[1] and item.type_ == count[0]:
                                    if item.count < curCount:
                                        curCount -= item.count
                                        self.gui.inventory[idx] = ITEM_NONE
                                    elif item.count == curCount:
                                        curCount = 0
                                        self.gui.inventory[idx] = ITEM_NONE
                                        break
                                    else:
                                        item.count -= curCount
                                        curCount = 0
                                        break
                                idx += 1
                            idx = 0
                            for item in self.gui.qbar1[:]:
                                if item and item.name == count[1] and item.type_ == count[0]:
                                    if item.count < curCount:
                                        curCount -= item.count
                                        self.gui.qbar1[idx] = ITEM_NONE
                                    elif item.count == curCount:
                                        curCount = 0
                                        self.gui.qbar1[idx] = ITEM_NONE
                                        break
                                    else:
                                        item.count -= curCount
                                        curCount = 0
                                        break
                                idx += 1
                            idx = 0
                            for item in self.gui.qbar2[:]:
                                if item and item.name == count[1] and item.type_ == count[0]:
                                    if item.count < curCount:
                                        curCount -= item.count
                                        self.gui.qbar2[idx] = ITEM_NONE
                                    elif item.count == curCount:
                                        curCount = 0
                                        self.gui.qbar2[idx] = ITEM_NONE
                                        break
                                    else:
                                        item.count -= curCount
                                        curCount = 0
                                        break
                                idx += 1
                            # remove items from inventory

                    return True
                    #"CheckQuestDone": doneargs, # args = [(questText, QUEST_KILLMOB, number, mobid), (questText, QUEST_GATHER, number, itemid, itemtype), (questText, QUEST_REQUIREDQUEST, questid, npcname)]
                def GenReward():
                    items = []
                    for reward in qDone[1]:
                        type_, count, name = reward
                        # 여기다가 아이템 코드만으로 아이템을 생성하는 걸 넣는다.
                        # 뭐 픽액스 이런건 리워드로 안주면 땡. 다이아 5개 주면 그게 그거지
                        # 리워드로 주는 건 광물, 블럭, 인챈트스크롤 밖에 없다.
                        if name == "Item":
                            if type_ == ITEM_IRON:
                                self.gui.PutItemInInventory(Item(ITEM_IRON, count, color=(107,107,107), stackable=True))
                            elif type_ == ITEM_COAL:
                                self.gui.PutItemInInventory(Item(ITEM_COAL, count, color=(60,60,60), stackable=True))
                            elif type_ == ITEM_SILVER:
                                self.gui.PutItemInInventory(Item(ITEM_SILVER, count, color=(201,201,201), stackable=True))
                            elif type_ == ITEM_GOLD:
                                self.gui.PutItemInInventory(Item(ITEM_GOLD, count, color=(207,207,101), stackable=True))
                            elif type_ == ITEM_DIAMOND:
                                self.gui.PutItemInInventory(Item(ITEM_DIAMOND, count, color=(80,212,217), stackable=True))
                            elif type_ in [ITEM_SENCHANTSCROLL, ITEM_GENCHANTSCROLL, ITEM_DENCHANTSCROLL]:
                                if type_ == ITEM_SENCHANTSCROLL:
                                    color = (255,255,255)
                                elif type_ == ITEM_GENCHANTSCROLL:
                                    color = (207,207,101)
                                elif type_ == ITEM_DENCHANTSCROLL:
                                    color = (80,212,217)
                                for i in range(count):
                                    element = self.gui.GenElement(type_)
                                    returneditem = Item(type_, 1, color=color, element=element)
                                    returneditem.maxEnchant = 0
                                    self.gui.PutItemInInventory(returneditem)
                        elif name == "Block":
                            self.gui.PutItemInInventory(Block(type_, count))


                if self.curQuests[mob[0].name] == questDone and CheckQuestDone() and questDone:
                    self.gui.talkBox.AddText(qDone[0], (30,30,30), (8,29,1))
                    GenReward()
                    self.questLog[mob[0].name] += [self.questIdxes[mob[0].name]]
                    self.questIdxes[mob[0].name] += 1
                    self.curQuests[mob[0].name] = []
                else:
                    self.curQuests[mob[0].name] = questDone
                    self.gui.talkBox.AddText(oktext, (30,30,30), (8,29,1))
            def Close():
                self.guiMode = False
                self.gui.ShowInventory(self.guiMode)
            self.gui.talkBox.AddSelection("OK", Close, (8,29,1), (8,29,1))

            self.guiMode = True
            self.gui.toolMode = TM_TALK
            self.gui.ShowInventory(self.guiMode)


    def OnMobRHit(self, mob, t):
        self.curAttackingMob = mob[0].entity
        if t - self.prevAttack > self.attackDelay:
            self.prevAttack = t

            item = self.gui.qbar[self.gui.selectedItem]
            if item and item.name == "Skill":
                pos = self.cam1.pos
                pos = Vector(pos.x, pos.y, -pos.z)
                mpos = Vector(*mob[0].pos)
                if (mpos-pos).Length() < item.skill.range:
                    item.skill.Apply(self.entity, mob[0].entity)

        # XXX 여기서 마법 또는 상점 인터랙션?
        # 마법 연사력을 결정해서 딜레이를 줘야함

    def IsStairThere(self, x,y,z):
        x1 = x-(x%32)
        y1 = y-(y%32)
        z1 = z-(z%32)
        if (x1,y1,z1) in self.stairs:
            for stair in self.stairs[(x1,y1,z1)]:
                if stair[0] == x and stair[1] == y and stair[2] == z:
                    return True
        return False

    def GetStair(self):
        mobIntersects = []
        pos = self.cam1.pos
        pos = (pos.x, pos.y, -pos.z)
        x,y,z = pos
        x -= x%32
        y -= y%32
        z -= z%32
        _9pos = [
                (x-32, y, z-32), (x, y, z-32), (x+32, y, z-32),
                (x-32, y, z), (x, y, z), (x+32, y, z),
                (x-32, y, z+32), (x, y, z+32), (x+32, y, z+32),]
        for surpos in _9pos:
            if surpos in self.stairs:
                for stair in self.stairs[surpos]:
                    dir_ = self.cam1.GetDirV().Normalized().MultScalar(3.0)
                    dir_ = (dir_.x, dir_.y, -dir_.z)
                    x,y,z,f,b = stair
                    min = float(x),float(y),float(z)
                    max = x+1.0,y+1.0,z+1.0
                    intersects, coord = self.chunks.HitBoundingBox(min,max,pos,dir_)
                    if intersects:
                        mobIntersects += [(stair, coord)]
        if mobIntersects:
            pos = self.cam1.pos
            pos = Vector(pos.x, pos.y, -pos.z)
            lowest = mobIntersects[0][:3]
            for mobcoord in mobIntersects[1:]:
                stair, coord = mobcoord
                c = Vector(*coord[:3])
                if (c-pos).Length() < (Vector(*lowest[1])-pos).Length():
                    lowest = mobcoord
            stair, coord = lowest
            c = Vector(*coord[:3])
            if (c-pos).Length() < 3.0:
                return lowest
        return None

    def LPressing(self, t, m, k):
        if not self.gui.invShown:
            mob = self.GetMob()
            if mob:
                self.OnMobHit(mob, t)
                self.chColor = self.RED_CH
                return

            stair = self.GetStair()
            if stair:
                x,y,z,f,b = stair[0]
                x1 = x-(x%32)
                y1 = y-(y%32)
                z1 = z-(z%32)
                for stair2 in self.stairs[(x1,y1,z1)][:]:
                    xx,yy,zz,ff,bb = stair2
                    if xx == x and yy == y and zz == z:
                        self.stairs[(x1,y1,z1)].remove(stair2)
                        try:
                            glDeleteLists(self.stairsDL[(x1,y1,z1)][xx,yy,zz], 1)
                            del self.stairsDL[(x1,y1,z1)][xx,yy,zz]
                        except:
                            pass
                        if b == ITEM_WOODENSTAIR:
                            color = (116,100,46)
                        if b == ITEM_STAIR:
                            color = (30,30,30)
                        self.gui.PutItemInInventory(Item(b, 1, color=color, stackable=True))
                return

                # XXX HP를 깎고 스테어를 지운다.
                #self.DestroyStair()

        self.digging = False
        item = self.gui.qbar[self.gui.selectedItem]
        if not self.gui.invShown and self.lastBlock and self.prevBlock:
            x,y,z,face,block = self.lastBlock
            x2,y2,z2,face2,block2 = self.prevBlock
            if x==x2 and y==y2 and z==z2 and block == block2 and block != BLOCK_WATER:
                self.digging = True
            if t-self.prevDig > self.digDelay:

                if block in [BLOCK_CODE, BLOCK_SPAWNER] and (block in self.gui.spawns or block in self.gui.codes):
                    return
                x2,y2,z2,face2,block2 = self.prevBlock
                if x==x2 and y==y2 and z==z2 and block == block2 and block != BLOCK_WATER:
                    tool = self.gui.qbar[self.gui.selectedItem]
                    if block in [BLOCK_GRASS, BLOCK_DIRT, BLOCK_SAND, BLOCK_LEAVES, BLOCK_GRAVEL]:
                        self.sounds["Shovel"].play()
                    else:
                        self.sounds["Dig"].play()

                    if tool and tool.name == TYPE_ITEM and tool.type_ == ITEM_PICKAXE and block not in [BLOCK_GRASS, BLOCK_DIRT, BLOCK_SAND, BLOCK_LEAVES, BLOCK_GRAVEL]+[BLOCK_LOG, BLOCK_WOOD]:
                        self.blockHP -= (float(t - self.prevDig)*tool.stats[0]/100.0)
                        tool.count -= int(float(t-self.prevDig)*tool.stats[1]/50.0)
                        if tool.count <= 0:
                            self.gui.qbar[self.gui.selectedItem] = ITEM_NONE
                    elif tool and tool.name == TYPE_ITEM and tool.type_ == ITEM_AXE and block in [BLOCK_LOG, BLOCK_WOOD, BLOCK_LEAVES]:
                        self.blockHP -= (float(t - self.prevDig)*tool.stats[0]/100.0)
                        tool.count -= int(float(t-self.prevDig)*tool.stats[1]/50.0)
                        if tool.count <= 0:
                            self.gui.qbar[self.gui.selectedItem] = ITEM_NONE
                    elif tool and tool.name == TYPE_ITEM and tool.type_ == ITEM_SHOVEL and block in [BLOCK_GRASS, BLOCK_DIRT, BLOCK_SAND, BLOCK_GRAVEL]:
                        self.blockHP -= (float(t - self.prevDig)*tool.stats[0]/100.0)
                        tool.count -= int(float(t-self.prevDig)*tool.stats[1]/50.0)
                        if tool.count <= 0:
                            self.gui.qbar[self.gui.selectedItem] = ITEM_NONE
                    elif tool and tool.name == TYPE_ITEM and tool.type_ in [ITEM_SHOVEL, ITEM_AXE, ITEM_PICKAXE]:
                        self.blockHP -= (float(t - self.prevDig)*tool.stats[0]*0.5/100.0)
                        tool.count -= int(float(t-self.prevDig)*tool.stats[1]/50.0)
                        if tool.count <= 0:
                            self.gui.qbar[self.gui.selectedItem] = ITEM_NONE
                    else:
                        self.blockHP -= (float(t - self.prevDig)*5.0/100.0)
                else:
                    if self.lastBlock:
                        x,y,z,f,b = self.lastBlock
                        hp = 100.0
                        if b == BLOCK_WOOD:
                            hp = 150.0
                        if b == BLOCK_COALORE:
                            hp = 120.0
                        if b == BLOCK_IRONORE:
                            hp = 150.0
                        if b == BLOCK_SILVERORE:
                            hp = 180.0
                        if b == BLOCK_GOLDORE:
                            hp = 250.0
                        if b == BLOCK_DIAMONDORE:
                            hp = 500.0

                        self.blockHP = hp
                        self.maxBlockHP = hp

                if self.blockHP <= 0 and self.lastBlock:
                    if self.lastBlock:
                        x,y,z,f,b = self.lastBlock
                        hp = 100.0
                        if b == BLOCK_WOOD:
                            hp = 150.0
                        if b == BLOCK_COALORE:
                            hp = 120.0
                        if b == BLOCK_IRONORE:
                            hp = 150.0
                        if b == BLOCK_SILVERORE:
                            hp = 180.0
                        if b == BLOCK_GOLDORE:
                            hp = 250.0
                        if b == BLOCK_DIAMONDORE:
                            hp = 500.0

                        self.blockHP = hp
                        self.maxBlockHP = hp

                    x,y,z,f,b = self.lastBlock
                    block, items, color = self.chunks.DigBlock(x,y,z)
                    if block:
                        if b in [BLOCK_GRASS, BLOCK_DIRT, BLOCK_SAND, BLOCK_LEAVES, BLOCK_GRAVEL]:
                            self.sounds["ShovelDone"].play()
                        else:
                            self.sounds["DigDone"].play()

                        if block == BLOCK_SPAWNER:
                            if (x,y,z) in self.gui.spawns:
                                del self.gui.spawns[(x,y,z)]
                        if block == BLOCK_CODE:
                            if (x,y,z) in self.gui.codes:
                                del self.gui.codes[(x,y,z)]
                        if block == BLOCK_GRASS:
                            block = BLOCK_DIRT
                        if block not in [BLOCK_CHEST, BLOCK_IRONORE, BLOCK_COALORE, BLOCK_SILVERORE, BLOCK_GOLDORE, BLOCK_DIAMONDORE]:
                            self.SpawnBlockItems(x,y,z, block, color)
                        else:
                            if block == BLOCK_IRONORE:
                                self.gui.PutItemInInventory(Item(ITEM_IRON, 1, color=(107,107,107), stackable=True))
                            if block == BLOCK_COALORE:
                                self.gui.PutItemInInventory(Item(ITEM_COAL, 1, color=(60,60,60), stackable=True))
                            if block == BLOCK_SILVERORE:
                                self.gui.PutItemInInventory(Item(ITEM_SILVER, 1, color=(201,201,201), stackable=True))
                            if block == BLOCK_GOLDORE:
                                self.gui.PutItemInInventory(Item(ITEM_GOLD, 1, color=(207,207,101), stackable=True))
                            if block == BLOCK_DIAMONDORE:
                                self.gui.PutItemInInventory(Item(ITEM_DIAMOND, 1, color=(80,212,217), stackable=True))
                            #XXX: 아이템이 인벤에 넣을 공간이 없으면 땅에 드랍하는 거 구현해야함

                    if items:
                        for item in items:
                            if item == ITEM_TORCH:
                                self.gui.PutItemInInventory(Item(item, 1, color=(255,255,255), stackable=True))
                            if item == ITEM_CHEST:
                                if (x,y,z) in self.gui.boxes:
                                    self.gui.PutItemInInventory(Item(item, 1, color=(255,255,255), stackable=False, inv=self.gui.boxes[(x,y,z)]))
                                    del self.gui.boxes[(x,y,z)]
                self.prevDig = t


    def SpawnBlockItems(self, x,y,z, block, color):
        self.blockItems += [(x+0.5,y+0.5,z+0.5, block, color, pygame.time.get_ticks(), None)]

    def CheckJump(self, y):
        if self.prevY - 0.05 <= y <= self.prevY + 0.05:
            self.canJump = True
        else:
            self.canJump = False
        self.prevY = y


    def GetNearbyItems(self):
        pos = self.cam1.pos
        x,y,z = pos.x,pos.y,-pos.z
        for item in self.blockItems[:]:
            xx,yy,zz,b,c,t,d = item
            if (Vector(x,y,z) - Vector(xx,yy,zz)).Length() < self.bound[1]+0.3:
                block = Block(b, 1)
                block.colorIdx = c
                block.color = self.gui.colors[c]
                if self.gui.PutItemInInventory(block):
                    self.sounds["EatItem"].play()
                    self.blockItems.remove(item)

    def ItemFall(self):
        idx = 0
        delIdx = []
        for item in self.blockItems[:]:
            xx,yy,zz,b,c,prevTick,d = item
            if pygame.time.get_ticks() - prevTick > 5*60*1000:
                delIdx += [idx]
            else:
                x,y,z = self.chunks.FixPos(Vector(xx,yy,zz), Vector(xx,yy-0.11,zz), (0.33,0.33,0.33))
                self.blockItems[idx] = x,y,z,b,c,prevTick,d
                idx += 1

        delIdx.reverse()
        for idx in delIdx:
            del self.blockItems[idx]

    def RegenTex(self,t,m,k):
        if self.regenTex:
            self.gui.inventex = texture = glGenTexturesDebug(1)
            teximg = pygame.image.tostring(self.gui.invenimg, "RGBA", 0) 
            glBindTexture(GL_TEXTURE_2D, self.gui.inventex)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)

            self.gui.tooltex = texture = glGenTexturesDebug(1)
            teximg = pygame.image.tostring(self.gui.toolimg, "RGBA", 0) 
            glBindTexture(GL_TEXTURE_2D, self.gui.tooltex)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)

            self.tex = texture = glGenTexturesDebug(1)
            image = pygame.image.load("./images/digdig/manicdigger.png")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)

            self.mobtex = texture = glGenTexturesDebug(1)
            image = pygame.image.load("./images/digdig/mobs.png")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)

            self.skyeast = texture = glGenTexturesDebug(1)
            image = pygame.image.load("./images/digdig/clouds1_east.jpg")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            
            self.skywest = texture = glGenTexturesDebug(1)
            image = pygame.image.load("./images/digdig/clouds1_west.jpg")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            
            self.skynorth = texture = glGenTexturesDebug(1)
            image = pygame.image.load("./images/digdig/clouds1_north.jpg")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            
            self.skysouth = texture = glGenTexturesDebug(1)
            image = pygame.image.load("./images/digdig/clouds1_south.jpg")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            
            self.skyup = texture = glGenTexturesDebug(1)
            image = pygame.image.load("./images/digdig/clouds1_up.jpg")
            teximg = pygame.image.tostring(image, "RGBA", 0) 
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
            

    def Render(self, t, m, k):
        for mob in self.mobs:
            mob.Tick(t,m,k)
        for mob in self.npcs:
            mob.Tick(t,m,k)

        updateFrameCounter = 0
        fogMode=GL_LINEAR# { GL_EXP, GL_EXP2, GL_LINEAR };	// Storage For Three Types Of Fog
        fogfilter= 0				#	// Which Fog To Use
        fogColor= [0.5, 0.5, 0.5, 1.0]#;		// Fog Color

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)




        if True or t - self.renderPrevTime > self.renderDelay:
            self.DoMove(t,m,k)
            self.FallOrJump(t)
            self.ItemFall()
            self.GetNearbyItems()

            self.renderPrevTime = t
            glFogi(GL_FOG_MODE, fogMode)#;		// Fog Mode
            glFogfv(GL_FOG_COLOR, fogColor)#;			// Set Fog Color
            glFogf(GL_FOG_DENSITY, 0.1)#;				// How Dense Will The Fog Be
            glHint(GL_FOG_HINT, GL_DONT_CARE)#;			// Fog Hint Value
            glFogf(GL_FOG_START, G_FAR-1.0)#;				// Fog Start Depth
            glFogf(GL_FOG_END, G_FAR+5.0)#;				// Fog End Depth
            glClearColor(132.0/255.0, 217.0/255.0, 212.0/255.0,1.0)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            GameDrawMode()



            glDisable(GL_FOG)#;	
            dirV = self.cam1.GetDirV()
            posV = self.cam1.pos# - dirV
            self.cam1.ApplyCamera() 
            posV = Vector(posV.x, posV.y-G_FAR/10.0, posV.z)


            glDisable(GL_DEPTH_TEST)
            texID = self.skyup
            glBindTexture(GL_TEXTURE_2D, texID)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            offsetClose = G_FAR/2
            offset = G_FAR/2.0
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(posV.x-(G_FAR-offset), posV.y+(G_FAR-offsetClose)-0.0, (-posV.z)-(G_FAR-offset))

            glTexCoord2f(1.0, 0.0)
            glVertex3f(posV.x+(G_FAR-offset), posV.y+(G_FAR-offsetClose)-0.0, (-posV.z)-(G_FAR-offset))

            glTexCoord2f(1.0, 1.0)
            glVertex3f(posV.x+(G_FAR-offset), posV.y+(G_FAR-offsetClose)-0.0, (-posV.z)+(G_FAR-offset))

            glTexCoord2f(0.0, 1.0)
            glVertex3f(posV.x-(G_FAR-offset), posV.y+(G_FAR-offsetClose)-0.0, (-posV.z)+(G_FAR-offset))
            glEnd()

            texID = self.skyeast
            glBindTexture(GL_TEXTURE_2D, texID)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            offsetClose = G_FAR/2
            offset = G_FAR/2.0
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(posV.x+(G_FAR-offset)-0.0, posV.y-(G_FAR-offsetClose), (-posV.z)+(G_FAR-offset))

            glTexCoord2f(0.0, 0.0)
            glVertex3f(posV.x+(G_FAR-offset)-0.0, posV.y+(G_FAR-offsetClose), (-posV.z)+(G_FAR-offset))

            glTexCoord2f(1.0, 0.0)
            glVertex3f(posV.x+(G_FAR-offset)-0.0, posV.y+(G_FAR-offsetClose), (-posV.z)-(G_FAR-offset))

            glTexCoord2f(1.0, 1.0)
            glVertex3f(posV.x+(G_FAR-offset)-0.0, posV.y-(G_FAR-offsetClose), (-posV.z)-(G_FAR-offset))
            glEnd()

            texID = self.skywest
            glBindTexture(GL_TEXTURE_2D, texID)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            offsetClose = G_FAR/2
            offset = G_FAR/2.0
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(posV.x-(G_FAR-offset)+0.0, posV.y-(G_FAR-offsetClose), (-posV.z)-(G_FAR-offset))

            glTexCoord2f(0.0, 0.0)
            glVertex3f(posV.x-(G_FAR-offset)+0.0, posV.y+(G_FAR-offsetClose), (-posV.z)-(G_FAR-offset))

            glTexCoord2f(1.0, 0.0)
            glVertex3f(posV.x-(G_FAR-offset)+0.0, posV.y+(G_FAR-offsetClose), (-posV.z)+(G_FAR-offset))

            glTexCoord2f(1.0, 1.0)
            glVertex3f(posV.x-(G_FAR-offset)+0.0, posV.y-(G_FAR-offsetClose), (-posV.z)+(G_FAR-offset))
            glEnd()

            texID = self.skynorth
            glBindTexture(GL_TEXTURE_2D, texID)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            offsetClose = G_FAR/2
            offset = G_FAR/2.0
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(posV.x-(G_FAR-offset), posV.y-(G_FAR-offsetClose), (-posV.z)+(G_FAR-offset)-0.0)

            glTexCoord2f(0.0, 0.0)
            glVertex3f(posV.x-(G_FAR-offset), posV.y+(G_FAR-offsetClose), (-posV.z)+(G_FAR-offset)-0.0)

            glTexCoord2f(1.0, 0.0)
            glVertex3f(posV.x+(G_FAR-offset), posV.y+(G_FAR-offsetClose), (-posV.z)+(G_FAR-offset)-0.0)

            glTexCoord2f(1.0, 1.0)
            glVertex3f(posV.x+(G_FAR-offset), posV.y-(G_FAR-offsetClose), (-posV.z)+(G_FAR-offset)-0.0)
            glEnd()

            texID = self.skysouth
            glBindTexture(GL_TEXTURE_2D, texID)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            offsetClose = G_FAR/2
            offset = G_FAR/2.0
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(posV.x+(G_FAR-offset), posV.y-(G_FAR-offsetClose), (-posV.z)-(G_FAR-offset)+0.0)

            glTexCoord2f(0.0, 0.0)
            glVertex3f(posV.x+(G_FAR-offset), posV.y+(G_FAR-offsetClose), (-posV.z)-(G_FAR-offset)+0.0)

            glTexCoord2f(1.0, 0.0)
            glVertex3f(posV.x-(G_FAR-offset), posV.y+(G_FAR-offsetClose), (-posV.z)-(G_FAR-offset)+0.0)

            glTexCoord2f(1.0, 1.0)
            glVertex3f(posV.x-(G_FAR-offset), posV.y-(G_FAR-offsetClose), (-posV.z)-(G_FAR-offset)+0.0)
            glEnd()
            glEnable(GL_DEPTH_TEST)

            #glEnable(GL_FOG)#;	
            mat = ViewingMatrix()
            if mat is not None:
                frustum = NormalizeFrustum(GetFrustum(mat))
                #frustum = NormalizeFrustum(GetFrustum(mat))
                if updateFrameCounter == 0:
                    updateFrame = True
                else:
                    updateFrame = False
                if self.regenTex:
                    MobRSt.RebuildMobs(self.bound)
                for npc in self.npcs:
                    if self.chunks.CubeInFrustumPy(*(npc.pos+(0.5,frustum))):
                        npc.Render2(None, self.cam1, t)
                for mob in self.mobs:
                    if self.chunks.CubeInFrustumPy(*(mob.pos+(0.5,frustum))):
                        mob.Render2(None, self.cam1, t) # 이것도 C로 옮기면 빨라질지도 모른다네
                        # 오픈GL을 이용하는 것보다 CPU를 이용하여 트랜슬레이트하고 한번에 그리는게 빠른가 경험상 그런듯
                        # 하지만 귀찮으니 놔두자...XXX: 나중에.

                glBindTexture(GL_TEXTURE_2D, self.tex)
                glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

                self.RenderStairs(frustum)
                self.chunks.GenVerts(frustum, (self.cam1.pos.x, self.cam1.pos.y, -self.cam1.pos.z), updateFrame, self.gui.tooltex, self.tex)
                updateFrameCounter += 0
                updateFrameCounter %= 1 # 화면이 좀 깨지기는 하지만 프레임률이 4번에 1번 하면 2배로 올라가는?
                # 8번에 1번 하면 뭐 무슨 3배로 올라가겠네 우왕 빠르당 ㅠㅠ 이걸로 가자.
                # 하지만 4번에 1번 이상은 별 효용이 없는 듯. 40배까지 올려야 2배로 올라감
                # 맵 로딩이 진짜 왕창 느리다. 옥트리 검사하는 거 때문에 진짜 느린 거 같은데.
                # 옥트리도 저장할 수 있게 해야겠다.
                # 아니? 옥트리 계산은 원래 빠른데? 음....캐슁 문제인가. 아니면, 50%만 cpu를 먹는 문제인가.
                # 하여간에 속도가 빠르고 싶다면 여기서 좀 숫자를 바꿔주면 떙이다.
                # 버퍼를 따로 써서 옥트리의 위치를 저장해서라도 옥트리의 내용을 저장해야겠다.
                #
                # 프레임 리미터도 넣자. 1초에 20번 이상은 그리지 않음!
                #
                # 옥트리 저장:
                # 128 즉 레벨 1에서는 x,y,z를 128로 나눈다.
                # 레벨 2에서는 64로 나눈다.
                # 그러면 octreeBuffer에서의 좌표가 나온다.
                # 이거를 1,8,64 등의 오프셋과 적용해서 좌표를 이용해 저장하면 된다. 로드도 같은방법
                #return
            glEnable(GL_DEPTH_TEST)

            # 32
            # 01
            # 76
            # 45
            vidx = [ (0, 1, 2, 3),  # front
                    (5, 4, 7, 6),  # back
                    (1, 5, 6, 2),  # right
                    (3, 7, 4, 0),  # left
                    (3, 2, 6, 7),  # top
                    (4, 5, 1, 0) ] # bottom    


            idx = 0
            for block in self.blockItems[:]:
                x,y,z,b,c,t,dList = block
                if not dList or self.regenTex:
                    dList = glGenLists(1)
                    self.blockItems[idx] = x,y,z,b,c,t,dList
                    glPushMatrix()
                    glTranslatef(x,y,z)
                    tex1 = 0.0, 0.0
                    tex2 = 0.0, 0.0
                    tex3 = 0.0, 0.0
                    tex4 = 0.0, 0.0
                    tex5 = 0.0, 0.0
                    tex6 = 0.0, 0.0

                    if b < len(BLOCK_TEX_COORDS):
                        texupx = (BLOCK_TEX_COORDS[b*2*3 + 0]*32.0) / 512.0
                        texupy = (BLOCK_TEX_COORDS[b*2*3 + 1]*32.0) / 512.0
                        texmidx = (BLOCK_TEX_COORDS[b*2*3 + 2]*32.0) / 512.0
                        texmidy = (BLOCK_TEX_COORDS[b*2*3 + 3]*32.0) / 512.0
                        texbotx = (BLOCK_TEX_COORDS[b*2*3 + 4]*32.0) / 512.0
                        texboty = (BLOCK_TEX_COORDS[b*2*3 + 5]*32.0) / 512.0
                        tex1 = texupx,texupy
                        tex2 = texbotx,texboty
                        tex3 = texmidx,texmidy
                        tex4 = texmidx,texmidy
                        tex5 = texmidx,texmidy
                        tex6 = texmidx,texmidy
                    glNewList(dList, GL_COMPILE)
                    if b == BLOCK_COLOR:
                        DrawCube((0,0,0), (0.33,0.33,0.33), tuple(self.gui.colors[c])+(255,), tex1,tex2,tex3,tex4,tex5,tex6, self.tex, False, 32.0) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
                    else:
                        DrawCube((0,0,0), (0.33,0.33,0.33), (255,255,255,255), tex1,tex2,tex3,tex4,tex5,tex6, self.tex, False, 32.0) # 텍스쳐는 아래 위 왼쪽 오른쪽 뒤 앞
                    glEndList()
                    glPopMatrix()

                else:
                    glPushMatrix()
                    glTranslatef(x,y,z)
                    glCallList(dList)
                    glPopMatrix()
                idx += 1


            pos = self.cam1.pos
            pos = Vector(pos.x, pos.y, -pos.z)
            dir_ = self.cam1.GetDirV()
            dir_ = Vector(dir_.x, dir_.y, -dir_.z)
            dir_ = dir_.Normalized()
            dir_ = dir_.MultScalar(math.sqrt(2)*9.0)
            dir_ += pos
            self.prevBlock = self.lastBlock
            mat = ViewingMatrix()
            lookPos = None
            if mat is not None:
                self.lastBlock = lookPos = self.chunks.LookAtBlock(pos, dir_, 9, self.bound, mat)#self.difY)

            if lookPos and lookPos[4] != BLOCK_WATER:
                x,y,z,face,block = lookPos
                glLineWidth(6.0)
                #glDisable(GL_DEPTH_TEST)
                glDisable(GL_TEXTURE_2D)
                glBegin(GL_LINES)
                glColor4f(1.0, 0.5, 0.5, 0.8)
                if face == 0:
                    y -= 0.01
                    glVertex3f(x, y, z)
                    glVertex3f(x+1.0, y, z)

                    glVertex3f(x+1.0, y, z)
                    glVertex3f(x+1.0, y, z+1.0)

                    glVertex3f(x+1.0, y, z+1.0)
                    glVertex3f(x, y, z+1.0)

                    glVertex3f(x, y, z+1.0)
                    glVertex3f(x, y, z)
                if face == 1:
                    y += 0.01
                    glVertex3f(x, y+1.0, z)
                    glVertex3f(x+1.0, y+1.0, z)

                    glVertex3f(x+1.0, y+1.0, z)
                    glVertex3f(x+1.0, y+1.0, z+1.0)

                    glVertex3f(x+1.0, y+1.0, z+1.0)
                    glVertex3f(x, y+1.0, z+1.0)

                    glVertex3f(x, y+1.0, z+1.0)
                    glVertex3f(x, y+1.0, z)
                if face == 2:
                    x -= 0.01
                    glVertex3f(x, y, z)
                    glVertex3f(x, y+1.0, z)

                    glVertex3f(x, y+1.0, z)
                    glVertex3f(x, y+1.0, z+1.0)

                    glVertex3f(x, y+1.0, z+1.0)
                    glVertex3f(x, y, z+1.0)

                    glVertex3f(x, y, z+1.0)
                    glVertex3f(x, y, z)
                if face == 3:
                    x += 0.01
                    glVertex3f(x+1.0, y, z)
                    glVertex3f(x+1.0, y+1.0, z)

                    glVertex3f(x+1.0, y+1.0, z)
                    glVertex3f(x+1.0, y+1.0, z+1.0)

                    glVertex3f(x+1.0, y+1.0, z+1.0)
                    glVertex3f(x+1.0, y, z+1.0)

                    glVertex3f(x+1.0, y, z+1.0)
                    glVertex3f(x+1.0, y, z)
                if face == 4:
                    z -= 0.01
                    glVertex3f(x,y,z)
                    glVertex3f(x+1.0,y,z)

                    glVertex3f(x+1.0,y,z)
                    glVertex3f(x+1.0,y+1.0,z)

                    glVertex3f(x+1.0,y+1.0,z)
                    glVertex3f(x,y+1.0,z)

                    glVertex3f(x,y+1.0,z)
                    glVertex3f(x,y,z)
                if face == 5:
                    z += 0.01
                    glVertex3f(x,y,z+1.0)
                    glVertex3f(x+1.0,y,z+1.0)

                    glVertex3f(x+1.0,y,z+1.0)
                    glVertex3f(x+1.0,y+1.0,z+1.0)

                    glVertex3f(x+1.0,y+1.0,z+1.0)
                    glVertex3f(x,y+1.0,z+1.0)

                    glVertex3f(x,y+1.0,z+1.0)
                    glVertex3f(x,y,z+1.0)
                glEnd()
                glEnable(GL_TEXTURE_2D)
                glEnable(GL_DEPTH_TEST)



            GUIDrawMode()
            glDisable(GL_FOG)#;	
            if self.chunks.InWater(self.cam1.pos.x, self.cam1.pos.y, -self.cam1.pos.z):
                glDisable(GL_TEXTURE_2D)
                glBegin(GL_QUADS)
                glColor4ub(23,92,219, 100)
                glVertex3f(0.0, -float(SH), 100.0)
                glVertex3f(float(SW), -float(SH), 100.0)
                glVertex3f(float(SW), 0.0, 100.0)
                glVertex3f(0.0, 0.0, 100.0)
                glEnd()
                glEnable(GL_TEXTURE_2D)

            """
            glBindTexture(GL_TEXTURE_2D, self.guitex)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            #GUISt.RenderGUI()

            glBegin(GL_QUADS)
            glTexCoord2f(0.0, float(512)/512.0)
            glVertex3f(0.0, -float(512), 100.0)
            glTexCoord2f(float(512)/512.0, float(512)/512.0)
            glVertex3f(float(512), -float(512), 100.0)
            glTexCoord2f(float(512)/512.0, 0.0)
            glVertex3f(float(512), 0.0, 100.0)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(0.0, 0.0, 100.0)
            """
            """
            glTexCoord2f(0.0, float(SH)/1024.0)
            glVertex3f(0.0, -float(SH), 100.0)
            glTexCoord2f(float(SW)/1024.0, float(SH)/1024.0)
            glVertex3f(float(SW), -float(SH), 100.0)
            glTexCoord2f(float(SW)/1024.0, 0.0)
            glVertex3f(float(SW), 0.0, 100.0)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(0.0, 0.0, 100.0)
            """
            """
            glColor3f(1.0, 1.0, 0.0)
            glVertex3f(-10.0, 0.0, -10.0)
            glVertex3f(10.0, 0.0, -10.0)
            glVertex3f(10.0, 0.0, 10.0)
            glVertex3f(-10.0, 0.0, 10.0)
            glEnd()
            """
            #self.RenderWeapon(0,1,(255,0,0,255), False)
            self.RenderCrossHair()
            self.RenderHPMP()
            self.RenderMobHP()
            self.gui.Render(t, m, k)
            self.gui.RenderNumber(int(self.fps.GetFPS()), 0, 0)
            self.gui.RenderNumber(int(self.cam1.pos.x), 0, SH-20)
            self.gui.RenderNumber(int(self.cam1.pos.y), 40, SH-20)
            self.gui.RenderNumber(int(-self.cam1.pos.z), 80, SH-20)
            if self.digging:
                self.RenderBlockHP()
            pygame.display.flip()
                    


    def KeyTest(self, t, m, k):
        self.show = not self.show
        self.housing.Show(self.show)
    def OpenInventory(self, t, m, k):
        if self.guiMode:
            if k.pressedKey == K_c:
                self.gui.charTab = not self.gui.charTab
            elif k.pressedKey == K_i:
                self.gui.invModeIdx += 1
                if self.gui.invModeIdx >= 4:
                    self.gui.invModeIdx = 0
                if self.gui.invModeIdx == 0:
                    self.gui.makes = self.gui.makes1
                if self.gui.invModeIdx == 1:
                    self.gui.makes = self.gui.makes2
                if self.gui.invModeIdx == 2:
                    self.gui.makes = self.gui.makes3
                if self.gui.invModeIdx == 3:
                    self.gui.makes = self.gui.makes4
        if k.pressedKey == K_TAB:
            self.gui.qbMode2 = not self.gui.qbMode2
            if self.gui.qbMode2:
                self.gui.qbar = self.gui.qbar2
            else:
                self.gui.qbar = self.gui.qbar1
        elif k.pressedKey == K_i and not self.guiMode:
            self.guiMode = not self.guiMode
            self.gui.toolMode = TM_TOOL
            self.gui.ShowInventory(self.guiMode)
        elif k.pressedKey == K_c and not self.guiMode:
            self.guiMode = not self.guiMode
            self.gui.toolMode = TM_CHAR
            self.gui.ShowInventory(self.guiMode)
        elif k.pressedKey == K_e and not self.guiMode:
            self.guiMode = not self.guiMode
            self.gui.toolMode = TM_EQ
            self.gui.ShowInventory(self.guiMode)
        elif k.pressedKey == K_ESCAPE:
            self.guiMode = False
            self.gui.ShowInventory(self.guiMode)

    def GenId(self):
        r = self.id
        self.id += 1
        return r
    def Run(self):
        global g_Textures
        self.regenTex = False
        pygame.init()
        self.sounds = {
                "Dig": pygame.mixer.Sound("./images/digdig/thump.wav"),
                "Shovel": pygame.mixer.Sound("./images/digdig/shovel.wav"),
                "Put": pygame.mixer.Sound("./images/digdig/putblock.wav"),
                "DigDone": pygame.mixer.Sound("./images/digdig/digdone.wav"),
                "ShovelDone": pygame.mixer.Sound("./images/digdig/shoveldone.wav"),
                "EatItem": pygame.mixer.Sound("./images/digdig/eatitem.wav"),
                "Hit": pygame.mixer.Sound("./images/digdig/hitmelee.wav"),
                "Hit2": pygame.mixer.Sound("./images/digdig/hit2.wav"),
                }
        for sound in self.sounds.itervalues():
            sound.set_volume(0.8)
        isFullScreen = FULLSCREEN
        screen = pygame.display.set_mode((SW,SH), HWSURFACE|OPENGL|DOUBLEBUF|isFullScreen)#|FULLSCREEN)
        pygame.mouse.set_cursor(*pygame.cursors.load_xbm("./images/digdig/cursor.xbm", "./images/digdig/cursor-mask.xbm"))
        
        resize(SW,SH)
        init()
        self.WHITE_CH = (255,255,255,160)
        self.RED_CH = (189,45,6,160)
        self.BLUE_CH = (6,118,189,160)
        self.chColor = self.WHITE_CH
        self.curAttackingMob = None

        glViewport(0, 0, SW, SH)
        self.cam1 = Camera()
        self.cam1.pos.y = 90
        emgr = EventManager()
        self.fps = fps = FPS()
        emgr.BindLPressing(self.LPressing)
        emgr.BindLDown(self.LDown)
        emgr.BindLUp(self.LUp)
        emgr.BindRDown(self.RDown)
        emgr.BindRUp(self.RUp)
        emgr.BindRPressing(self.RPressing)
        emgr.BindKeyDown(self.OpenInventory)
        #emgr.BindTick(self.DoMove)
        emgr.BindMotion(self.DoCam)
        emgr.BindTick(self.Render)
        emgr.BindTick(self.RegenTex)
        self.font = pygame.font.Font("./fonts/NanumGothicBold.ttf", 19)
        self.id = 0
        # 스탯등을 올릴 때 처음엔 네 대 때려야 죽을게 3대 때리면 죽고 싸우다보면 2대 때리면 죽고 이런식으로
        # 좀 뭔가 레벨업 하듯이 할맛 나게

        
        #gui = GUI()
        #caret = Caret()
        #self.inventoryV = VisibilitySet()
        #cbg = InvenBG((0,30,500,450))
        #self.inventoryV.AddBG(cbg)
        #self.inventoryV.Show(False)
        #cbg = QBBG((0,450,300,30))
        self.gui = DigDigGUI()
        try:
            self.entity = pickle.load(open("./map/player.pkl", "r"))
        except:
            self.entity = FightingEntity("Player", {"HP": 100, "MP": 100, "Str": 5, "Dex": 5, "Int": 5, "Melee Damage":5,"Defense":5,"Poison Damage":5,"Poison Resist":5,"Electric Damage":5,"Electric Resist":5,"Ice Damage":5,"Ice Resist":5,"Fire Damage":5,"Fire Resist":5,"Sword Skill":5,"Mace Skill":5,"Spear Skill":5,"Knuckle Skill":5,"Armor Skill":5,"Magic Skill":5})
            entity = self.entity
            entity.curhp = entity.CalcMaxHP()
            entity.curmp = entity.CalcMaxMP()
        self.entity.eqs = self.gui.eqs
        self.entity.inventory = self.gui.inventory
        self.entity.onhit = self.entity.OnDead
        self.entity.ondead = self.entity.OnDead
        skills = (AppSt.entity.magics.values()+AppSt.entity.swordSkills.values()+AppSt.entity.maceSkills.values()+AppSt.entity.spearSkills.values()+AppSt.entity.knuckleSkills.values())

        idx = 0
        for skill in skills:
            self.gui.skills[idx] = skill
            idx += 1

        for item in self.gui.qbar1:
            sIdx = 0
            for skill in self.gui.skills[:]:
                if item and item.name == "Skill" and skill and item.skill.name == skill.skill.name:
                    item.skill = self.gui.skills[sIdx].skill
                    self.gui.skills[sIdx] = ITEM_NONE
                    break
                sIdx += 1
        for item in self.gui.qbar2:
            sIdx = 0
            for skill in self.gui.skills[:]:
                if item and item.name == "Skill" and skill and item.skill.name == skill.skill.name:
                    item.skill = self.gui.skills[sIdx].skill
                    self.gui.skills[sIdx] = ITEM_NONE
                    break
                sIdx += 1

        self.scripts = {}
        for coord in self.gui.codes:
            self.scripts[coord] = ScriptLauncher(coord)
        pygame.mixer.music.load("./sounds/digdigtheme.wav")
        pygame.mixer.music.set_volume(0.2)
        #pygame.mixer.music.play(-1)
        def prr():
            print 'aa'
        """
        but = Button(prr, u"테스트", (0,40,0,0))
        self.housing = VisibilitySet()
        self.housing.Add(but)
        self.housing.Show(False)
        emgr.BindKeyDown(self.KeyTest)
        """
        """
        but = Button(house.SetSE, u"남동", (0,40,0,0))
        self.housing.Add(but)
        but = Button(house.SetSW, u"남서", (0,80,0,0))
        self.housing.Add(but)
        but = Button(house.SetFloor, u"바닥", (0,120,0,0))
        self.housing.Add(but)
        self.housing.Show(False)
        """
        skin = [
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 0*64.0/512.0)],
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (1*64.0/512.0, 0*64.0/512.0),
            (1*64.0/512.0, 0*64.0/512.0)],
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0)],
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0)],
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (1*64.0/512.0, 1*64.0/512.0),
            (1*64.0/512.0, 1*64.0/512.0)],
            [(0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (0*64.0/512.0, 1*64.0/512.0),
            (1*64.0/512.0, 1*64.0/512.0),
            (1*64.0/512.0, 1*64.0/512.0)]]
        skin2 = [
            [(0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 2*64.0/512.0)],
            [(0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (1*64.0/512.0, 2*64.0/512.0),
            (1*64.0/512.0, 2*64.0/512.0)],
            [(0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0)],
            [(0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0)],
            [(0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (1*64.0/512.0, 3*64.0/512.0),
            (1*64.0/512.0, 3*64.0/512.0)],
            [(0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (0*64.0/512.0, 3*64.0/512.0),
            (1*64.0/512.0, 3*64.0/512.0),
            (1*64.0/512.0, 3*64.0/512.0)]]

        skins = {MOB_SKELETON: skin, MOB_NPC: skin2}
        self.mobR = MobRenderer(skins)

        """
        entity = FightingEntity("Mob1", self.cam1.pos, {"HP": 100, "MP": 100, "Str": 5, "Dex": 5, "Int": 5})
        self.mobs = [MobGL((0.0,0.0,0.0), self.bound, skin, MOB_SKELETON, (200,200,200,255), entity) for i in range(1)]
        """


        entity = FightingEntity("Mob1", {"HP": 100, "MP": 100, "Str": 5, "Dex": 5, "Int": 5, "Melee Damage":10,"Defense":5,"Poison Damage":5,"Poison Resist":5,"Electric Damage":5,"Electric Resist":5,"Ice Damage":5,"Ice Resist":5,"Fire Damage":5,"Fire Resist":5,"Sword Skill":5,"Mace Skill":5,"Spear Skill":5,"Knuckle Skill":5,"Armor Skill":5,"Magic Skill":5})
        self.mobs = []
        #self.mobs = [MobGL((0.0,0.0,0.0), self.bound, skin, MOB_SKELETON, (200,200,200,255), entity) for i in range(1)]

        try:
            self.stairs = pickle.load(open("./map/stairs.pkl", "r"))
        except:
            self.stairs = {} # 32x32x32의 청크수준의 좌표를 담음
        self.stairsDL = {}
        
        pygame.mouse.set_visible(False)

        import chunkhandler
        self.chunks = chunks = chunkhandler.Chunks()
        done = False

        glEnable(GL_CULL_FACE)
        self.tex = texture = glGenTexturesDebug(1)
        glEnable(GL_TEXTURE_2D)
        image = pygame.image.load("./images/digdig/manicdigger.png")
        #teximg = pygame.surfarray.array3d(image)
        teximg = pygame.image.tostring(image, "RGBA", 0) 
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
	glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)# Linear Filtering
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_NEAREST)
        #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)# Linear Filtering
        #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)# Linear Filtering

        
        self.mobtex = texture = glGenTexturesDebug(1)
        image = pygame.image.load("./images/digdig/mobs.png")
        teximg = pygame.image.tostring(image, "RGBA", 0) 
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
	glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)# Linear Filtering
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_NEAREST)

        self.skyeast = texture = glGenTexturesDebug(1)
        image = pygame.image.load("./images/digdig/clouds1_east.jpg")
        teximg = pygame.image.tostring(image, "RGBA", 0) 
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
        
        self.skywest = texture = glGenTexturesDebug(1)
        image = pygame.image.load("./images/digdig/clouds1_west.jpg")
        teximg = pygame.image.tostring(image, "RGBA", 0) 
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
        
        self.skynorth = texture = glGenTexturesDebug(1)
        image = pygame.image.load("./images/digdig/clouds1_north.jpg")
        teximg = pygame.image.tostring(image, "RGBA", 0) 
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
        
        self.skysouth = texture = glGenTexturesDebug(1)
        image = pygame.image.load("./images/digdig/clouds1_south.jpg")
        teximg = pygame.image.tostring(image, "RGBA", 0) 
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
        
        self.skyup = texture = glGenTexturesDebug(1)
        image = pygame.image.load("./images/digdig/clouds1_up.jpg")
        teximg = pygame.image.tostring(image, "RGBA", 0) 
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, teximg)
        MobRSt.RebuildMobs(self.bound)



        glMatrixMode(GL_MODELVIEW)

        try:
            self.cam1.pos = pickle.load(open("./map/pos.pkl", "r"))
        except:
            self.cam1.pos.y = 64.0+21.0;
        
        p = self.cam1.pos+(self.cam1.GetDirV().MultScalar(2.0))
        idx = 0
        for mob in self.mobs:
            mob.pos = p.x+idx*1.0, p.y, (-p.z)
            idx += 1
        
        """
        questIdx = 0
        quests[questIdx]

        SpawnNPC("name", "SpawnerName", quests)
        """


        checkargs = []
        doneargs = [("Bring 10 Cobblestone blocks", QUEST_GATHER, 10, BLOCK_COBBLESTONE, "Block")]
        oktext = "I need 10 Cobblestone blocks...\nWould you bring me 10 Cobblestone blocks?"
        notoktext = "Hi"
        donetext = "Thank you sir! Here's your reward."
        rewards = [(ITEM_SENCHANTSCROLL, 5, "Item"), (ITEM_SILVER, 5, "Item")] # 아이템이 한가지인경우 그냥생성, 아이템이 인챈트스크롤인 경우 함수로 생성

        quests = [
           {"CheckOKToGiveQuest": checkargs, # args = [(QUEST_REQUIREDQUEST, 1, npcname)]
            "CheckQuestDone": doneargs, # args = [(questText, QUEST_KILLMOB, number, mobid), (questText, QUEST_GATHER, number, itemid, itemtype), (questText, QUEST_REQUIREDQUEST, questid, npcname)]
            "OnRequestQuest": [oktext, notoktext], # questText는 퀘스트의 내용이 퀘스트로그에 표시되는 텍스트
            "OnQuestDone": [donetext, rewards]},
           {"CheckOKToGiveQuest": [], # args = [(QUEST_REQUIREDQUEST, 1, npcname)]
            "CheckQuestDone": [("Bring 10 Dirt blocks", QUEST_GATHER, 10, BLOCK_DIRT, "Block")], # args = [(questText, QUEST_KILLMOB, number, mobid), (questText, QUEST_GATHER, number, itemid, itemtype), (questText, QUEST_REQUIREDQUEST, questid, npcname)]
            "OnRequestQuest": ["I need 10 Dirt blocks...\nWould you bring me 10 Dirt blocks?", notoktext], # questText는 퀘스트의 내용이 퀘스트로그에 표시되는 텍스트
            "OnQuestDone": [donetext, [(ITEM_COAL, 64, "Item"), (BLOCK_LOG, 64, "Block")]]},
           {"CheckOKToGiveQuest": [], # args = [(QUEST_REQUIREDQUEST, 1, npcname)]
            "CheckQuestDone": [("Bring 15 Cobblestone blocks", QUEST_GATHER, 15, BLOCK_COBBLESTONE, "Block")], # args = [(questText, QUEST_KILLMOB, number, mobid), (questText, QUEST_GATHER, number, itemid, itemtype), (questText, QUEST_REQUIREDQUEST, questid, npcname)]
            "OnRequestQuest": ["I need 15 Cobblestone blocks...\nWould you bring me 15 Cobblestone blocks?", notoktext], # questText는 퀘스트의 내용이 퀘스트로그에 표시되는 텍스트
            "OnQuestDone": [donetext, [(ITEM_SILVER, 10, "Item"), (ITEM_GOLD, 10, "Item"), (ITEM_DIAMOND, 10, "Item"), (ITEM_IRON, 64, "Item")]]},
           {"CheckOKToGiveQuest": [], # args = [(QUEST_REQUIREDQUEST, 1, npcname)]
            "CheckQuestDone": [("Bring 15 Dirt blocks", QUEST_GATHER, 15, BLOCK_DIRT, "Block")], # args = [(questText, QUEST_KILLMOB, number, mobid), (questText, QUEST_GATHER, number, itemid, itemtype), (questText, QUEST_REQUIREDQUEST, questid, npcname)]
            "OnRequestQuest": ["I need 15 Dirt blocks...\nWould you bring me 15 Dirt blocks?", notoktext], # questText는 퀘스트의 내용이 퀘스트로그에 표시되는 텍스트
            "OnQuestDone": [donetext, [(ITEM_GENCHANTSCROLL, 5, "Item"), (ITEM_DENCHANTSCROLL, 5, "Item")]]},
        ]

        p = self.cam1.pos+(self.cam1.GetDirV().MultScalar(2.0))
        self.npcs = [MobGL((p.x,p.y,-p.z), self.bound, skin, MOB_NPC, (200,200,200,255), None, "Test") for i in range(1)]
        self.quests = {"Test": quests}
        self.questIdxes = {"Test": 0}
        self.questLog = {"Test": []}
        self.curQuests = {"Test": []}
        self.mobKillLog = {}


        #self.chunks.SaveRegion("test", (64,0,64), (127+64,127,127+64))
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
                    self.regenTex = True
                    g_Textures = []
                    pass
                emgr.Event(e)
            emgr.Tick()
            self.gui.invShown = self.gui.setInvShown
            self.regenTex = False
            fps.End()
            #print fps.GetFPS()
        self.chunks.Save()
        pickle.dump(self.cam1.pos, open("./map/pos.pkl", "w"))
        pickle.dump(self.gui.inventory, open("./map/inv.pkl", "w"))
        pickle.dump(self.gui.qbar1, open("./map/qb.pkl", "w"))
        pickle.dump(self.gui.qbar2, open("./map/qb2.pkl", "w"))
        pickle.dump(self.gui.boxes, open("./map/chests.pkl", "w"))
        pickle.dump(self.gui.codes, open("./map/codes.pkl", "w"))
        pickle.dump(self.gui.spawns, open("./map/spawns.pkl", "w"))
        pickle.dump(self.gui.eqs, open("./map/eqs.pkl", "w"))
        pickle.dump(self.stairs, open("./map/stairs.pkl", "w"))
        self.entity.ondead = None
        self.entity.onhit = None
        self.entity.eqs = None
        self.entity.inventory = None
        pickle.dump(self.entity, open("./map/player.pkl", "w"))



if __name__ == '__main__':
    def run():
        app = DigDigApp()
        app.Run()
    run()
    #chunkhandler.Test()
    """
    v1 = Vector(-1.1,0.1,-0.1)
    v2 = Vector(0.1,0.1,1.1)
    print v1.Dot(v2)
    """


"""
ㅋㅋㅋㅋㅋㅋㅋㅋ 마인크래프트 클론을 만들어서 드워프 포트리스처럼 만들자.
기본적으로 서버가 있고 무한맵.
음.... 맵 데이터를 DB에 저장하는가?
걍 리스트로 해도 졸라 느릴텐데, DB에 하면 더 느리겠지?
3차원인데 100000x100000x100000 막 이럴텐데 말이지.
Surface만 읽어올려고 해도 현재 뷰포인트에서 그걸 다 가져오는 알고리즘만 해도 엄청 느릴 것 같다.
그 부분은 Pyrex로?

일단 프러스텀 영역에 맞는 타일들만 가져와서
타일의 각 면이 다른 벽과 인접하지 않았다면 일단 그리고, 인접한다면 그 면은 뺀다.
면 단위로 한다.
거기서 다시 Z소팅을 통해 비지블 영역만 가져와야 한다. -- 이건 생략 가능. 단지 벽 뒷면이라던가 이런 부분은 그릴 필요가 없는데... 괜히 느리지 않을까?
쿼드 중에서 첫번째 vertex와 2번째 버텍스를 검사해서 플레이어를 향하지 않는다면 뺀다. Pyrex로.

- 프러스텀에 맞는 모든 쳥크에 대해(굉장히 많을 수 있고 맵 전체가 될 수 있을까? FAR PLANE이 있으니까 그거에 걸리겠지 뭐.
- 6개의 각 면에 인접하는 벽이 없으면 렌더리스트에 추가(제일 느림)
- 시계방향 검사 컬링(보이는 영역을 현재 coord로 cpu에서 트랜슬레이트 해야하지만 그래도 한다.)
- 타일링이 가능한가? 2방향으로 일렬로 쭉 검사. 2방향 중 평균 타일링이 가장 많이 되는 부분을 골라서 타일링함. GL_REPEAT으로 구현

즉 현재 보이는 타일만 가져오기 위해 이걸 다 해야한다는....
최적화 가능한 장소:
    땅이 예를들어 100x100x100으로 속에 빈 공간이 하나도 없을 때에는? 이걸 다 검사하면 진짜 느릴걸????
    100x100x100x6번을 검사해야 하는데 그럼 이건 완전 600만번을 검사해야 한다. 그러지 말고
    16x16x16 또는 일정한 숫자를 한개의 트리로 만들어서 미리 인접영역에 대한 검사를 해두고... 맵 생성시에
    실시간으로 업뎃한다.
    음...... 옥트리를 만들어서 속에 빈 공간과 인접한 영역에도 빈 공간/물타일 등의 투명타일이 하나도 없는 그런 트리는 아예 검사도 하지 않게 하자.
    또한 전체가 물타일인 트리 역시 주변이 다 물이라면 검사할 필요가 없고 뭐 이렇다.



Y축 갯수는 128층으로 제한한다. 땅 기준 평균 위로 48층, 아래로 80층
X,Z축은 그냥 맵을 돌아다닐 때 마다 생성된다. 자연동굴 기능은 아직 넣지 않는다.
맵이 일정 이상 생성되고 플레이어가 한 번도 본 적이 없는 땅 영역 안에 자연동굴을 넣어야 할텐데. 산도 이어서 만들어야하고.
음.... 그렇다면 아예 산, 강, 폭포 이런걸 기준으로 생성하고 타일만 그걸 기준으로 생성하도록 하면 되겠군?

1024x768해상도에서 최악의 시나리오는 2x2픽셀당 블럭 한개. 그러면... 프러스텀 안에 거의 512x512x512의 갯수가 있다.
그러면 이게 16x16x16으로 되어있다고 치고 그럼 32768개의 청크를 검사해야 한다. 하지만 이건 진짜 최악의 경우고 파 플레인이 있으니까
32x32x4 정도 해서 4096개 정도 검사.
음....아주 최악의 경우 보통 8만개의 트라이앵글이 그려지지 않을까 예상.
음...pygame으로 OPENGL로 하자. Ogre쓸려니까 뒤질거같음;
-------------------
음... 복잡한 GUI는 필요가 없다. 걍 이미지 출력으로 끝내자. 한글입출력은 간단함....
-------
http://www.crownandcutlass.com/features/technicaldetails/frustum.html
-------
일단, 옥트리의 각 꼭지점중 하나가 프러스텀 안에 있으면 프러스텀 안에 있는 것.
음....... 그런데 옥트리가 프러스텀보다 크다면?

프러스텀:
    꼭지점들
    선들
    면들

옥트리:
    꼭지점들
    선들
    면들

기본적으로 옥트리가 프러스텀을 완전히 감싸고 있을 경우 모든 차일드를 검사해서 프러스텀 바깥에 있는 걸 추려내야 한다.
프러스텀 바깥에 있는 거만 검사하는거다.
프러스텀 바깥에 있는 거는 어떻게 검사하나?
노드의 각 선이 완전히 프러스텀 바깥에 있고, 노드가 프러스텀을 완전히 감싸고 있지 않을 경우, 이건 밖에 있는거다. 나머지는 안에있는 것.

즉, 노드가 프러스텀을 완전히 감싸는지 검사
아니라면 노드가 프러스텀 밖에 있는지를 검사
아니라면 노드가 완전히 프러스텀 안에 있는지를 검사 --> 다그림
아니라면 노드가 반정도 프러스텀 안에 있는지 검사 --> 차일드를 검사하고 최종 차일드라면 다그림


필요한 수학도구: 프러스텀 안에 노드가 있는지, 걸치는지 검사하는 루틴
노드 안에 프러스텀이 완벽하게 감싸고 있는지 검사하는 루틴
프러스텀 밖에 노드가 있는지 검사하는 루틴

플레인만으로 볼륨안밖을 검사할 수 있을 것 같다. 아..... 각 프러스텀 플레인의 면으로 안밖을 결정하고, 만약 노드의 모든 면선점이 완벽하게 밖에 있다면
밖에 있는거고
아니라면 다음 플레인으로 검사해서 완벽하게 밖에있다 그러면 또 밖에 있는거고
최소 한 프러스텀플레인 / 최대 모든 프러스텀플레인으로 검사해서 완벽하게 밖에 있는 게 아니면 그리는 거다.
점이 밖에 있다면 면이 밖에 있는 거다. 그럼 점이 플레인의 +영역에 있나 -영역에 있나만 검사하면 된다.


	C.x = (A.y * B.z) - (A.z * B.y);
	C.y = (A.z * B.x) - (A.x * B.z);
	C.z = (A.x * B.y) - (A.y * a.x);
	v.x = point2.x - point1.x;
	v.y = point2.y - point1.y;
	v.z = point2.z - point1.z;

---------------------
음....... 
----------
GUI. GUI는 블릿으로 한다. 텍스쳐 4장에다가 그린 후 화면에 쿼드 4개로 Ortho로 뿌린다.
----------
이제 블럭 충돌검사, 땅파기를 구현한다.
chunkdata로 좌표 주변 4x4x4를 가져와서 충돌검사
팔 때마다 Octree변경 잘해야함
------
음 나는 봤음 블럭 뭔가 가리킨쪽에 안쌓이고 오른쪽끝자락에 쌓이는 버그를.
다시 해봣는데 안나타나지만 이런 버그가 있긴 있었다는 걸 기록해두자능.
음 내 생각에 아마 마우스가 잠깐 튀어서 그랬을 수도 있다고 생각되지만... 그건 증거없는 희망적인 생각일 수도 있고;;

아. 마우스 피킹하는 레이가 화면상에서는 내 앞에 있지만, 실제로는 레이는 블럭 좌표내에 Frustum을 적용하지 않은 좌표에 있다. 그러므로
그 레이가 실제 어떻게 생겼는지는 뭐 잘 모르지.
-----------------------------------------------
음 버텍스 라이팅을 할 때 어떻게 해야하나.
라잇 소스가 카메라 윗쪽 태양이라면 낮이면 어디에 가도 환하다 일단.
ColorPointer로 라이팅을 cpu로 계산?
아.....노멀이 있어야 라이팅이 되는군하;;
----------------
--------
이제 GUI를 하자.
---------
프로그램으로 함정, 기계, 머신건 도어 등등 여러가지를 만들 수 있다.
------
GUI했으니 이제 맵생성을 하고 파는걸 하고 여러블럭을 한다.
==0 또는 !=0이런것들 전부 제대로 바꿔줘야 한다.
-------------
만드는 거에만 집중하고 뭐 몬스터 이런 건 그냥 하지 않는다.
서로 싸우는 거는 기계 등을 진짜 강화시킨다.
-----------------------
알파값이 있는 face들은 따로 모아서 나중에 렌더링 해야한다.
----------
인벤토리 done
맵생성 done
아이템 half
토치와 라이팅
물이나 라바 흐르기
땅파기 구현 half
코드/기계
나무같은거 자라는거
몹, 전투 등등

물 흐르기는 옥트리에 contains_water 플래그값을 넣어야 한다.

전투는 커스텀 디펜스처럼 커스텀 스킬을 부여 가능.
---------------
"""
# 청크 쿼드트리, 청크 메모리가 꽉차면 프리하고 다른거 로드하는기능 꼭 넣기 XXX:
"""
한칸 Y값 차이나는 거 계단ㅁ 없어도 그냥 점프 안해도 걸어가면 올라갈 수 있게.
+1.0을 y에 해서 충돌검사에 안걸리면 y+1.0으로 고쳐서 하도록 한다.
------------
타일 채울 때 땅속에 grass가 없게 한다.
현재 채우는 땅의 바로 밑이라던가 그런데를 검사해서 grass면 없앤다던가
64이상의 타일을 다 검사해서 grass면 dirt로 바꾸고 이러면 된다.
-----------
땅팔때 애니메이션 말고 그냥 체력바를 표시하자.
현재 선택된 블럭을 하이라이트하는건 해야하는데 그거는 GL_LINE으로 할까 depth test 끄고
-------------
물속에서는 즉 물 블럭은 pick할지 안할지 옵션에서 조절해서 버켓인 경우 그리고 물속이 아닌 경우 물을 파고 그러게 한다.
--------
아이템이 나오면 일단 막 밑으로 떨어지고 옆으로도 살짝 튕기는 그런 효과가 있다가 땅에 완전히 떨어지면 static목록에 들어가게 된다.

Worldobject를 만들고
위치를 지정하고
그리면 땡

간단하게 하려면 아예 맵상에 존재할 수 있는 블럭 오브젝트를 제한하고 그 수가 넘...이건 접자. 그냥 그리면 됨.;
하지만 제한을 하기는 해야하고 시간이 다되면 지우는것도 해야한다.
땅에 버린 아이템은 저장되지 않는다.

이제 아이템 먹는거 까지 대충 했으니까 인벤토리에 아이템을 표시하고 클릭하는 그걸 구현한다. 전에 구현했었지 아마.....

인벤토리 /퀵바 드래그드랍을 구현
------------
자주쓰이는 글자들을 캐슁하는 방법도 좋다.
--------------
이제 아이템 제작 창.
그냥 특별히 제작 툴이 없어도 리스트에서 뭐든 만들 수 있도록 한다.
뭘 녹이고 이러는 거만 포지 옆에서 하도록.
나중에 기계로 만들면 대량생산이 가능하고...?!
-----------------------
이제 토치를 만들자.

옥트리 안에다가 토치를 넣어야 한다.
그리고 렌더링시 주변 4 옥트리를?.....음.
그러지 말고 chunk버퍼처럼 버퍼로 해서 주변 몇개를 쉽게 얻어올 수 있도록 한다.
대신 한칸한칸 하는게 아니라 8x8x8을 하나로 해서 그 안에다가 좌표와 함께 넣고 뭐 이런다.
그리고 주변 몇개를 얻어올까? 주변.... 꽤 많이 얻어와야할거같은데. 8x8x8짜리를 3개씩 얻어오면 16x16x16안에 있는 조명으로 밝히기를 하는 조명 할 수 있다.
-----
다하면 채팅기능. 명령어기능. sqlite를 이용해서 데이터를 저장하는 기능. 클래스 변경하면 호환성 없는 피클은 그만~
음 텍스트 에어리어는 넣었다. 자자.....
------------------------
이제 기계 만들어볼까?
텍스트 에디터는.. 하지 말고
파일 브라우져를 만들어서 스크립트 폴더에 스크립트를 넣으면 그 스크립트를 실행할 수 있게 한다. 루아로 할까 파이싼...파이썬으로 하자.
필드 아이템은...아이템은... sqlite에 넣자.;;;;
torch랑 chest는....그냥 다 만들었으니 놔두고 나머지는 앞으로는 sqlite ㅠㅠ
-----
mutex.lock(function, argument)
Execute function(argument), unless the mutex is locked. In the case it is locked, place the function and argument on the queue. See unlock() for explanation of when function(argument) is executed in that case.
mutex.unlock()
Unlock the 
---------
배선하기: 현재 보는 방향으로 세로로 뿌리게 한다. 다른 배선의 위치는 검사하지 않음. 알아서 해야함.
세로로 뿌리고 좌측으로 ㄱ인지 역기역인지만 결정하게 한다. ㄴ이나 역 ㄴ을 할 때는 반대방향에서 하면 됨.
아 전부 다 ㄱ자로 해도 되네? 동서남북인지만 알면....
땅에 까는건 일자 기역자 다 되고
면 2,3,4,5 옆면에 까는건 일자만 현재 방향에서 세로로 된다.
선이 겹칠 때 땅속으로 파고 들어가서 아...그럴 필요가 없는데. 그냥 겹치게 해도 원하는 효과 나올 듯.
걍 산 위에서 아래로 연결할 때를 대비해서 이렇게 한다.
-----------
배선하기
코드를 실행시에 8방향을 검사해서(코드블럭 자체에 붙어있는 배선은 건들지 않음, 하지만 언덕 위에서 연결하는 걸
지원하기 위해 현재높이 4방향, 한칸 위 높이 4방향을 검사함)
각각의 이 코드를 향하고 있는 배선을 쭉 따라가서
가장 마지막에 연결된 배선이 아닌 기계와 연결하고
그게 뭔지를 알아본다.
cpu, power따위는 없애고 코드블럭만 쓴다.
코드블럭은 OnHit(주먹으로 침, 화살등으로 쏨)으로 액티베이트 되거나
일정 거리 이상으로 사람이 들어오면 작동하게 하고
?블럭은 범용으로 여러가지로 쓰이게 된다.

나중에 스킨을 입혀서 문이나 뭐 그런걸로 변신하도록 하게도 한다.

Spanwer를 변수처럼 써서 그냥 coord를 대표하는 그런걸로 쓴다. 이름을 붙이거나 좌표를 써야함
처음엔 자동으로 이름이 붙어짐
게임상에 푯말 글자 출력도 막 네온사인처럼 움직이는 글자 할 수 있음!
------------
일단 아이템이 땅에 떨어지는 걸 구현한다.
스포너 위에 상자를 올리면 상자에 들어있는 아이템이 푝푝 튀어나옴? +_+
------------
자 이제....잡을 수 있는 몹과 전투 캐릭터를 구현.
너무 복잡하게 하지 말고...딱 디아2 정도만..-_- 하자. 진짜~~~어렵겠는데
몹은 그냥.... 일직선으로 캐릭터의 방향으로 점프를 하면서 달려오기만 한다. 길찾기 이런거 없음 막히면 못옴; 막혀도 오는 건 벽타고 오는거 뿐임;;
몹은

인간형은 사각형 머리 몸통 팔2개 다리2개 6개의 큐브로 구현. 큐브를 회전시키는 걸로 애니메이션을 구현
몹을 그렸는데........ 느린데? -_-
C로 그리고 pyrex에서 GL콜을 할까? 큐븐데 차이가 있을지....
큐브들을 텍스코드랑 같이 저장해두고
그걸 몹의 수와 몹의 애니메이션 상태를 따라 회전따로 다하고 뭐 이럴까
일단 pyrex로 버텍스 포인터로 해보고 느린지 보도록 하자.
---------
코드로 플레이어가 몹을 발견하거나 했을 때의 매크로도 짤 수 있도록.
뭐 매크로로 블럭을 짠다던가 건물을 짓는 것도 가능?
-----------
맵상의 아이템이나 몹들을 chunk9개 안에 있는 것들만 업데이트 한다.
싱글플레이어에서는 마스터 맵을 따로 저장하고 세이브파일로 마스터맵을 복사해서 플레이하고 세이브하게 한다.
몹 위에 체력바 그리기done
플레이어의 체력바 그리기done
-----------
블럭으로 몹을 가릴 수 있다. 충돌검사를 Python으로 가져온다. - DONE
----------
이제 일정 Range안에 들어오면 OnSpawnerRange 코드를 실행 하는 것과
몹이나 NPC를 좌측클릭하거나 우측클릭하면 액션이 실행되는 걸 하자.
우측클릭은 대화 좌측클릭은 상점이나 뭐 그런가? 우클릭은 대화 좌클릭은 공격을 하나.

일단 Hit으로 스폰 Hit하면 이벤트 파이어.
----------
아 스포너는 인터랙션이 없고 출력장치일 뿐이다.
코드가 인터랙션 다 받고 그런다.
코드 대신 뭐 스위치라던가 밟는 패널 이런거 전부 코드블럭이 모양만 다른 것이다.
코드 = 인풋+함수
스포너 = 아웃풋
스포너 대신 여러가지 아웃풋이 가능한 기능이 여러가지인 블럭들이나 횃불같은 아이템을 넣는다.

루프가 없으니 뮤텍스 쓸 필요도 없겠네;
---------------
몹이 많으니까 느리므로 최적화를 하던가
몹의 숫자를 최소화 한다! 1:1전투가 길고 리워드가 많으면 된다.
---------------
이제 전투를 구현한다. 아이템도 구현한다. 아이템 제작도 한다. 스킬도 구현한다.
---------
무기
방패
모자
몸통
장갑
신발
목걸이
반지

0, 200

26,228
26,262
26,296
26,330

250,228
250,262
250,296
250,330
---------------
주변 보더가 1인 글자를 그릴 수 있을까?
음 좌측 왼쪽, 왼쪽위 왼쪽 아래로 한번씩 복사하고
이런식으로 9방향으로 복사하면
대충 나오지 않을까.;; 
오 되넹;; (....)
------
엘레베이터, 자동차, 열차, 탈 수 있는 날아다니는 비행체 등등을 만들 수 있도록.
포탈은 없고 매우 빠른 열차를 이용할 수 있도록 하자.

심시티나 캐피탈리즘 같은 요소를 넣어? (....) 상점운영이 되도록 음....


네온사인을 만들기 위해 코드로 컬러를 바꿀 수 있는 이름 붙일 수 있는 블럭을 넣는다?
-----------------------------------------
일단..... 캐슁. 캐슁이 되야한다. 캐슁을 잘할 수 있는 방법이 없을까?
-------------------------------------------------------------------
6면이 다 가려진 건 한 번 뚫릴 때 까지 그려질 염려가 없다.
그러므로 뚫렸을 때에만 뚫린 부분에만 업뎃을 하면 된다.
반면, terrain부분은 계속 그려지고 계속 업뎃이 된다.
실시간으로 load/save를 해도 되니까 현재 뷰포인트를 중심으로 일정 박스 안에 있는 6면이 안가려진 놈들은 다 버텍스 캐쉬에 두고
한 번 캐쉬가 만들어지면 움직일 때 마다 안보이게 된 부분을 캐쉬에서 없애고 보이게 된 부분을 새롭게 추가하고 이러면 될 것 같다.
음 안보이게 되는 부분이라던가 보이게 되는 부분이라던가를 알려면
이 버텍스 버퍼 자체를 한 개를 만들어서 한번에 다 그리는 게 아니라
버텍스 버퍼 자체를 여러개를 만들어서 아하... 버텍스 버퍼를 여러개 만들어서 버텍스 버퍼가 더이상 필요 없어지면 다른 용도로 쓰거나 free하고
뭐 그러면 되겠구만.

파거나 하는 부분만 항상 새롭게 계산해 주면 된다!
레벨 6 수준이면 몇개가 되지...
레벨 5수준이면 몇개?
레벨 3 정도 수준으로 버텍스 버퍼를 여러개로 나누면 될 것 같다. 그럼 청크 하나에 64개의 버텍스 버퍼가 나온다. 이정도면 될 듯. 사이즈가 0인 건 그려지지도 않을테니....
그리고 변형되는 레벨3수준의 청크는 파면 버텍스를 추가하고 쌓아도 버텍스를 추가하고 버텍스를 없애는 건 뭐랄까 뭐 30초에 한번씩 업뎃으로 하고 이러면 될 것 같다.
---------------------------------------------------
캐슁 완료. 이제 radiosity....는 나중에 하자;;
일단 OpenGL로 진행되는 라이팅을 죄다 컬러버퍼로 바꿔야함. 그 전에, 각 버텍스의 컬러를 다르게 설정하면 그냥.... 비슷함.
--------------------------
음 그냥 주변 vertex color를 읽어와서 그거랑 선형보정? -_-?
좀 느리긴 할지도 모르겠지만 어차피 한번 그리는거고, 태양이면 고정이니까....
그거까지만 해도 굉장히 멋질것 같고, OpenGL라이팅을 끄면 radiosity만한 효과가 나올 것도 같고.
이런건 나중에 하고 이제 전투아이템을 만들어보고 아이템과 몹의 인터랙션을 간단하게 구현해보자. 스탯과 아이템을 구현해야!
-------
Entity에 OnDead이벤트 등이나 OnHit등을 바인드하게 해줘서 죽거나 맞을 때 애니메이션이나 제거, 아이템스폰 등을 처리해줘야 한다.
----
음 예제 게임을 만들면 게임 만들기가 아주 쉽게 해서 게임 만드는 툴 자체를 만들어보자.
-----
약한 아이템을 만들면 재미없으니까 일단 먼치킨 아이템과 먼치킨 몹으로 시작하자. 시작캐릭터도 먼치킨 그럼 누가이기지
키우는 재미 없이 플레이하고 아이템 얻는 재미만 얻도록 하자.
아...음..... 아이템을 사용할 수는 있지만 경제적인 요소에 더 집중을 일단

그러면..... 대화창을 만들고 선택할 수 있는 메뉴ㅜ가 있어야겠지.
파일 선택창을 개조하면 될 듯.
상점창도 있어야 하겠고..뭐.

캐슁을 했더니 넓은시야에서는 더 빠르고 좁은 시야에서는 좀 더 느린 것 같다. 시야가 좁으면 프러스텀컬링을 하는데 그게 잘 안되나?
---------------------------------------------
일단 캐릭터를 만들자....
스탯창, 스킬창을 만들자.
---------
스탯이나 스킬을 마음대로 올리면서 커스터마이징 해서 키우는 거 말고
그냥 드래곤퀘스트처럼 fixed된 걸 만들고
디아2에서 자주쓰이는 캐릭터 템플릿이나 울온의 템플릿처럼 좋은 템플릿을 만든다.
간단하게.
---------
일단 스킬을 사용할 수 있어야 한다.
스킬은 퀵바에 넣을 수 있다.
퀵바를 여러개 두고 퀵바 셀렉터에서 선택하도록 한다. 건설용, 마법용 등등으로 쓰도록.
Q를 누르고 1~0을 누르면 퀵바가 바뀐다.
좌/우측버튼 스킬설정
퀵바 스킬설정
아. 전투모드, 건설모드 따로 두고 퀵바 선택도 따로 하게하고 뭐 그럼 되나?
퀵바를 여러개를 두나.....
---------------------
음 무기 스탯은 드래곤퀘스트 비슷한 시스템을 넣어보자.
클래스를 고르는 것도 아니고 아예 드퀘4처럼 캐릭터를 고정해 보자.
주인공 역시 고정되어있음
-------
음.................게임 자체에 내가 질려있어서 그다지 재밌지가 못하다. 으헝헝
애니는...나중에 하고 공격하는 표시를 어떤게 할가?
----------------
공격표시는 크로스헤어의 배경을 색을 바꿔서 했다.
이제 음.... 아 알았다. 무기라던가 이런것의 실체에 대한 이미지가 머릿속에 너무 강해서, 무기 자체나 전투 자체의 실체는 보잘것없는 숫자라는 것을
잠시 잊고 있었다는. 게임 자체에서 보여주는 건 별로 없다. 상상력이 중요한 것. 게임을 하기가 힘든 건 상상을 하기가 힘들기 때문에 더욱 그렇지 않을까.
하여간에... 적은 정보와 알맞는 연출로 상상하기가 쉽도록 만들어주는 게 중요한 듯.
----------
스포너나 코드는 오른쪽 메뉴에서 파괴 버튼을 눌러야 파괴되도록 한다.
--------------
기본 게임 틀을 만들고, 유져가 게임 자체를 제작해서 다른사람이 플레이할 수 있게 유저 스스로 퀘스트나 아이템 등을 만들 수 있도록 한다.
admin모드로 들어가면 누구나 수정 가능하고 뭐 그런식.
멀티플레이어 가능하게 하면 진짜 좋을 거 같긴 하다.
------
self.mobs가 출현하는게 8군데 있다.(AppSt.mobs 이걸 그냥 그..... 딕셔너리 기반으로 해서 그.....
현재 청크 주변에 있는 딕셔너리에 있는 몹들만 표시되도록. 몹이 이동할 때마다 아...그 네트워크 게임에서도 비슷하게 했었지.
-----
이제 미니맵과 북쪽표시하기.
원형으로 해서 회전도 시켜야함
가장 높은 y청크를 얻어서 이미지로 C에서 만든 다음에 파이썬스트링으로 만들어서 파이썬으로 전달하면 여기서 텍스쳐 생성/리젠할때쓰면 됨
---------
왜 전투하는걸 못만드는지 알았다. RPG게임에서 전투는 가장 하기 싫은 "일"이다. 일거리를 만들려니 하기가 힘든 것.
-------
        # 스포너 뿐만이 아니라, 덮어씌울때 모든 아이템이나 상자등을 다 어떻게 처리한다? 아예, 그곳에 상자나 아이템이 있으면 로드하지 못하게
        # 막아야 할 것 같다. XXX:
        # 또한 복사할 때 스포너나 아이템이 복사되지 않도록 해야한다.(상자, 스포너, 코드블락)?
        # 음......여러가지 장치를 해둔 경우 그것도 복사하고 싶겠지만 그건 걍 포기??
        # 그것도 다 복사되게 해야하는 듯. 특히 복사하는 용도의 스포너는 복사하지 않고, 그 외의 스포너는 복사를 하되
        # 만약 스포너의 이름이 중복되는 경....음.................
        #
        # 아예 어드민의 용도로만 사용하게 하도록 하자 그냥;;
        # XXX: 이제 부수지 못하도록 스포너 2개로 Lockdown거는 것을 구현하자. 락다운을 걸면 땅의 주인만 락다운을 풀 수가 있음
        # 땅의 소유지를 결정하는 것도 스포너 2개로.
------------------------------
게임을 만드는 게임. 게임을 만드는 것 자체가 재미있으니까 게임을 만드는 게임. (....)
------------------------------
이제 계단을 만들어 보자.
그냥 Move함수에서 그리고 FallOrJump함수에서 조금씩 올라가거나 조금씩 내려가도록 boundy+위치y를 기반으로 검사해서 올려주거나 내려주면 된다.
----------
결국엔 몹이라던가 이런거 전부 C로 옮겨야 하겠지만 일단 여기서 계단을 만들어 보자.
-----------
GUI를 안그리면 30FPS가 나온다. 즉, 전부 C로 옮기고 vertexpointer를 쓰면 빠르지 않을까 싶다.
vertexpointer를 64번에 나눠 쓰는 것보다 한번에 쓰는것 역시 더 빨라지지 않을까? 메모리 복사가 가끔 일어나겠지만 말이다.

메모리 복사가 안일어나려면 그냥 음....여러번에 그리는 게 더 나을까?
------------
GUI를 일단 리스트에 버텍스, texit, texcoord, color, line인지 quad인지 여부를 다 저장해두고
업데이트가 한개라도 되었으면 rebuildvertexpointer로 전달해서 새로 만들고
업뎃이 안된 경우 그냥 전달해서 그린다.
아마 픽셀을 그리는 게 느린 경우일 수도 있다고 생각하지만 맵을 그리는 것도 빠른데 설마 그게 느려서 그런 건 아닌 것 같고
glbegin이 심각하게 느린걸로 생각된다. 그게 안느리다면 displaylist도 필요 없겠지.

아 그럼 gui를 디스플레이 리스트로 그리고 드래깅 중인 아이템만 그냥 그리고
나머지는 업뎃 될 때마다 디스플레이 리스트로 하고
게다가 뭐랄까 몹 애니메이션은...... 버텍스 애니메이션을 할까 스켈레탈 애니메이션 말고??
버텍스 숫자도 별로 안되는데 스켈레탈을 할 필요가 없는 듯?

버텍스 애니메이션은 매트릭스 트랜스폼이 없어서 더 빠른가? 한번 일단 테스트를

확실히 translation이 없으니까 훨씬... 빠르다.
하긴 translation이 있어도 빠르면 버텍스 애니메이션을 쓸 필요가 없었겠지
glGetMatrix?그걸로 로테이션 매트릭스를 가져와서 직접 변경시키고
각 프레임을 디스플레이 리스트로 만들어서 쓴다.
push하고 loadidentity부르고 로컬 회전/트랜슬레이션을 마친 후에 modelviewmatrix를 가져오면 될 듯 하다.
그리고 글로벌 트랜슬레이션/회전 한 번으로 한개의 몹을 그린다.
-----------------------
음 이제 큐브 인 프러스텀으로 했더니 G_FAR를 줄이면 좀 빨라진다.
-----------
태양광 계산도 버텍스 수준에서 하면 더 부드럽다.
그럼 그걸 하고 모든 라이팅을 버텍스라이팅으로 color버퍼로 하도록 해보자.
GenVerts에다가 태양의 Dir을 전해주면 그걸 GenQuads에서 써서한다
태양의 Y값이 0보다 크면 태양이 0인 것으로 간주한다.
하늘은....MODULATE로 어둡게 만들거나 점점 빨간색으로 바꾸다가 알파값을 0으로 만들기? 스카이박스를 안쓰고 밤이 있게하자.
계단도 태양광을 받아야 하고 몹도 태양광을 받아야 한다.
-----------------
자 저건 나중에 하고......이제 게임을 만들어 보자.
게임을 만든다는건
NPC인터랙션 메뉴를 만들고 상점등을 만들고
캐릭터 창을 만들고 스킬같은걸 고르게 하고
스킬을 사용하고 전투를 구현하고 뭐 그런걸 한다. 코드로 치면 게임의 내용과는 관계가 좀 없음

일단 장비를 입자

아이템 제작에 포지와 콜이나 챠콜이 필요하도록 하는 것도 필요하지만서도..
---------------
이제 인챈팅 테이블을 만들어서 아이템 인챈팅을 거기서 하도록 한다?
아니면... 인챈트 메뉴를 E버튼에 넣어 만들까.
음..........골드, 실버, 다이아몬드 한개와 인챈트 스크롤을 합치면 여러가지 속성이 있는 인챈트 스크롤이 나온다?
가장 약한 아이템이라도 실버/골드/다이아중 하나가 든다. 실버 골드 다이아는 희소성이 비슷하기 때문에 그냥....
속성이 다른 인챈트 스크롤이 나오기로 하고, 플레이어의 어떤 특정한 속성에 비례해서 더 좋은 인챈트 스크롤이 나오도록 하자.
아이템은 최대 5회 인챈트를 할 수 있고, 인챈트를 성공하면 스크롤의 속성이 ADD되며, 인챈트를 실패하면 스크롤이 날아간다는 슬픈 이야기가.
--------------------------------
이제 인챈트 메뉴를 E버튼에 다른 탭으로 선택할 수 있게 오른쪽 여백에다가 넣고
아이템의 속성을 보게한다
일단 그전에 공격력을 높여주는 엔티티를 만들자
자 그전에 버텍스 애니메이션을 하자
회전행렬, 트랜슬레이션행렬을 검색해서 수동으로 함
또는 회전행렬을 포함한 디스플레이 리스트를 여러개 만들면 되겠군?
용량이 쩔까나?-_-;
몹당 한개의 디스플레이리스트가 아닌 몹 종류당 또는 모든 인간형몹당 디스플레이리스트 1개 이렇게 하면 되겠지.
몹당 디스플레이 1개 하면 아 텍스쳐 코드만 바꿔주면 되겠구만 이라던가 그냥 몹 종류당 하나 하면 텍스쳐 코드도 안바꿔도 되고 텍스코드는
begin안에 드어가니까
음 걍 몹종류당 리스트세트 하나(애니 프레임당 리스트 1개)


스크롤을 넣는 창과 아이템을 넣는 창이 있고, 넣고 버튼을 누르면 인챈트가 완료?
그러지 말고, 인챈트 스크롤을 집고 그걸 무기 위에 오른쪽 버튼으로 드랍하면 인챈트가 적용? ㅇㅇ
--------------
랜덤한 구름을 128x128짜리로 한장 만들어서
전체 맵에 반복해서 흘러가게 한다.
태양은 뭐 그냥 동쪽에서 위로갔다가 서쪽으로 가고
태양을 GenQuads에 전달.
-------------------------
이제 스킬을 만들고 스킬 아이콘을 만든다.
초반 마법
Fireball
Lightning
Poison
Snowball
을 만들어 보자.
아이콘도 만들고 효과도 만들어야 하네!
공격 모션도 칼이나 손으로 때리는거 보여야하고. 일단 보류하고 스킬의 사용부터 하려면 아이콘부터.

탭키를 누르면 퀵바가 바뀌는건 완료.

스킬을 퀵바에 넣고 퀵바에서 스킬을 클릭하면 사라지고, 퀵바에 이미 스킬이 있는걸 스킬창에서 Pick하면 퀵바에 있는 스킬이 사라지고
정도를 구현해 보자.
스킬도 인벤토리처럼 한다. 60개의 스킬이면 충분함. 게임 끝까지 해도 남음

Char모드에 스킬탭, 캐릭터탭이 있다.
캐릭터 탭은 흰바탕에 그냥 글씨만 쓰면 될 듯. 스탯은 스킬을 쓸 때마다 제한없이 오르고 스킬수치도 무제한으로 오른다?
스탯은 str은 공격 dex는 방어 int는 마법atk이나 dfn에 영향을.
---------------
미니맵과 좌표를 출력하는게 필요함
-----------
효과가 없으니까 텍스트 창에다가 공격 내용을 출력한다.
텍스트창도 만들고 퀘스트창도 하자
음............그 뭐냐... 몹 애니메이션 하자.
----------
이제 퀘스트창이랑 현재 때리는 몹의 HP표시
-------
이제 캐릭터창. 스탯, 스킬을 그냥 표시하기만 함. 뭐 스탯도 쓰다보면 오르고 그럼
---------
몹도 계단을 적용시켜야함
------------------------
이제 몹, 블럭 필드 아이템, npc, 스포너, 코드등을 계단처럼 청크별로 저장해야함
--------------------------
맵 락 기능을 넣고 NPC를 하나 넣어서 대화를 하게 해본다.
물흐르기 라바흐르면서 데미지입기 등을 구현하고 뭐 포지라던가 그런 자원을 모아서 쓸 수 있게 하는 게 필요함
-------------
이제 npc를 어떻게 추가할까?
블럭을 하나 만들고 npc블럭? 스포너를 깔고 그 옆에 npc가 스폰되도록 하기? 그게 젤 좋겠다. npc스폰되고 관련 코드도 스포너에 다 들어있고.
스포너는 바닥을 파고 바닥에 깔면 그 바로 위에 npc가 스폰되는 걸로 하자.
스포너의 스킨을 바꿀까? 걍 쓸까. 음 플레이어가 코드의 일정 거리 안에 들어오면 코드가 실행되도록 해야
자동 스폰이 된다.

대화 세트를 뭔가 딕셔너리로 스크립트에서 만들어서 보내주면
대화 내용을 얻고
뉴 퀘스트라던가 그런걸로 새로운 퀘스트를 추가
퀘스트 완료 확인도 하고
OnQuestComplete라는게 있고 뭐....


OnTalk -- 대화를 하느냐, 퀘스트를 완료했는가를 체크해서 리워드를 주거나 퀘스트를 완료하고 다음 대화를 보여주고 이런다.
OnSelectMenuItem - 다음 대화를 보여주느냐, 어떤 상태값을 체크하느냐, 퀘스트를 받느냐를 체크
잠깐만. 선택지를 주고 마구 꼬으면 만들기가 힘들다. 만들기가 쉬워야 하니까
대화창을 주고 선택지 없이 퀘스트를 받거나 안받거나 완료하거나 안하거나 간단하게 한다.

# 이거면 충분함. 이걸로 다 구현할 수 있다능!
# 이걸로 가져오기 퀘스트(배달퀘스트도 버릴수없는 아이템을 주고 가져오기로 구현), 몹죽이기 퀘스트, 대화퀘스트 등을 다 구현 가능
# 특정한 기계를 작동해야 하는 경우 기계에 npcid를 부여하고 플래그를 셋
quests = [
   {
    "CheckOKToGiveQuest": args, # args = [(QUEST_REQUIREDQUEST, 1, npcname)]
    "CheckQuestDone": args, # args = [(questText, QUEST_KILLMOB, number, mobid), (questText, QUEST_GATHER, number, itemid, itemtype), (questText, QUEST_REQUIREDQUEST, questid, npcname)]
    "OnRequestQuest": [text, givequestfunc], # questText는 퀘스트의 내용이 퀘스트로그에 표시되는 텍스트
    "OnQuestDone": [donetext, donequestfunc]},
   {
    "CheckOKToGiveQuest": args, # args = [(QUEST_REQUIREDQUEST, 1, npcname)]
    "CheckQuestDone": args, # args = [(QUEST_KILLMOB, number, mobid)]
    "OnRequestQuest": [text, givequestfunc],
    "OnQuestDone": [donetext, donequestfunc]},
   {
    "CheckOKToGiveQuest": args, # args = [(QUEST_REQUIREDQUEST, 1, npcname)]
    "CheckQuestDone": args, # args = [(QUEST_KILLMOB, number, mobid)]
    "OnRequestQuest": [text, givequestfunc],
    "OnQuestDone": [donetext, donequestfunc]},
   {
    "CheckOKToGiveQuest": args, # args = [(QUEST_REQUIREDQUEST, 1, npcname)]
    "CheckQuestDone": args, # args = [(QUEST_KILLMOB, number, mobid)]
    "OnRequestQuest": [text, givequestfunc],
    "OnQuestDone": [donetext, donequestfunc]},
   {
    "CheckOKToGiveQuest": args, # args = [(QUEST_REQUIREDQUEST, 1, npcname)]
    "CheckQuestDone": args, # args = [(QUEST_KILLMOB, number, mobid)]
    "OnRequestQuest": [text, givequestfunc],
    "OnQuestDone": [donetext, donequestfunc]},
]
questIdx = 0
quests[questIdx]

SpawnNPC("name", "SpawnerName", quests)

메시지창을 띄우기 전에 퀘스트 완료를 검사해서
퀘스트가 관료되면 띄우는OnQuestDone을 쓴다.
즉... 루트는 항상 2가지를 가지고 있고 OnQuestNotDone, QuestDone을 가지고 있다.
한 NPC가 두가지 이상의 퀘스트를 가지고 있다면
루트를 리스트로 만들어서 1번이 다되면 idx+=1하고 2번을 출력, 2번이 다되면 3번을 출력 이런다.

이 텍스트들은 모두 다시 읽을 수 있도록 기능을 만들어 둔다.

메인퀘스트의 숫자가 몇 이상이 되어야 나오는 사이드퀘스트들도 있다?

NPC의 머리 위에 느낌표가 있으면 새로운 퀘스트
물음표가 있으면 퀘스트를 다 했냐고 물어보는 것
머리위에 상점아이콘이라던가 그런 걸 놓는다.

AppSt.gui.msgBox.Clear()
AppSt.gui.msgBox.AddText()
AppSt.gui.msgBox.AddSelection(bind)
def bind():
    AppSt.gui.msgBox.Clear()
    AppSt.gui.msgBox.AddText()
    AppSt.gui.msgBox.AddSelection(nextbind)

---------------
광산을 만들고 오어를 캐는 순간 리젠되게 하면 울온처럼 할 수 있다.
땅을 팔 수는 없고, 자기가 구입한 땅 영역 안에만 블럭을 사서 쌓을 수 있도록 하면 땡
상자는 아무데나 놓을 수 없고, 자기 땅 안에만 놓을 수 있다.
--------------------
잉여 인챈트 스크롤은 어따쓰게할까.

링류나 목걸이류는 인챈트 횟수가 10번 15번(골드) 20번(다이아)
--------------
이제 퀘스트로그를 만들어서 현재 퀘스트 진행 상황을 알려준다.
스포닝을 스포너에서 할 수 있게 하고 땅속에 묻은 코드블럭에게 가까이 가면 실행되게 하는 그런것도 넣는다.
코드블럭을 다른종류를 만들어서 가까이 가면 트리거되게? 아 옵션으로 LaunchOn Hit, Nearby등으로 넣는다. 체크박스....
------
틱에서 현재 좌표와 가까운곳에 코드블럭이 있는지 보고 있으면 레인지 안이면 코드실행을 계속 딜레이 줘서 한다.
-----------------------
잉여 인챈트 스크롤 같은종류 2개로 인챈트 스크롤 1개를 만들도록 하면 되려나?
-------------------
몹 스포너도 땅속에 묻고 최대 1마리가 리스폰되도록 한다.
RPG모드에서는 땅파기가 안되도록 한다. 땅은 내가 파서 맵을 다 만듬. ㅇㅇ..
-------------------------
음..... 퀘스트가 끝나면 다른 NPC의 퀘스트 리스트를 +1 하는 기능도 만들어야 하겠네.
음.... 퀘스트에서 다른 NPC의 퀘스트 리스트를+1하는게 빠를까 아니면 각각의 NPC에서 다른 NPC의 퀘스트Done을 체크하는게 빠를까.
첫번째는 까다롭고 두번째는 편리한데....
그냥 이 기능을 넣지 말자. (....) 각각의 NPC가 그냥 각각의 퀘스트를 줌. 다른 NPC와의 연계는 없음;;
아이템의 종류가 많다면 아이템을 주면서 뭔가 하면 좋겠지만 인챈트스크롤 만들 수도 있고 뭐.....
땅파기는 Dirt는 절대로 파지 못하게 하고 나무는 파게되면 나무가 사라지지 않도록 하자. Sand도 파지 못하게 할까?
음.....땅파기는 자기가 구입한 땅만 팔 수 있도록 해보자.
---------------------
퀘스트와......마을과........상점과......몹스포너등을 실시간 생성?
땅은 아무데나 파게하고 막 다 부셔도 멀리가면 마을 또있고 이런식으로?
어떤 마을을 생성하고
마을끼리 포탈로 연결할 수 있게 하고
포탈을 마을의 중심에 생성하고
실시간 생성이면 음....

맵의 리젼을 좀 제한해서 모로윈드 수준으로만 만들어도 괜찮을 듯. 그렇게 생성된 마을 안에 메인 퀘스트를 이리저리 꼬아서? 음..
---------------------
자.......이제 멀티플레이어 기능을 만들자능....

첫번째로 주변 32x32x32청크 수준으로 맵을 서버에서 다운받고
다운로드가 안된 맵은 움직일 수가 없음

블럭 파거나 쌓는걸 다운로드받고
움직임을 다운로드받고 뭐 이런다. 나머지는 뭐....공격하는 명령을 다운받음? 뭐 그런식.
-------------------------------------------------------
물흐르기, 라바흐르기, 라바에 닿으면 죽기, 라바영역을 구현하기
동굴만들기, 빛 계산 고치기, 네트워킹, RPG게임의 구현과 스토리짜기
-----------------------------------------------------------
흠.. 뭔가 심시티 같은 그런 이익을 생산해내는 놔두기만 하면 이익을 주는 그런걸 만들어야 한다.
블럭을 하나 만들어서 가만 놔두면 이익을 생산하도록 한다.
업그레이드도 가능하고, 골드, 실버, 다이아를 투자해서 업그레이드를 할수록 시간이 갈수록 점점 생산량이 많아지는 그런 것.
처음엔 광물을 캐지만 갈수록 이런걸로 돈을 번다.
좋은데?


코드블럭을 다른종류를 만들어서 가까이 가면 트리거되게? 아 옵션으로 LaunchOn Hit, Nearby등으로 넣는다. 체크박스....
------
캐피탈리즘2와 같은 개념을 넣고싶은데 어떻게 해볼까
파산하면 금을 캐서 재기할 수 있도록. 이히히

음....그러지 말고 그냥 아이템 뽑기를 힘들게 하자. 현재 스킬 기반으로 플러스 스킬이 나오는 게 아니라
+1될 때마다 기하급수적으로 어렵게 만드는 것.
----------------------------
흠...아이템 뽑기는 됐으니까 아이템 뽑을 재료인 금,은,다이아를 더 많이 벌 수 있는 방법을 캐피탈리즘과 같은 방식, 또는 땅파기 방식으로
할 수 있게 한다.
땅파기가 숙련되면 땅을 파서 좀 더 많은 광물을 같은 블럭에서 얻을 수 있게 하거나
캐피탈리즘처럼 뭔가 잘 하면..... 돈을 크게 벌고 망하면 돈을 못벌고 이런식.
재기는 언제나 땅파기로 할 수 있도록.

Business Block으로 이게 팩토리인지 상점인지를 결정하게 하고서는....
아 복잡하게 하지 말고 간단하게.
Business Block으로 주식에 투자해서 오르면 성공 망하면 잃고 뭐 그런식
아 아니면 GUI에 그냥 버튼을 넣는다.
10개의 주식을 두고 그중에서 투자하게 한다. 결국 슬롯머신 대신인가?
아...그냥 아예 슬롯머신을 넣자;;

그리고는.....몹을 잡으면 땅파는 것보다 금은다이아를 더 많이 얻게 한다.
아이템이 없으면 몹을 잡을 수가 없음 땅을 파야함
-----------------
아이템은 쓸곳이 있어야만 한다.
몹을 잡으면 퀘스트를 깰 수 있다는 것! (..)
-----------
파이어볼은 빨간 큐브(크기는 작음)
스노우볼은 하얀 큐브
포이즌은 녹색 큐브
라이트닝은 음....노란색으로 잘 만들어 보자
--------
슬롯머신: 땅파는 것보다 느린 꾸준한 이익을 얻을 수 있다. 가끔 더 많이 나온다. 잭팟이 터진다.
인챈트 아이템은 만드는 방법 밖에 없다.
몹을 잡으면 땅파는 것보다는 많이 실버 골드 다이아를 얻을 수 있다. 하지만 슬롯머신의 잭팟에 비하면 아무것도 아님.


게임의 목표는 슬롯머신에서 잭팟을 따는 것이다. 일반적으로는 잭팟이 거의 나오지 않지만 퀘스트상으로 잭팟이 나온다.
만약 일반적으로 해서 잭팟이 나오면 보너스 엔딩!


슬롯머신: 기본적으로 3개가 똑같이 나오면 그 오어 64개가 나온다.
대각선 이런건 안쳐줌
2개가 똑같으면 2개가 나오고, 다 다르면 아무것도 안나온다.
실버 골드 다이아 중 1개를 넣으면 슬롯머신이 돌려진다. 다이아는 통상의 2배 골드는 1.5배 실버는 1배.
걍 막 랜덤하게 하지 말고 2개 나올 확률이 50%인데, 그 50%중 실버2개 나올 확률 50% 골드나올 확률 30% 다이아 나올 확률 20% 이렇게 한다.
3개가 똑같을 확률을 1%
다이아 인챈트 스크롤이 3개 연속으로 나오면 잭팟인데, 그 잭팟이 터질 확률을 0.00001%로 한다.
즉, 허접한 슬롯머신.
아무것도 안뜨는 것을 랜덤한 조합으로 하게 하고, 나머지는 고정 확률
일반적인 슬롯머신을 쓸 때 잭팟이 뜨면 엔딩이 빨리 나오게 해서 더 허무하게 한다.
-------------------
유져가 박스를 땅에 깔고 일정 거리 이상 멀어지면 박스가 인벤토리에 들어오도록 한다.
인벤토리에 빈 공간이 없으면 인벤토리의 아이템 1개를 박스에 넣고 빈공간에....
박스에도 인벤토리에도 빈 공간이 없으면 박스를 하나 생성해서 생성된 박스 안에 박스를 넣고 인벤토리 아이템 하나도 그안에 넣고 인벤에 넣는다.
단, 집에 있는 박스는 그렇게 되지 않도록 한다.
---------------------------
5개의 퀘스트
땅을 파라고 한다
다이아 9개를 모아서 슬롯머신을 만들어 오라고 한다
몹 스포너에 대해서 이야기 한다, 몹을 스폰하여 몬스터를 잡도록 한다. 다이아 9개를 더 모아서 몹 스포너를 만들게 하여 몹을 잡게 한다.
몹 스포너의 몹은 캐릭터의 스킬과 비슷한 몹이 항상 비례해서 나오게 한다. 캐릭터가 강해질수록 강한 몹이 나온다. 잡스킬을 많이 올리면 잡스킬이 많은 몹이 나온다
캐릭터가 어느정도 강해지면 슬롯머신의 해킹방법을 알려주고 코드를 짜게 한다. 특정한 코드를 입력하면 잭팟이 한방에 나오게 된다.
 -- 여기서 실버 64개를 모아오고
 -- 또 골드 64개를 모아오고
 -- 또 여기서 다이아 64개를 모아오면 스크립트 언락을 해준다.
 -- 직접 코드를 짤 필요는 없으며 퀘스트가 끝나고 코드블럭을 설치한 후에 script내에 스크립트를 실행하면 바로 잭팟이 터진다. 스크립트 activated메시지가
    뜨도록 한다.
    퀘스트 완료 전에는 스크립트를 실행해도 언락이 안된다. Encryption key is missing이라고 한다.

6:4:3으로
실버 골드 다이아를 환전 가능하게 한다.
상점에서 하게 한다.
2:1실버로 철도 구입할 수 있도록 한다.
4:1실버로 모래나 DIRT도 구입 철이 아닌 모든 블럭은 4:1실버로 살 수 있다. LOG는 실버와 1:1임
2:1실버로 석탄도 구입
석탄을 쓸곳이 많으면 좋을텐데. 일단 대장간이 없더라도 무기장비 만들때 석탄을 쓰도록 한다.

여러가지 dirt나 잎사귀 같은 것도 팔아서 실버를 모을 수 있도록 하거나 실버로 모든 블럭을 다 살 수 있게 한다.
마지막으로 "컬러블럭"을 만든다. 2실버로 1블럭을 살 수 있는데, 구입시에 컬러를 정해서 일정수량을 구입할 수 있다.
컬러를 바꾸고 싶다면 제값 다 받고 팔아서 다시 구입하면 된다.

마지막으로 물흐르기 라바흐르기 라이팅고치기


저걸 완료하면 일단 압축해서 저장해두고 조금씩 향상시킨다. 게임 만들기를 더 편하게 하고 뭐 이런다. 컴퓨터를 구입하게 되면 그래픽도 향상시켜서
결국 완전한 게임 엔진 하나를 만든다. 모델같은것도 로드할 수 있게 한다.


일단, 환전소 스크린을 만든다. 블럭 판매소 스크린도 만든다.

음....이런 판매소를 inventory를 열면 "탭으로" 선택할 수 있게 한다.  일단 i 키로 사이클할 수 있게 한다.

        # HnH같은 방식으로 맵을 만들고 아이템등도 만들고서는.....
        # 음식을 제공하는 뭔가를 만들고 30일에 한번씩 업뎃해야 계속 살아남을 수 있게 해서 30일 후에 계정 삭제를 그런식으로 구현
        # 주인이 없는 땅은 자동으로 풀리고 광물의 원상복구가 된다.
        # 땅은 땅 표시 블럭을 뿌리고 작동시켜서 동남,서남,동북,서북쪽으로 가로 몇칸 세로 몇칸을 구입할지 결정하면 X,Z평면이 모두 자기땅이 된다.
        # 울온같기도 하면서 HnH같기도 하고 자기 땅에다가 몹 스포너같은 걸 만들어서 이용자들에게 아이템을 제공하게 하고
        # 개인 던젼이나 개인 상점 등을 만들 수 있게 한다. 큰 성도 지을 수 있겠고 뭐 그럴 듯.
        # 기본적으로 남에 땅에는 들어갈 수 있지만 남에 아이템은 만질 수 없고 부시거나 뭔가를 쌓을 수도 없다.
        # 갇히는 걸 방지하기 위해 땅끼리는 일정 간격(4칸?)을 떨어지게 하고 땅의 표시점 옆으로 워프하여 나가는 메뉴도 제공한다.
        # 땅의 주변 테두리 2칸은 주인이 정할 수 있는 컬러블럭으로 채워지게 된다. 땅을 팔게 되면 그 영역은 리셋이 되어 저장한 맵 생성 데이터로 재생성 되게 된다.
        # 모든 아이템이 사라짐! 그러므로 땅을 팔 때에는 그러한 경고문을 넣고 체크박스를 체크하고 OK를 누르게 한다.

colors는 있으니까 인벤토리에 있는 블럭이 컬러블럭일 경우 ModBlock에다가 컬러를 넘겨준다.
렌더링시에 블럭의 타입이 BLOCK_COLOR면 따로 렌더링한다.
음...........컬러를 HSV로 하는게 나을뻔 했나 아니면 이것도 괜찮은가. 이건 TODO


이제 환전소만 하면 된다.

#인챈트 스크롤 복사하는 아이템이 고급 몬스터에게서 떨어진다. XXX:
쩌는 인챈트 스크롤이 있으면 그걸 복사해서 쓸 수 있음!

뭔가 멋진 성도 짓고 이래서 뭔가 멋진 게임을 만들 수 있을 거 같은데!


게임 스토리가 있어야 하는데 그걸 먼저 써야겠다. 한글로 쓰고 영어로 번역한다.
설명체로 쓴다. 설명체로도 충분히 스토리가 가능함


+수준이 높을수록 더 강한 몹도 나온다. 즉, +는 강한 몹을 나오게 하기 위한 것.
아이템 제작 10만번을 채우면 +5000이 무조건 나오게 할까 말까
--------------
마스터 맵이 있고 그걸 카피해서 다른 세이브파일을 만드는 그런 기능을 만들어야 한다.
----------------------
이게 완성되면 웹게임으로 슬롯머신 인챈트 그걸 한다. 이걸 완성하고 한다.
---------------------
스크롤 2개로 스크롤 만드는 게 문제가 있다. 좋은게 나왔는데 그걸 써버릴 가능성이 있음.
스크롤을 실버로 바꾸게 할까...
스크롤을 드래그 해서 드랍해야지만 팔리도록 특별하게 한다.
컬러블럭도 그렇게 한다.
----------------
일단 몹 스포너부터 만들고 몹에게 지면 몹이 사라질 뿐이다.
몹 스폰을 하는데에는 1 실버가 든다.
몹을 잡으면 실버골드다이아가 나온다.
몹의 강하기는 자신의 최종 스탯과 비슷하게 나온다.
각 무기의 공격력과 방어력을 높여주는 스킬을 패시브로 하고 특별한 스킬도 넣는다.

음 몹을 랜덤하게 생성할까 아니면 플레이어가 몹을 디자인할까.
플레이어가 몹을 디자인하는데, 더 강한 스킬을 줄수록 더 많은 리워드를 얻도록 한다.

즉 오른클릭하면 몹 스폰 메뉴가 나오고 돈을 얼마 들일것인지 결정하고
적당한 돈을 들이면서 몹의 강하기 정도가 나오고 리워드가 표시되고 스폰 버튼을 누르면 몹이 스폰
내가 이기면 리워드를 얻고 내가 죽거나 일정 거리를 벗어나게 되면 들인 돈의 반을 돌려주고 패배

게임은 거기까지고 이제 스토리를 만들어야 한다. 건물도 많이 지어야 하고....
-----------------------
각각의 청크 캐쉬 버퍼의 사각형을 멀리있는거부터 그리고(투명블럭만)
청크 캐쉬 버퍼 자체도 멀리있는거부터 그려서
투명한 블럭의 에러를 해결한다.
--------------------------
멀리있는거부터 하는건 간단할 것 같고
일단 스토리라던가 그런걸 짜야할텐데.
스토리가 있고 그걸 기반으로 퀘스트를 짜야한다.

요즘은 자극적인 스토리를 짜서 그걸 포장해서 덜 자극적이도록 보이도록 하는게 유행인데....
성경의 스토리를 그대로 각색해서 짜서 창세기부터 요한계시록까지 스토리를 짜본다.
주인공은 한명으로 하고 예수님을 상징하는 존재를 한 명 둔다.
주인공은 하나님의 말을 듣지 않고 자기가 하고싶은대로 하지만 그럭저럭 착한사람으로 그린다.
주인공이 어떻게 된다는 말은 없고 그저 성경에 나오는 스토리와 비슷한 스토리를 열거하고 말해준다. 주인공은 그걸 경험한다.
---------------
매닉 디거의 Cuboid기능도 넣어야 한다.
----------------
그렇게 여러가지를 하고 나서 게임 제작 엔진으로 만든다. 나중에 컴퓨터를 구입해서 VBO등을 지원하는 옵션등을 넣고 뭐 그런다.
-----------------
스토리를 대충 짠다.

일단 주제가 필요하다. 주제는 역시 카지노 대박나는 스토리
스토리 간략하게 카지노 해킹 모듈을 설치해서 대박이 나는 스토리이다.

사이드스토리가 많이 필요하다. 에피소드. 그리고 주 스토리 관련 에피도 많이 필요하다.

장사를 해서 물건을 팔 수도 있게 대항해시대와 같은 방식.
이런 장사 아이템은 사용하거나 보이지는 않고 텍스트로만.

순간이동 또는 앞쪽으로 수십칸을 빠르게 이동하는 그런 걸 구현한다. 터보 이동
------------
wxPython등을 써서 OnDraw를 설정할 때 다시 그려야하는 영역만 다시 그리는 똑똑한 코드가 필요하다.
--------------------------
구텐베르크에서 여러 스토리를 읽어와서 각색만 해서 연출만 다르게 하고 그대로 쓴다.
오즈의 마법사가 에피소드 하베스팅에 꽤 괜찮은 것 같고, 허클베리 핀 같은 것도 괜찮은 것 같다.
책이 정말 많은데 에피소드를 모아서 나열하고, 그 에피소드를 지나가면서 메인스토리가 진행하도록 한다.
메인스토리와 에피소드는 별개이지만 메인스토리와의 연관성이 조금씩 있어야 하니까 그걸 좀 맞게 진행한다.
연관성이란 건 같은 캐릭터나 그런 사람들이 연결되거나 그런 쪽으로 가장 연관성이 있고, 같은 물품이나 아이템 등도 연관성이 있다.
어차피 완성도 따질 것도 아니고 게임에서 스토리는 중요치 않은 편이니 발로 쓸 스토리지만 꽤 흥미있을 것 같다.
Tik-tok of oz를 성인버젼으로 각색해서 DigDig에 어울리고 판타지에 어울리도록 각색하면 될 듯 하다.

처음 시작은 일하기 싫어로 시작해서
여러가지를 겪은 후에
그냥 전에 하던 일이나 계속 해야겠다 이걸로 끝난다.
무슨 북한 선전물 같긴 한데 딱히 떠오르는 게 이거니 어쩔 수 없지.



Workaholic

"I don't want to work!", Jake cried. "I can't code anymore. My mind won't obey my command anymore!"

Jake was a Programmer. He worked at Casino Enmity as a master developer.

In Kingdom Vegas, people worked as a miner at day, and after work they all submitted themselves to God, named Vegas. People rarely encountered with silvers, golds and diamonds while mining and they spent all their earnings in gambling in nearest city casino.

People always wanted have their own homes. In glasses, In colored glasses. To buy colored glasses they needed money.
All they had abundantly was woods and stones, and people didn't like wood and stones. There were so many stone and wood houses and people didn't like it.

They dreamt of hitting a jackpot and building a large house or castle or tower with colored glasses.

Besides miners, there also was Warriors and Magicians. By killing monsters they could earn some silvers. Every one of Kingdom Vegas wanted to build a house with colored glasses. So Warriors also gambled.


Jake was updating a World Maintenance code. Kingdom Vegas was mainly a Spirit City. Actually, people in Kingdom Vegas didn't have their own body. Everyone was just a spirit. And they made a spirit program to make realize a Virtual World and people connected themselves into the Spirit Core and that was how they could communicate, work, spend time. Without the Spirit Code, they could not communicate with each other, nor could do something fun or interesting. All they could do was feel eternal emptiness around themselves and suffer. So a spirit named Vegas sacrificed himself and made a Virtual World where people could communicate with each other and have a fun time.

First it was just bunch of mother nature. So people dug the ground and cut the trees and built themselves a home and community centers. And then people invented more sophiscated building block named Color Block. But since a world has limited supply of Vegas' spirit, not everyone could have colored blocks. Actually colored blocks were pretty abundant but there were so many spirits. To get a colored block they had to sacrifice a silver into the Spirit Core. There were silver everywhere and you could get silver with gold and diamonds and you could dig up silvers and golds and diamonds anywhere deeper than level 64. World was actually infinite, so people dug and dug and they got tired of digging ground so they made a Casino and they Gambled. It's so hard work to just dig around, people wanted to boast in their homes to forget there pain. They were spirit. Nobody HAD to work. They worked because it was fun. Spirits don't die. They just eternally suffer. But the fun soon became another suffering. So they invented gambling.

With this great Spirit Core people started build a Kingdom and they called it Kingdom Vegas. And people made a city.

World was made of spirit named Vegas. And since it was just a mind of a spirit, it always kept breaking. So there were many Core Programmers to maintain their world. Spirit Vegas was a spirit no more. Spirit Vegas became an energy and it supported this Virtual World. Nobody knew what spirit vegas would feel or think. They just lived there. Some people called Vegas a God and some people called Vegas a stupid moron. Since nobody knows what sacrificing himself would cause how much pain.

Jake was one of the core programmers. If you become a core programmer and maintain a world for 50 years, you could get a bunch of diamonds and get huge number of Color Blocks and build another City and boast in their pride eternally. But programming was really hard. It's just that, it was easier than and funnier than digging the ground. Jake needed something that could work easily and faster.

"Do I have to do this for another 23 years.... if only I could do anything without pain and suffering.... even doing nothing alone would be fantastic!", Jake thought.

"Hey Jake! It's about the Gamble Time. Fix it already!", John said.

"Why, you could fix it for me", Jake said.

"I'm fixing my own quota. Do your work.", John said.

"I don't want to work. How are you managing this stupid workload. I mean, it's easier than digging around but it's still hard. You could boast about being a programmer and be happy but it's still a lot of work", Jake said.

"You want to know the secret? I only have 5 months left until my payday.", John said.

"Oh my! It's already been that long? Hey maybe some guy could sacrifice himself once more and Core won't break that easily!", Jake said.

"But who would suffer the great pain of sacrifice?", John said.

"I don't know... someone stupid enough to sacrifice himself like Vegas did. Hahaha.", Jake said.

"I heard that there is somewhere called Heaven and in that place, there is no suffering.", John said.

"Wow.... that is like my dream. I mean, if we didn't suffer in the first place, we don't have to have a fun anyways. Isn't it?", Jake said.

"I don't know.... fix it already!", John said.

Jake finally got it and a glitch in the entrance of Casino fixed and people could come in and submit themselves to God Vegas. It means, they gambled.


"Ohhhhhhhhhhhhhh myyyyyyyyyyyyyyyyyyyyyyyyyyyy !!!!!!!!!!!!!!!!!!!!!!", Someone cried.

"I've got 64 diamonds! Woohoo!"

Jake heard it and laughed. "Idiots..... I could get 10000 chestful of diamonds in 23 years.... even the jackpots still 10 chests! You are just giving ME all your diamonds for ME!", Jake thought.

Jake went his way home. In his way home, suddenly a magician appeared. "Give me the access code to the Casino or I'll make you suffer just like Vegas!", Magician said.

"Wh...what? What access code?", Jake said.

"Access code! So I can hack into the slotmachine system and get infinite jackpots!", Magician said.

"Ha there is no such a thing! Mammon himself created that machine and that is one thing where glitch doesn't appear! And what do you mean suffer like Vegas! Vegas doesn't exist anymore! It's a Kingdom! Can you make me like Vegas so I can be the Core too?", Jake said.

"Haha you don't remember anything do you? Since you don't know about access code let me just tell you how you can get so much diamonds. Go below. Below the indestructable blocks there is a Cave. Go in there. And you will see.", Magician said.

"Wait... what? If you could get so much diamonds, why would you need some stupid access code? Why don't YOU go there?", Jake said.

"Hahaha you don't know anything. You don't remember anything!!!! You Idiot!!!!!!!!!!!", Magician said it and disappeared into thin air.

"What was that all about... why isn't he working hard just like everyone else? There is no such a thing as shortcut anyways... you either dig or gamble or work as a Core Programmer! And that's it!", Jake thought and went home.








"I know what this place is! I remember everything from the begining! We once was called human. And then Jesus the son of God came to save us but we didn't believe it so we came to this place. This place is called hell!", A crazy man said.

"Hey, I don't remember anything just like everyone else but I know this. Heaven is just a fairy tale! Are you saying that there really is a place called Heaven? Then, tell me, how do we get there you crazy spirit!", Jake said.

"We can't. We are destined to suffer in this place forever. No amount of effort will make us escape from this agony....", And crazy man finally collapsed.

"Ha, I know we are suffering, but who are you to say that there is a place there is no suffering! You crazy fool!", Jake bitterly spitted it out and left the crazy man.

Jake went deeper into the cave. And Jake finally found the mind of Vegas!


"Help.... Mammon tricked me..... he said if I sacrifice myself just like Jesus did, we could be saved.....", Vegas cried.

"Wait.. what? I came here to get some diamonds! What the heck are you saying! Are you saying that there is heaven?

"Help..... I'll give you 1000000 diamonds, just release me from this stupid trap.......", Vegas cried.

"No.... even if you give me so much diamonds, if I release you, this world will vanish!", Jake said.

"You idiot...... we are suffering the same....... whether this world exist or not we are still suffering!", Vegas said.

"What the hell are you talking about? How are we suffering? If only I had diamonds, I could buy bunch of Color Blocks and build a giant castle and boast eternally! That's what I call Heaven! Ha! Just give me the diamonds before I make you suffer even more!", Jake said.

"Fool.... we are suffering the disconnection from God..... not the pain.... pain is nothing.... we are disconnected from out father God and that is the eternal pain you fool!", Vegas said.

And then, Jake remembered. Why he was here. He remembered everything, just like crazy man. "Oh no..............", Jake cried. And then, Jake collapsed and finally realized again what that emptiness was about. It was disconnection from God. So, Jake released Vegas and forgotten everything again.


THE END
----------
일단 멀티플레이어 기능을 만들어 보자.

서버에서 청크를 매니지
클라에서도 청크를 매니지
맵생성 등은 다 서버에서 담당
클라에서는 맵을 다운로드 받아 렌더링만 한다.
주변 128x128x128맵만 다운로드 받음.
그것을 벗어나면 다운로드도 받지 않고 아예 Free해버림
코드가 바뀔 건 없고 서버용으로 코드를 추가하면 된다.
음 digdig.py를 임포트해서 서버코드도 digdig.py에 넣자.? 그럴필요가ㅣ;

32x32x32수준으로 계속 다운로드 받고
먼저 다운받으면 바로바로 렌더링 한다.
다운 안받은 쪽의 땅으로는 이동이 안됨.
사람들이 블럭을 변경하면 바로바로 업뎃한다.

물흐르기도 구현해야한다
그림자조명 고치고 뭐

그전에 전투를 완성해 볼까? 뭐가 더 필요한지 잘 생각해보고 하나하나 한다.
스토리 없이 던젼크롤처럼 해보자
--------------------------------
자.... 다 접고 일단 귀찮은 일을 컴퓨터 프로그램이 대신 해주는 것에 대해 생각하며 아이디어를 짜보자.
뭐 새로운 아이디어를 내서 하기 보다는, 이미 있는 일들 중에 귀찮은 걸 대신 해주는 프로그램을 만들어 보자

아.....이 블락 엔진을 C++로 포팅해서 Ogre에서 쓸 수 있게 해볼까?
---------------------------
커맨드스케이프를 클릭할 수 있는 버젼으로 만들어서(그래픽은 없어도) 클릭질로 대신할 수 있게 하자.
랜덤한 요소를 넣어서 매번 플레이할 수 있게.
주로 캐릭터의 속성이나 적들의 속성이 바뀌고 그걸 기반으로 키우는 방법이 달라지도록 한다.
마치 매직 더 개더링의 카드세트가 바뀌듯 바뀌게 한다.

팀플레이도 되게 한다. 웹앱으로 하자.
보스몹은 플레이어의 수만큼 강해지게 해서 다른 몹은 혼자 잡아도 되지만 중간보스나 보스몹은 같이 잡게 한다.
--------------------
3가지 요소
신디사이져의 3가지 요소인
음, 모양, 섭하모닉을 잘 구현해서 신디사이져를 만들어서 싸게 판다.

섭하모닉은 1700Hz대의 주파수이며
음은 주로 700대의 주파수
모양은 주고 200대의 주파수이다. 이 3박자가 잘 맞춰져서 변화하면서 변화무쌍한 소리를 낸다.

한 악기가 이렇다 하는 것이고, 3가지 주파수를 주 음역대로 하는 악기도 있지만 역시 섭하모닉은 그렇게 높지 않다.
예를들어 1700번대의 주파수를 주 음역대로 하는 악기는 한 3000대의 섭하모닉을 가질 듯 하다.


걍 C4, C1, C7을 시작음으로 이용해서 비슷한 화음으로 음악을 만들었더니 꽤 비슷한 효과가 났다. 내가 만든 어메이징 그레이스는 결국 이것을 나타내며 이러한 소리를 내는 것이 최종 목적이 아닐까 한다. 그 아래에서 나는 소리가 중요한 것이 아닌 듯.
------------------
3D처럼 사운드 렌더러를 만든다. 신디사이져가 결국 그런 역할인가?
신디사이져는 알고리즘으로 만들어내는 프랙탈이다.
3D도 그런 그래픽이 있다.
그러므로 OpenGL과 같은 삼각형으로 만들어내는 것처럼 그러한 사운드 렌더러를 만든다.
Audacity는 포토샵이다.
내가 만들 것은 사운드로 된 블렌더 같은 프로그램이다. 어떻게 될지는 모르겠지만 하나님이 원하시면 만들어지고 그렇지 않다면 만들어지지 않는다.

폰트에 힌팅이 있다. 사운드에도 힌팅이 있다. 주파수가 도레미파에 맞춰지기 보다는 특정 형태에 맞춰서 그 주파수가 정확하게 들어맞는 그런 형식일 것이다.
물론 전체적인 형체는 도레미파 주파수에 맞는다. 부가 주파수가 그렇다는 것이다.

볼륨이 미치는 영향은 무엇인가? 현재 생각할 수 있는 것은, 볼륨이 바로 주파수를 만든다는 것이다. 볼륨의 차이가 주파수를 만든다.
--------------------------
사운드 렌더러이긴 한데. 기본적으로 주파수를 생성하고 주파수를 조합하고 주파수의 나열을 만들어 소리를 만드는 툴을 만든다.
포토샵에 더 가깝겠는데?
하지만 굳이 3D렌더러처럼 한다면 어떻게 할까?
기본적으로 포토샵같은 도트 에디팅을 지원하면서도
주파수의 조합으로 뭔가를 만들 수 있는
그리고 주파수간의 안티알리아싱 알고리즘을 만들고 뭐 그러는?(바로 이으면 지직거리니)
ADSR같은 개념을 더 확장시키면 거시적 기반의 뭔가를 만들 수 있다.
주파수ㅡ 조합과 ADSR같은 개념의 확장을 지원하는 사운드 렌더러.
보통 사람들은 이걸로 신디사이져를 만들지만 나는 이 신디사이져를 만드는 이론으로 사운드를 쉽게 만들어낼 수 있는 툴을 만든다.
릴리즈가 될 때 까지 클로즈드 소스로 만든다. 팔다가 나중에 소스를 릴리즈? 배끼기도 쉬울텐데 걍 오픈소스.
Bfxr처럼 비슷한 이론으로 랜덤한 사운드를 만들게도 한다.
아 그게 바로 신스메이커구나? (...) 신스메이커가 페인트 프로그램이라면 나는 포토샵
신스메이커가 90년대의 3D라면 나는 2000년대의 3D
--------------------------
어택 부분의 "코드" 또는 "화음"이 다르고 디케이의 화음이 다르고 서스테인의 화음이 다르고 릴리즈의 화음이 다른 것.
음악의 악기의 소리는 결국 화음이다. 내가 만든 어메이징 그레이스는 ADSR의 모든 화음이 똑같았다. 음이 같았다.
그러나 앞으로는 ADSR또는 더 세분화하여 각 음이 달라지게 한다.
음이 달라진다고 해서 아무 음이나 넣는게 아니라 올바른 느낌을 주는 화음을 고르고, 결국 음 하나가 멜로디가 되는 것이다.
---------------
게임을 만드는데 프로그래밍을 하는 게임을 만든다.
프로그래밍을 해서 게임을 만드는 것이 목적이다.
처음에는 간단한 코드를 짜다가 점점 제공하는 라이브러리를 자신이 짜도록 한다.
풀 코스로 해서 이 코스를 마치면 그 게임을 만드는 것이 가능하고, 보너스로 그 게임을 만드는 툴 자체를 만드는 부분을 엑스트라로 엔딩 이후 플레이할 수 있다.
"""
