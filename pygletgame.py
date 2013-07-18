# -*- coding: utf-8 -*-
import threading
import time
import pyglet
import sys
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

        y = H-y
        if InRect(*(self.rect+[x,y])):
            self.func()
    def Render(self):
        if not self.visible:
            return
        x,y,w,h = self.rect
        DrawQuadWithBorder(x,y,w,h,[42,42,42,255],[255,255,255,255])
        self.label.draw()

class ZoneButton(Button):
    def __init__(self, x,y,w,h, label, ident):
        Button.__init__(self, x,y,w,h, label, self.Move)
        self.ident = ident
        self.label = DrawText(x+w/2, y+h/2, label, 'center', 'center', color=(0,46,116,255))

    def Move(self):
        GameWSt.MoveRoom(self.ident)
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
    home.people += [Stash(u"창고", u"창고", u"인벤토리")]


    town = Room("town", u"마을", u"""\
당신이 살고있는 마을이다.
매우 작고 간소한 마을이지만 갖출 건 다 갖추었다.

하지만 당신의 집은 그 중에서도 가장 구석진 곳에 떨어진 가장 허름한 집이다.
""", True)
    town.people += [WeaponShop(u"무기상인", u"무기 상점", u"인벤토리")]
    town.people += [ItemShop(u"잡화상인", u"잡화 상점", u"인벤토리")]
    town.people += [MapShop(u"던젼맵상인", u"던젼 맵 상점", u"인벤토리")]

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
                        x=x, y=H-(y),
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

        self.left = False
        self.idx = -1

    def OnLDown(self, x,y):
        if not self.visible:
            return

        y = H-y
        if InRect(*(self.rect+[x,y])):
            self.func()


        if not self.menuVisible:
            return
        
        w = W-GameWSt.sideMenuW+10
        if InRect(w-30,0,25,25,x,y):
            self.OffMenu()



        # left part of shop
        self.left = False
        self.idx = -1
        idx = 0
        for yy in range(13):
            for xx in range(10):
                if InRect(GameWSt.leftX+xx*(GameWSt.itemW-5), GameWSt.invY+yy*(GameWSt.itemH-5), GameWSt.itemW, GameWSt.itemH, x, y):
                    self.left = True
                    self.idx = idx
                idx += 1

        # right part of sho
        idx = 0
        for yy in range(13):
            for xx in range(10):
                if InRect(GameWSt.invX+xx*(GameWSt.itemW-5), GameWSt.invY+yy*(GameWSt.itemH-5), GameWSt.itemW, GameWSt.itemH, x, y):
                    self.left = False
                    self.idx = idx
                idx += 1




    def OffMenu(self):
        if GameWSt.draggingIdx != -1:
            GameWSt.draggingItem.isDragging = False
            GameWSt.draggingContainer[GameWSt.draggingIdx] = GameWSt.draggingItem

            idx = targetIdx = GameWSt.draggingIdx
            targetC = GameWSt.draggingContainer
            if targetC == GameWSt.inventory:
                idx2 = 0
                found = False
                for yy in range(13):
                    for xx in range(10):
                        if idx == idx2:
                            targetC[targetIdx].SetPos(GameWSt.invX+xx*(GameWSt.itemW-5), GameWSt.invY+yy*(GameWSt.itemH-5))
                            found = True
                            break
                        idx2 += 1
                    if found:
                        break
            else:
                idx2 = 0
                found = False
                for yy in range(13):
                    for xx in range(10):
                        if idx == idx2:
                            targetC[targetIdx].SetPos(GameWSt.leftX+xx*(GameWSt.itemW-5), GameWSt.invY+yy*(GameWSt.itemH-5))
                            found = True
                            break
                        idx2 += 1
                    if found:
                        break

            GameWSt.draggingContainer = None
            GameWSt.draggingIdx = -1
            GameWSt.draggingItem = None
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

    def OnDragStart(self, container, idx):
        itemToDrag = container[idx]
        if itemToDrag.isEmpty:
            return

        if container == GameWSt.inventory:
            idx2 = 0
            found = False
            for yy in range(13):
                for xx in range(10):
                    if idx == idx2:
                        container[idx] = GameWSt.NewEmptyItem(GameWSt.invX+xx*(GameWSt.itemW-5), GameWSt.invY+yy*(GameWSt.itemH-5))
                        found = True
                        break
                    idx2 += 1
                if found:
                    break
        else:
            idx2 = 0
            found = False
            for yy in range(13):
                for xx in range(10):
                    if idx == idx2:
                        container[idx] = GameWSt.NewEmptyItem(GameWSt.leftX+xx*(GameWSt.itemW-5), GameWSt.invY+yy*(GameWSt.itemH-5))
                        found = True
                        break
                    idx2 += 1
                if found:
                    break

        GameWSt.draggingItem = itemToDrag
        GameWSt.draggingItem.isDragging = True
        GameWSt.draggingIdx = idx
        GameWSt.draggingContainer = container

    def OnDrop(self, targetC, targetIdx, sourceC, sourceIdx, draggingItem):
        toDrag = targetC[targetIdx]

        idx = targetIdx
        if targetC == GameWSt.inventory:
            # buy if has enough point else place draggingitem into original source
            if self.buySell and not GameWSt.BuyItem(draggingItem):
                GameWSt.draggingItem.isDragging = False
                GameWSt.draggingContainer[GameWSt.draggingIdx] = GameWSt.draggingItem

                idx = targetIdx = GameWSt.draggingIdx
                targetC = GameWSt.draggingContainer
                idx2 = 0
                found = False
                for yy in range(13):
                    for xx in range(10):
                        if idx == idx2:
                            targetC[targetIdx].SetPos(GameWSt.leftX+xx*(GameWSt.itemW-5), GameWSt.invY+yy*(GameWSt.itemH-5))
                            found = True
                            break
                        idx2 += 1
                    if found:
                        break

                GameWSt.draggingContainer = None
                GameWSt.draggingIdx = -1
                GameWSt.draggingItem = None
                return

            targetC[targetIdx] = draggingItem
            targetC[targetIdx].isDragging = False
            idx2 = 0
            found = False
            for yy in range(13):
                for xx in range(10):
                    if idx == idx2:
                        targetC[targetIdx].SetPos(GameWSt.invX+xx*(GameWSt.itemW-5), GameWSt.invY+yy*(GameWSt.itemH-5))
                        found = True
                        break
                    idx2 += 1
                if found:
                    break
        else:
            # sell right now and don't pick it up again
            if not self.buySell:
                targetC[targetIdx] = draggingItem
                targetC[targetIdx].isDragging = False
                idx2 = 0
                found = False
                for yy in range(13):
                    for xx in range(10):
                        if idx == idx2:
                            targetC[targetIdx].SetPos(GameWSt.leftX+xx*(GameWSt.itemW-5), GameWSt.invY+yy*(GameWSt.itemH-5))
                            found = True
                            break
                        idx2 += 1
                    if found:
                        break
            else:
                GameWSt.SellItem(draggingItem)




        if toDrag.isEmpty or self.buySell: # don't pick it up again if buySell
            GameWSt.draggingIdx = -1
            GameWSt.draggingContainer = None
            GameWSt.draggingItem = None
        else:
            GameWSt.draggingItem = toDrag
            GameWSt.draggingItem.isDragging = True
    def OnItemClick(self, container, idx):
        if GameWSt.draggingIdx == -1:
            self.OnDragStart(container, idx)
        else:
            self.OnDrop(container, idx, GameWSt.draggingContainer, GameWSt.draggingIdx, GameWSt.draggingItem)

        if GameWSt.draggingItem:
            x, y = GameWSt.lastMouseDown['l']
            GameWSt.draggingItem.SetPos(x-GameWSt.itemW/2,H-(y+GameWSt.itemH/2))

    def OnLDown2(self,x,y):
        if not self.menuVisible or not self.visible:
            return
        idx = self.idx
        if self.left and self.idx != -1:
            self.OnItemClick(self.container, idx)
        if not self.left and self.idx != -1:
            self.OnItemClick(GameWSt.inventory, idx)



