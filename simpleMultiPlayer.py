# -*- coding: utf-8 -*-
import threading
import time
import legume
import pyglet
import sys
import shared
import astar

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



    @w.event
    def on_key_press(s, m):
        if s == pyglet.window.key.ESCAPE:
            client.running = False
            w.close()
        if s == 114: # "r"
            client.force_resync()

    @w.event
    def on_mouse_press(x, y, b, m):
        if b == 4: # right click
            print('Clicked')
            client.lock.acquire()
            #client.spawn_ball(client._client, (x*x_ratio, y*y_ratio))
            client.lock.release()

    @w.event
    def on_show():
        client.force_resync()

    @w.event
    def on_close():
        client.running = False


    playerImg = pyglet.image.load(r'tiles\player.png')
    #bImg = pyglet.image.load(r'tiles\title_denzi_dragon.png')
    batchMap = pyglet.graphics.Batch()
    batchItem = pyglet.graphics.Batch()
    batchClothBG = pyglet.graphics.Batch()
    batchChar = pyglet.graphics.Batch()
    batchClothFG = pyglet.graphics.Batch()
    batchWeapon = pyglet.graphics.Batch()
    batchMagic = pyglet.graphics.Batch()

    posX = W//2
    posY = H//2
    humanImg = SubImg(playerImg,282,875,22,30)
    humanSpr = pyglet.sprite.Sprite(img=humanImg, x=posX, y=posY, batch=batchChar)
    cloakImg = SubImg(playerImg,287,906,20,25)
    cloakSpr = pyglet.sprite.Sprite(img=cloakImg, x=posX, y=posY-3, batch=batchClothBG)
    robeImg = SubImg(playerImg,320,935,16,21)
    robeSpr = pyglet.sprite.Sprite(img=robeImg, x=posX, y=posY-3, batch=batchClothFG)
    staffImg = SubImg(playerImg,169,985,6,29)
    staffSpr = pyglet.sprite.Sprite(img=staffImg, x=posX-9, y=posY+2, batch=batchWeapon)
    """
    main_batch1 = pyglet.graphics.Batch()
    main_batch2 = pyglet.graphics.Batch()
    sprite1 = pyglet.sprite.Sprite(img=aImg, x=0, y=0, batch=main_batch1)
    sprite2 = pyglet.sprite.Sprite(img=bImg, x=30, y=30, batch=main_batch2)
    """

    @w.event
    def on_draw():
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
