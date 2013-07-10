# -*- coding: utf-8 -*-
import threading
import time
import pyglet
import sys
import shared
import random
from euclid import *
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import mouse
import sys
from time import sleep
from sys import stdin, exit

#from PodSixNet.Connection import connection, ConnectionListener
W = 1020
H = 720
VSYNC = True

def DrawQuad(x,y,w,h, color):
    glColor4ub(*color)
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
        ('v2i', (x, H-y,
                x+w, H-y,
                x+w, H-(y+h),
                x, H-(y+h)))
    )
    
def DrawQuadWithBorder(x,y,w,h,bgcolor,borderColor, borderSize = 1):
    DrawQuad(x,y,w,h,bgcolor)
    DrawQuad(x,y,w,borderSize, borderColor)
    DrawQuad(x,y+h-borderSize,w,borderSize, borderColor)
    DrawQuad(x,y,borderSize,h, borderColor)
    DrawQuad(x+w-borderSize,y,borderSize,h, borderColor)

class Button(object):
    def __init__(self, x,y,w,h, label, callback):
        self.rect = [x,y,w,h]
        self.text = label
        self.func = callback
        self.visible = True
        self.label = DrawText(x+w/2, y+h/2, label, 'center', 'center')

    def SetVisible(self, vis):
        self.visible = vis
    def OnLDown(self, x,y):
        if not self.visible:
            return

        y = shared.H-y
        if InRect(*(self.rect+[x,y])):
            self.func()
    def Render(self):
        if not self.visible:
            return
        x,y,w,h = self.rect
        DrawQuadWithBorder(x,y,w,h,[42,42,42,255],[255,255,255,255])
        self.label.draw()

class ZoneButton(Button):
    def __init__(self, x,y,w,h, label, callback):
        Button.__init__(self, x,y,w,h, label, callback)
        self.label = DrawText(x+w/2, y+h/2, label, 'center', 'center', color=(0,46,116,255))

    def Render(self):
        if not self.visible:
            return
        x,y,w,h = self.rect
        DrawQuadWithBorder(x,y,w,h,[33,113,234,255],[0,46,116,255], 3)
        glColor4ub(0,46,116,255)
        self.label.draw()

def ConnectRooms(one, two):
    one.connected += [two]
    two.connected += [one]

G_rooms = {}
class Room(object):
    def __init__(self, ident, title, desc, isSafe):
        global G_rooms
        self.ident = ident
        self.title = title

        header = u"""<font color="white" face="Dotum" size="2"><b>"""
        footer = u"""</b></font>"""
        texts = desc.split("\n")
        text = '<br/>'.join(texts)
        self.desc = header + text + footer
        self.connected = []
        self.safeZone = isSafe
        self.people = []
        self.mobs = []
        self.items = []
        G_rooms[ident] = self
        
def GetRooms():
    global G_rooms
    home = Room("home", u"아늑한 나의 집", u"""\
당신의 집이다.

당신은 당신의 허름한 침대에 앉아있다. 작은 창으로 햇빛이 들어온다.
어제 잡은 몬스터들에게서 수집한 아이템들이 여기저기 지저분하게 널려있다.
몬스터들의 피 냄새도 난다. 거지 소굴이 따로 없다.
""", True)
    home.people += [Shop(u"창고", u"창고", u"인벤토리")]


    town = Room("town", u"마을", u"""\
당신이 살고있는 마을이다.
매우 작고 간소한 마을이지만 갖출 건 다 갖추었다.

하지만 당신의 집은 그 중에서도 가장 구석진 곳에 떨어진 가장 허름한 집이다.
""", True)
    town.people += [WeaponShop(u"무기상인", u"무기 상점", u"인벤토리")]
    town.people += [Shop(u"잡화상인", u"잡화 상점", u"인벤토리")]
    town.people += [Shop(u"던젼맵상인", u"던젼 맵 상점", u"인벤토리")]

    ConnectRooms(home, town)

    dungeon = Room("dungeon", u"던젼입구", u"""\
던젼의 입구이다.

이곳에서 던젼 맵을 사용하면 된다.

하지만 여기서도 멀리 보이는 당신의 집은 굉장히도 허름하게 보인다.
""", True)

    ConnectRooms(town, dungeon)


    return G_rooms

def InRect(x,y,w,h, x2, y2):
    if x <= x2 < x+w and y <= y2 < y+h:
        return True
    else:
        return False