class ItemShop(Shop):
    def __init__(self, name, leftname, rightname, x=0,y=0): # x,y는 bottomMenu의 텍스트 버튼 위치
        Shop.__init__(self, name, leftname, rightname, 0,0)
        self.container = GameWSt.itemShop
        self.buySell = True

    def OnLDown(self, x,y):
        Shop.OnLDown(self,x,y)
        Shop.OnLDown2(self,x,y)

    def Render(self):
        Shop.Render(self)

        if not self.menuVisible:
            return
        for item in GameWSt.itemShop:
            item.Render()

class MapShop(Shop):
    def __init__(self, name, leftname, rightname, x=0,y=0): # x,y는 bottomMenu의 텍스트 버튼 위치
        Shop.__init__(self, name, leftname, rightname, 0,0)
        self.container = GameWSt.mapShop
        self.buySell = True

    def OnLDown(self, x,y):
        Shop.OnLDown(self,x,y)
        Shop.OnLDown2(self,x,y)

    def Render(self):
        Shop.Render(self)

        if not self.menuVisible:
            return
        for item in GameWSt.mapShop:
            item.Render()

class WeaponShop(Shop):
    def __init__(self, name, leftname, rightname, x=0,y=0): # x,y는 bottomMenu의 텍스트 버튼 위치
        Shop.__init__(self, name, leftname, rightname, 0,0)
        self.container = GameWSt.weaponShop
        self.buySell = True

    def OnLDown(self, x,y):
        Shop.OnLDown(self,x,y)
        Shop.OnLDown2(self,x,y)

    def Render(self):
        Shop.Render(self)

        if not self.menuVisible:
            return
        for item in GameWSt.weaponShop:
            item.Render()

