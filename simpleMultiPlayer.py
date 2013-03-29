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
import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

# This example uses Python threads to manage async input from sys.stdin.
# This is so that I can receive input from the console whilst running the server.
# Don't ever do this - it's slow and ugly. (I'm doing it for simplicity's sake)


LOCALHOST = 'localhost'
REMOTEHOST = 'jinjuyu.no-ip.org'

VSYNC = False

PORT = 27806


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
        self.lock = threading.Lock()
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.moveCommandOn = False
        self.moveDelay = 30
        self.moveWait = 0
        self.mobClickDelay = 30
        self.mobClickWait = 0
        self.prevTick = time.clock()*1000
        self.tick = 0
        self.clickedMob = None
        self.pX = 0
        self.pY = 0
        self.x = 0
        self.y = 0
        self.running = True
        self.map = None
        self.pl = shared.Player('Player')


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

    def send(self):
        self.lock.acquire()
        #msg = shared.GetMap()
        #msg.none.value = 0
        #self._client.send_reliable_message(msg)
        self.lock.release()


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

con = connection
playerImg = pyglet.image.load(r'tiles\player.png')
floorImg = pyglet.image.load(r'tiles\floor.png')
wallImg = pyglet.image.load(r'tiles\wall.png')
mainImg = pyglet.image.load(r'tiles\main.png')

def DrawQuad(x,y,w,h, color):
    glColor4ub(*color)
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
        ('v2i', (x, shared.H-y,
                x+w, shared.H-y,
                x+w, shared.H-(y+h),
                x, shared.H-(y+h)))
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
        
def DrawText(x,y,text, xalign = 'left', yalign = 'top'):
    label = pyglet.text.Label(text,
                        font_name='Verdana',
                        font_size=10,
                        x=x, y=shared.H-(y),
                        anchor_x=xalign, anchor_y=yalign)
    return label

StatsS = None
class Stats(object):
    def __init__(self):
        global StatsS
        StatsS = self
        self.vis = True
        self.lineHeight = 17
        self.buttonHeight = 16
        self.statsY = 50
        self.nameY = 10
        self.pointY = 30
        self.strBut = Button(shared.W/2-50-80, self.statsY, 70, self.buttonHeight, "Level Up", self.OnStrLevelUp())
        self.dexBut = Button(shared.W/2-50-80, self.statsY+self.lineHeight, 70, self.buttonHeight, "Level Up", self.OnDexLevelUp())
        self.intBut = Button(shared.W/2-50-80, self.statsY+self.lineHeight*2, 70, self.buttonHeight, "Level Up", self.OnIntLevelUp())
        self.strUnBut = Button(shared.W/2-50-80-80, self.statsY, 70, self.buttonHeight, "Refund", self.OnStrRefund())
        self.dexUnBut = Button(shared.W/2-50-80-80, self.statsY+self.lineHeight, 70, self.buttonHeight, "Refund", self.OnDexRefund())
        self.intUnBut = Button(shared.W/2-50-80-80, self.statsY+self.lineHeight*2, 70, self.buttonHeight, "Refund", self.OnIntRefund())
        self.rect = [0, 0, shared.W/2-50, shared.H-150]
        self.nameText = DrawText(10,self.nameY,StateS.pl.name)
        self.pointsText = DrawText(10,self.pointY,"Points: %d" % StateS.pl.points)
        
        self.strText = DrawText(10,self.statsY,"Strength: %d" % StateS.pl.str)
        self.dexText = DrawText(10,self.statsY+self.lineHeight,"Dexterity: %d" % StateS.pl.dex)
        self.intText = DrawText(10,self.statsY+self.lineHeight*2,"Intelligence: %d" % StateS.pl.int)
        """
        """

    def Init(self):
        GUIS.AddGUI('Stats', self)
        GUIS.AddGUI('Stats', self.strBut)
        GUIS.AddGUI('Stats', self.dexBut)
        GUIS.AddGUI('Stats', self.intBut)
        GUIS.AddGUI('Stats', self.strUnBut)
        GUIS.AddGUI('Stats', self.dexUnBut)
        GUIS.AddGUI('Stats', self.intUnBut)
        GUIS.SetVisible("Stats", False)
    def OnStrLevelUp(self):
        pass
    def OnDexLevelUp(self):
        pass
    def OnIntLevelUp(self):
        pass
    def OnStrRefund(self):
        pass
    def OnDexRefund(self):
        pass
    def OnIntRefund(self):
        pass

    def SetVisible(self, vis):
        self.vis = vis
    def Render(self):
        if not self.vis:
            return
        x,y,w,h = self.rect
        DrawQuadWithBorder(x,y,w,h,[42,42,42,255],[255,255,255,255])

        self.nameText.draw()
        self.pointsText.draw()

        self.strText.draw()
        self.dexText.draw()
        self.intText.draw()
        






