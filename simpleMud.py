# -*- coding: utf-8 -*-
#
import os
os.environ['SDL_VIDEO_CENTERED'] = '1'
SW,SH = 800,600
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

MAIN = 0
INV = 1
CHAR = 2
SHOP = 3
FIGHT = 4


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
class Floor:
    ORE = 1
    HERB = 2
    def __init__(self):
        self.open = False
        self.oreOrHerb = [1 for i in range(4)]
        for i in range(4):
            self.oreOrHerb[i] = random.randint(1,2)
        self.monster = True
        self.quality = 0
        self.gatherCounter = 0

class Skill(object):
    def __init__(self, ident, name, **skillDef):
        self.ident = ident
        self.name = name
        self.skillDef = skillDef
        self.useCount = 0
        self.level = 1
        self.nextLevel = 3

    def GetName(self):
        return self.name
    def GetUseCount(self, level):
        return int(level**1.5)*3
    def Use(self, target):
        self.useCount += 1
        if self.useCount >= self.nextLevel:
            self.level+=1
            self.nextLevel += self.GetUseCount(level)

class Game:
    def __init__(self):
        self.gold = 0
        self.hp = 10
        self.mp = 10
        self.str = 10
        self.dex = 10
        self.con = 10
        self.int = 10
        self.exp = 0
        self.level = 1
        self.nextExp = self.GetExp(self.level)

        self.TabMode = 0
        self.inventory = []
        self.weapon = None
        self.shield = None
        self.upperT = None
        self.lowerT = None
        self.head = None
        self.gloves = None
        self.boots = None
        self.neck = None
        self.ring1 = None
        self.ring2 = None
        self.ring3 = None
        self.ring4 = None

        self.curMob = None

        self.placeChanged = True
        self.hammerSkills = [Skill('swing','Swing'), Skill('beating', "Beating"), Skill('homerun', "Home Run Swing"), Skill("smite", "Holy Smiting Swing")]
        self.spearSkills = [Skill('pierce','Pierce'), Skill('rapid', "Rapid Pierce"), Skill('penetrate', "Penetrate"), Skill("lightning", "Lightning Shooting Pierce")]
        self.swordSkills = [Skill('slash','Slash'), Skill('multislash', "Multi Slash"), Skill('cut', "Cut In Halves"), Skill("fire", "Burning Fiery Slash")]
        self.handSkills = [Skill('punch','Punch'), Skill('doublepunch', "Double Punch"), Skill('superpunch', "Super Punch"), Skill("ice", "Ice Cold Punch")]

    def GetSkillName(self, idx):
        if self.weapon:
            if self.weapon.itemDef["class"] == "Hammer":
                return self.hammerSkills[idx].GetName()
            if self.weapon.itemDef["class"] == "Sword":
                return self.swordSkills[idx].GetName()
            if self.weapon.itemDef["class"] == "Spear":
                return self.spearSkills[idx].GetName()
        else:
            return self.handSkills[idx].GetName()
    def GetExp(self, level):
        return (level**1.5)*50
    def GetHP(self):
        return 50
    def GetMaxHP(self):
        return 50
    def GetMP(self):
        return 50
    def GetMaxMP(self):
        return 50
    def GetSTR(self):
        return 50
    def GetDEX(self):
        return 50
    def GetCON(self):
        return 50
    def GetINT(self):
        return 50
    def GetLevel(self):
        return self.level
    def GetCurExp(self):
        return self.exp
    def GetNextExp(self):
        return self.nextExp

    def Fight(self):
        if self.monsterLvl >= 12:
            return
        self.gold -= (self.monsterLvl**1.8) * 500
        hp = self.hp
        atk = self.atk
        dfn = self.dfn
        mhp = self.GetMHP()
        matk = self.GetMATK()
        mdfn = self.GetMDFN()
        exp = self.GetMDFN()

        while (hp >= 0 and mhp >= 0):
            mhp -= atk * float(mdfn)/(mdfn**1.2)
            hp -= matk * float(dfn)/(dfn**1.2)
        if mhp <= 0:
            self.GetExp(exp)
            self.floors[self.monsterLvl].monster = False
            try:
                self.floors[self.monsterLvl+1].open = True
            except:
                pass
            self.monsterLvl += 1
        else:
            self.GetExp(exp*(float(mhp)/float(self.GetMHP())))


    def EarnExp(self, exp):
        self.exp += exp
        if self.exp >= self.nextExp:
            self.level += 1
            self.nextExp += self.GetExp(self.level)
            self.str += 3
            self.dex += 3
            self.con += 3
            self.int += 3


def InRect(x,y,w,h, x2, y2):
    if x <= x2 < x+w and y <= y2 < y+h:
        return True
    else:
        return False

def OnMouseDown(evt, g):
    y = 0
    if evt.button == LMB:
        for i in range(15):
            if InRect(0,0+y, 160, 40, evt.pos[0], evt.pos[1]):
                if i == 0: # shop
                    pass
                    #g.gold += 1
                if i == 1: # work
                    pass
                if i == 2: # training
                    g.GetExp(g.GetWinEXP()/10.0)
                if i >= 3: # grounds, 여기부터만 의미가 있도록 하자. 나머지는 클릭해도 소용없고 자원을 계속 자동으로 소모하면서 포션과 무기를 만든다.
                    # 트레이닝은 다른 버튼을 따로 만들까? Click! 이라고 써두자 트레이닝에다가.
                    # 여기는 fight monster 전용
                    if i-3 == g.monsterLvl:
                        #g.Fight()
                        break
            y += 40