def DrawText(x,y,text, xalign = 'left', yalign = 'top', color=(0,0,0,255),size=10,bold=True):
    label = pyglet.text.Label(text,
                        font_name='Dotum',
                        font_size=size,
                        bold=bold,
                        x=x, y=shared.H-(y),
                        color = color,
                        anchor_x=xalign, anchor_y=yalign)
    return label

def DrawHTMLText(x,y,w,text, size=10):
    text = pyglet.text.HTMLLabel(text,
                        width=w,
                        x=x, y=H-(y),multiline=False)
    text.font_size = size
    return text

class OutputWindow(object):
    def __init__(self, x, y, w, h):
        self.texts = []
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = x,y,w,h
        self.lastY = 0
        self.lineH = 15

    def AddText(self, txt, color=(0,0,0,255)):
        self.texts += [DrawHTMLText(self.x, self.y+self.lastY, self.w,txt, size=9)]
        self.lastY += self.lineH

        if len(self.texts)*self.lineH > self.h:
            self.lastY -= self.lineH
            del self.texts[0]
            for text in self.texts:
                text.y += self.lineH

    def Render(self):
        for text in self.texts:
            text.draw()

class Shop(Button):
    def __init__(self, name, leftname,rightname,x=0,y=0): # x,y는 bottomMenu의 텍스트 버튼 위치
        Button.__init__(self, x,y,100,25, name, self.OnClick)
        self.label = DrawText(x+100/2, y+25/2, name, 'center', 'center', color=(80,51,62,255))
        self.menuVisible = False

        w = W-GameWSt.sideMenuW+10
        self.text1 = DrawText(10, 10, leftname, 'left', 'top', color=(0,0,0,255))
        self.text2 = DrawText(w/2+5, 10, rightname, 'left', 'top', color=(0,0,0,255))
        self.text3 = DrawText(w-22-1, 5+1, u"X", 'left', 'top', color=(0,0,0,255),bold=True)

    def OnLDown(self, x,y):
        if not self.visible:
            return

        y = shared.H-y
        if InRect(*(self.rect+[x,y])):
            self.func()


        if not self.menuVisible:
            return
        
        w = W-GameWSt.sideMenuW+10
        if InRect(w-30,0,25,25,x,y):
            self.OffMenu()

    def OffMenu(self):
        GameWSt.menuVis = False
        GameWSt.menu = None
        self.menuVisible = False
    def OnMenu(self):
        if GameWSt.menu:
            GameWSt.menu.OffMenu()
        GameWSt.menuVis = True
        GameWSt.menu = self
        self.menuVisible = True

    def OnClick(self):
        self.menuVisible = not self.menuVisible
        if self.menuVisible:
            self.OnMenu()
        else:
            self.OffMenu()
    def Render(self):
        if not self.visible:
            return
        x,y,w,h = self.rect
        DrawQuadWithBorder(x,y,w,h,[223,185,200,255],[120,0,48,255], 3)
        glColor4ub(0,46,116,255)
        self.label.draw()

        if not self.menuVisible:
            return
        w = W-GameWSt.sideMenuW+10
        DrawQuadWithBorder(0,0,w/2,H-GameWSt.bottomMenuH+5-GameWSt.qSlotH+5,[0, 196,166,255],GameWSt.bgColor, 5)
        DrawQuadWithBorder(w/2-5,0,w/2,H-GameWSt.bottomMenuH+5-GameWSt.qSlotH+5,[0, 196,166,255],GameWSt.bgColor, 5)
        DrawQuadWithBorder(w-30,0,25,25,[66, 236,180,255],GameWSt.bgColor, 5)
        self.text1.draw()
        self.text2.draw()
        self.text3.draw()

        for item in GameWSt.inventory:
            item.Render()

class WeaponShop(Shop):
    def __init__(self, name, leftname, rightname, x=0,y=0): # x,y는 bottomMenu의 텍스트 버튼 위치
        Shop.__init__(self, name, leftname, rightname, 0,0)

    def OnLDown(self, x,y):
        Shop.OnLDown(self,x,y)

    def Render(self):
        Shop.Render(self)

        if not self.menuVisible:
            return
        for item in GameWSt.weaponShop:
            item.Render()

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
def IsRieul(chr):
    chr = ord(chr)
    c = chr - 0xAC00
    a = c / (21 * 28)
    c = c % (21 * 28)
    b = c / 28
    c = c % 28
    if c == 8:
        return True
    else:
        return False

