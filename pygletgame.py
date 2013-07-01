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



class MyGameWindow(pyglet.window.Window):
    def __init__(self):
        config = Config(depth_size=16, double_buffer=True,)
        pyglet.window.Window.__init__(self, vsync=VSYNC,config=config)
        self.set_maximum_size(W, H)
        self.set_minimum_size(W, H)
        self.set_size(W,H)
        self.set_location(3,29)
        self.set_caption("MudAdventure")


        self.label = pyglet.text.Label(u"안녕세상",
                        font_name='Verdana',
                        font_size=10,)

        self.sideMenuW = 240
        self.bottomMenuH = 200

        self.texts = []
        marginX = 10
        marginY = 25
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



        args = [u"아늑한 나의 집", 0, 0]
        self.roomTitle = NewText(args)

        args = [u"""\
<font color="white" face="Verdana" size="2">
당신의 집이다. <br/>
<br/>
당신은 당신의 허름한 침대에 앉아있다. 작은 창으로 햇빛이 들어온다. <br/>
어제 잡은 몬스터들에게서 수집한 아이템들이 여기저기 지저분하게 널려있다.<br/>
몬스터들의 피 냄새도 난다. 거지 소굴이 따로 없다.<br/>
</font>
""", 0, 30]
        self.roomDesc = NewPara(args)
        self.SetRoomDesc(args[0])





    def SetRoomTitle(self, txt):
        self.roomTitle.text = txt
    def SetRoomDesc(self, txt):
        self.roomDesc.text = txt

    def on_key_release(self, s, m):
        """
        state.clickedButton = ""
        state.clickedMob = None
        state.moveCommandOn = False
        """
    def on_key_press(self, s, m):
        if s == key.ESCAPE:
            print 'Good Bye !'
            pyglet.app.exit()

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
        self.clear()
        self.label.draw()
        for txt in self.texts:
            txt.draw()


        w = self.sideMenuW
        DrawQuadWithBorder(W-w, 0, w, H, (0, 78, 196, 255), (0,0,0,0), 5)
        DrawQuadWithBorder(0, H-self.bottomMenuH, W-w+5, self.bottomMenuH, (196, 0, 78, 255), (0,0,0,0), 5)

    def on_show(self):
        pass
    def on_close(self):
        pass
        #state.running = False
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



"""
