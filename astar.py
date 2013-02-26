# -*- coding: utf8 -*-
# Copyright: yubgipenguin@gmail.com Jin Ju Yu
# License: LGPL
class AStarNode:
    def __init__(self, parentNode, x, y, gCost, hCost):
        self.x = x
        self.y = y
        self.g = gCost
        self.h = hCost
        self.parent = parentNode

    def GetFCost(self):
        return self.g+self.h

class AStarFinder:
    """
    the map structure
    0 walkabla
    1 unwalkable
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    something like this.
    Access with X, Y(zero based)

    map[y*mapHeight + x]
    """
    def __init__(self, theMap, mapWidth, mapHeight, startX, startY, targetX, targetY):
        self.theMap = theMap
        self.w = mapWidth
        self.h = mapHeight
        self.start = startX, startY
        self.target = targetX, targetY
        self.openList = [] # put nodes here
        self.closedList = [] # put nodes here

        self.costGHorizontal = 10
        self.costGDiagonal = 14


    def CalcGCost(self, x, y, parentNodeX, parentNodeY): # cost from parent, use costGHorizontal and costGDiagonal here
        if abs(x-parentNodeX) == 1 and abs(y-parentNodeY) == 1:
            return self.costGDiagonal
        else:
            return self.costGHorizontal

    def CalcHCost(self, x, y): # cost to target, horizontal only, no diagonal, manhattan method
		return 10*(abs(x - self.target[0]) + abs(y - self.target[1]))

    def IsNodeWalkable(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            walkable = self.theMap[y*self.w + x]
            if walkable == 0:
                return True
            else:
                return False
        else:
            return False

    def _IsNodeInList(self, nodeList, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            for node in nodeList:
                if node.x == x and node.y == y:
                    return True
            else:
                return False
        else:
            return False

    def _GetNodeInList(self, nodeList, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            for node in nodeList:
                if node.x == x and node.y == y:
                    return node
            else:
                return None
        else:
            return None

    def IsNodeInOpenList(self, x, y):
        return self._IsNodeInList(self.openList, x, y)

    def IsNodeInClosedList(self, x, y):
        return self._IsNodeInList(self.closedList, x, y)

    def GetNodeInOpenList(self, x, y):
        return self._GetNodeInList(self.openList, x, y)

    def AddNodeToOpenList(self, parent, x, y, g, h):
        node = AStarNode(parent, x, y, g, h)
        self.openList += [node]

    def MoveNodeToClosedList(self, node):
        index = self.openList.index(node)
        del self.openList[index]
        self.closedList += [node]

    def GetSurroundingCoords(self, node): # not in closed list, and walkable
        x, y = node.x, node.y

        surroundings = [(x-1, y-1), (x, y-1), (x+1, y-1),
                        (x-1, y),           (x+1, y),
                        (x-1, y+1), (x, y+1), (x+1, y+1)]
        foundSurroundings = []
        for curCoord in surroundings:
            if self.IsNodeWalkable(*curCoord) and (not self.IsNodeInClosedList(*curCoord)):
                foundSurroundings += [curCoord]

        return foundSurroundings

    def GetLowestFScoreOpenNode(self):
        if self.openList:
            lowestFScore = self.openList[0].GetFCost()
            lowestFScoreNode = self.openList[0]
            for node in self.openList[1:]:
                if node.GetFCost() < lowestFScore:
                    lowestFScore = node.GetFCost()
                    lowestFScoreNode = node

            return lowestFScoreNode
        else:
            return None

    def CalculatePath(self, lastNode):
        curNode = lastNode
        nodes = []
        while curNode:
            nodes += [curNode]
            curNode = curNode.parent
        nodes = [(node.x, node.y) for node in nodes]
        nodes.reverse()
        return nodes


    def Find(self):
        # 1. check integrity
        if self.start == self.target:
            return None
        if (not self.IsNodeWalkable(*self.start)) or (not self.IsNodeWalkable(*self.target)):
            return None
        # 2.start with starting positon
        startGCost = 0
        startHCost = self.CalcHCost(*self.start)
        self.AddNodeToOpenList(None, self.start[0], self.start[1], startGCost, startHCost)

        # 3. do the a* process
        while True:
            curNode = self.GetLowestFScoreOpenNode()
            # move current node to closed list

            if curNode == None:
                # there is no path!
                return None

            # if the node which is currently being moved to the closedList is targetNode it is finished!
            if curNode.x == self.target[0] and curNode.y == self.target[1]:
                return self.CalculatePath(curNode)

            self.MoveNodeToClosedList(curNode)

            # find surroundings and add those to open list
            surroundings = self.GetSurroundingCoords(curNode)
            for coord in surroundings:
                if self.IsNodeInOpenList(*coord):
                    # 만약 이미 오픈리스트에 서라운딩 노드가 있고 그 노드에 저장된 GCost가 현재 선택된 currentNode에서부터 서라운딩 노드에의 GCost보다 크다면
                    # 그 노드의 Parent를 curNode로 설정하고 GCost를 새로 계산한 GCost로 재설정 한다.
                    newGCost = curNode.g + self.CalcGCost(coord[0], coord[1], curNode.x, curNode.y)
                    nodeInOpenList = self.GetNodeInOpenList(*coord)
                    if newGCost < nodeInOpenList.g:
                        nodeInOpenList.parent = curNode
                        nodeInOpenList.g = newGCost
                else:
                    thisGCost = curNode.g + self.CalcGCost(coord[0], coord[1], curNode.x, curNode.y)
                    thisHCost = self.CalcHCost(*coord)
                    self.AddNodeToOpenList(curNode, coord[0], coord[1], thisGCost, thisHCost)


if __name__ == '__main__':
    #       0001020304050607080910111213141516
    map =  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #0
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #1
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #2
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #3
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #4
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #5
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #6
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #7
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #8
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #9
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #10
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #11

    finder = AStarFinder(map, 17, 12, 4, 6, 12, 6)
    found = finder.Find()
    print found
    #def __init__(self, theMap, mapWidth, mapHeight, startX, startY, targetX, targetY):

    """
    result
    [(4, 6), (5, 7), (6, 8), (7, 9), (8, 10), (9, 9), (10, 8), (11, 7), (12, 6)]
       a        b       c       d       e        f        g        h        i
    #       0001020304050607080910111213141516
    map =  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #0
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #1
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #2
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #3
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #4
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #5
            0,0,0,0,a,0,0,0,1,0,0,0,i,0,0,0,0, #6
            0,0,0,0,0,b,0,0,1,0,0,h,0,0,0,0,0, #7
            0,0,0,0,0,0,c,0,1,0,g,0,0,0,0,0,0, #8
            0,0,0,0,0,0,0,d,1,f,0,0,0,0,0,0,0, #9
            0,0,0,0,0,0,0,0,e,0,0,0,0,0,0,0,0, #10
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #11

    아이디어: 
    길이 없을 경우  hCost가 가장 작은 노드를 선택하여 최소한 목표와 가장 가까운 거리로 이동하도록 할 수 있게 한다.
    """