class Skill(object):
    def __init__(self, shortTitle, title, desc):
        self.txt = shortTitle
        self.title = title
        self.desc = desc
        self.point = 0

    def Use(self, target1, target2, targets):
        pass

    def OnLDown(self):
        pass

    def CalcManaCost(self):
        return 0
    def GetDesc(self):
        return self.desc

class HealPotion(Skill):
    def __init__(self):
        Skill.__init__(self, u"힐포", u"힐링 포션", u"마시면 체력을 완전히 회복한다.")

    def Use(self, target1, target2, targets):
        healAmountNeeded = target1.CalcMaxHP()-target1.hp
        target1.hppotion -= healAmountNeeded
        if target1.hppotion < 0:
            healAmountNeeded += target1.hppotion
            target1.hppotion = 0
        target1.hp += healAmountNeeded

    def OnLDown(self):
        self.Use(GameWSt.char, None, [])

class ManaPotion(Skill):
    def __init__(self):
        Skill.__init__(self, u"마포", u"마나 포션", u"마시면 마력을 완전히 회복한다.")

    def Use(self, target1, target2, targets):
        healAmountNeeded = target1.CalcMaxMP()-target1.mp
        target1.mppotion -= healAmountNeeded
        if target1.mppotion < 0:
            healAmountNeeded += target1.mppotion
            target1.mppotion = 0
        target1.mp += healAmountNeeded

    def OnLDown(self):
        self.Use(GameWSt.char, None, [])
class SuperAttack(Skill):
    def __init__(self):
        Skill.__init__(self, u"후려", u"후려치기", u"현재 공격중인 적을 후려친다.")

    def Use(self, target1, target2, targets):
        pass

    def OnLDown(self):
        self.Use(GameWSt.char, GameWSt.curTarget, GameWSt.mobs)

class Item(object):
    def __init__(self, short, title, desc, x,y, isEmpty=False):
        self.short = short
        self.title = title
        self.desc = desc
        x,y,w,h = x, y, GameWSt.itemW, GameWSt.itemH
        self.label = DrawText(x+w/2, y+h/2, short, 'center', 'center', size=9)

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.isEmpty = isEmpty

    def Render(self):
        DrawQuad(self.x+5, self.y+5, self.w-10, self.h-10, (144, 244, 229, 255))
        if not self.isEmpty:
            self.label.draw()

    def GetDesc(self):
        return self.desc

class QuickSlot(object):
    def __init__(self, pos, skill):
        x,y,w,h = pos*(GameWSt.qSlotH+4-5), H-GameWSt.bottomMenuH-GameWSt.qSlotH+5, GameWSt.qSlotH+4, GameWSt.qSlotH
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = DrawText(x+w/2, y+h/2, skill.txt, 'center', 'center', size=9)
        self.skill = skill

    def Render(self):
        self.label.draw()

    def OnLDown(self,x,y):
        if InRect(self.x,self.y,self.w,self.h,x,H-y):
            self.skill.OnLDown()
GameWSt = None


class PopupWindow(object):
    def __init__(self, title, desc, x,y, ident):
        self.x = x
        self.y = y
        self.w = 300
        self.h = 400
        header = u"""<font color="black" face="Dotum" size="2">%s<br/><br/><b>""" % title
        footer = u"""</b></font>"""
        texts = desc.split("\n")
        text = '<br/>'.join(texts)
        self.desc = header + text + footer

        margin = 10
        self.margin = margin
        self.text = pyglet.text.HTMLLabel(self.desc,
                        width=self.w-margin*2,
                        x=x+margin, y=H-(y+margin+13),multiline=True)
        self.text.font_size = 9

        self.ident = ident

    def Render(self):
        DrawQuadWithBorder(self.x, self.y, self.w, self.h, (200, 200, 200, 150), (30,30,30,150), 0) # zone menu
        self.text.draw()

class Character(object):
    def __init__(self):
        self.hpPoint = 0
        self.mpPoint = 0
        self.hp = 100
        self.mp = 100

        self.hppotionPoint = 0
        self.hppotion = 3000
        self.mppotionPoint = 0
        self.mppotion = 3000

    def CalcMaxHP(self):
        return 100
    def CalcMaxMP(self):
        return 100
    def CalcHPPotion(self):
        return 3000
    def CalcMPPotion(self):
        return 3000