class TextBox(object):
    def __init__(self, font, fontH, x, y, w, h):
        self.font = font
        self.fontH = fontH + 4
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.texts = []
        self.dragStart = None
        self.curPos = None
        self.scrollPos = 0
        self.scrollPosScr = 0.0

    def OnMouseDown(self,evt):
        if evt.button == LMB and InRect(self.x+self.w-32, self.y, 32, 32,evt.pos[0], evt.pos[1]):
            self.scrollPos -= (self.h/self.fontH)
        elif evt.button == LMB and InRect(self.x+self.w-32, self.y+self.h-32, 32, 32, evt.pos[0], evt.pos[1]):
            self.scrollPos += (self.h/self.fontH)
        if self.scrollPos < 0:
            self.scrollPos = 0
        if self.scrollPos > len(self.texts) - (self.h/self.fontH):
            self.scrollPos = len(self.texts) - (self.h/self.fontH)
    def Clear(self):
        self.texts = []
    def AddText(self, txt, color):
        self.texts += [(txt, color)]
        self.scrollPos = len(self.texts) - (self.h/self.fontH)

    def DrawScrollBar(self, scr):
        scr.fill((80,80,80), pygame.Rect(self.x+self.w-32,self.y,32,self.h))
        scr.fill((160,160,160), pygame.Rect(self.x+self.w-32,self.y+self.h-32,32,32))
        scr.fill((160,160,160), pygame.Rect(self.x+self.w-32,self.y,32,32))
        if len(self.texts) > self.h/self.fontH and self.scrollPos!=len(self.texts)-(self.h/self.fontH):
            scr.fill((160,160,160), pygame.Rect(self.x,self.y+self.h,self.w,4))
            
    def Render(self, scr):
        ii = 0
        scr.fill((20,20,20), pygame.Rect(self.x,self.y,self.w,self.h))
        if len(self.texts) > self.h/self.fontH:
            for txtc in self.texts[self.scrollPos:self.scrollPos+(self.h/self.fontH)]:
                txt, color = txtc
                scr.blit(*Text.GetSurf(self.font, txt, (self.x, self.y + ii), color))
                ii += self.fontH
        else:
            for txtc in self.texts:
                txt, color = txtc
                scr.blit(*Text.GetSurf(self.font, txt, (self.x, self.y + ii), color))
                ii += self.fontH
        self.DrawScrollBar(scr)

def Sell(g):
    numCustomers = random.randint(0,4)
    for i in range(numCustomers):
        sellPot = random.randint(1,100)
        sellEqs = random.randint(1,100)
        if sellPot > g.potions:
            sellPot = g.potions
        g.potions -= sellPot
        if sellEqs > g.eqs:
            sellEqs = g.eqs
        g.eqs -= sellEqs

        for j in range(sellPot):
            g.gold += random.randint(20,80)
        for j in range(sellEqs):
            g.gold += random.randint(20,80)
    g.customers += numCustomers

class NPCMOB:
    def __init__(self, npcID, name, hostile = False):
        self.npcID = npcID
        self.name = name
        self.npcDef = {}
        self.items = []
        self.hostile = hostile
        self.txts = []
        self.txtIdx = 0
        def a():
            pass
        self.doneFunc = a
    def GetHP(self):
        return 50
    def GetMaxHP(self):
        return 50
    def GetMP(self):
        return 50
    def GetMaxMP(self):
        return 50