class Stash(Shop):
    def __init__(self, name, leftname, rightname, x=0,y=0): # x,y는 bottomMenu의 텍스트 버튼 위치
        Shop.__init__(self, name, leftname, rightname, 0,0)
        self.container = GameWSt.stash
        self.buySell = False

    def OnLDown(self, x,y):
        Shop.OnLDown(self,x,y)
        Shop.OnLDown2(self,x,y)

    def Render(self):
        Shop.Render(self)

        if not self.menuVisible:
            return
        for item in GameWSt.stash:
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
    def __init__(self, shortTitle, title, desc, cost, delay):
        self.txt = shortTitle
        self.title = title
        self.desc = desc
        self.descOrg = desc
        self.point = 0
        self.cost = cost
        self.wait = 99999999999
        self.delay = delay

    def SetDesc(self):
        self.SetFooter()
        self.desc = self.descOrg + u"\n\n" + self.footer
    def OnTick(self, tick):
        self.wait += tick
        if self.wait > self.delay:
            self.wait = self.delay+10
    def Use(self, target1, target2, targets):
        self.wait = 0
        if IsJong(self.title[-1]):
            jong = u"을"
        else:
            jong = u"를"
        GameWSt.DoMsg(u"%s%s 사용했습니다." % (self.title, jong))

    def OnLDown(self):
        pass
    def IsReady(self):
        if self.wait > self.delay:
            return True
        else:
            return False
    def CalcManaCost(self):
        return 0
    def GetDesc(self):
        return self.desc
    def NotReady(self):
        GameWSt.DoMsg(u"아직 준비가 되지 않았습니다.")
    def NotEnoughMana(self):
        GameWSt.DoMsg(u"마나가 부족합니다.")
    def NoTarget(self):
        GameWSt.DoMsg(u"현재 전투중이 아닙니다.")


class HealPotion(Skill):
    def __init__(self):
        Skill.__init__(self, u"힐포", u"힐링 포션", u"마시면 체력을 완전히 회복한다.", 0, 0)
        self.SetDesc()
    def SetFooter(self):
        self.footer = u"현재 포인트: %d\n쿨타임: %.2f초" % (self.point, self.delay/1000.0)

    def Use(self, target1, target2, targets):
        Skill.Use(self,target1,target2,targets)
        healAmountNeeded = target1.CalcMaxHP()-target1.curHP
        target1.SetHPPo(target1.curHPPo - healAmountNeeded)
        if target1.curHPPo < 0:
            healAmountNeeded += target1.curHPPo
            target1.SetHPPo(0)
        target1.SetHP(target1.curHP + healAmountNeeded)

    def OnLDown(self):
        if self.IsReady() and GameWSt.char.curHP < GameWSt.char.CalcMaxHP():
            self.Use(GameWSt.char, None, [])
        elif not self.IsReady():
            self.NotReady()
        elif GameWSt.char.curHP == GameWSt.char.CalcMaxHP():
            GameWSt.DoMsg(u"체력이 이미 꽉 찼습니다.")
    def AddPoint(self, amt):
        self.point += amt
        self.SetDesc()