GUIS = None
class GUI(object):
    def __init__(self):
        global GUIS
        GUIS = self
        self.guiGroups = {}
    def AddGUI(self, group, gui):
        if group not in self.guiGroups:
            self.guiGroups[group] = []
        self.guiGroups[group] += [gui]
    def SetVisible(self, group, vis):
        for gui in self.guiGroups[group]:
            gui.SetVisible(vis)
    def OnLDown(self, x,y):
        for guiGroup in self.guiGroups:
            for gui in self.guiGroups[guiGroup]:
                if hasattr(gui, "OnLDown"):
                    gui.OnLDown(x,y)
    def RenderAll(self):
        for guiGroup in self.guiGroups:
            for gui in self.guiGroups[guiGroup]:
                gui.Render()


class Client(ConnectionListener):
    def __init__(self, host, port):
        self.Connect((host, port))
    
    def Loop(self):
        connection.Pump()
        self.Pump()
    
    def UseSkill(self, idx, skillPlace):
        con.Send({'action': 'useskill', 'idx':idx, 'skillPlace':skillPlace})
    def MoveTo(self, x, y):
        con.Send({'action': 'moveto', 'x': x, 'y': y})
    def MobClicked(self, idx, button):
        con.Send({'action': 'mobclick', 'idx': idx, 'button':button})
    
    #######################################
    ### Network event/message callbacks ###
    #######################################
    def Network_handshake(self, data): # handshake
        if data["msg"] == "ITEMDIGGERS PING %s" % shared.VERSION:
            self.Send({'action': 'handshake', 'msg': "ITEMDIGGERS PONG %s" % shared.VERSION})

    def Network_handshaken(self, data): # hand shaken
        connection.Send({"action": "map"})

    def Network_map(self, data): # map generated
        StateS.map = shared.MapGen(data['w'],data['h'])
        StateS.map.map = data["map"]
        StateS.map.rooms = data["rooms"]
        StateS.map.walls = data["walls"]
        StateS.moveTo(data['x'], data['y'])

    def Network_genmob(self, data): # mob generated
        mob = shared.Mob(MobMgrS, SubImg(*((playerImg,) + data["imgRect"] + data["imgBGRect"])))
        mob.SetPos(data["x"], data["y"])
        mob.idx = data["idx"]

    def Network_movemob(self, data): # mob move to
        for mob in MobMgrS.mobs:
            if mob.idx == data["idx"]:
                mob.SetPos(data["x"], data["y"])

    def Network_moveto(self, data): # char move to
        StateS.moveTo(data['x'], data['y'])
    # built in stuff
    def Network_connected(self, data):
        print "You are now connected to the server"
    
    def Network_error(self, data):
        print 'error:', data['error'][1]
        connection.Close()
    def Network_disconnected(self, data):
        print 'Server disconnected'
        exit()