class MyGameWindow(pyglet.window.Window):
    def __init__(self):
        global GameWSt
        GameWSt = self
        config = Config(depth_size=16, double_buffer=True,)

        pyglet.window.Window.__init__(self, vsync=VSYNC,config=config)
        self.set_maximum_size(W, H)
        self.set_minimum_size(W, H)
        self.set_size(W,H)
        self.set_location(3,29)
        self.set_caption("TextAdventure")
        icon1 = pyglet.image.load('pygletgame/icons/icon16x16.png')
        icon2 = pyglet.image.load('pygletgame/icons/icon32x32.png')
        self.set_icon(icon1, icon2)
        
        self.label = pyglet.text.Label(u"안녕세상",
                        font_name='Dotum',
                        bold = True,
                        font_size=10,)

        self.sideMenuW = 240
        self.bottomMenuH = 200
        self.midMenuH = 300
        self.qSlotH = 40
        self.posMenuH = 190
        self.safeColor = (0,0,0,255)
        self.unsafeColor = (61,24,0,255)

        self.char = Character()
        self.curTarget = None
        self.mobs = []

        w = W-self.sideMenuW+10
        self.invX = w/2
        self.invY = 25
        self.leftX = 5
        self.itemW = self.qSlotH+3
        self.itemH = self.qSlotH




        idx = 40
        idxX = idx%10
        idxY = (idx-idxX)/10
        newItem = Item(u"단도", u"단도", u"짧고 날카로운 칼이다.", self.invX+idxX*(self.itemW-5), self.invY+idxY*(self.itemH-5))
        newItem2 = Item(u"단도", u"단도", u"짧고 날카로운 칼이다.", self.leftX+idxX*(self.itemW-5), self.invY+idxY*(self.itemH-5))




        self.inventory = []
        self.itemShop = []
        self.weaponShop = []
        self.stash = []
        for yy in range(13):
            for xx in range(10):
                self.inventory += [Item(u"없음", u"없음", u"빈 아이템", self.invX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5), isEmpty=True)]
        self.inventory[idx] = newItem

        for yy in range(13):
            for xx in range(10):
                self.itemShop += [Item(u"없음", u"없음", u"빈 아이템", self.leftX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5), isEmpty=True)]

        for yy in range(13):
            for xx in range(10):
                self.weaponShop += [Item(u"없음", u"없음", u"빈 아이템", self.leftX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5), isEmpty=True)]
        self.weaponShop[idx] = newItem2

        for yy in range(13):
            for xx in range(10):
                self.stash += [Item(u"없음", u"없음", u"빈 아이템", self.leftX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5), isEmpty=True)]



        self.rooms = GetRooms()

        self.output = OutputWindow(10, 20+H-self.bottomMenuH-self.midMenuH-self.qSlotH+5, W-self.sideMenuW-20, self.midMenuH-20)
        self.DoSysOutput(u"TextAdventure에 오신 것을 환영합ㅂㅂㅂ")
        self.DoSysOutput(u"이 게임은 만들다 말았음zz")

        self.SetRoom("home")

        self.qSlot = [
                QuickSlot(0, HealPotion()),
                QuickSlot(1, ManaPotion()),
                QuickSlot(2, SuperAttack()),
                QuickSlot(3, HealPotion()),
                QuickSlot(4, HealPotion()),
                QuickSlot(5, HealPotion()),
                QuickSlot(6, HealPotion()),
                QuickSlot(7, HealPotion()),
                QuickSlot(8, HealPotion()),
                QuickSlot(9, HealPotion()),
                QuickSlot(10, HealPotion()),
                QuickSlot(11, HealPotion()),
                QuickSlot(12, HealPotion()),
                QuickSlot(13, HealPotion()),
                QuickSlot(14, HealPotion()),
                QuickSlot(15, HealPotion()),
                QuickSlot(16, HealPotion()),
                QuickSlot(17, HealPotion()),
                QuickSlot(18, HealPotion()),
                QuickSlot(19, HealPotion()),
                ]

        GameWSt.menuVis = False
        GameWSt.menu = None
        self.lastMouseDown = {"l":[0,0], "r":[0,0], "m":[0,0]}


        self.popupWindow = None

    def DoSysOutput(self, txt):
        self.DoOutput(u"""<b><font color="#57701D">시스템==> </font><font color="#161F00">%s</font></b>""" % txt)
    def DoMsg(self,txt):
        self.DoOutput(u"""<b><font color="#161F00">%s</font></b>""" % txt)
    def DoOutput(self, txt, color=(0,0,0,255)):
        self.output.AddText(txt, color)
    def SetRoom(self, room):
        self.curRoom = room
        marginX = 10
        marginY = 25

        self.texts = []
        def NewText(args):
            txt, x, y = args
            x += marginX
            y += marginY
            text = pyglet.text.Label(txt,
                            font_name='Dotum',
                            font_size=12,bold = True,
                            x=x, y=H-(y),)
            self.texts += [text]
            return text

        def NewPara(args):
            txt, x, y = args
            x += marginX
            y += marginY
            text = pyglet.text.HTMLLabel(txt,
                            width=self.width-self.sideMenuW,
                            x=x, y=H-(y),multiline=True)
            text.font_size = 9
            self.texts += [text]
            return text

        args = [self.rooms[self.curRoom].title, 0, 0]
        self.roomTitle = NewText(args)

        args = [self.rooms[self.curRoom].desc, 0, 30]
        self.roomDesc = NewPara(args)
        self.SetRoomDesc(args[0])

        self.SetSafety(self.rooms[self.curRoom].safeZone)

        self.zoneButtons = []

        y = 0
        for room in self.rooms[self.curRoom].connected:
            self.zoneButtons += [ZoneButton(W-self.sideMenuW+10, y+10, self.sideMenuW-20, 30, room.title, lambda : self.MoveRoom(room.ident))]
            y += 35

        xbase = 10
        ybase = H-self.bottomMenuH+10
        x = xbase
        y = ybase
        self.npcs = []
        for people in self.rooms[self.curRoom].people[:]:
            people.rect[0] = x
            people.rect[1] = y
            people.label.x = x+100/2
            people.label.y = H-(y+25/2)
            x += 105
            if x+105 > H-self.sideMenuW:
                x = xbase
                y += 30
            self.npcs += [people]

        title = self.rooms[self.curRoom].title
        if IsJong(title[-1]) and not IsRieul(title[-1]):
            jong = u"으로"
        else:
            jong = u"로"

        self.DoMsg(u"%s%s 이동하였다." % (title, jong))

    def MoveRoom(self, roomName):
        if self.menu:
            self.menu.OffMenu()
        self.SetRoom(roomName)
        
    def SetRoomTitle(self, txt):
        self.roomTitle.text = txt
    def SetRoomDesc(self, txt):
        self.roomDesc.text = txt
    def SetSafety(self, val):
        self.isSafe = val
        if val:
            self.bgColor = self.safeColor
        else:
            self.bgColor = self.unsafeColor

    def on_key_release(self, s, m):
        """
        state.clickedButton = ""
        state.clickedMob = None
        state.moveCommandOn = False
        """
    def on_key_press(self, s, m):
        if s == key.ESCAPE:
            if self.menuVis:
                self.menu.OffMenu()
            #self.Exit()

        """
        if s in [key.Q, key.W, key.E, key.R, key.T]:
            x = state.lastMouseX
            y = state.lastMouseY

            clickedMobX = state.x+(x-shared.posX+shared.tileW/2)//shared.tileW
            clickedMobY = state.y+(y-shared.posY+shared.tileH/2)//shared.tileH
            found = False
            for mob in MobMgrS.mobs:
                if mob.x == clickedMobX and mob.y == clickedMobY:
                    state.clickedMob = mob
                    found = True
                    break
            if not found:
                state.clickedMob = None
            
            CheckMoveOn()


        if s == key.Q:
            state.clickedButton = "q"
        if s == key.W:
            state.clickedButton = "w"
        if s == key.E:
            state.clickedButton = "e"
        if s == key.R:
            state.clickedButton = "r"
        if s == key.T:
            state.clickedButton = "t"
        if s == key.S:
            GUIS.SetVisible("Stats", not StatsS.vis)
        if s == key.ESCAPE:
            state.running = False
            w.close()
        """

    def on_draw(self):
        self.on_tick()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(self.bgColor[0]/255.0, self.bgColor[1]/255.0, self.bgColor[2]/255.0, 1.0)
        self.clear()
        DrawQuadWithBorder(W-self.sideMenuW, 0, self.sideMenuW, self.posMenuH, (0, 78, 196, 255), self.bgColor, 5) # zone menu
        DrawQuadWithBorder(W-self.sideMenuW, self.posMenuH-5, self.sideMenuW, H-self.posMenuH+5, (153, 210, 0, 255), self.bgColor, 5) # char menu
        DrawQuadWithBorder(0, H-self.bottomMenuH, W-self.sideMenuW+5, self.bottomMenuH, (196, 0, 78, 255), self.bgColor, 5) # mobs, npc, interactive object menu
        DrawQuadWithBorder(0, H-self.bottomMenuH-self.midMenuH-(self.qSlotH-5), W-self.sideMenuW+5, self.midMenuH+5, (227, 155, 0, 255), self.bgColor, 5)

        x = 0
        for i in range(20):
            DrawQuadWithBorder(x, H-self.bottomMenuH-self.qSlotH+5, self.qSlotH+4, self.qSlotH, (196, 166, 0, 255), self.bgColor, 5)
            x += self.qSlotH-5+4

        self.output.Render()

        self.label.draw()
        for txt in self.texts:
            txt.draw()

        for slot in self.qSlot:
            slot.Render()


        for button in self.zoneButtons:
            button.Render()
        for button in self.npcs:
            button.Render()



        if self.popupWindow:
            self.popupWindow.Render()



    def on_show(self):
        pass
    def on_close(self):
        self.Exit()
    def Exit(self):
        print 'Good Bye !'
        pyglet.app.exit()
    def on_mouse_motion(self, x, y, b, m):
        found = False
        for pos in range(20):
            xx,yy,ww,hh = pos*(GameWSt.qSlotH+4-5), H-GameWSt.bottomMenuH-GameWSt.qSlotH+5, GameWSt.qSlotH+4, GameWSt.qSlotH
            if InRect(xx,yy,ww,hh,x,H-y):
                if not (self.popupWindow and self.popupWindow.ident == self.qSlot[pos]):
                    self.popupWindow = PopupWindow(self.qSlot[pos].skill.title, self.qSlot[pos].skill.GetDesc(), x, H-y, self.qSlot[pos])
                elif self.popupWindow:
                    self.popupWindow.x = x
                    self.popupWindow.y = H-y
                    self.popupWindow.text.x = x+self.popupWindow.margin
                    self.popupWindow.text.y = (y-self.popupWindow.margin-13)
                    
                found = True
                break

        container = None
        if isinstance(self.menu, WeaponShop):
            container = self.weaponShop

        if container:
            for yy in range(13):
                for xx in range(10):
                    xxx,yyy,www,hhh = self.leftX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5), self.itemW, self.itemH
                    item = container[yy*10+xx]
                    if InRect(xxx,yyy,www,hhh,x,H-y) and not container[yy*10+xx].isEmpty:
                        if not (self.popupWindow and self.popupWindow.ident == item):
                            self.popupWindow = PopupWindow(item.title, item.GetDesc(), x, H-y, item)
                        elif self.popupWindow:
                            self.popupWindow.x = x
                            self.popupWindow.y = H-y
                            self.popupWindow.text.x = x+self.popupWindow.margin
                            self.popupWindow.text.y = (y-self.popupWindow.margin-13)
                            
                        found = True
                        break
                if found:
                    break

        container = self.inventory
        if self.menuVis:
            for yy in range(13):
                for xx in range(10):
                    xxx,yyy,www,hhh = self.invX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5), self.itemW, self.itemH
                    item = container[yy*10+xx]
                    if InRect(xxx,yyy,www,hhh,x,H-y) and not container[yy*10+xx].isEmpty:
                        if not (self.popupWindow and self.popupWindow.ident == item):
                            self.popupWindow = PopupWindow(item.title, item.GetDesc(), x, H-y, item)
                        elif self.popupWindow:
                            self.popupWindow.x = x
                            self.popupWindow.y = H-y
                            self.popupWindow.text.x = x+self.popupWindow.margin
                            self.popupWindow.text.y = (y-self.popupWindow.margin-13)
                            
                        found = True
                        break
                if found:
                    break




        if not found:
            self.popupWindow = None

        if self.popupWindow: # fix overflown popup window
            if ((H-y)+self.popupWindow.h) > H:
                self.popupWindow.y = H-self.popupWindow.h
                self.popupWindow.text.y = self.popupWindow.h-self.popupWindow.margin-13
            if x+self.popupWindow.w > W:
                self.popupWindow.x = W-self.popupWindow.w
                self.popupWindow.text.x = self.popupWindow.x+self.popupWindow.margin

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """
        state.lastMouseX = x
        state.lastMouseY = y
        """

    def on_mouse_release(self, x, y, b, m):
        """
        state.clickedButton = ""
        state.clickedMob = None
        state.lastMouseX = x
        state.lastMouseY = y
        state.moveCommandOn = False
        """

    def on_mouse_press(self, x, y, b, m):
        if b == mouse.LEFT:
            for button in self.zoneButtons:
                button.OnLDown(x,y)
            for button in self.npcs:
                button.OnLDown(x,y)
            for slot in self.qSlot:
                slot.OnLDown(x,y)

            self.lastMouseDown["l"] = [x,y]
        if b == mouse.MIDDLE:
            self.lastMouseDown["m"] = [x,y]
        if b == mouse.RIGHT:
            self.lastMouseDown["r"] = [x,y]

        """
        state.lastMouseX = x
        state.lastMouseY = y

        clickedMobX = state.x+(x-shared.posX+shared.tileW/2)//shared.tileW
        clickedMobY = state.y+(y-shared.posY+shared.tileH/2)//shared.tileH
        found = False
        for mob in MobMgrS.mobs:
            if mob.x == clickedMobX and mob.y == clickedMobY:
                state.clickedMob = mob
                found = True
                break
        if not found:
            state.clickedMob = None

        if b == mouse.RIGHT:
            state.clickedButton = "rmb"
            CheckMoveOn()
            state.lock.acquire()
            #state.spawn_ball(state._state, (x*x_ratio, y*y_ratio))
            state.lock.release()
        if b == mouse.MIDDLE:
            CheckMoveOn()
            state.clickedButton = "mmb"
        if b == mouse.LEFT:
            CheckMoveOn()
            state.clickedButton = "lmb"
            GUIS.OnLDown(x,y)
        """

    def on_tick(self):
        tick = pyglet.clock.tick() # time passed since previous frame
        self.label.text = u"안녕세상" + `tick`

