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
class MyGameWindow(pyglet.window.Window):
    def __init__(self):
        config = Config(depth_size=16, double_buffer=True,)
        pyglet.window.Window.__init__(self, vsync=VSYNC,config=config)
        self.set_maximum_size(W, H)
        self.set_minimum_size(W, H)
        self.set_size(W,H)
        self.set_location(3,29)
        self.set_caption("MudAdventure")


        self.label = pyglet.text.Label('Hello, world!')

    def on_key_release(self, s, m):
        """
        state.clickedButton = ""
        state.clickedMob = None
        state.moveCommandOn = False
        """
    def on_key_press(self, s, m):
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

    def on_show():
        pass
    def on_close():
        pass
        #state.running = False
    def on_mouse_motion(x, y, b, m):
        """
        state.lastMouseX = x
        state.lastMouseY = y
        """

    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        """
        state.lastMouseX = x
        state.lastMouseY = y
        """

    def on_mouse_release(x, y, b, m):
        """
        state.clickedButton = ""
        state.clickedMob = None
        state.lastMouseX = x
        state.lastMouseY = y
        state.moveCommandOn = False
        """

    def on_mouse_press(x, y, b, m):
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

    def on_tick():
        # Linux에서는 time.time을 써야 하고 window에서는 time.clock을 써야 한다.
        """
        curTick = int(time.clock()*1000)
        tick = state.tick = curTick-state.prevTick
        state.prevTick = curTick
        
        # mouse pos
        x, y = state.lastMouseX, state.lastMouseY

        #if state.clickedMob and ( (state.mobClickWait+tick) > state.mobClickDelay):
        #    state.client.MobClicked(state.clickedMob.idx, state.clickedButton)
        #state.mobClickWait += tick

        if state.moveCommandOn and ( (state.moveWait+tick) > state.moveDelay):
            state.moveWait = 0
            if state.clickedMob:
                state.client.UseSkill(state.clickedMob.idx, state.clickedButton)
            else:
                state.client.MoveTo(state.x+(x-shared.posX+shared.tileW/2)//shared.tileW, state.y+(y-shared.posY+shared.tileH/2)//shared.tileH)
        state.moveWait += tick
        
        """



def main():
    w = MyGameWindow()

    pyglet.app.run()

if __name__ == "__main__":
    main()
"""
머드게임같은데 인터페이스가 편안하고 좋은 걸 만든다.
일반 머드게임인데 어떻게 개선할 수 있을까?

그래픽 쓰지 말고 텍스트만 쓴다.
"""