StateS = None
MobMgrS = None
def main():
    global StateS, MobMgrS


    try:
        # Try and create a window with multisampling (antialiasing)
        config = Config(depth_size=16, double_buffer=True,)
        w = pyglet.window.Window(vsync=VSYNC,config=config) # "vsync=False" to check the framerate
    except pyglet.window.NoSuchConfigException:
        # Fall back to no multisampling for old hardware
        w = pyglet.window.Window(vsync=VSYNC,)


    #w = pyglet.window.Window(vsync=VSYNC)
    w.set_maximum_size(shared.W, shared.H)
    w.set_minimum_size(shared.W, shared.H)
    w.set_size(shared.W,shared.H)
    w.set_location(3,29)
    w.set_caption("ItemDiggers")

    label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=12,
                          x=w.width-100, y=20,
                          anchor_x='center', anchor_y='center')

    state = State()
    StateS = state
    MobMgrS = shared.MobManager()
    gui = GUI()

    def Test():
        print "test"
    #gui.AddGUI("Test", Button(0,0,100,20,"Test", Test))
    stats = Stats()
    stats.Init()


    state.client = Client(REMOTEHOST, shared.PORT)

    def CheckMoveOn():
        if not StatsS.vis:
            state.moveCommandOn = True
        elif StatsS.vis and not InRect(*(StatsS.rect + [state.lastMouseX,state.lastMouseY])):
            state.moveCommandOn = True

    @w.event
    def on_key_release(s, m):
        state.clickedButton = ""
        state.clickedMob = None
        state.moveCommandOn = False
    @w.event
    def on_key_press(s, m):
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


    @w.event
    def on_show():
        pass

    @w.event
    def on_close():
        state.running = False
    

    
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
        state.clickedButton = ""
        state.clickedMob = None
        state.lastMouseX = x
        state.lastMouseY = y
        state.moveCommandOn = False

    @w.event
    def on_mouse_press(x, y, b, m):
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

    state.inited = False
    def on_tick():
        # calc tick
        state.client.Loop()

        if not state.inited:
            if state.map:
                state.inited = True
                # 서버 움직임 완료. 이제 서버 몹 움직임!

                """
                rat = shared.Mob(MobMgrS, SubImg(playerImg, 184, 74, 28, 20))

                randRoom = state.map.rooms[random.randint(0, len(state.map.rooms)-1)]
                randX = random.randint(randRoom[0], randRoom[0]+randRoom[2]-1)
                randY = random.randint(randRoom[1], randRoom[1]+randRoom[3]-1)
                rat.SetPos(randX,randY)
                """

                for y in range(state.map.h):
                    for x in range(state.map.w):
                        if state.map.map[y*state.map.w + x] == 0:
                            state.floorSprs += [[pyglet.sprite.Sprite(img=floorTile, x=(x-0)*shared.tileW+shared.posX, y=(y-0)*shared.tileH+shared.posY, batch=state.batchMap), x,y]]
                for y in range(state.map.h):
                    for x in range(state.map.w):
                        if state.map.walls[y*state.map.w + x] == 1:
                            state.wallSprs += [[pyglet.sprite.Sprite(img=wallTile, x=(x-0)*shared.tileW+shared.posX, y=(y-0)*shared.tileH+shared.posY, batch=state.batchMap), x,y]]

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
        if MobMgrS.waited+tick > MobMgrS.delay:
            MobMgrS.waited = 0
            MobMgrS.Move()
        MobMgrS.waited += tick
        """
        #state.send()

    #XXX
    """
    이제 움직임을 서버에서 하게 한다. - 완료
    그리고 맵에 모든 몹/프ㅜㄹ레이어의 위치를1로 넣은 후 움직일 때 마다 자신의 위치만 0으로 잡고 움직임 완료 후 1을 넣어주면 된다. 완료
    몹은 모두 서버에서 - 완료
    현재 클릭된 몹이 무엇인가를 서버에서 알아야함(클릭된 몹의 id를 서버로 전송) - 완료
    일단 맵젠만 서버에서 해둠 - 완료
    여기서 젠하지 말고 서버에서 다운로드함 - 완료!
    이제 몹을 서버에서 생성/이동 - 완료!
    이제 몹이 이동할 때 겹쳐지지 않게 맵에 1을 넣기! - 완료

    클릭된 몹에 스킬을 사용함 - 완료
    스킬을 만듬
    주인공 스탯이나 스킬을 만듬
    이제 스킬이 서버에 생성되어 있다. 완료
    로그인 시에 가지고 있는 스킬의 정보를 클라로 전송하여 클라에 표시되게 한다.
    스킬포인트를 올리면 스킬의 정보가 변경되므로 재전송 한다.
    주인공의 마나를 만들어서 마나가 있을 시에만 스킬이 사용되도록 한다.
    주인공의 모든 스킬/스탯(마나 체력)정보를 클라로 전송하여 클라에 표시되게 한다.
    모든 스킬/스탯의 정보가 서버에서 변경될 때마다 클라로 전송하여 표시되게 한다.
    그러려면 일단 GUI

    qwert나 마우스 버튼을 눌렀을 때 몹의 위치까지 움직이는데 그러지 말고 스킬 레인지 안에 들어오면 moveto를 보내도 멈추고 스킬을 쓰게 한다. - 완료

    """
    """
    몹을 일정수준 이상 죽이면 슬롯머신 게이지가 차서 슬롯머신을 돌리면 오브나 레어 유닉등이 떨어진다!

    아이템이 없고 몬스터나 포인트로 스탯 및 스킬의 능력치만 올리는 시스템. 스킬도 없고 그냥 공격의 형태만 AOE, 한발용 이렇게 2가지로 하고 직업을 오오라나 힐링 탱킹 버프 등으로 세분화.
    솔플도 가능하도록 한다. 레벨이 없고 포인트만 얻음. 

    그냥 접속만 해두면 시간이 흘러도 점수가 오르게 한다. 아이디어는 좋은데 실용성이 없네 하지만 몬스터를 잡으면 경험치도 주지만 몬스터를 잡은 숫자로 포인트를 주는 건
    할만한 듯 하다. 힐해준 포인트나 버프 걸어주는 포인트 등등 얻어맞은 것도 포인트로
    접속만 해둬도 시간이 흐르면서 점수 오르는 건 동접자를 올리고 싶을 때에나 쓸만한 듯 하다.
    
    여기서 중점은, 기존에 몹을 잡으면 경험치만 줬지만 포인트를 줌으로 인해 같은 액션으로 더 많은 걸 받아간다는 것. 뭘 해도 전보다 이익이 더 크다!



    땅에다가 스킬쓰는 걸 하려면 좀 더 복잡함 그냥 AOE도 타겟온리로 하고... AOE와 원타겟 온리로 하고 오오라를 만들어서 적이 가까이 오면 오오라로 지지도록 한다.

    오오라는 지속스킬이라 캐스팅이 빨라도 소용없고 AOE는 데미지가 약한 편이고 원타겟은 데미지가 세다.
    그냥 드퀘3처럼 평타/마법/AOE 이런식으로 한다.
    속성별 데미지는 복잡하지 않게 포켓몬처럼 수퍼 이펙티브/낫 소 이펙티브/일반 이런식으로 한다.
    스킬의 종류도 그냥 각 속성별 한개씩만 넣는다.
    """

    state.batchMap = pyglet.graphics.Batch()
    state.batchStructure = pyglet.graphics.Batch()

    humanImg = SubImg(playerImg,282,875,22,30)
    humanSpr = pyglet.sprite.Sprite(img=humanImg, x=shared.posX, y=shared.posY)
    cloakImg = SubImg(playerImg,287,906,20,25)
    cloakSpr = pyglet.sprite.Sprite(img=cloakImg, x=shared.posX, y=shared.posY-3)
    robeImg = SubImg(playerImg,320,935,16,21)
    robeSpr = pyglet.sprite.Sprite(img=robeImg, x=shared.posX, y=shared.posY-3)
    staffImg = SubImg(playerImg,169,985,6,29)
    staffSpr = pyglet.sprite.Sprite(img=staffImg, x=shared.posX-9, y=shared.posY+2)

    floorTile = SubImg(floorImg, 288, 96, shared.tileW, shared.tileH)
    wallTile = SubImg(wallImg, 416, 64, shared.tileW, shared.tileH)
    state.floorSprs = []
    state.wallSprs = []


    arial = pyglet.font.load('Arial', 12, bold=True, italic=False)
    fps = pyglet.clock.ClockDisplay(font=arial)
    @w.event
    def on_draw():
        on_tick()
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
        glTranslatef(-float(shared.tileW*state.x), -float(shared.tileH*state.y), 0.0)
        state.batchMap.draw()
        state.batchStructure.draw()
        MobMgrS.Draw()

        # Draw Char
        glLoadIdentity()
        cloakSpr.draw()
        humanSpr.draw()
        robeSpr.draw()
        staffSpr.draw()

        # Draw Magic Effect ETC.
        glTranslatef(-float(shared.tileW*state.x), -float(shared.tileH*state.y), 0.0)

        glLoadIdentity()
        #label.draw()
        fps.draw()
        GUIS.RenderAll()
        """
        if state.ball_positions is not None:
            for x, y in state.ball_positions:
                x /= x_ratio
                y /= y_ratio
                ball_sprite.set_position(x, y)
                ball_sprite.draw()
        """

    #pyglet.clock.schedule_interval(state.showlatency, 0.75)

    # keep pyglet draw running regularly.
    def b(dt): pass
    pyglet.clock.schedule(b)

    #net_thread = threading.Thread(target=state.go)
    #net_thread.start()

    pyglet.app.run()
    state.running = False

if __name__ == '__main__':
    #import logging
    #logging.basicConfig(filename='client.log', level=logging.DEBUG)
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
