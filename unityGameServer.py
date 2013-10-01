# -*- coding: utf8 -*-

import asyncore
import asynchat
import socket
import sqlite3
import threading
import json
import time
import md5
import datetime
import codecs


class _Debug(object):
    def __init__(self):
        self.f = codecs.open("unityGameServer.log", "a", "utf8")
        #self.f.write(str(datetime.datetime.now())+"\n")
    def __del__(self):
        self.f.close()
    def Log(self, txt):
        txt = unicode(txt)
        print txt
        self.f.write("[" + str(datetime.datetime.now()) + "]: " + txt + "\n")
        self.f.flush()
Debug = _Debug()

class Lobby(object):
    def __init__(self):
        self.clients = set()
        self.game = None
 
    def Leave(self, client):
        client.game.Leave(client.gameObject)
        self.clients.remove(client)
        Debug.Log("Leave: " + str(client.addr))
    def Join(self, client):
        self.clients.add(client)
 
    def Broadcast(self, data):
        self.game.Lock()
        for client in self.clients:
            client.Send(data)
        self.game.Unlock()
 
 
class Server(asynchat.async_chat):
    def __init__(self):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("127.0.0.1", 54321))
        self.listen(5)
        self.lobby = None
        self.game = None

 
    def set_lobby(self, lobby):
        self.lobby = lobby
 
    def handle_accept(self):
        sock, addr = self.accept()
        Debug.Log("Client connected: " + str(addr))

        self.game.Lock()

        gameObject = GameObject()
        client = Client(sock, addr, self.lobby)

        self.game.gameObjects.add(gameObject)
        gameObject.game = self.game
        gameObject.client = client
        client.game = self.game
        client.gameObject = gameObject

        client.OnConnect()
        gameObject.OnConnect()

        self.game.Unlock()

        
class Client(asynchat.async_chat):
    def __init__(self, conn, addr, lobby):
        asynchat.async_chat.__init__(self, sock=conn)
        self.in_buffer = ""
        self.set_terminator(chr(127)+chr(64)+chr(1)+chr(64)+chr(32)+chr(64))
        self.addr = addr
 
        self.lobby = lobby
        self.lobby.Join(self)
        self.game = None
        self.gameObject = None

        self.isDestroyed = False

        self.hsmsg = "THEPGAMERPG"
        self.hs = json.dumps({"msgtype":"handshake", "hs": self.hsmsg}) # Handshake
        self.hsed = False


        self.dataPerSec = 3000 # in bytes
        self.dataDown = 0
        self.prevTime = time.clock()
        self.wait = 0


    def SendHandshake(self):
        #Debug.Log("Sending Handshake..." + str(self.addr))
        self.Send(self.hs)
    def Send(self, msgTxt):
        self.push(msgTxt + self.terminator)
    def OnConnect(self):
        #Debug.Log("Client object created for " + str(self.addr)
        self.SendHandshake()

    def collect_incoming_data(self, data):

        # Check if client if sending too much data in one second
        curTime = time.clock()
        diff = curTime-self.prevTime
        self.prevTime = curTime
        self.wait += diff

        if self.wait > 1.0:
            self.dataDown = 0
            self.wait = 0.0

        self.dataDown += len(data)
        if len(data) > self.dataPerSec:
            Debug.Log("Receiving too much data in one second! -> Closing...")
            self.close_when_done()
            return




        if not self.isDestroyed:
            self.game.Lock()
            self.in_buffer += data
            if len(self.in_buffer) > 1000:
                Debug.Log("Receiving too much data without terminator! -> Closing...")
                self.game.Unlock()
                self.close_when_done()
                return

            self.game.Unlock()
    
    def found_terminator(self):
        """
        if self.in_buffer.rstrip() == "QUIT":
            self.lobby.leave(self)
            self.close_when_done_when_done()
        else:
        """
        if not self.isDestroyed:
            #self.lobby.Broadcast(self.in_buffer)

            self.ProcessLine(self.in_buffer)
            self.game.Lock()
            self.in_buffer = ""
            self.game.Unlock()

    def ProcessLine(self, buffer):
        self.game.Lock()
        buffer = unicode(buffer, "utf8")
        #txt = json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
        try:
            obj = json.loads(buffer)
        except:
            self.game.Unlock()
            Debug.Log("Data inconsistency found! --> Closing.")
            self.close_when_done()
            return

        if not self.hsed:
            if "msgtype" in obj and obj["msgtype"] == "handshake" and "hs" in obj and obj["hs"] == self.hsmsg:
                self.hsed = True
                #Debug.Log("Handshaken!: " + str(self.addr))
            else:
                Debug.Log("Handshake failed -> Closing...: " + str(self.addr))
                self.game.Unlock()
                self.close_when_done()
                return
        else:
            self.gameObject.PushMsg(obj)
        self.game.Unlock()

    def handle_close(self):
        self.game.Lock()
        if not self.isDestroyed:
            self.close()
            self.isDestroyed = True
            self.lobby.Leave(self)
        self.game.Unlock()

