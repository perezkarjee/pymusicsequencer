# -*- coding: utf-8 -*-
import threading
import time
import legume
import pyglet
import sys
import shared
import astar
import random
from euclid import *
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import mouse

LOCALHOST = 'localhost'
REMOTEHOST = 'aura.psyogenix.co.uk'

VSYNC = True

PORT = 27806
class BallClient(object):
    def __init__(self):
        self.running = True
        #shared.BallEnvironment.__init__(self)
        self._client = legume.Client()
        self._client.OnMessage += self.message_handler
        self.lastdelta = time.time()
        self.lock = threading.Lock()
        self.ball_positions = None
        self.pX = 0
        self.pY = 0
        self.x = 0
        self.y = 0

    def message_handler(self, sender, args):
        if legume.messages.message_factory.is_a(args, 'TestPos'):
            print('Message: %d %d' % (args.x.value, args.y.value))
        else:
            print('Message: %s' % args)
        """
        if legume.messages.message_factory.is_a(args, 'BallUpdate'):
            self.load_ball_from_message(args)
        else:
            print('Message: %s' % args)
        """

    def connect(self, host='localhost'):
        self._client.connect((host, PORT))

    def go(self):
        while self.running:
            try:
                """
                self._update_balls()
                """
                self.lock.acquire()
                self._client.update()
                """
                self.lastdelta = time.time()
                self.ball_positions = self.get_ball_positions()
                """
            except:
                self.running = False
                raise
            finally:
                self.lock.release()
            time.sleep(0.0001)
        print('Exited go')

    def force_resync(self):
        """
        for ball in self._balls.itervalues():
            ball.force_resync = True
        """

    def load_ball_from_message(self, message):
        """
        print('Got status for ball %s' % message.ball_id.value)
        if message.ball_id.value not in self._balls:
            print('Creating new ball')
            new_ball = shared.Ball(self)
            new_ball.load_from_message(message)
            self.insert_ball(new_ball)
        else:
            self._balls[message.ball_id.value].load_from_message(message)
        """

        """
    def spawn_ball(self, endpoint, position):
        message = shared.CreateBallCommand()
        message.x.value = position[0]
        message.y.value = position[1]
        endpoint.send_message(message)
        """

    def showlatency(self, dt):
        print('latency: %3.3f    fps:%3.3f' % (
            self._client.latency, pyglet.clock.get_fps()))

    def moveTo(self, dX, dY):
        self.pX = self.x
        self.pY = self.y
        self.x = dX
        self.y = dY

    def move(self, dX, dY):
        self.pX = self.x
        self.pY = self.y
        self.x += dX
        self.y += dY

W = 800
H = 600