class ManaPotion(Skill):
    def __init__(self):
        Skill.__init__(self, u"마포", u"마나 포션", u"마시면 마력을 완전히 회복한다.", 0, 0)
        self.SetDesc()

    def SetFooter(self):
        self.footer = u"현재 포인트: %d\n쿨타임: %.2f초" % (self.point, self.delay/1000.0)

    def Use(self, target1, target2, targets):
        Skill.Use(self,target1,target2,targets)
        healAmountNeeded = target1.CalcMaxMP()-target1.curMP
        target1.SetMPPo(target1.curMPPo - healAmountNeeded)
        if target1.curMPPo < 0:
            healAmountNeeded += target1.curMPPo
            target1.SetMPPo(0)
        target1.SetMP(target1.curMP + healAmountNeeded)
    def AddPoint(self, amt):
        self.point += amt
        self.SetDesc()

    def OnLDown(self):
        if self.IsReady() and GameWSt.char.curMP < GameWSt.char.CalcMaxMP():
            self.Use(GameWSt.char, None, [])
        elif not self.IsReady():
            self.NotReady()
        elif GameWSt.char.curMP == GameWSt.char.CalcMaxMP():
            GameWSt.DoMsg(u"마나가 이미 꽉 찼습니다.")

class Stun(Skill):
    def __init__(self, player):
        # XXX: 스턴은 20초 이상은 기절시키지 못하도록 포인트를 넣을 수 있는 것에 제한을 둔다.
        Skill.__init__(self, u"기절", u"기절시키기", u"현재 공격중인 적 하나를 기절시킨다.", 50, 30000)
        self.player = player
        self.SetDesc()

    def SetFooter(self):
        self.footer = u"현재 포인트: %d\n지속시간: %.3f초\n마나사용: %d\n쿨타임: %.2f초" % (self.point, self.CalcDmg()/1000.0, self.CalcManaCost(), self.delay/1000.0)

    def AddPoint(self, amt):
        self.point += amt
        self.SetDesc()
    def CalcManaCost(self):
        return 100
    def CalcDmg(self):
        dur = 1000+(self.point)*1
        if dur > 5000:
            dur = 5000+((self.point)/10.0)
        if dur > 10000:
            dur = 10000+((self.point)/30.0)
        if dur > 20000:
            dur = 20000
        return dur
    def Use(self, target1, target2, targets):
        Skill.Use(self,target1,target2,targets)
        if self.player.curMP >= self.CalcManaCost():
            self.player.SetMP(self.player.curMP-self.CalcManaCost())
            target2.Stun(self.CalcDmg())
        else:
            self.NotEnoughMana()

    def OnLDown(self):
        if self.IsReady() and GameWSt.curTarget:
            self.Use(GameWSt.char, GameWSt.curTarget, GameWSt.mobs)
        elif not self.IsReady():
            self.NotReady()
        elif self.IsReady() and not GameWSt.curTarget:
            self.NoTarget()

class SuperAttack(Skill):
    def __init__(self, player):
        Skill.__init__(self, u"후려", u"후려치기", u"현재 공격중인 적 하나를 후려친다.", 5, 500)
        self.player = player
        self.SetDesc()

    def SetFooter(self):
        self.footer = u"현재 포인트: %d\n공격력: %d\n마나사용: %d\n쿨타임: %.2f초" % (self.point, self.CalcDmg(), self.CalcManaCost(), self.delay/1000.0)

    def AddPoint(self, amt):
        self.point += amt
        self.SetDesc()
    def CalcManaCost(self):
        return self.cost * (self.point+1)
    def CalcDmg(self):
        return int(self.player.CalcAtk()*1.3*(self.point+1))
    def Use(self, target1, target2, targets):
        Skill.Use(self,target1,target2,targets)
        if self.player.curMP >= self.CalcManaCost():
            self.player.SetMP(self.player.curMP-self.CalcManaCost())
            target2.TakeDmg(self.CalcDmg())
        else:
            self.NotEnoughMana()

    def OnLDown(self):
        if self.IsReady() and GameWSt.curTarget:
            self.Use(GameWSt.char, GameWSt.curTarget, GameWSt.mobs)
        elif not self.IsReady():
            self.NotReady()
        elif self.IsReady() and not GameWSt.curTarget:
            self.NoTarget()