def MakeDrawCallConstant():
    def b(dt): pass
    pyglet.clock.schedule(b)


def main():
    w = MyGameWindow()
    MakeDrawCallConstant()
    pyglet.app.run()

if __name__ == "__main__":
    main()
"""
머드게임같은데 인터페이스가 편안하고 좋은 걸 만든다.
일반 머드게임인데 어떻게 개선할 수 있을까?

그래픽 쓰지 말고 텍스트만 쓴다.


몹
캐릭터
전투
상점
집에가면 창고
인벤토리 등

아이템은 갈수록 세지는데
아이템이 잘 떨어지지 않는다.
포인트를 넣으면 더 세진다.
그런데 어떤 아이템은 같은 포인트를 넣어도 더 세진다.
레벨은 없고 무조건 포인트
돈도 없고 무조건 포인트
스킬도 다 포인트로 업글
스탯도 다 포인트로 업글

장비중에 특수한 게 있어서 스킬이나 스탯 포인트의 효율을 높여주는 장비들이 희귀아이템
스킬은 초반부터 아무 스킬이나 다 쓸 수 있다.

적의 공격 딜레이에 랜덤 베리에이션을 준다. 이용자의 공격 딜레이에도 준다?


일단 콘솔창 -- 완료
이제 상인과 몹

몹을 죽이면 현재 방의 목록에서 사라진다. 하지만 다른 방으로 갔다오면 다시 생긴다.
몹을 클릭한 후에 스킬을 쓰면 가장 마지막에 클릭한 몹에게 스킬이 시전된다.



스킬 자체를 캐릭터마다 20개만 만들어서 미리 퀵바에 지정해 두고 그걸 쓰게 한다.
퀵바는 커스터마이즈가 불가능하도록 하자.


무기상인은 무기를 잡화상인은 아이템 부스트나 인챈트 보석 룬등을 판다.

포션 충전은 마을에 오면 자동으로 되며 필드에서도 충전이 된다. 가만 있어도 차고 적을 잡으면 더 빨리 찬다.



흠 경험치가 없고 포인트만 있으면 상점에선 뭘 파나?
기본 마을 상점에선 싸구려만 팔고, 난이도를 포인트를 소비하여 높일 수 있고 난이도를 높이면 마을 상점이 점점 업글?
아 상점을 포인트로 업글하도록 한다.


아이템 설명 보여주는 팝업 윈도우를 만든다.
"""