def centerimg(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width/2
    image.anchor_y = image.height/2
    return image

def SubImg(img, x,y,w,h):
    newimg = centerimg(img.get_region(x,img.height-y-h,w,h))
    return newimg

class State:
    def __init__(self):
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.rButtonDown = False
        self.moveDelay = 150
        self.moveWait = 0
        self.prevTick = time.clock()*1000
        self.tick = 0


class FPS:
    def __init__(self):
        self.fpsCounter = 0
        self.fpsSum = 0
        self.start = 0.0
        self.end = 0.0
        self.delay = 4000
        self.sumStart = int(time.clock()*1000)
    def Start(self):
        timetaken = float(self.end-self.start)
        if timetaken == 0: timetaken = 1.0
        fps = 1000.0/timetaken
        self.fpsSum += fps
        self.fpsCounter += 1
        self.start = int(time.clock()*1000)

    def End(self):
        self.end = int(time.clock()*1000)
    def GetFPS(self):
        if self.fpsCounter == 0:
            fps = 0
        else:
            fps = self.fpsSum/self.fpsCounter
        tick = int(time.clock()*1000)
        if tick - self.sumStart > self.delay:
            self.sumStart = int(time.clock()*1000)
            self.fpsCounter = 0
            self.fpsSum = 0
        return fps

def InRect(x,y,w,h, x2, y2):
    if x <= x2 < x+w and y <= y2 < y+h:
        return True
    else:
        return False

StateS = None
MobMgrS = None
mapW = 20
mapH = 20
posX = W//2
posY = H//2
tileW = 32
tileH = 32
def main():
    global StateS, MobMgrS
    if "--remote" in sys.argv:
        host = REMOTEHOST
    else:
        host = LOCALHOST
    print('Using host: %s' % host)

    client = BallClient()
    client.connect(host)

    try:
        # Try and create a window with multisampling (antialiasing)
        config = Config(sample_buffers=1, samples=4,
                        depth_size=16, double_buffer=True,)
        w = pyglet.window.Window(vsync=VSYNC,config=config) # "vsync=False" to check the framerate
    except pyglet.window.NoSuchConfigException:
        # Fall back to no multisampling for old hardware
        w = pyglet.window.Window(vsync=VSYNC,)


    #w = pyglet.window.Window(vsync=VSYNC)
    w.set_maximum_size(W, H)
    w.set_minimum_size(W, H)
    w.set_size(W,H)
    w.set_location(3,29)
    w.set_caption("ItemDiggers")

    label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=12,
                          x=w.width-100, y=20,
                          anchor_x='center', anchor_y='center')

    state = State()
    StateS = state

    @w.event
    def on_key_press(s, m):
        if s == key.W:
            client.move(0,1)
        if s == key.S:
            client.move(0,-1)
        if s == key.A:
            client.move(-1,0)
        if s == key.D:
            client.move(1,0)
        if s == key.ESCAPE:
            client.running = False
            w.close()
        if s == 114: # "r"
            client.force_resync()


    @w.event
    def on_show():
        client.force_resync()

    @w.event
    def on_close():
        client.running = False
    
    map = shared.MapGen(mapW,mapH)
    map.Gen(4, 5, 5, 3, 3)

    
    @w.event
    def on_mouse_motion(x, y, b, m):
        state.lastMouseX = x
        state.lastMouseY = y

    @w.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        state.lastMouseX = x
        state.lastMouseY = y

    @w.event
    def on_mouse_release(x, y, b, m):
        state.lastMouseX = x
        state.lastMouseY = y
        if b == mouse.RIGHT:
            state.rButtonDown = False

    @w.event
    def on_mouse_press(x, y, b, m):
        state.lastMouseX = x
        state.lastMouseY = y
        if b == mouse.RIGHT:
            state.rButtonDown = True
            client.lock.acquire()
            #client.spawn_ball(client._client, (x*x_ratio, y*y_ratio))
            client.lock.release()
        if b == mouse.MIDDLE:
            print 'MClicked %d, %d' % (x,y)
        if b == mouse.LEFT:
            print 'LClicked %d, %d' % (x,y)

    def on_tick():
        # calc tick
        curTick = int(time.clock()*1000)
        tick = state.tick = curTick-state.prevTick
        state.prevTick = curTick
        
        # mouse pos
        x, y = state.lastMouseX, state.lastMouseY

        if state.rButtonDown and ( (state.moveWait+tick) > state.moveDelay):
            state.moveWait = 0
            prevTime = time.clock()
            def TimeFunc():
                curTime = time.clock()
                return (curTime-prevTime)*1000
            finder = astar.AStarFinder(map.map, mapW, mapH, client.x, client.y, client.x+(x-posX)//tileW, client.y+(y-posY)//tileH, TimeFunc, 10)
            found = finder.Find()
            if found and len(found) >= 2:
                cX, cY = found[1][0], found[1][1]
                client.moveTo(cX, cY)
        state.moveWait += tick

        if MobMgrS.waited+tick > MobMgrS.delay:
            MobMgrS.waited = 0
            MobMgrS.Move()
        MobMgrS.waited += tick

    """
    이제 움직임을 서버에서 하게 한다.
    """

    playerImg = pyglet.image.load(r'tiles\player.png')
    floorImg = pyglet.image.load(r'tiles\floor.png')
    wallImg = pyglet.image.load(r'tiles\wall.png')
    #bImg = pyglet.image.load(r'tiles\title_denzi_dragon.png')
    state.batchMap = pyglet.graphics.Batch()
    state.batchStructure = pyglet.graphics.Batch()
    #state.batchItem = pyglet.graphics.Batch()
    #state.batchMonsterBG = pyglet.graphics.Batch()
    #state.batchMonster = pyglet.graphics.Batch()
    state.batchClothBG = pyglet.graphics.Batch()
    state.batchChar = pyglet.graphics.Batch()
    state.batchClothFG = pyglet.graphics.Batch()
    state.batchWeapon = pyglet.graphics.Batch()
    #state.batchMagic = pyglet.graphics.Batch()

    humanImg = SubImg(playerImg,282,875,22,30)
    humanSpr = pyglet.sprite.Sprite(img=humanImg, x=posX, y=posY, batch=state.batchChar)
    cloakImg = SubImg(playerImg,287,906,20,25)
    cloakSpr = pyglet.sprite.Sprite(img=cloakImg, x=posX, y=posY-3, batch=state.batchClothBG)
    robeImg = SubImg(playerImg,320,935,16,21)
    robeSpr = pyglet.sprite.Sprite(img=robeImg, x=posX, y=posY-3, batch=state.batchClothFG)
    staffImg = SubImg(playerImg,169,985,6,29)
    staffSpr = pyglet.sprite.Sprite(img=staffImg, x=posX-9, y=posY+2, batch=state.batchWeapon)


    floorTile = SubImg(floorImg, 288, 96, tileW, tileH)
    wallTile = SubImg(wallImg, 416, 64, tileW, tileH)
    state.floorSprs = []
    state.wallSprs = []

    randRoom = map.rooms[random.randint(0, len(map.rooms)-1)]
    randX = random.randint(randRoom[0], randRoom[0]+randRoom[2]-1)
    randY = random.randint(randRoom[1], randRoom[1]+randRoom[3]-1)
    client.pX = client.x = randX
    client.pY = client.y = randY


    class MobManager(object):
        def __init__(self):
            self.mobs = []
            self.waited = 0
            self.delay = 250

        def AddMob(self, mob):
            self.mobs += [mob]

        def RemoveMob(self, mob):
            del self.mobs[self.mobs.index(mob)]

        def Draw(self):
            for mob in self.mobs:
                mob.Draw()

        def Move(self):
            for mob in self.mobs:
                prevTime = time.clock()
                def TimeFunc():
                    curTime = time.clock()
                    return (curTime-prevTime)*1000
                finder = astar.AStarFinder(map.map, mapW, mapH, mob.x, mob.y, mob.x+random.randint(-4,4), mob.y+random.randint(-4,4), TimeFunc, 10)
                found = finder.Find()
                if found and len(found) >= 2:
                    cX, cY = found[1][0], found[1][1]
                    mob.SetPos(cX,cY)
    MobMgrS = MobManager()


    class Mob(object):
        def __init__(self, img, bgImg = None):
            self.img = img
            self.bgImg = bgImg
            if bgImg:
                self.sprBG = pyglet.sprite.Sprite(img=img, x=0, y=0)
            else:
                self.sprBG = None
            self.spr = pyglet.sprite.Sprite(img=img, x=0, y=0)
            self.x = 0
            self.y = 0
            MobMgrS.AddMob(self)

        
        def Draw(self):
            if self.sprBG:
                self.sprBG.draw()
            self.spr.draw()
        def Delete(self):
            MobMgrS.RemoveMob(self)

        def SetPos(self, x, y):
            self.x = x
            self.y = y
            if self.sprBG:
                self.sprBG.x = x*tileW+posX
                self.sprBG.y = y*tileH+posY
            self.spr.x = x*tileW+posX
            self.spr.y = y*tileH+posY


    rat = Mob(SubImg(playerImg, 184, 74, 28, 20))

    randRoom = map.rooms[random.randint(0, len(map.rooms)-1)]
    randX = random.randint(randRoom[0], randRoom[0]+randRoom[2]-1)
    randY = random.randint(randRoom[1], randRoom[1]+randRoom[3]-1)
    rat.SetPos(randX,randY)

    for y in range(mapH):
        for x in range(mapW):
            if map.map[y*map.w + x] == 0:
                state.floorSprs += [[pyglet.sprite.Sprite(img=floorTile, x=(x-0)*tileW+posX, y=(y-0)*tileH+posY, batch=state.batchMap), x,y]]
    for y in range(mapH):
        for x in range(mapW):
            if map.walls[y*map.w + x] == 1:
                state.wallSprs += [[pyglet.sprite.Sprite(img=wallTile, x=(x-0)*tileW+posX, y=(y-0)*tileH+posY, batch=state.batchMap), x,y]]

    """
    main_batch1 = pyglet.graphics.Batch()
    main_batch2 = pyglet.graphics.Batch()
    sprite1 = pyglet.sprite.Sprite(img=aImg, x=0, y=0, batch=main_batch1)
    sprite2 = pyglet.sprite.Sprite(img=bImg, x=30, y=30, batch=main_batch2)
    """
    """
    fps = FPS()
        """
    arial = pyglet.font.load('Arial', 12, bold=True, italic=False)
    fps = pyglet.clock.ClockDisplay(font=arial)
    @w.event
    def on_draw():
        """
        fps.Start()
        """
        on_tick()
        """
        if client.pX != client.x or client.pY != client.y:
            # XXX: 모든 타일을 다 업뎃하면 느림. 해결을... 페이징을 해야한다. 음! 이미 있는 타일은 리로드 안하고 없는 타일은 로드 하고
            # 필요없는 타일은 삭제 하고 싶지만 뱃치에서 삭제하는 게 지원 안함. 그러므로 뱃치를 다시 처음부터 만든다. 
            client.pX = client.x
            client.pY = client.y
            startX = client.x-(W//2)//tileW
            if startX < 0:
                startX = 0
            startY = client.y-(H//2)//tileH-1
            if startY < 0:
                startY = 0
            endX = startX + (W)//tileW
            if endX >= map.w:
                endX = map.w
            endY = startY + (H)//tileH+2
            if endY >= map.h:
                endY = map.h
            state.batchMap = pyglet.graphics.Batch()
            state.floorSprs = []
            for y in range(startY, endY):
                for x in range(startX, endX):
                    if map.map[y*map.w + x] == 0:
                        state.floorSprs += [[pyglet.sprite.Sprite(img=floorImg, x=(x-client.x)*tileW+posX, y=(y-client.y)*tileH+posY, batch=state.batchMap), x,y]]
            state.batchMap = pyglet.graphics.Batch()
            state.floorSprs = []
            for y in range(startY, endY):
                for x in range(startX, endX):
                    if map.map[y*map.w + x] == 0:
                        state.floorSprs += [[pyglet.sprite.Sprite(img=floorImg, x=(x-client.x)*tileW+posX, y=(y-client.y)*tileH+posY, batch=state.batchMap), x,y]]
            # 이제 좀 빨라졌는데 그래도 느리네?
            # 아이템이랑 몹 더 넣으면 더 느려질텐데...
        """
        w.clear()
        """
        label = pyglet.text.Label('%d' % fps.GetFPS(),
                          font_name='Times New Roman',
                          font_size=12,
                          x=w.width-100, y=20,
                          anchor_x='center', anchor_y='center')
        """
        # Draw Map, Structures, Mobs
        glLoadIdentity()
        glTranslatef(-float(tileW*client.x), -float(tileH*client.y), 0.0)
        state.batchMap.draw()
        state.batchStructure.draw()
        #state.batchItem.draw()
        MobMgrS.Draw()
        #state.batchMonsterBG.draw()
        #state.batchMonster.draw()

        # Draw Char
        glLoadIdentity()
        state.batchClothBG.draw()
        state.batchChar.draw()
        state.batchClothFG.draw()
        state.batchWeapon.draw()

        # Draw Magic Effect ETC.
        glTranslatef(-float(tileW*client.x), -float(tileH*client.y), 0.0)
        #state.batchMagic.draw()

        glLoadIdentity()
        label.draw()
        fps.draw()
        """
        fps.End()
        """

        """
        main_batch2.draw()
        main_batch1.draw()
        """
        """
        if client.ball_positions is not None:
            for x, y in client.ball_positions:
                x /= x_ratio
                y /= y_ratio
                ball_sprite.set_position(x, y)
                ball_sprite.draw()
        """

    #pyglet.clock.schedule_interval(client.showlatency, 0.75)

    # keep pyglet draw running regularly.
    def b(dt): pass
    pyglet.clock.schedule(b)

    net_thread = threading.Thread(target=client.go)
    net_thread.start()

    pyglet.app.run()
    client.running = False

if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='client.log', level=logging.DEBUG)
    main()