class BetterSuperAttack(SuperAttack):
    def __init__(self, player):
        SuperAttack.__init__(self, player)
        self.txt = u"힘차"
        self.title = u"힘차게 후려치기"
        self.descOrg = u"현재 공격중인 적 하나를 힘차게 후려친다."
        self.cost = 10
        self.delay = 500

        self.SetDesc()
    def CalcManaCost(self):
        return self.cost * (self.point+1)
    def CalcDmg(self):
        return int(self.player.CalcAtk()*2.3*(self.point+1))
    def SetFooter(self):
        self.footer = u"현재 포인트: %d\n공격력: %d\n마나사용: %d\n쿨타임: %.2f초" % (self.point, self.CalcDmg(), self.CalcManaCost(), self.delay/1000.0)

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
        self.isDragging = False

    def SetPos(self, x, y):
        self.x = x
        self.y = y#H-y-self.h
        self.label.x = x+self.w/2
        self.label.y = H-(y+self.h/2)
    def Render(self):
        if not self.isDragging:
            DrawQuad(self.x+5, self.y+5, self.w-10, self.h-10, (144, 244, 229, 255))
        else:
            DrawQuadWithBorder(self.x+5, self.y+5, self.w-10, self.h-10, (144, 244, 229, 255), (0,0,0,255), 1)
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


class PopupWindowClass(object):
    def __init__(self, title, desc, x,y, ident):
        self.x = x
        self.y = y
        self.w = 200
        self.h = 300
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
        self.text.font_size = 10

        self.ident = ident

    def Render(self):
        DrawQuadWithBorder(self.x, self.y, self.w, self.h, (200, 200, 200, 230), (30,30,30,150), 0) # zone menu
        self.text.draw()
G_popupWindow = PopupWindowClass(u"", u"", 0, 0, None)
def PopupWindow(title, desc, x, y, ident):
    global G_popupWindow
    G_popupWindow.x = x
    G_popupWindow.y = y
    header = u"""<font color="black" face="Dotum" size="2">%s<br/><br/><b>""" % title
    footer = u"""</b></font>"""
    texts = desc.split("\n")
    text = '<br/>'.join(texts)
    G_popupWindow.desc = header + text + footer
    G_popupWindow.ident = ident
    G_popupWindow.text.text = G_popupWindow.desc
    G_popupWindow.text.x = x+G_popupWindow.margin
    G_popupWindow.text.y = H-(y+G_popupWindow.margin+13)
    return G_popupWindow


class Element(object): # 아이템의 속성
    # 아이템 레벨이 오르면 자동으로 값이 올라가게 하려면?
    # min max 사이의 값이 랜덤하게 아이템에 붙는 거니까
    # min max값을 레벨에 따라 올라가게 만든 후에
    # 그 올라간 값을 아이템에 붙인다.
    # min*minMod*level
    # max*maxMod*level이 최종 min max값이 된다.
    #
    # 4 4 3 = 48
    # 8 10 3 = 240
    # 이러면 48~240사이의 값이 아이템에 붙는다.
    ATK = "atk"
    DFN = "dfn"
    MAXHP = "maxhp"
    MAXMP = "maxmp"
    HPPOTION = "hppotion"
    MPPOTION = "mppotion"
    POWATKLVL = "powerattacklvl"

    def __init__(self, name, min, max, minMod, maxMod, level):
        self.name = name # ATK, DFN, etc
        self.min = min
        self.max = max
        self.level = level
        self.minMod = minMod
        self.maxMod = maxMod