class Character(object):
    def __init__(self):
        self.name = None 

class GameObject(object):
    def __init__(self):
        self.client = None
        self.game = None
        self.msgs = []

        self.accName = None
        self.curChar = None

    def OnConnect(self):
        pass
        #Debug.Log("Game object created for " + str(self.client.addr))

    def PushMsg(self, msg):
        self.msgs += [msg]
    def CheckMsg1(self,msg):
        if "msgtype" not in msg:
            return False
        return True
    def CheckMsg2(self, msg,argstuple):
        args = [arg[0] for arg in argstuple]
        types = [arg[1] for arg in argstuple]
        idx = 0
        for arg in args:
            if arg not in msg:
                return False
            typ = types[idx]
            if typ != type(msg[arg]):
                if typ == str and unicode == type(msg[arg]):
                    pass
                else:
                    Debug.Log(typ, type(msg[arg]))
                    return None
            idx += 1
        return True


    def Tick(self):
        # XXX: 메시지 처리
        # 이동은 전적으로 클라에서 한다.
        # 타격 판정도 클라에서 한다. 중요하지 않다.
        # 전투 계산만 서버에서 한다.
        # 울온 프리서버 정도의 수준으로 만든다.
        funcTable = {
            "txt": [self.OnRawTxt, ("txt", str), ("testList", list)], # msgtype: [HandlerFunc, arg1, arg2, ..., argN]
            "login": [self.OnLogin, ("acc", str), ("pw", str)],
            "create": [self.OnCreate, ("acc", str), ("pw", str)],
            "txtpluslevel": [self.OnStruct, ("txt", str), ("level", int)],
        }

        for msg in self.msgs:
            if self.CheckMsg1(msg):
                typ = msg["msgtype"]
                for func in funcTable:
                    result = self.CheckMsg2(msg, funcTable[func][1:])
                    if typ == func and result == True:
                        try:
                            funcTable[func][0](msg)
                        except KeyError:
                            Debug.Log("Data inconsistency found! --> Closing.")
                            self.client.close_when_done()
                            return
                        except IndexError:
                            Debug.Log("Data inconsistency found! --> Closing.")
                            self.client.close_when_done()
                            return
                        except:
                            Debug.Log("Server error! --> Closing.")
                            self.client.close_when_done()
                            raise
                    elif result == False:
                        pass
                    elif result == None:
                        Debug.Log("Data inconsistency found! --> Closing.")
                        self.client.close_when_done()
                        return
            else:
                Debug.Log("Data inconsistency found! --> Closing.")
                self.client.close_when_done()
                return


        self.msgs = []

    def OnStruct(self, msg):
        Debug.Log(msg["txt"], msg["level"])
    def OnRawTxt(self, msg):
        Debug.Log(msg["txt"])
        Debug.Log(msg["testList"])
    def OnLogin(self, msg):
        acc = msg["acc"]
        pw = msg["pw"]
        Debug.Log(acc, pw)
    def OnCreate(self, msg):
        acc = msg["acc"]
        pw = msg["pw"]
        Debug.Log(acc, pw)

