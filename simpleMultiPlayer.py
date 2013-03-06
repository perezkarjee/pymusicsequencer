# -*- coding: utf-8 -*-
import threading
import time
import legume
import pyglet
import sys
import shared
import astar
import random

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

W = 1000
H = 700

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
        self.moveDelay = 100
        self.moveWait = 0
        self.prevTick = time.clock()*1000

def main():
    if "--remote" in sys.argv:
        host = REMOTEHOST
    else:
        host = LOCALHOST
    print('Using host: %s' % host)

    client = BallClient()
    client.connect(host)


    w = pyglet.window.Window(vsync=VSYNC)
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

    @w.event
    def on_key_press(s, m):
        if s == pyglet.window.key.W:
            client.move(0,1)
        if s == pyglet.window.key.S:
            client.move(0,-1)
        if s == pyglet.window.key.A:
            client.move(-1,0)
        if s == pyglet.window.key.D:
            client.move(1,0)
        if s == pyglet.window.key.ESCAPE:
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
    
    mapW = 128
    mapH = 128
    map = shared.MapGen(mapW,mapH)
    map.Gen()
    posX = W//2
    posY = H//2
    tileW = 32
    tileH = 32

    
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
        if b == pyglet.window.mouse.RIGHT:
            state.rButtonDown = False

    @w.event
    def on_mouse_press(x, y, b, m):
        state.lastMouseX = x
        state.lastMouseY = y
        if b == pyglet.window.mouse.RIGHT:
            state.rButtonDown = True
            client.lock.acquire()
            #client.spawn_ball(client._client, (x*x_ratio, y*y_ratio))
            client.lock.release()
        if b == pyglet.window.mouse.MIDDLE:
            print 'MClicked %d, %d' % (x,y)
        if b == pyglet.window.mouse.LEFT:
            print 'LClicked %d, %d' % (x,y)

    def on_tick():
        curTick = int(time.clock()*1000)
        tick = curTick-state.prevTick
        state.prevTick = curTick
        x, y = state.lastMouseX, state.lastMouseY

        if state.rButtonDown and ( (state.moveWait+tick) > state.moveDelay):
            state.moveWait -= state.moveDelay
            prevTime = time.clock()
            def TimeFunc():
                curTime = time.clock()
                return (curTime-prevTime)*1000
            finder = astar.AStarFinder(map.map, mapW, mapH, client.x, client.y, client.x+(x-posX)//tileW, client.y+(y-posY)//tileH, TimeFunc)
            found = finder.Find()
            if found and len(found) >= 2:
                cX, cY = found[1][0], found[1][1]
                client.moveTo(cX, cY)
        state.moveWait += tick

    """
    이제 움직임을 서버에서 하게 한다.
    """

    playerImg = pyglet.image.load(r'tiles\player.png')
    floorImg = pyglet.image.load(r'tiles\floor.png')
    #bImg = pyglet.image.load(r'tiles\title_denzi_dragon.png')
    batchMap = pyglet.graphics.Batch()
    batchItem = pyglet.graphics.Batch()
    batchClothBG = pyglet.graphics.Batch()
    batchChar = pyglet.graphics.Batch()
    batchClothFG = pyglet.graphics.Batch()
    batchWeapon = pyglet.graphics.Batch()
    batchMagic = pyglet.graphics.Batch()

    humanImg = SubImg(playerImg,282,875,22,30)
    humanSpr = pyglet.sprite.Sprite(img=humanImg, x=posX, y=posY, batch=batchChar)
    cloakImg = SubImg(playerImg,287,906,20,25)
    cloakSpr = pyglet.sprite.Sprite(img=cloakImg, x=posX, y=posY-3, batch=batchClothBG)
    robeImg = SubImg(playerImg,320,935,16,21)
    robeSpr = pyglet.sprite.Sprite(img=robeImg, x=posX, y=posY-3, batch=batchClothFG)
    staffImg = SubImg(playerImg,169,985,6,29)
    staffSpr = pyglet.sprite.Sprite(img=staffImg, x=posX-9, y=posY+2, batch=batchWeapon)

    floorImg = SubImg(floorImg, 288, 96, tileW, tileH)
    floorSprs = []

    randRoom = map.rooms[random.randint(0, len(map.rooms)-1)]
    randX = random.randint(randRoom[0], randRoom[0]+randRoom[2]-1)
    randY = random.randint(randRoom[1], randRoom[1]+randRoom[3]-1)
    client.pX = client.x = randX
    client.pY = client.y = randY
    for y in range(mapH):
        for x in range(mapW):
            if map.map[y*map.w + x] == 0:
                floorSprs += [[pyglet.sprite.Sprite(img=floorImg, x=(x-randX)*tileW+posX, y=(y-randY)*tileH+posY, batch=batchMap), x,y]]
    """
    main_batch1 = pyglet.graphics.Batch()
    main_batch2 = pyglet.graphics.Batch()
    sprite1 = pyglet.sprite.Sprite(img=aImg, x=0, y=0, batch=main_batch1)
    sprite2 = pyglet.sprite.Sprite(img=bImg, x=30, y=30, batch=main_batch2)
    """

    @w.event
    def on_draw():
        on_tick()
        if client.pX != client.x or client.pY != client.y:
            client.pX = client.x
            client.pY = client.y
            for sprPos in floorSprs:
                spr, x, y = sprPos
                spr.set_position((x-client.x)*tileW+posX, (y-client.y)*tileH+posY)

        w.clear()
        label.draw()
        batchMap.draw()
        batchItem.draw()
        batchClothBG.draw()
        batchChar.draw()
        batchClothFG.draw()
        batchWeapon.draw()
        batchMagic.draw()
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
그래픽이 노가다가 쩔 것 같다.
던크 타일이 좋긴 좋은데 32x32로 딱 나뉜 게 아니다. 수동으로 나중에 다 해줘야 함.
하나씩 하나씩 필요한 거 골라서 하면 된다.
"""
