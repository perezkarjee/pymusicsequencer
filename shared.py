import legume
import astar
class TestPos(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+1
    MessageValues = {
        'name' : 'string 128',
        'x' : 'int',
        'y' : 'int',
        }

legume.messages.message_factory.add(TestPos)




class MapGen(object):
    def __init__(self, w, h):
        self.map = [0 for i in (w*h)]
        self.w = w
        self.h = h

    def Gen(self):
        """
        사각형의 방을 만든 후 주변의 랜덤한 위치에 길목을 만듬
        각 방들의 길목을 모두 이음
        완성된 길목들의 주변에 벽을 쌓음
        끝
        """
        pass

    def FillOneRoom(self, x,y,w,h):
        for yy in range(h):
            for xx in range(w):
                self.map[(yy+y)*self.h+(x+xx)] = 1