class SQLite3Utils(object):
    """
    검색을 안 해도 되는 것들은 JSON으로 변형해서 TEXT로 넣는다.
    """
    def __init__(self):
        self.conn = sqlite3.connect('example.db') 
        self.c = self.conn.cursor()
        self.InitDB()

    def CheckTableExists(self, tableName):
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accountNames';")
        if self.c.fetchone():
            return True
        return False

    def InitDB(self):
        if not self.CheckTableExists("accountNames"):
            self.c.execute('''CREATE TABLE accountNames 
                    (joinDate text, name text)''')
        if not self.CheckTableExists("loginInfo"):
            self.c.execute('''CREATE TABLE loginInfo 
                    (name text, pw text)''')
        if not self.CheckTableExists("characters"):
            self.c.execute('''CREATE TABLE characters 
                    (ownerName text, charName text, dataJSON text)''')
        if not self.CheckTableExists("stash"):
            self.c.execute('''CREATE TABLE stash 
                    (ownerName text, dataJSON text)''')
            # 패스워드 암호화: md5로 해쉬값을 만들고 거기에 acc를 붙이고 다시 해쉬값을 만들고 원래 해쉬값과 더한 후 다시 해쉬값을 만든다.

    def Save(self):
        self.conn.commit()
    def Close(self):
        self.conn.close()
    def CreateTable(self):
        "create table t1 (t1key INTEGER PRIMARY KEY,data TEXT,num double,timeEnter DATE);"
        """
    def CheckTableExists(self):
        "SELECT name FROM sqlite_master WHERE type='table' AND name='table_name';"
        """
    def AddColumn(self):
        "ALTER TABLE {tableName} ADD COLUMN COLNew {type};"

        "insert into t1 (data,num) values ('This is sample data',3);"
        """
INT
INTEGER
TINYINT
SMALLINT
MEDIUMINT
BIGINT
UNSIGNED BIG INT
INT2
INT8	
CHARACTER(20)
VARCHAR(255)
VARYING CHARACTER(255)
NCHAR(55)
NATIVE CHARACTER(70)
NVARCHAR(100)
TEXT
CLOB
BLOB
REAL
DOUBLE
DOUBLE PRECISION
FLOAT	
NUMERIC
DECIMAL(10,5)
BOOLEAN
DATE
DATETIME


     $ sqlite3 test.db  "select * from t1 limit 2";
     1|This is sample data|3|
     2|More sample data|6|

    $ sqlite3 test.db "select * from t1 order by t1key limit 1 offset 2";
     3|And a little more|9|     

     CREATE TABLE t1 (t1key INTEGER
                  PRIMARY KEY,data TEXT,num double,timeEnter DATE);
     INSERT INTO "t1" VALUES(1, 'This is sample data', 3, NULL);
     INSERT INTO "t1" VALUES(2, 'More sample data', 6, NULL);
     INSERT INTO "t1" VALUES(3, 'And a little more', 9, NULL);     


create table employee(empid integer,name varchar(20),title varchar(10));
sqlite> create table department(deptid integer,name varchar(20),location varchar(10));


insert into employee values(101,'John Smith','CEO');
insert into employee values(102,'Raj Reddy','Sysadmin');
insert into employee values(103,'Jason Bourne','Developer');
insert into employee values(104,'Jane Smith','Sale Manager');
insert into employee values(105,'Rita Patel','DBA');

insert into department values(1,'Sales','Los Angeles');
insert into department values(2,'Technology','San Jose');
insert into department values(3,'Marketing','Los Angeles');


update employee set deptid=3 where empid=101;
update employee set deptid=2 where empid=102;
update employee set deptid=2 where empid=103;
update employee set deptid=1 where empid=104;
update employee set deptid=2 where empid=105;

drop table dept;


>create table t1 (t1Key INTEGER PRIMARY KEY, data TEXT, num double, timeEnter DATE);
>insert into(data, num) values('this is sample', 2);
>insert into(data, num) values('this is sample2', 20);
>update t1 set timeEnter = DATETIME('NOW');
>select * from t1;

--> 결과는 아래와 같이 나타난다.
1:this is sample|2.0|2010-06-05 14:48:46
2:this is sample2|20.0|2010-06-05 14:48:46


--> 또 다음과 같이 입력도 가능하다.
>insert into t1(data, num, timeEnter) values ('sample', 10, DATETIME('2010-06-06 00:00:00');





UPDATE table1 
SET a = t2.a, b = t2.b, .......
FROM table2 t2
WHERE table1.id = t2.id



        - 전체 query
   sqlite> select * from worldTimeList;

- 일부 query
   sqlite> select _id, city_name from worldTimeList where city_name='Seoul';

- row 삭제
   sqlite> DELETE FROM worldTimeList where _id=3;

- 전체 삭제
   sqlite> DELETE FROM worldTimeList;
        """

class Game(object):
    def __init__(self):
        self.server = None
        self.gameObjects = set()
        self.lock = threading.Lock()
        self.db = SQLite3Utils()

    def Lock(self):
        self.lock.acquire()
    def Unlock(self):
        self.lock.release()

    def Leave(self, gameObject):
        self.gameObjects.remove(gameObject)
    def Tick(self):
        self.Lock()
        for go in self.gameObjects:
            go.Tick()
        self.Unlock()

    def SaveGame(self):
        self.Lock()
        self.db.Save()
        self.Unlock()
    def Quit(self):
        self.db.Close()


if __name__ == '__main__':
    lobby = Lobby()
    game = Game()
    server = Server()

    lobby.game = game
    game.server = server
    server.game = game

    server.set_lobby(lobby)
    Debug.Log("Server started!")

    try:
        while True:
            # Process events
            # msg = ...
            game.Tick()
            asyncore.loop(
                    timeout=0.1,
                    count=1
                    )
    except KeyboardInterrupt:
        game.SaveGame()
        game.Quit()

"""
세이브파일은 압축해서 헤더의 앞글자만 바꾼다.(PKZip의 경우 PK헤더를 AA로 바꾼다던지)
"""
