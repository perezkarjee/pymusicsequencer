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
        self.desc = desc
        self.connected = []
        self.safeZone = isSafe
        self.people = []
        self.mobs = []
        self.items = []
        G_rooms[ident] = self
        
def GetRooms():
    global G_rooms
    home = Room("home", u"아늑한 나의 집", u"""\
<font color="white" face="Verdana" size="2">
당신의 집이다. <br/>
<br/>
당신은 당신의 허름한 침대에 앉아있다. 작은 창으로 햇빛이 들어온다. <br/>
어제 잡은 몬스터들에게서 수집한 아이템들이 여기저기 지저분하게 널려있다.<br/>
몬스터들의 피 냄새도 난다. 거지 소굴이 따로 없다.<br/>
</font>""", True)
    town = Room("town", u"마을", u"""\
<font color="white" face="Verdana" size="2">
당신이 살고있는 마을이다.</br>
매우 작고 간소한 마을이지만 갖출 건 다 갖추었다.<br/>
<br/>
하지만 당신의 집은 그 중에서도 가장 구석진 곳에 떨어진 가장 허름한 집이다.<br/>
</font>""", True)
    ConnectRooms(home, town)

    return G_rooms


def InRect(x,y,w,h, x2, y2):
    if x <= x2 < x+w and y <= y2 < y+h:
        return True
    else:
        return False

def DrawText(x,y,text, xalign = 'left', yalign = 'top', color=(0,0,0,255)):
    label = pyglet.text.Label(text,
                        font_name='Verdana',
                        font_size=10,
                        x=x, y=shared.H-(y),
                        color = color,
                        anchor_x=xalign, anchor_y=yalign)
    return label


class OutputWindow(object):
    def __init__(self, x, y, w, h):
        self.texts = []
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = x,y,w,h
        self.lastY = 0
        self.lineH = 13

    def AddText(self, txt, color=(0,0,0,255)):
        self.texts += [DrawText(self.x+10, self.y+self.lastY+5, txt, 'left', 'top', color=color)]
        self.lastY += self.lineH

        if len(self.texts)*self.lineH > self.h-10:
            self.lastY -= self.lineH
            del self.texts[0]
            for text in self.texts:
                text.y += self.lineH

    def Render(self):
        for text in self.texts:
            text.draw()
class MyGameWindow(pyglet.window.Window):
    def __init__(self):
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
                        font_name='Verdana',
                        font_size=10,)

        self.sideMenuW = 240
        self.bottomMenuH = 200
        self.midMenuH = 335
        self.posMenuH = 190
        self.safeColor = (0,0,0,255)
        self.unsafeColor = (61,24,0,255)
        self.rooms = GetRooms()

        self.SetRoom("home")

        self.output = OutputWindow(0, H-self.bottomMenuH-self.midMenuH, W-self.sideMenuW, self.midMenuH)
        a = 0
        while a < 40:
            self.output.AddText("aaa")
            a+=1
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
                            font_name='Verdana',
                            font_size=12,
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

    def MoveRoom(self, roomName):
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
            self.Exit()

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
        glClearColor(self.bgColor[0]/255.0, self.bgColor[1]/255.0, self.bgColor[2]/255.0, 1.0)
        self.clear()
        DrawQuadWithBorder(W-self.sideMenuW, 0, self.sideMenuW, self.posMenuH, (0, 78, 196, 255), self.bgColor, 5) # zone menu
        DrawQuadWithBorder(W-self.sideMenuW, self.posMenuH-5, self.sideMenuW, H-self.posMenuH+5, (153, 210, 0, 255), self.bgColor, 5) # char menu
        DrawQuadWithBorder(0, H-self.bottomMenuH, W-self.sideMenuW+5, self.bottomMenuH, (196, 0, 78, 255), self.bgColor, 5) # mobs, npc, interactive object menu
        DrawQuadWithBorder(0, H-self.bottomMenuH-self.midMenuH, W-self.sideMenuW+5, self.midMenuH+5, (227, 155, 0, 255), self.bgColor, 5)

        self.output.Render()

        self.label.draw()
        for txt in self.texts:
            txt.draw()


        for button in self.zoneButtons:
            button.Render()



    def on_show(self):
        pass
    def on_close(self):
        self.Exit()
    def Exit(self):
        print 'Good Bye !'
        pyglet.app.exit()
    def on_mouse_motion(self, x, y, b, m):
        """
        state.lastMouseX = x
        state.lastMouseY = y
        """

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



def main():
    w = MyGameWindow()
    def b(dt): pass
    pyglet.clock.schedule(b)

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



일단 콘솔창
"""