def GetElements():
    ele = {}
    return ele

class Character(object):
    def __init__(self):
        self.totalPoint = 0

        self.hpPoint = 0
        self.mpPoint = 0
        self.hp = 5
        self.mp = 5
        self.curHP = 1#self.CalcMaxHP()
        self.curMP = 1#self.CalcMaxMP()

        self.atkPoint = 0
        self.dfnPoint = 0
        self.atk = 3
        self.dfn = 2

        self.hppotionPoint = 0
        self.hppotion = 20
        self.curHPPo = self.CalcHPPotion()
        self.mppotionPoint = 0
        self.mppotion = 20
        self.curMPPo = self.CalcMPPotion()

        self.texts = []
        y = 0
        self.txtPoint = DrawText(W-GameWSt.sideMenuW+10, GameWSt.posMenuH+10 + y, u"포인트: %d" % (self.totalPoint,), 'left', 'top')
        self.texts += [self.txtPoint]
        y += 20
        self.txtHP = DrawText(W-GameWSt.sideMenuW+10, GameWSt.posMenuH+10 + y, u"체력: %d/%d" % (self.curHP, self.CalcMaxHP()), 'left', 'top')
        self.texts += [self.txtHP]
        y += 20
        self.txtMP = DrawText(W-GameWSt.sideMenuW+10, GameWSt.posMenuH+10 + y, u"마력: %d/%d" % (self.curMP, self.CalcMaxMP()), 'left', 'top')
        self.texts += [self.txtMP]
        y += 20
        self.txtHPPo = DrawText(W-GameWSt.sideMenuW+10, GameWSt.posMenuH+10 + y, u"체력포션: %d/%d" % (self.curHPPo, self.CalcHPPotion()), 'left', 'top')
        self.texts += [self.txtHPPo]
        y += 20
        self.txtMPPo = DrawText(W-GameWSt.sideMenuW+10, GameWSt.posMenuH+10 + y, u"마력포션: %d/%d" % (self.curMPPo, self.CalcMPPotion()), 'left', 'top')
        self.texts += [self.txtMPPo]
        y += 20
        self.txtAtk = DrawText(W-GameWSt.sideMenuW+10, GameWSt.posMenuH+10 + y, u"공격력: %d" % (self.CalcAtk()), 'left', 'top')
        self.texts += [self.txtAtk]
        y += 20
        self.txtDfn = DrawText(W-GameWSt.sideMenuW+10, GameWSt.posMenuH+10 + y, u"방어력: %d" % (self.CalcDfn()), 'left', 'top')
        self.texts += [self.txtDfn]


        self.stunned = False
        self.stunWait = 0
        self.stunDur = 0






    def CalcMaxHP(self):
        return ((self.hpPoint/2)+1) * self.hp
    def CalcMaxMP(self):
        return ((self.mpPoint/2)+1) * self.mp
    def CalcHPPotion(self):
        return ((self.hppotionPoint/2)+1) * self.hppotion
    def CalcMPPotion(self):
        return ((self.mppotionPoint/2)+1) * self.mppotion
    def CalcAtk(self):
        return ((self.atkPoint/2)+1) * self.atk
    def CalcDfn(self):
        return ((self.dfnPoint/2)+1) * self.dfn

    def Stun(self, dur):
        self.stunned = True
        self.stunWait = 0
        self.stunDur = dur
        pass

    def SetHPPo(self, hp):
        self.curHPPo = hp
        self.txtHPPo.text = u"체력포션: %d/%d" % (self.curHPPo, self.CalcHPPotion())

    def SetMPPo(self, mp):
        self.curMPPo = mp
        self.txtMPPo.text = u"마력포션: %d/%d" % (self.curMPPo, self.CalcMPPotion())
    def SetHP(self, hp):
        self.curHP = hp
        self.txtHP.text = u"체력: %d/%d" % (self.curHP, self.CalcMaxHP())

    def SetMP(self, mp):
        self.curMP = mp
        self.txtMP.text = u"마력: %d/%d" % (self.curMP, self.CalcMaxMP())

    def TakeDmg(self, dmg):
        dmg -= self.CalcDfn()
        if dmg < 1:
            dmg = 1
        self.SetHP(self.curHP - dmg)
        if self.curHP <= 0:
            self.SetHP(0)
            self.Die()

    def Die(self):
        pass

    def Tick(self, tick):
        self.stunWait += tick

    def Render(self):
        for text in self.texts:
            text.draw()

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
        newItem2 = Item(u"단도2", u"단도2", u"짧고 날카로운 칼이다.", self.leftX+idxX*(self.itemW-5), self.invY+idxY*(self.itemH-5))




        self.inventory = []
        self.itemShop = []
        self.mapShop = []
        self.weaponShop = []
        self.stash = []
        for yy in range(13):
            for xx in range(10):
                #self.inventory += [self.NewEmptyItem(self.invX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5))]
                self.inventory += [Item(u"단도", u"단도", u"짧고 날카로운 칼이다.", self.invX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5))]
        self.inventory[idx] = newItem

        for yy in range(13):
            for xx in range(10):
                self.itemShop += [self.NewEmptyItem(self.leftX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5))]

        for yy in range(13):
            for xx in range(10):
                self.weaponShop += [self.NewEmptyItem(self.leftX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5))]
        self.weaponShop[idx] = newItem2

        for yy in range(13):
            for xx in range(10):
                #self.stash += [self.NewEmptyItem(self.leftX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5))]
                self.stash += [Item(u"단도", u"단도", u"짧고 날카로운 칼이다.", self.leftX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5))]

        for yy in range(13):
            for xx in range(10):
                self.mapShop += [self.NewEmptyItem(self.leftX+xx*(self.itemW-5), self.invY+yy*(self.itemH-5))]
        self.draggingItem = None
        self.draggingIdx = -1
        self.draggingContainer = None



        self.rooms = GetRooms()
        self.dungeons = {}

        self.output = OutputWindow(10, 22+H-self.bottomMenuH-self.midMenuH-self.qSlotH+5, W-self.sideMenuW-20, self.midMenuH-10)
        self.DoSysOutput(u"TextAdventure에 오신 것을 환영합ㅂㅂㅂ")
        self.DoSysOutput(u"이 게임은 만들다 말았음zz")

        self.SetRoom("home")

        self.qSlot = [
                QuickSlot(0, HealPotion()),
                QuickSlot(1, ManaPotion()),
                QuickSlot(2, SuperAttack(self.char)),
                QuickSlot(3, BetterSuperAttack(self.char)),
                QuickSlot(4, Stun(self.char)),
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



        arial = pyglet.font.load('Arial', 12, bold=True, italic=False)
        self.fps = pyglet.clock.ClockDisplay(font=arial)

        self.draw = False

    def BuyItem(self, item):
        self.DoMsg(u"아이템을 샀습니다.")
        return True
    def SellItem(self, item):
        pass
    def NewEmptyItem(self, x, y):
        return Item(u"없음", u"없음", u"빈 아이템", x,y, isEmpty=True)
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
            self.zoneButtons += [ZoneButton(W-self.sideMenuW+10, y+10, self.sideMenuW-20, 30, room.title, room.ident)]
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

            clickedMobX = state.x+(x-posX+tileW/2)//tileW
            clickedMobY = state.y+(y-posY+tileH/2)//tileH
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
        self.draw = not self.draw
        if self.draw:
            return
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(self.bgColor[0]/255.0, self.bgColor[1]/255.0, self.bgColor[2]/255.0, 1.0)
        glLoadIdentity()
        self.clear()
        DrawQuadWithBorder(W-self.sideMenuW, 0, self.sideMenuW, self.posMenuH, (0, 78, 196, 255), self.bgColor, 5) # zone menu
        DrawQuadWithBorder(W-self.sideMenuW, self.posMenuH-5, self.sideMenuW, H-self.posMenuH+5, (153, 210, 0, 255), self.bgColor, 5) # char menu
        DrawQuadWithBorder(0, H-self.bottomMenuH, W-self.sideMenuW+5, self.bottomMenuH, (196, 0, 78, 255), self.bgColor, 5) # mobs, npc, interactive object menu
        DrawQuadWithBorder(0, H-self.bottomMenuH-self.midMenuH-(self.qSlotH-5), W-self.sideMenuW+5, self.midMenuH+5, (227, 155, 0, 255), self.bgColor, 5)

        x = 0
        for i in range(20):
            DrawQuadWithBorder(x, H-self.bottomMenuH-self.qSlotH+5, self.qSlotH+4, self.qSlotH, (196, 166, 0, 255), self.bgColor, 5)
            x += self.qSlotH-5+4
        self.char.Render()

        self.output.Render()

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
        if self.draggingItem:
            self.draggingItem.Render()


        glTranslatef(0, 0, 0.0)
        self.fps.draw()



    def on_show(self):
        pass
    def on_close(self):
        self.Exit()
    def Exit(self):
        print 'Good Bye !'
        pyglet.app.exit()
    def on_mouse_motion(self, x, y, b, m):
        if self.draggingIdx == -1:
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
            if isinstance(self.menu, MapShop):
                container = self.mapShop
            if isinstance(self.menu, ItemShop):
                container = self.itemShop
            if isinstance(self.menu, Stash):
                container = self.stash

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

        if self.draggingIdx != -1:
            self.popupWindow = None
            self.draggingItem.SetPos(x-self.itemW/2,H-(y+self.itemH/2))

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
            self.lastMouseDown["l"] = [x,y]
            for button in self.zoneButtons:
                button.OnLDown(x,y)
            for button in self.npcs:
                button.OnLDown(x,y)
            for slot in self.qSlot:
                slot.OnLDown(x,y)

        if b == mouse.MIDDLE:
            self.lastMouseDown["m"] = [x,y]
        if b == mouse.RIGHT:
            self.lastMouseDown["r"] = [x,y]

        """
        state.lastMouseX = x
        state.lastMouseY = y

        clickedMobX = state.x+(x-posX+tileW/2)//tileW
        clickedMobY = state.y+(y-posY+tileH/2)//tileH
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
        #self.label.text = u"안녕세상" + `tick`

        for slot in self.qSlot:
            slot.skill.OnTick(tick*100000)
        self.char.Tick(tick*100000)

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




아이템 드래그 드랍! 클릭 앤 드랍이지만.
이제 포인트를 만든다.
포인트를 표시하고 상점에서 아이템 구입 판매를 하게 한다.
아이템을 구입하면 상점의 빈 자리에 새로운 아이템을 스폰해야 한다.(OnDrop에서 buy에 성공하면 새로운 아이템 스폰을 하게 한다.)
아이템에 CalcPrice를 넣는다.

일단 플레이어 속성을 만들자.
체력 마력 공격력 방어력
다른 속성은 복잡하므로 넣지 말자. 스킬에도 속성이 없고 공격력이 간접적으로 적용된다.
아이템을 만드는데 아이템에 들어갈 수 있는 속성들의 리스트와 그 속성의 숫자 범위를 정의해 두고 랜덤하게 나오게 한다.
또한 아이템의 레벨에 따라 숫자의 범위가 점점 커진다.
아이템의 속성은 일반 아이템은 속성 1개, 매직 아이템은 속성 2개, 레어 아이템은 속성 4개, 유니크 아이템은 속성이 5개가 들어갈 수 있다.
인챈트 스크롤이 있어 아이템을 인챈트할 때마다 그 인챈트 스크롤에 붙은 옵션이 1개씩 늘어난다.
일반 아이템은 1번 인챈트 가능
매직 아이템은 2번 인챈트 가능
레어 아이템은 4번 인챈트 가능
유니크 아이템은 5번 인챈트가 가능하다.

즉 유니크의 경우 속성이 10개가 붙을 수 있다.

이제 적을 만든다.

쿨다운 중에 아이콘에 오버레이를 씌워서 점점 게이지가 올라차고 끝나면 게이지가 사라져서 쿨다운중임을 알린다.
마나가 부족하면 배경이 회색으로 되어 사용할 수 없음을 알린다.

스턴은 20초 이상은 기절시키지 못하도록 포인트를 넣을 수 있는 것에 제한을 둔다.

포인트를 넣을 수도 있지만 뺄 수도 있다.

아이템의 가격은 살 때와 팔 때가 동일하다.
"""
