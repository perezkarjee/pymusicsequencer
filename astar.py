# -*- coding: utf8 -*-
# http://www.gamedev.net/reference/articles/article2003.asp
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

class BinaryHeap:
    def __init__(self):
        self.bheap = []

    def _IsCurrentSmallerThanParent(self, curNodeIdx):
        if curNodeIdx >= 2:
            parentNodeIdx = self._GetParentNodeIdx(curNodeIdx)
            if self.bheap[parentNodeIdx-1].GetFCost() > self.bheap[curNodeIdx-1].GetFCost():
                return True
            else:
                return False
        else:
            return False

    def _IsCurrentBiggerThanTwoChildren(self, curNodeIdx):
        child1, child2 = self._GetChildrenNodeIdx(curNodeIdx)
        if child1 and self.bheap[child1-1].GetFCost() < self.bheap[curNodeIdx-1].GetFCost():
            return True
        # or
        if child2 and self.bheap[child2-1].GetFCost() < self.bheap[curNodeIdx-1].GetFCost():
            return True

    def _GetSmallerChildNode(self, childNode1, childNode2):
        if childNode1 != None and childNode2 == None:
            return childNode1
        elif childNode1 == None and childNode2 != None:
            return childNode2
        elif childNode1 == None and childNode2 == None:
            return None

        if self.bheap[childNode1-1].GetFCost() <= self.bheap[childNode2-1].GetFCost():
            return childNode1
        else:
            return childNode2

    def _GetParentNodeIdx(self, curNodeIdx):
        if curNodeIdx >= 2: # floor'd integer
            return curNodeIdx/2
        else:
            return None
    def _GetChildrenNodeIdx(self, curNodeIdx):
        newChild1 = curNodeIdx*2
        newChild2 = newChild1+1
        if newChild1 > len(self.bheap):
            newChild1 = None
        if newChild2 > len(self.bheap):
            newChild2 = None

        return newChild1, newChild2

    def AddItem(self, node):
        self.bheap += [node]
        if len(self.bheap) != 1:
            newlyAddedNodeIdx = len(self.bheap)
            while self._IsCurrentSmallerThanParent(newlyAddedNodeIdx):
                parentNodeIdx = self._GetParentNodeIdx(newlyAddedNodeIdx)
                self.SwapNodes(newlyAddedNodeIdx, parentNodeIdx)
                newlyAddedNodeIdx = parentNodeIdx
        else:
            pass

    def IsHeapEmpty(self):
        if len(self.bheap) == 0:
            return True
        else:
            return False

    def GetTopNode(self):
        assert len(self.bheap) != 0, "No item in the heap!"
        return self.bheap[0]
    def PopTopNode(self):
        assert len(self.bheap) != 0, "No item in the heap!"

        topNode = self.bheap[0]
        if len(self.bheap) == 1:
            del self.bheap[0]
        else:
            self.bheap[0] = self.bheap[-1]
            del self.bheap[-1]
            curNodeIdx = 1

            while self._IsCurrentBiggerThanTwoChildren(curNodeIdx):
                child1, child2 = self._GetChildrenNodeIdx(curNodeIdx)
                child = self._GetSmallerChildNode(child1, child2)
                if child:
                    self.SwapNodes(curNodeIdx, child)
                    curNodeIdx = child
        
        return topNode

    def SwapNodes(self, curNodeIdx, anotherNodeIdx):
        anotherNodeValue = self.bheap[anotherNodeIdx-1]
        self.bheap[anotherNodeIdx-1] = self.bheap[curNodeIdx-1]
        self.bheap[curNodeIdx-1] = anotherNodeValue



    def ModifyItem(self, nodeIdx, newParent, newGCost):
        nodeItem = self.bheap[nodeIdx-1]
        nodeItem.parent = newParent
        nodeItem.g = newGCost

        newlyAddedNodeIdx = nodeIdx
        while self._IsCurrentSmallerThanParent(newlyAddedNodeIdx):
            parentNodeIdx = self._GetParentNodeIdx(newlyAddedNodeIdx)
            self.SwapNodes(newlyAddedNodeIdx, parentNodeIdx)
            newlyAddedNodeIdx = parentNodeIdx

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
    def __init__(self, theMap, mapWidth, mapHeight, startX, startY, targetX, targetY, timeFunc=None, timeOut = 100, returnNearest=True):
        self.theMap = theMap
        self.w = mapWidth
        self.h = mapHeight
        self.start = startX, startY
        self.target = targetX, targetY
        self.openList = BinaryHeap()
        self.closedList = [] # put nodes here

        self.costGHorizontal = 10
        self.costGDiagonal = 21#10+10+1. better to move 2 horizontal than one diagonel. to encourage diagonal movement use 14


        self.timeFunc = timeFunc
        self.timeOut = timeOut
        self.returnNearest = returnNearest


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
            nodeIdx = 0
            for node in nodeList:
                if node.x == x and node.y == y:
                    return node, nodeIdx
                nodeIdx += 1
            else:
                return None
        else:
            return None

    def IsNodeInOpenList(self, x, y):
        return self._IsNodeInList(self.openList.bheap, x, y)

    def IsNodeInClosedList(self, x, y):
        return self._IsNodeInList(self.closedList, x, y)

    def GetNodeInOpenList(self, x, y):
        return self._GetNodeInList(self.openList.bheap, x, y)

    def AddNodeToOpenList(self, parent, x, y, g, h):
        node = AStarNode(parent, x, y, g, h)
        self.openList.AddItem(node)

    def MoveTopOpenNodeToClosedList(self):
        node = self.openList.PopTopNode()
        self.closedList += [node]

    def GetSurroundingCoords(self, node): # not in closed list, and walkable
        x, y = node.x, node.y

        surroundingsHorizontals = [          (x, y-1), 
                                   (x-1, y),           (x+1, y),
                                             (x, y+1),           ]
        top, left, right, bottom = surroundingsHorizontals
        leftTop  = (x-1, y-1)
        rightTop = (x+1, y-1)
        leftBottom = (x-1, y+1)
        rightBottom = (x+1, y+1)

        foundSurroundings = []
        for curCoord in surroundingsHorizontals:
            if self.IsNodeWalkable(*curCoord) and (not self.IsNodeInClosedList(*curCoord)):
                foundSurroundings += [curCoord]

        def IsDiagonalNodeWalkable(target, nearTarget1, nearTarget2):
            if self.IsNodeWalkable(*target) and (not self.IsNodeInClosedList(*target)):
                if self.IsNodeWalkable(*nearTarget1) or self.IsNodeWalkable(*nearTarget2):
                    return True
            return False

        if IsDiagonalNodeWalkable(leftTop, left, top): # 왼쪽 아래로의 이동은 가능하나 왼쪽과 아래가 막혀있는 경우 이동 불가함을 구현한다.
            foundSurroundings += [leftTop]
        if IsDiagonalNodeWalkable(rightTop, right, top):
            foundSurroundings += [rightTop]
        if IsDiagonalNodeWalkable(leftBottom, left, bottom):
            foundSurroundings += [leftBottom]
        if IsDiagonalNodeWalkable(rightBottom, right, bottom):
            foundSurroundings += [rightBottom]

        return foundSurroundings

    def GetLowestHCostNode(self):
        newList = self.openList.bheap + self.closedList
        if newList:
            lowestHScore = newList[0].h
            lowestHScoreNode = newList[0]
            for node in newList:
                if node.h < lowestHScore:
                    lowestHScore = node.h
                    lowestHScoreNode = node

            return lowestHScoreNode
        else:
            return None

    def GetLowestFScoreOpenNode(self):
        if not self.openList.IsHeapEmpty():
            return self.openList.PopTopNode()
        else:
            return None

    def CalculatePath(self, lastNode):
        curNode = lastNode
        nodes = []
        while curNode:
            if curNode in nodes: # 만약 두 개의 노드가 서로를 가리키고 있거나 하여 중복된 노드가 나오면...
                return None
            nodes += [curNode]
            curNode = curNode.parent
        nodes = [(node.x, node.y) for node in nodes]
        nodes.reverse()
        #return self.SimplifyPath(nodes)
        return nodes

    def Find(self):
        # 1. check integrity
        if self.start == self.target:
            return None
        sX, sY, eX, eY = self.start+self.target
        if not (0 <= sX < self.w and 0 <= eX <= self.w and 0 <= sY <= self.h and 0 <= eY <= self.h):
            return None
        #if (not self.IsNodeWalkable(*self.start)): #or (not self.IsNodeWalkable(*self.target)):
        #    return None
        # 2.start with starting positon
        startGCost = 0
        startHCost = self.CalcHCost(*self.start)
        self.AddNodeToOpenList(None, self.start[0], self.start[1], startGCost, startHCost)

        # 3. do the a* process
        while True:
            if self.timeFunc:
                if self.timeFunc() >= self.timeOut:
                    if self.returnNearest:
                        nearestNode = self.GetLowestHCostNode()
                        if nearestNode:
                            return self.CalculatePath(nearestNode)
                        else:
                            return None
                    else:
                        return None

            if self.openList.IsHeapEmpty():
                # there is no path! just return nearest-to-target path or return None based on the option
                if self.returnNearest:
                    nearestNode = self.GetLowestHCostNode()
                    if nearestNode:
                        return self.CalculatePath(nearestNode)
                    else:
                        return None
                else:
                    return None
           
            curNode = self.openList.GetTopNode()


            # if the node which is currently being moved to the closedList is targetNode it is finished!
            if curNode.x == self.target[0] and curNode.y == self.target[1]:
                return self.CalculatePath(curNode)

            # move current node to closed list
            self.MoveTopOpenNodeToClosedList()

            # find surroundings and add those to open list
            surroundings = self.GetSurroundingCoords(curNode)
            for coord in surroundings:
                if self.IsNodeInOpenList(*coord):
                    # 만약 이미 오픈리스트에 서라운딩 노드가 있고 그 노드에 저장된 GCost가 현재 선택된 currentNode에서부터 서라운딩 노드에의 GCost보다 크다면
                    # 그 노드의 Parent를 curNode로 설정하고 GCost를 새로 계산한 GCost로 재설정 한다.
                    newGCost = curNode.g + self.CalcGCost(coord[0], coord[1], curNode.x, curNode.y)
                    nodeInOpenList, nodeIdx = self.GetNodeInOpenList(*coord)
                    if newGCost < nodeInOpenList.g:
                        self.openList.ModifyItem(nodeIdx+1, curNode, newGCost)
                else:
                    thisGCost = curNode.g + self.CalcGCost(coord[0], coord[1], curNode.x, curNode.y)
                    thisHCost = self.CalcHCost(*coord)
                    self.AddNodeToOpenList(curNode, coord[0], coord[1], thisGCost, thisHCost)

    def SimplifyPath(self, path):
        """
        [(0, 0), (1, 0), (2, 0), (3, 0), (4, 1), (5, 2)] -> [(0, 0), (3, 0), (5, 2)]
     offsetX -> 1,0    1,0     1,0    (1,1)   (1,1)
        removeThese = [1, 2]
        """
        if len(path) >= 2:
            prevNode = path[1]
            removeThese = []
            nodePrevOffsetX = path[1][0] - path[0][0]
            nodePrevOffsetY = path[1][1] - path[0][1]
            prevNodeIdx = 1
            for node in path[2:]:
                nodeOffsetX = node[0] - prevNode[0]
                nodeOffsetY = node[1] - prevNode[1]
                #print nodeOffsetX, nodeOffsetY, nodePrevOffsetX, nodePrevOffsetY
                if nodeOffsetX == nodePrevOffsetX and nodeOffsetY == nodePrevOffsetY:
                    removeThese += [prevNodeIdx]
                nodePrevOffsetX = nodeOffsetX
                nodePrevOffsetY = nodeOffsetY
                prevNode = node
                prevNodeIdx += 1

            newPath = []
            for idx in range(len(path)):
                if idx not in removeThese:
                    newPath += [path[idx]]
            return newPath
        else:
            return path

def Test1():
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
    print finder.SimplifyPath(found)
    #def __init__(self, theMap, mapWidth, mapHeight, startX, startY, targetX, targetY, timeFunc=None, timeOut = 10, returnNearest=True):

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
def Test2():
    #       0001020304050607080910111213141516
    map =  [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #0
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #1
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #2
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #3
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #4
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #5
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #6
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #7
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #8
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #9
            0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0, #10
            0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0] #11

    finder = AStarFinder(map, 17, 12, 4, 6, 12, 6)
    found = finder.Find()
    print found
    print finder.SimplifyPath(found)

def Test3():
    #       0001020304050607080910111213141516
    map =  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #0
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #1
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #2
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #3
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #4
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, #5
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #6
            1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, #7
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #8
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #9
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, #10
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #11

    finder = AStarFinder(map, 17, 12, 4, 6, 12, 6)
    found = finder.Find()
    print found
    print finder.SimplifyPath(found)


if __name__ == '__main__':
    Test2()
    #Test2()
    #Test3()