class Map(object):
    def __init__(self):
        self.places = {}
        self.curPlace = ''
        self.font = pygame.font.Font("./fonts/FanwoodText.ttf", 16)
        self.txtBox = None
        self.fightBox = TextBox(self.font, 16, SW/4, 80, SW/2, SH-160)

    def OnFightClick(self, evt, g, font):
        pass
    def OnInvClick(self, evt, g, font):
        y = 52
        name, rect = Text.GetSurf(font, "Weapon:", (5, y), (240,240,240))
        item = g.weapon
        offset = 10
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.weapon]
                    g.weapon = None
                return

        name, rect = Text.GetSurf(font, "Shield:", (400, y), (240,240,240))
        item = g.shield
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.shield]
                    g.shield = None
                return

        y += 30
        name, rect = Text.GetSurf(font, "Upper Torso:", (5, y), (240,240,240))
        item = g.upperT
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.upperT]
                    g.upperT = None
                return

        name, rect = Text.GetSurf(font, "Lower Torso:", (400, y), (240,240,240))
        item = g.lowerT
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.lowerT]
                    g.lowerT = None
                return

        y += 30
        name, rect = Text.GetSurf(font, "Head:", (5, y), (240,240,240))
        item = g.head
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.head]
                    g.head = None
                return

        name, rect = Text.GetSurf(font, "Gloves:", (400, y), (240,240,240))
        item = g.gloves
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.gloves]
                    g.gloves = None
                return

        y += 30
        name, rect = Text.GetSurf(font, "Boots:", (5, y), (240,240,240))
        item = g.boots
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.boots]
                    g.boots = None
                return

        name, rect = Text.GetSurf(font, "Necklaces:", (400, y), (240,240,240))
        item = g.neck
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.neck]
                    g.neck = None
                return

        y += 30
        name, rect = Text.GetSurf(font, "Ring:", (5, y), (240,240,240))
        item = g.ring1
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.ring1]
                    g.ring1 = None
                return

        name, rect = Text.GetSurf(font, "Ring:", (400, y), (240,240,240))
        item = g.ring2
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.ring2]
                    g.ring2 = None

                return

        y += 30
        name, rect = Text.GetSurf(font, "Ring:", (5, y), (240,240,240))
        item = g.ring3
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.ring3]
                    g.ring3 = None
                return

        name, rect = Text.GetSurf(font, "Ring:", (400, y), (240,240,240))
        item = g.ring4
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if len(g.inventory) < 39:
                    g.inventory += [g.ring4]
                    g.ring4 = None
                return


        xs = [5, 265, 525]
        y=300

        xIdx = 0
        for item in g.inventory[:]:
            name, rect = Text.GetSurf(font, item.itemDef['name'], (xs[xIdx], y), (240,240,240))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                if item.itemDef['type'] == 'Weapon':
                    backup = g.weapon
                    g.weapon = item
                    g.inventory.remove(item)
                    if backup:
                        g.inventory += [backup]
                if item.itemDef['type'] == 'Shield':
                    backup = g.shield
                    g.shield = item
                    g.inventory.remove(item)
                    if backup:
                        g.inventory += [backup]
                if item.itemDef['type'] == 'UpperTorso':
                    backup = g.upperT
                    g.upperT = item
                    g.inventory.remove(item)
                    if backup:
                        g.inventory += [backup]
                if item.itemDef['type'] == 'LowerTorso':
                    backup = g.lowerT
                    g.lowerT = item
                    g.inventory.remove(item)
                    if backup:
                        g.inventory += [backup]
                if item.itemDef['type'] == 'Head':
                    backup = g.head
                    g.head = item
                    g.inventory.remove(item)
                    if backup:
                        g.inventory += [backup]
                if item.itemDef['type'] == 'Gloves':
                    backup = g.gloves
                    g.gloves = item
                    g.inventory.remove(item)
                    if backup:
                        g.inventory += [backup]
                if item.itemDef['type'] == 'Boots':
                    backup = g.boots
                    g.boots = item
                    g.inventory.remove(item)
                    if backup:
                        g.inventory += [backup]
                if item.itemDef['type'] == 'Necklace':
                    backup = g.neck
                    g.neck = item
                    g.inventory.remove(item)
                    if backup:
                        g.inventory += [backup]
                if item.itemDef['type'] == 'Ring':
                    if not g.ring1:
                        g.ring1 = item
                        g.inventory.remove(item)
                    elif not g.ring2:
                        g.ring2 = item
                        g.inventory.remove(item)
                    elif not g.ring3:
                        g.ring3 = item
                        g.inventory.remove(item)
                    elif not g.ring4:
                        g.ring4 = item
                        g.inventory.remove(item)
                    else:
                        backup = g.ring4
                        g.ring4 = item
                        g.inventory.remove(item)
                        if backup:
                            g.inventory += [backup]
                return

            xIdx += 1
            if xIdx >= 3:
                xIdx = 0
                y += 22

    def OnCharClick(self, evt, g):
        pass
    def OnShopClick(self, evt, g):
        pass
    def OnClick(self, evt, g):
        x = 5
        y = 300
        for item in self.places[self.curPlace].items[:]:
            name, rect = Text.GetSurf(self.font, item.itemDef['name'], (x, y), (240,240,240))
            if rect[0] + rect[2] > SW:
                x = 5
                y += 30
            rect = x,y,rect[2],rect[3]
            if evt.button == LMB and InRect(*(rect+evt.pos)):
                if len(g.inventory) < 39:
                    g.inventory += [item]
                    self.places[self.curPlace].items.remove(item)
                break

            x += rect[2]+10

        x = 5
        y = 400
        for npc in self.places[self.curPlace].npcs:
            if npc.hostile:
                name, rect = Text.GetSurf(self.font, npc.name, (x, y), (240,240,240))
                if rect[0] + rect[2] > SW:
                    x = 5
                    y += 30
                rect = x,y,rect[2],rect[3]
                if evt.button == LMB and InRect(*(rect+evt.pos)) and self.txtBox.scrollPos == len(self.txtBox.texts) - (self.txtBox.h/self.txtBox.fontH):
                    g.TabMode = FIGHT
                    g.curMob = npc
                    break
                x += rect[2]+10
            else:
                name, rect = Text.GetSurf(self.font, npc.name, (x, y), (240,240,240))
                if rect[0] + rect[2] > SW:
                    x = 5
                    y += 30
                rect = x,y,rect[2],rect[3]
                if evt.button == LMB and InRect(*(rect+evt.pos)) and self.txtBox.scrollPos == len(self.txtBox.texts) - (self.txtBox.h/self.txtBox.fontH):
                    pos = len(self.txtBox.texts)
                    for txt in npc.txts[npc.txtIdx].split('\n'):
                        self.txtBox.AddText(txt, (120,120,80))
                    self.txtBox.AddText('', (120,120,80))
                    self.txtBox.scrollPos = pos
                    npc.doneFunc()
                    break
                x += rect[2]+10



        x = 5
        y = 500
        self.places[self.curPlace].links.sort()
        for link in self.places[self.curPlace].links:
            name, rect = Text.GetSurf(self.font, self.places[link].name, (x, y), (240,240,240))
            if rect[0] + rect[2] > SW:
                x = 5
                y += 30
            rect = x,y,rect[2],rect[3]
            if evt.button == LMB and InRect(*(rect+evt.pos)):
                self.curPlace = link
                g.placeChanged = True
                break
            x += rect[2]+10


    def Render(self, font, screen):
        x = 5
        y = 300
        name, rect = Text.GetSurf(font, 'Items: ', (5, 270), (240,240,240))
        screen.blit(name, rect)
        for item in self.places[self.curPlace].items:
            name, rect = Text.GetSurf(font, item.itemDef['name'], (x, y), (240,240,240))
            if rect[0] + rect[2] > SW:
                x = 5
                y += 30
            rect = x,y,rect[2],rect[3]
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)
            x += rect[2]+10

        x = 5
        y = 400
        name, rect = Text.GetSurf(font, 'NPCs/Enemies: ', (5, 370), (240,240,240))
        screen.blit(name, rect)
        for npc in self.places[self.curPlace].npcs:
            if npc.hostile:
                name, rect = Text.GetSurf(font, npc.name, (x, y), (240,120,120))
                if rect[0] + rect[2] > SW:
                    x = 5
                    y += 30
                rect = x,y,rect[2],rect[3]
                screen.fill((40,40,40), rect)
                screen.blit(name, rect)
                x += rect[2]+10
            else:
                name, rect = Text.GetSurf(font, npc.name, (x, y), (240,240,240))
                if rect[0] + rect[2] > SW:
                    x = 5
                    y += 30
                rect = x,y,rect[2],rect[3]
                screen.fill((40,40,40), rect)
                screen.blit(name, rect)
                x += rect[2]+10

        x = 5
        y = 500
        name, rect = Text.GetSurf(font, 'Places you could go: ', (5, 470), (240,240,240))
        screen.blit(name, rect)
        self.places[self.curPlace].links.sort()
        for link in self.places[self.curPlace].links:
            name, rect = Text.GetSurf(font, self.places[link].name, (x, y), (240,240,240))
            if rect[0] + rect[2] > SW:
                x = 5
                y += 30
            rect = x,y,rect[2],rect[3]
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)
            x += rect[2]+10

        for mob in self.places[self.curPlace].mobs:
            name, rect = Text.GetSurf(font, mob.name, (x, y), (240,240,240))
            if rect[0] + rect[2] > SW:
                x = 5
                y += 30
            rect = x,y,rect[2],rect[3]
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)
            x += rect[2]+10


    def RenderFight(self, font, screen, g, map):
        screen.fill((50,50,50), (0,0,SW/4,SH))
        screen.fill((50,50,50), (SW-SW/4,0,SW/4,SH))
        screen.fill((40,40,40), (SW/4,0,SW/2,80))
        screen.fill((40,40,40), (SW/4,SH-80,SW/2,80))

        y = SH-80+5
        name, rect = Text.GetSurf(font, "You:", (SW/4+10, y), (240,240,240))
        screen.blit(name, rect)

        y += 22
        name, rect = Text.GetSurf(font, "HP: %d/%d" % (g.GetHP(), g.GetMaxHP()), (SW/4+10, y), (240,240,240))
        screen.blit(name, rect)

        y += 22
        name, rect = Text.GetSurf(font, "MP: %d/%d" % (g.GetMP(), g.GetMaxMP()), (SW/4+10, y), (240,240,240))
        screen.blit(name, rect)

        y = 5
        name, rect = Text.GetSurf(font, "%s:" % g.curMob.name, (SW/4+10, y), (240,80,80))
        screen.blit(name, rect)

        y += 22
        name, rect = Text.GetSurf(font, "HP: %d/%d" % (g.curMob.GetHP(), g.curMob.GetMaxHP()), (SW/4+10, y), (240,80,80))
        screen.blit(name, rect)

        y += 22
        name, rect = Text.GetSurf(font, "MP: %d/%d" % (g.curMob.GetMP(), g.curMob.GetMaxMP()), (SW/4+10, y), (240,80,80))
        screen.blit(name, rect)

        self.fightBox.Render(screen)


        y = 5
        name, rect = Text.GetSurf(font, "Skills:", (5, y), (240,240,240))
        screen.blit(name, rect)
        y += 30
        name, rect = Text.GetSurf(font, "%s" % g.GetSkillName(0), (5, y), (240,240,240))
        screen.fill((30,30,30), rect)
        screen.blit(name, rect)

        y += 30
        name, rect = Text.GetSurf(font, "%s" % g.GetSkillName(1), (5, y), (240,240,240))
        screen.fill((30,30,30), rect)
        screen.blit(name, rect)

        y += 30
        name, rect = Text.GetSurf(font, "%s" % g.GetSkillName(2), (5, y), (240,240,240))
        screen.fill((30,30,30), rect)
        screen.blit(name, rect)

        y += 30
        name, rect = Text.GetSurf(font, "%s" % g.GetSkillName(3), (5, y), (240,240,240))
        screen.fill((30,30,30), rect)
        screen.blit(name, rect)

        y += 40
        name, rect = Text.GetSurf(font, "Magic:", (5, y), (240,240,240))
        screen.blit(name, rect)

        """
        y += 30
        name, rect = Text.GetSurf(font, "%s" % g.GetMagic(0), (5, y), (240,240,240))
        screen.fill((30,30,30), rect)
        screen.blit(name, rect)
        y += 30
        name, rect = Text.GetSurf(font, "%s" % g.GetMagic(1), (5, y), (240,240,240))
        screen.fill((30,30,30), rect)
        screen.blit(name, rect)
        y += 30
        name, rect = Text.GetSurf(font, "%s" % g.GetMagic(2), (5, y), (240,240,240))
        screen.fill((30,30,30), rect)
        screen.blit(name, rect)
        y += 30
        name, rect = Text.GetSurf(font, "%s" % g.GetMagic(3), (5, y), (240,240,240))
        screen.fill((30,30,30), rect)
        screen.blit(name, rect)
        """


        y += 40
        name, rect = Text.GetSurf(font, "Runaway", (5, y), (240,240,240))
        screen.fill((20,20,20), rect)
        screen.blit(name, rect)

        y = 5
        name, rect = Text.GetSurf(font, "Items:", (5+SW*3/4, y), (240,240,240))
        screen.blit(name, rect)


        screen.fill((120,120,120), (SW-24,0,24,24))
        screen.fill((120,120,120), (SW-24,SH-24,24,24))



    def RenderInv(self, font, screen, g):
        y = 22

        screen.fill((50,50,50), (0,22,SW,SH-22))

        name, rect = Text.GetSurf(font, "[Equipments]", (5, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)


        y = 52
        name, rect = Text.GetSurf(font, "Weapon:", (5, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.weapon
        offset = 10
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        name, rect = Text.GetSurf(font, "Shield:", (400, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.shield
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        y += 30
        name, rect = Text.GetSurf(font, "Upper Torso:", (5, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.upperT
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        name, rect = Text.GetSurf(font, "Lower Torso:", (400, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.lowerT
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        y += 30
        name, rect = Text.GetSurf(font, "Head:", (5, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.head
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        name, rect = Text.GetSurf(font, "Gloves:", (400, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.gloves
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        y += 30
        name, rect = Text.GetSurf(font, "Boots:", (5, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.boots
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        name, rect = Text.GetSurf(font, "Necklaces:", (400, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.neck
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        y += 30
        name, rect = Text.GetSurf(font, "Ring:", (5, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.ring1
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        name, rect = Text.GetSurf(font, "Ring:", (400, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.ring2
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        y += 30
        name, rect = Text.GetSurf(font, "Ring:", (5, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.ring3
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

        name, rect = Text.GetSurf(font, "Ring:", (400, y), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)
        item = g.ring4
        if item:
            newX = rect[0]+rect[2] + offset
            name, rect = Text.GetSurf(font, item.itemDef['name'], (newX, y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)


        xs = [5, 265, 525]
        y=300
        name, rect = Text.GetSurf(font, "[Inventory]", (5, y-30), (240,240,240))
        screen.fill((40,40,40), rect)
        screen.blit(name, rect)

        xIdx = 0
        for item in g.inventory:
            name, rect = Text.GetSurf(font, item.itemDef['name'], (xs[xIdx], y), (240,240,240))
            screen.fill((40,40,40), rect)
            screen.blit(name, rect)

            xIdx += 1
            if xIdx >= 3:
                xIdx = 0
                y += 22

    def RenderChar(self, font, screen, g):
        screen.fill((40,40,40), (0,22,SW,SH-22))
        y = 22 + 5
        name, rect = Text.GetSurf(font, "Level: %d" % (g.GetLevel()), (5, y), (240,240,240))
        screen.blit(name, rect)
        y += 30

        name, rect = Text.GetSurf(font, "Exp: %d/%d" % (g.GetCurExp(), g.GetNextExp()), (5, y), (240,240,240))
        screen.blit(name, rect)


        y += 30
        name, rect = Text.GetSurf(font, "HP: %d/%d" % (g.GetHP(), g.GetMaxHP()), (5, y), (240,240,240))
        screen.blit(name, rect)
        name, rect = Text.GetSurf(font, "MP: %d/%d" % (g.GetMP(), g.GetMaxMP()), (5+400, y), (240,240,240))
        screen.blit(name, rect)
        y += 30

        name, rect = Text.GetSurf(font, "STR: %d" % (g.GetSTR()), (5, y), (240,240,240))
        screen.blit(name, rect)
        name, rect = Text.GetSurf(font, "DEX: %d" % (g.GetDEX()), (5+400, y), (240,240,240))
        screen.blit(name, rect)
        y += 30

        name, rect = Text.GetSurf(font, "CON: %d" % (g.GetCON()), (5, y), (240,240,240))
        screen.blit(name, rect)
        name, rect = Text.GetSurf(font, "INT: %d" % (g.GetINT()), (5+400, y), (240,240,240))
        screen.blit(name, rect)
        y += 30

        skills = [g.handSkills, g.swordSkills, g.spearSkills, g.hammerSkills]
        for j in range(4):
            for i in range(4):
                skill = skills[j][i]
                name, rect = Text.GetSurf(font, "%s - Level: %d (%d/%d)  -|-  Damage: %d  -|-  MP Cost: %d" % \
                        (skill.name, skill.level, skill.useCount, skill.nextLevel, 50, 5), (5, y), (240,240,240))
                screen.blit(name, rect)
                y += 20
            y += 10



        pass
    def RenderShop(self, font, screen, g):
        pass


    def GetCurPlace(self):
        return self.places[self.curPlace]



class Place(object):
    def __init__(self, placeID, name, desc):
        self.placeID = placeID
        self.name = name
        self.desc = desc
        self.links = []
        self.items = []
        self.mobs = []
        self.npcs = []

class ItemManager(object):
    def __init__(self):
        self.items = []

    def Spawn(self, itemID, itemDef):
        item = Item(itemID, itemDef)
        self.items += [item]
        return item

ItemManager = ItemManager()

class Item(object):
    def __init__(self, itemID, itemDef):
        self.itemID = itemID
        self.itemDef = itemDef
class ItemDef(object):
    def __init__(self, itemID, itemDef):
        self.itemID = itemID
        self.itemDef = itemDef
    def SpawnItem(self):
        return ItemManager.Spawn(self.itemID, self.itemDef)
class TopButtons(object):
    def __init__(self):
        self.buttons = []

    def AddButton(self, txt, func):
        self.buttons += [(txt, func)]
    def OnMouse(self, evt, font, g):
        x=0
        y=0
        for button in self.buttons:
            t,f = button
            name, rect = Text.GetSurf(font, t, (x, y), color=(230,200,128))
            if InRect(rect[0], rect[1], rect[2], rect[3], evt.pos[0], evt.pos[1]):
                f(g)
                break
            x += rect[2]+5


    def Render(self, screen, font):
        x=0
        y=0
        for button in self.buttons:
            t,f = button
            name, rect = Text.GetSurf(font, t, (x, y), color=(230,200,128))
            screen.fill((50,50,50), rect)
            screen.blit(name, rect)
            x += rect[2]+5

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Jin\'s RPG')
    #screen.blit(background, (0, 0))
    done = False
    imgs = {
            'rock': pygame.image.load("img/rock.png"),
            'crock': pygame.image.load("img/clearedrock.png"),
            'shop': pygame.image.load("img/shop.png"),
            'workshop': pygame.image.load("img/workshop.png"),
            'training': pygame.image.load("img/training.png"),
            'herb': pygame.image.load("img/herb.png"),
            'ore': pygame.image.load("img/ore.png"),
            }

    font = pygame.font.Font("./fonts/FanwoodText.ttf", 16)
    font2 = pygame.font.Font("./fonts/FanwoodText.ttf", 14)
    g = Game()
    startTick = pygame.time.get_ticks()
    endTick = pygame.time.get_ticks()
    gatherCountTick = 0
    craftCountTick = 0
    fightCountTick = 0

    g.TabMode = MAIN
    def ChangeToMain(g):
        g.TabMode = MAIN
    def ChangeToInventory(g):
        g.TabMode = INV
    def ChangeToCharacterSheet(g):
        g.TabMode = CHAR
    def ChangeToShop(g):
        g.TabMode = SHOP
    topButtons = TopButtons()
    topButtons.AddButton("Main", ChangeToMain)
    topButtons.AddButton("Inventory", ChangeToInventory)
    topButtons.AddButton("Character Sheet", ChangeToCharacterSheet)
    topButtons.AddButton("Your Magical Shop Express", ChangeToShop)


    items = [ItemDef('potion', {'name': 'Potion', 'type': 'Potion'}),
            ItemDef('warhammer', {'name': 'War Hammer', 'type': 'Weapon', 'class': 'Hammer'}),
            ItemDef('sword', {'name': 'Sword', 'type': 'Weapon', 'class': 'Sword'}),
            ItemDef('spear', {'name': 'Spear', 'type': 'Weapon', 'class': 'Spear'}),
            ItemDef('leather_jacket', {'name': 'Leather Jacket', 'type': 'UpperTorso'}),
            ItemDef('leather_pants', {'name': 'Leather Pants', 'type':'LowerTorso'}),
            ItemDef('ring1', {'name': 'Gold Ring', 'type':'Ring'})]

    map = Map()
    place = Place('StartingPoint', 'Home', '''It is your house.
Very small, 1 bedroom, 1 bathroom, rent price: 300G a month
Light is coming from the window, it is a nice warm feeling.
From the news on your MagicElectronics TV, there was an explosion at the mana station not very far from your house.
You remember loud noise in the earlier morning you ignored while you slept through.''')
    map.places[place.placeID] = place
    map.places[place.placeID].items = [item.SpawnItem() for item in items]
    #map.places[place.placeID].items += [items[-1].SpawnItem()]*1
    map.curPlace = place.placeID

    place = Place('ManaStation', 'Mana Station', '''Mana Station is where you can buy up some manas or mana potions for journey.
Because of the explosion, it is closed down for now.''')
    map.places[place.placeID] = place

    jake = NPCMOB('jake', 'Jake')
    jake.txts += ["""\
Jake: Aww man I'm out of mana and this happened!
You: What's up?
Jake: I don't know but something about terrorism?
You: It won't blow up by itself, I mean manas are the most stable energy source on earth!
Jake: Yeah but if someone could used Antimana it could blow up like this...
You: Antimana? Who would use that expensive material to just blow up some stupid mana station?
Jake: That's why they are in such a fuss...
You: If you had one drop of antimana you could just create massive amount of gold with that why the explosion?
Jake: Yeah I'm just here to buy up some mana and look at this....
You: Did anybody die?
Jake: Yeah, wierd on that, nobody got hurt but building disappeared and every bit of mana underground dried up.
You: Huh, wierd.. was nobody in the building?
Jake: Yes there was, but only the building disappeared.
You: I suspect someone stole the building....
Jake: Heh, that would be fun, I heard a rumor that some wierd people are collecting massive amount of mana
      to overtake the whole earth.
You: Aww no, that again?
Jake: Yeah, as if it is possible, ha ha ha.
You: Hahaha. But why the building?
Jake: Didn't know? This particular station was entirely made out of pure mana.
You: Huh, didn't know that. Why don't you take some of my mana.
Jake: Thanks, buddy."""]
    def RemoveFromStation():
        map.places['ManaStation'].npcs.remove(jake)
    jake.doneFunc = RemoveFromStation

    cop = NPCMOB('cop', 'A Magical Crime Division Officer')
    place.npcs = [jake]

    place = Place('UnprotectedWilderness', 'Unprotected Wilderness', '''It is a wilderness where monsters appear at day and night.
There are many hunters among these area and also many monsters.
Because of the vastness of the land, people could not protect every area,
so wilderness could have been protected pretty well.''')
    map.places[place.placeID] = place

    mob = NPCMOB('slime', 'Slime')
    mob.hostile = True
    place.npcs = [mob]

    mob = NPCMOB('wildrat', 'Wild Rat')
    mob.hostile = True
    place.npcs += [mob]


    place = Place('UnprotectedWildernessNorth', 'Unprotected Wilderness North', '''Northern Wilderness area.''')
    map.places[place.placeID] = place

    place = Place('MagicSquareSouth', 'Magic Square South', '''Magic Square southern area.''')
    map.places[place.placeID] = place
    npc = NPCMOB('antimagicRogue1', 'An Extremely Suspicious Looking Guy')
    npc.txts += ["""\
You: Hi, there, did you blow up the mana station?
An Extremely Suspicious Looking Guy: ....
And then the guy disappeared into the crowd.
You: Oh, hey, I hit the jackpot, I should follow him!
"""]
    def RemoveFromStation():
        map.places['MagicSquareSouth'].npcs.remove(npc)
    npc.doneFunc = RemoveFromStation
    place.npcs += [npc]

    place = Place('MagicSquareCenter', 'Magic Square Center', '''Magic Square center area. This is where the people are hagning out.''')
    map.places[place.placeID] = place

    place = Place('MagicSquareEast', 'Magic Square East', '''Magic Square eastern area.''')
    map.places[place.placeID] = place

    place = Place('MagicSquareNorth', 'Magic Square North', '''Magic Square northern area.''')
    map.places[place.placeID] = place

    place = Place('MagicalUnionCivicCenter', 'Magical Union Civic Center', '''This is where you get some service from government.''')
    map.places[place.placeID] = place

    map.places['StartingPoint'].links += ['ManaStation', 'UnprotectedWilderness']
    map.places['ManaStation'].links += ['StartingPoint', 'UnprotectedWilderness']
    map.places['UnprotectedWilderness'].links += ['StartingPoint', 'ManaStation', 'UnprotectedWildernessNorth']
    map.places['UnprotectedWildernessNorth'].links += ['MagicSquareSouth', 'UnprotectedWilderness']
    map.places['MagicSquareSouth'].links += ['MagicSquareCenter', 'UnprotectedWildernessNorth']
    map.places['MagicSquareCenter'].links += ['MagicSquareSouth', 'MagicSquareEast', 'MagicSquareNorth']
    map.places['MagicSquareEast'].links += ['MagicSquareCenter']
    map.places['MagicSquareNorth'].links += ['MagicSquareCenter', 'MagicalUnionCivicCenter']
    map.places['MagicalUnionCivicCenter'].links += ['MagicSquareNorth']



    #place1 = map.GetCurPlace()

    txtBox = TextBox(font, 16, 0, 22, SW, 240)
    map.txtBox = txtBox
    while not done:
        gatherCountTick += endTick-startTick
        craftCountTick += endTick-startTick
        fightCountTick += endTick-startTick
        startTick = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == MOUSEBUTTONDOWN:
                if g.TabMode != FIGHT:
                    topButtons.OnMouse(event, font, g)
                #OnMouseDown(event, g)
                if g.TabMode == MAIN:
                    txtBox.OnMouseDown(event)
                    map.OnClick(event, g)
                if g.TabMode == INV:
                    map.OnInvClick(event, g, font)
                if g.TabMode == CHAR:
                    map.OnCharClick(event, g)
                if g.TabMode == SHOP:
                    map.OnShopClick(event, g)
                if g.TabMode == FIGHT:
                    map.OnFightClick(event, g, font)
            elif event.type == MOUSEMOTION:
                pass
            elif event.type == MOUSEBUTTONUP:
                pass

        if g.placeChanged == True:
            g.placeChanged = False
            txtBox.Clear()
            txtBox.AddText(map.GetCurPlace().name, (200,200,200))
            txtBox.AddText('', (200,200,200))
            for txt in map.GetCurPlace().desc.split('\n'):
                txtBox.AddText(txt, (200,200,200))
            txtBox.AddText('', (200,200,200))

            # 아이템이나 인물은 네모 상자에 넣어 따로 렌더링하고 클릭가능한 버튼으로 하고 배경을 좀 진한색으로 한다.
        """

        if fightCountTick >= 800:
            fightCountTick -= 800
            g.Fight()
        if craftCountTick >= 500:
            craftCountTick -= 500
            if g.ore:
                g.eqs += g.ore
                g.ore = 0
            if g.mOre:
                g.eqs += g.mOre*2
                g.mOre = 0
            if g.eOre:
                g.eqs += g.eOre*3
                g.eOre = 0

            if g.herb:
                g.potions += g.herb
                g.herb = 0
            if g.mHerb:
                g.potions += g.mHerb*2
                g.mHerb = 0
            if g.eHerb:
                g.potions += g.eHerb*3
                g.eHerb = 0
            if random.randint(1,2) == 1:
                Sell(g)

        if gatherCountTick >= 100:
            gatherCountTick -= 100
            for j in range(12):
                if g.floors[j].open and not g.floors[j].monster:
                    for i in range(4):
                        if g.floors[j].oreOrHerb[i] == Floor.HERB:
                            if g.floors[j].quality == 1:
                                g.herb += 1
                            if g.floors[j].quality == 2:
                                g.mHerb += 1
                            if g.floors[j].quality == 3:
                                g.eHerb += 1

                        if g.floors[j].oreOrHerb[i] == Floor.ORE:
                            if g.floors[j].quality == 1:
                                g.ore += 1
                            if g.floors[j].quality == 2:
                                g.mOre += 1
                            if g.floors[j].quality == 3:
                                g.eOre += 1




        screen.fill((0,0,0))
        screen.blit(imgs['shop'], (0,0,160,40))
        screen.blit(imgs['workshop'], (0,40,160,40))
        screen.blit(imgs['training'], (0,80,160,40))
        i = 40
        color = 200,200,128
        bcolor = 40, 50, 24
        for j in range(12):
            if g.floors[j].open:
                screen.blit(imgs['crock'], (0,80+i,160,40))
                if not g.floors[j].monster:
                    for k in range(4):
                        if g.floors[j].oreOrHerb[k] == Floor.ORE:
                            screen.blit(imgs['ore'], (4+40*k,4+80+i,32,32))
                        else:
                            screen.blit(imgs['herb'], (4+40*k,4+80+i,32,32))
                else:
                    screen.blit(*Text.GetSurf(font, "Now Fighting", (40, 80+i+2), color=color, border=True, borderColor=bcolor))
                    screen.blit(*Text.GetSurf(font, "  Monsters!", (40, 80+i+20), color=color, border=True, borderColor=bcolor))

            else:
                screen.blit(imgs['rock'], (0,80+i,160,40))
            i += 40
        color = 200,200,128
        bcolor = 170, 170, 170
        i = 0
        screen.blit(*Text.GetSurf(font, "Reach 100000 Gold to Win!", (170, 10+i), color=(230,200,128), border=False, borderColor=bcolor))

        i += 35
        screen.blit(*Text.GetSurf(font, "Gold", (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 18
        screen.blit(*Text.GetSurf(font, ": %d" % g.gold , (180, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "Customers ", (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 18
        screen.blit(*Text.GetSurf(font, ":% d" % g.customers , (180, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "Poor Herb: %d" % g.herb , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "Medium Herb: %d" % g.mHerb , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "Exceptional Herb: %d" % g.eHerb , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25

        i += 10
        screen.blit(*Text.GetSurf(font, "Poor Ore: %d" % g.ore , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "Medium Ore: %d" % g.mOre , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "Exceptional Ore: %d" % g.eOre , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25

        i += 10
        screen.blit(*Text.GetSurf(font, "Potions: %d" % g.potions , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "Equipments: %d" % g.eqs , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25

        i += 10
        screen.blit(*Text.GetSurf(font, "Level: %d" % g.level , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "Exp Point: %d/%d" % (g.exp, g.GetNextExp()) , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "HP: %d" % g.hp , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "Attack: %d" % g.atk , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25
        screen.blit(*Text.GetSurf(font, "Defense: %d" % g.dfn , (170, 10+i), color=color, border=False, borderColor=bcolor))
        i += 25


        color = 200,200,128
        bcolor = 40, 50, 24
        screen.blit(*Text.GetSurf(font, "Click!", (60, 100), color=color, border=True, borderColor=bcolor))
        """
        screen.fill((0,0,0))
        if g.TabMode == MAIN:
            txtBox.Render(screen)
            map.Render(font, screen)
        if g.TabMode == INV:
            map.RenderInv(font, screen, g)
        if g.TabMode == CHAR:
            map.RenderChar(font2, screen, g)
        if g.TabMode == SHOP:
            map.RenderShop(font, screen, g)
        if g.TabMode == FIGHT:
            map.RenderFight(font, screen, g, map)
        if g.TabMode != FIGHT:
            topButtons.Render(screen, font)

        pygame.display.flip()
        endTick = pygame.time.get_ticks()

if __name__ == "__main__":
    main()

"""
걍 단순히 머드게임을 만든다.
울온의 기능을 완전히 넣고 스킬을 올리려면 단순하게 퀘스트를 수행하면 할 수 있도록 한다.
스토리를 넣어볼까?

텍스트박스에 스크롤바를 넣어야 한다.
------------
여기에 떠오르는 아이디어를 적고 그걸 구현한다. 한개씩.

전투화면은 Main에 띄운다. 전투중엔 텍스트박스가 사라지고 Fight메뉴가 뜨게되며
포션류와 같은 사용가능한 아이템이 오른편에 메뉴로 뜨게되고(스크롤가능)
좌편에는 사용가능한 스킬
가운데에는 전투 로그와 가운데 상단에는 주인공의 체력 마력이 뜨게 되며
하단에는 전투중인 몹의 체력 마력이 뜬다. 1:1전투만 가능 포켓몬처럼?
-----------
무기마다 기술이 4개씩 붙어있다. 공격력은 무기에 붙어있지 않고 캐릭터의 공격력 위주로 간다.
대신, 같은 야구방망이라도 여러가지 매직 이펙트가 붙어있다.
야구방망이: Swing, Beating, Home Run Swing, Holy Smiting Swing


각 메뉴를 완성한다
일단 플레이어의 정의를 완성한다.
STR, DEX, INT가 있다.
STR이 올라가면 공격력이 올라가고
DEX가 올라가면 방어가 올라가고
INT가 올라가면 마나가 올라간다.
CON이 올라가면 체력이 올라간다.
이거밖에 없음. 나머지는 걍 레벨이 올라갈 때마다 레벨로만 모디파이어를 얻어서 저절로 강해지거나, 아이템이 점점 강해짐 캐릭터만으론 별로!
----------------
세계는 모두 마나로 이루어져 있는데 안티마나를 이용해 세계의 껍질을 한꺼풀 벗기면 주변의 모든 사물이나 생명체를 구성하는 마나를 모두 흡수 가능. 이걸 이용해 세계를 정복할 힘을 얻으려다가 세계 멸망이 되려는걸 주인공이 막음!

2탄:
    엄청난 양의 안티마나가 발견되어 모두가 그걸 차지하려고 하고, 또 세계가 멸망하려고 할 때 주인공이 걍 물흘러가듯 스토리 따라가다가 그걸 또 막음

3탄:
    안티마나를 만들어내는 고대의 주술이 발견되어 또 모두가 그걸 차지하려고 하고 또 세계가 멸망하려고 할 때 주인공이 당연하다는 듯 막음. 끝.
에필로그
주인공이 안티마나를 이용해 세계의 기아와 전쟁을 종식시킴 끝.!!!!!!!


스토리를 쓰는 방법: 어릴 때 독후감을 쓰라고 하듯이 걍 장소를 정하고 느낀점 또는 묘사를 쓰면 된다. 대화는 쉬운데 느낀점이나 묘사가 꽤 어려울 듯 하다.
어렵게 생각하지 말고 쉽게 하면 된다.

랜덤한 단어를 선택해서 그 단어들에 맞도록 스토리를 짜내면 된다.
------------------
호랑이가 폴짝 폴짝 뛰어다니면서 보석을 모으고 토끼를 잡는 게임.
반짝반짝 빛나는 보석들과 에쁜 숲속 배경이 포인트!
-------------------
무기는 배트, 스피어, 소드이다.
스피어: Pierce, Rapid Pierce, Penetrate, Lightning Pierce
소드: Slash, Multi Slash, Cut In Halves, Fiery Slash
맨손기술도 있음: Punch, Double Punch, Super Punch, Ice Cold Punch
싸워서 지더라도 자동으로 병원으로 호송되며 스킬 경험치나 싸워서 얻은 경험치는 남는다.
병원 호송 패널티는 돈의 10% 감소.
마법:
    힐, 적 MaxHP서서히깍기, MaxMP서서히깎기, 몇턴동안 힐불가, 독마법 까지만 하자.
----------------------
적이 먼저 공격하는 경우도 있고, 이긴 후에 내가 먼저 공격할 수도 있다.
적이 먼저 공격할 찬스는 75%
------------
건축물의 패턴을 만들어서 건축물 생성기를 만드는것!
랜덤 심즈3의 심과같은 랜덤 사람도 만들고!
만약 도시를 랜덤으로 생성할 수 있다면 더 멋질 것!
자동차 등의 물품등도 랜덤으로 생성!

굳이 실제 현실과 똑같은 형태일 건 없고 프로그레시브하게 생성 가능한 여러가지 아이템을 만든다.

모든 액션게임은 달리기 또는 레이싱게임으로 기본이 잡힌다. 그리고 레이싱이나 달리기를 막는 무언가를 피하거나 이겨내는 것으로 게임플레이가 형성된다.
"""