"""
음. 맵 그냥 스프라이트로 하고 glTranslatef를 써본다.


그래픽이 노가다가 쩔 것 같다.
던크 타일이 좋긴 좋은데 32x32로 딱 나뉜 게 아니다. 수동으로 나중에 다 해줘야 함.
하나씩 하나씩 필요한 거 골라서 하면 된다.

맵은 미리 버텍스 리스트를 만들어 두고
몹이나 효과및 아이템은 걍 프레임 때마다 버텍스리스트를 만들어서 렌더링하게 한다. 모든 레이어를 다.
뎁스 테스트를 없애고 알파 블렌딩만 만들어서 쓴다.


#!/usr/bin/env python
# ----------------------------------------------------------------------------
# Pyglet Demo Base for GLSL Examples on http://www.pythonstuff.org
# pythonian_at_inode_dot_at  (c) 2010
#
# based on the "graphics.py" batch/VBO demo by
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

'''Displays a rotating torus using the pyglet.graphics API.

This example is very similar to examples/opengl.py, but uses the
pyglet.graphics API to construct the indexed vertex arrays instead of
using OpenGL calls explicitly.  This has the advantage that VBOs will
be used on supporting hardware automatically.

The vertex list is added to a batch, allowing it to be easily rendered
alongside other vertex lists with minimal overhead.

It also show a FPS display, HTML-Text and keyboard control.
This is the basic code for the GLSL-Examples on http://www.pythonstuff.org
'''
html = '''
<font size=+3 color=#FF3030>
<b>Pyglet Basic OpenGL Demo</b>
</font><br/>
<font size=+2 color=#00FF60>
R = Reset<br/>
Q, Esc = Quit<br/>
F = Toggle Figure<br/>
T = Toggle Wireframe<br/>
W, S, A, D = Up, Down, Left, Right<br/>
Space = Move/Stop<br/>
Arrows = Move Light 0<br/>
H = This Help<br/>
</font>
'''

from math import pi, sin, cos, sqrt
from euclid import *

import pyglet
from pyglet.gl import *
from pyglet.window import key

try:
    # Try and create a window with multisampling (antialiasing)
    config = Config(sample_buffers=1, samples=4,
                    depth_size=16, double_buffer=True,)
    window = pyglet.window.Window(resizable=True, config=config, vsync=False) # "vsync=False" to check the framerate
except pyglet.window.NoSuchConfigException:
    # Fall back to no multisampling for old hardware
    window = pyglet.window.Window(resizable=True)

label = pyglet.text.HTMLLabel(html, # location=location,
                              width=window.width//2,
                              multiline=True, anchor_x='center', anchor_y='center')

fps_display = pyglet.clock.ClockDisplay() # see programming guide pg 48

@window.event
def on_resize(width, height):
    if height==0: height=1
    # Keep text vertically centered in the window
    label.y = window.height // 2
    # Override the default on_resize handler to create a 3D projection
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60., width / float(height), .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED

def update(dt):
    global autorotate
    global rot

    if autorotate:
        rot += Vector3(0.1, 12, 5) * dt
        rot.x %= 360
        rot.y %= 360
        rot.z %= 360
pyglet.clock.schedule(update)

def dismiss_dialog(dt):
    global showdialog
    showdialog = False
pyglet.clock.schedule_once(dismiss_dialog, 10.0)

# Define a simple function to create ctypes arrays of floats:
def vec(*args):
    return (GLfloat * len(args))(*args)

@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -3.5);
    glRotatef(rot.x, 0, 0, 1)
    glRotatef(rot.y, 0, 1, 0)
    glRotatef(rot.z, 1, 0, 0)

    if togglewire:
        glPolygonMode(GL_FRONT, GL_LINE)
    else:
        glPolygonMode(GL_FRONT, GL_FILL)

    if togglefigure:
        batch1.draw()
    else:
        batch2.draw()

    if togglewire:
        glPolygonMode(GL_FRONT, GL_FILL)

    glActiveTexture(GL_TEXTURE0)
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    if showdialog:
        glLoadIdentity()
        glTranslatef(0, -200, -450)
        label.draw()

    glLoadIdentity()
    glTranslatef(250, -290, -500)
    fps_display.draw()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)

@window.event
def on_key_press(symbol, modifiers):
    global autorotate
    global rot
    global togglefigure
    global togglewire
    global light0pos
    global light1pos
    global showdialog

    if symbol == key.R:
        print 'Reset'
        rot = Vector3(0, 0, 90)
    elif symbol == key.ESCAPE or symbol == key.Q:
        print 'Good Bye !'   # ESC would do it anyway, but not "Q"
        pyglet.app.exit()
        return pyglet.event.EVENT_HANDLED
    elif symbol == key.H:
        showdialog = not showdialog
    elif symbol == key.SPACE:
        print 'Toggle autorotate'
        autorotate = not autorotate
    elif symbol == key.F:
        togglefigure = not togglefigure
        print 'Toggle Figure ', togglefigure
    elif symbol == key.T:
        togglewire = not togglewire
        print 'Toggle Wireframe ', togglewire
    elif symbol == key.A:
        print 'Stop left'
        if autorotate:
            autorotate = False
        else:
            rot.y += -rotstep
            rot.y %= 360
    elif symbol == key.S:
        print 'Stop down'
        if autorotate:
            autorotate = False
        else:
            rot.z += rotstep
            rot.z %= 360
    elif symbol == key.W:
        print 'Stop up'
        if autorotate:
            autorotate = False
        else:
            rot.z += -rotstep
            rot.z %= 360
    elif symbol == key.D:
        print 'Stop right'
        if autorotate:
            autorotate = False
        else:
            rot.y += rotstep
            rot.y %= 360
    elif symbol == key.LEFT:
        print 'Light0 rotate left'
        tmp = light0pos[0]
        light0pos[0] = tmp * cos( lightstep ) - light0pos[2] * sin( lightstep )
        light0pos[2] = light0pos[2] * cos( lightstep ) + tmp * sin( lightstep )
        glLoadIdentity()
        glLightfv(GL_LIGHT0, GL_POSITION, vec(*light0pos))
    elif symbol == key.RIGHT:
        print 'Light0 rotate right'
        tmp = light0pos[0]
        light0pos[0] = tmp * cos( -lightstep ) - light0pos[2] * sin( -lightstep )
        light0pos[2] = light0pos[2] * cos( -lightstep ) + tmp * sin( -lightstep )
        glLoadIdentity()
        glLightfv(GL_LIGHT0, GL_POSITION, vec(*light0pos))
    elif symbol == key.UP:
        print 'Light0 up'
        tmp = light0pos[1]
        light0pos[1] = tmp * cos( -lightstep ) - light0pos[2] * sin( -lightstep )
        light0pos[2] = light0pos[2] * cos( -lightstep ) + tmp * sin( -lightstep )
        glLoadIdentity()
        glLightfv(GL_LIGHT0, GL_POSITION, vec(*light0pos))
    elif symbol == key.DOWN:
        print 'Light0 down'
        tmp = light0pos[1]
        light0pos[1] = tmp * cos( lightstep ) - light0pos[2] * sin( lightstep )
        light0pos[2] = light0pos[2] * cos( lightstep ) + tmp * sin( lightstep )
        glLoadIdentity()
        glLightfv(GL_LIGHT0, GL_POSITION, vec(*light0pos))
    else:
        print 'OTHER KEY'

def setup():
    # One-time GL setup
    global light0pos
    global light1pos
    global togglewire

    light0pos = [20.0,   20.0, 20.0, 1.0] # positional light !
    light1pos = [-20.0, -20.0, 20.0, 0.0] # infinitely away light !

    glClearColor(1, 1, 1, 1)
    glColor4f(1.0, 0.0, 0.0, 0.5 )
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    # Uncomment this line for a wireframe view
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always
    # include it.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    glLightfv(GL_LIGHT0, GL_POSITION, vec(*light0pos))
    glLightfv(GL_LIGHT0, GL_AMBIENT, vec(0.3, 0.3, 0.3, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(1.0, 1.0, 1.0, 1.0))

    glLightfv(GL_LIGHT1, GL_POSITION, vec(*light1pos))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.6, .6, .6, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1.0, 1.0, 1.0, 1.0))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.8, 0.5, 0.5, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

class Torus(object):
    list = None
    def __init__(self, radius, inner_radius, slices, inner_slices,
                 batch, group=None):
        # Create the vertex and normal arrays.
        vertices = []
        normals = []

        u_step = 2 * pi / (slices - 1)
        v_step = 2 * pi / (inner_slices - 1)
        u = 0.
        for i in range(slices):
            cos_u = cos(u)
            sin_u = sin(u)
            v = 0.
            for j in range(inner_slices):
                cos_v = cos(v)
                sin_v = sin(v)

                d = (radius + inner_radius * cos_v)
                x = d * cos_u
                y = d * sin_u
                z = inner_radius * sin_v

                nx = cos_u * cos_v
                ny = sin_u * cos_v
                nz = sin_v

                vertices.extend([x, y, z])
                normals.extend([nx, ny, nz])
                v += v_step
            u += u_step

        # Create a list of triangle indices.
        indices = []
        for i in range(slices - 1):
            for j in range(inner_slices - 1):
                p = i * inner_slices + j
                indices.extend([p, p + inner_slices, p + inner_slices + 1])
                indices.extend([p, p + inner_slices + 1, p + 1])

        self.vertex_list = batch.add_indexed(len(vertices)//3, 
                                             GL_TRIANGLES,
                                             group,
                                             indices,
                                             ('v3f/static', vertices),
                                             ('n3f/static', normals))
       
    def delete(self):
        self.vertex_list.delete()
        
class Sphere(object):
    vv = []            # vertex vectors
    vcount = 0
    vertices = []
    normals = []
    textureuvw = []
    tangents = []
    indices  = []

    def myindex( self, list, value ):
        for idx, obj in enumerate(list):
            if abs(obj-value) < 0.0001:
              return idx
        raise ValueError # not found

    def splitTriangle(self, i1, i2, i3, new):
        '''
        Interpolates and Normalizes 3 Vectors p1, p2, p3.
        Result is an Array of 4 Triangles
        '''
        p12 = self.vv[i1] + self.vv[i2]
        p23 = self.vv[i2] + self.vv[i3]
        p31 = self.vv[i3] + self.vv[i1]
        p12.normalize()
        try:
            if new[0] == "X":
                ii0 = self.myindex(self.vv, p12)
            else:
                self.vv.append( p12 )
                ii0 = self.vcount
                self.vcount += 1
        except ValueError:
            print "This should not happen 1"
        p23.normalize()
        try:
            if new[1] == "X":
                ii1 = self.myindex(self.vv, p23)
            else:
                self.vv.append( p23 )
                ii1 = self.vcount
                self.vcount += 1
        except ValueError:
            print "This should not happen 2"
        p31.normalize()
        try:
            if new[2] == "X":
                ii2 = self.myindex(self.vv, p31)
            else:
                self.vv.append( p31 )
                ii2 = self.vcount
                self.vcount += 1
        except ValueError:
            print "This should not happen 3"
        rslt = []
        rslt.append([i1,  ii0, ii2])
        rslt.append([ii0, i2,  ii1])
        rslt.append([ii0, ii1, ii2])
        rslt.append([ii2, ii1,  i3])
        return rslt

    def recurseTriangle(self, i1, i2, i3, level, new):
        if level > 0:                     # split in 4 triangles
            p1, p2, p3, p4 = self.splitTriangle( i1, i2, i3, new )
            self.recurseTriangle( *p1, level=level-1, new=new[0]+"N"+new[2] )
            self.recurseTriangle( *p2, level=level-1, new=new[0]+new[1]+"N" )
            self.recurseTriangle( *p3, level=level-1, new="XNX" )
            self.recurseTriangle( *p4, level=level-1, new="X"+new[1]+new[2] )
        else:
           self.indices.extend( [i1, i2, i3] ) # just MAKE the triangle

    def flatten(self, x):
        result = []

        for el in x:
            #if isinstance(el, (list, tuple)):
            if hasattr(el, "__iter__") and not isinstance(el, basestring):
                result.extend(self.flatten(el))
            else:
                result.append(el)
        return result

    def __init__(self, radius, slices, batch, group=None):
        print "Creating Sphere... please wait"
        # Create the vertex array.
        self.vv.append( Vector3( 1.0, 0.0, 0.0) ) # North
        self.vv.append( Vector3(-1.0, 0.0, 0.0) ) # South
        self.vv.append( Vector3( 0.0, 1.0, 0.0) ) # A
        self.vv.append( Vector3( 0.0, 0.0, 1.0) ) # B
        self.vv.append( Vector3( 0.0,-1.0, 0.0) ) # C
        self.vv.append( Vector3( 0.0, 0.0,-1.0) ) # D
        self.vcount = 6

        self.recurseTriangle( 0, 2, 3, slices, "NNN" ) # N=new edge, X=already done
        self.recurseTriangle( 0, 3, 4, slices, "XNN" )
        self.recurseTriangle( 0, 4, 5, slices, "XNN" )
        self.recurseTriangle( 0, 5, 2, slices, "XNX" )
        self.recurseTriangle( 1, 3, 2, slices, "NXN" )
        self.recurseTriangle( 1, 4, 3, slices, "NXX" )
        self.recurseTriangle( 1, 5, 4, slices, "NXX" )
        self.recurseTriangle( 1, 2, 5, slices, "XXX" )

        print "Sphere Level ", slices, " with ", self.vcount, " Vertices"

        for v in range(self.vcount):
            self.normals.extend(self.vv[v][:])
        self.vv = [(x * radius) for x in self.vv]
        self.vertices = [x[:] for x in self.vv]
        self.vertices = self.flatten( self.vertices )

        self.vertex_list = batch.add_indexed(len(self.vertices)//3,
                                             GL_TRIANGLES,
                                             group,
                                             self.indices,
                                             ('v3f/static', self.vertices),
                                             ('n3f/static', self.normals))

    def delete(self):
        self.vertex_list.delete()

rot          = Vector3(0, 0, 90)
autorotate   = True
rotstep      = 10
lightstep    = 10 * pi/180
togglefigure = False
togglewire   = False
showdialog   = True

setup()

batch1  = pyglet.graphics.Batch()
torus = Torus(1, 0.3, 80, 25, batch=batch1)
batch2  = pyglet.graphics.Batch()
sphere = Sphere(1.2, 4, batch=batch2)
pyglet.app.run()

#thats all

"""
