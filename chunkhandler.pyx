"""
DigDigRPG
Copyright (C) 2011 Jin Ju Yu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
cdef extern from "stdlib.h":
    ctypedef unsigned long size_t
    void free(void *ptr)
    void *malloc(size_t size)
    void *realloc(void *ptr, size_t size)
    size_t strlen(char *s)
    char *strcpy(char *dest, char *src)
    void *memset(void *str, int c, size_t n)
    void *memcpy(void *str1, void *str2, size_t n)
    void *memmove(void *str1, void *str2, size_t n)

cdef extern from "gl/gl.h":
    ctypedef int           GLint
    ctypedef unsigned int  GLenum
    ctypedef unsigned int  GLsizei
    ctypedef void GLvoid
    cdef void glVertexPointer(GLint size, GLenum type, GLsizei stride, GLvoid *pointer)
    cdef void glTexCoordPointer(GLint size, GLenum type,GLsizei stride, GLvoid *pointer)
    cdef void glColorPointer(GLint size, GLenum type,GLsizei stride, GLvoid *pointer)
    cdef void glNormalPointer(GLenum type,GLsizei stride, GLvoid *pointer)
    cdef void glIndexPointer(GLenum type, GLsizei stride, GLvoid *pointer)
    cdef void glDrawElements(GLenum 	mode,   GLsizei  count, GLenum  type,GLvoid *indices)
    cdef void glDrawArrays(	GLenum  	mode,            GLint  	first,            GLsizei  	count)


    
    
cdef extern from "genquads.h":
    struct tChunk:
        unsigned char *chunk
        char *heights
        unsigned char *colors

        int x,y,z
    ctypedef tChunk Chunk
    struct tOctree:
        tOctree *parent
        tOctree **children
        int filled
        void *extra
    ctypedef tOctree Octree
    struct tXYZ:
        float x,y,z
    ctypedef tXYZ XYZ
    struct tTorch:
        int x
        int y
        int z
        int face
    ctypedef tTorch Torch

    struct tChest:
        int x
        int y
        int z
        int frontFacing
    ctypedef tChest Chest
    struct tItem:
        int type
        float x
        float y
        float z
        int idx
    ctypedef tItem Item



    struct tExtra:
        Torch *torches
        int torchLen
        int torchIdx
        Chest *chests
        int chestLen
        int chestIdx
        Item *items
        int itemLen
        int itemIdx

    ctypedef tExtra Extra



    char HitBoundingBox(float minB[3],float maxB[3], float origin[3], float dir[3],float coord[3])
    int InWater(float x, float y, float z, float vx, float vy, float vz)
    int CheckCollide(float x, float y, float z, float vx, float vy, float vz, float bx, float by_, float bz, float ydiff)
    void FixPos(float *fx, float *fy,float *fz, float ox,float oy,float oz,float nx,float ny,float nz, int bx, int by_, int bz, Octree *octrees[9], Chunk *chunks[9], int pos[9][3])

    int PickWithMouse(XYZ vp, XYZ dirV, int pos[9][3], Octree *octrees[9], Chunk *chunks[9], int outCoords[3], int *outFace, int limit, float ydiff, float viewmat[16])
    void FillHeights(Chunk *chunk)
    void FillTrees(Chunk *chunk, char trees[1000])
    void FillMap(unsigned char *chunkData)
    void FillTerrain(unsigned char *chunkData, int *points, int len, int ox, int oy, int oz, int upward, int lwidth, int rwidth, int bwidth, int twidth, int heightlimit, unsigned char fill1, unsigned char fill2, unsigned char fill3)
    void FillSea(unsigned char *chunkData, int *points, int len, int ox, int oy, int oz, int upward, int lwidth, int rwidth, int bwidth, int twidth, int heightlimit, unsigned char fill1, unsigned char fill2, unsigned char fill3, int depth)
    void CalcRecursive(Chunk * chunk, Octree *octree, int x, int y, int z, int depth)
    int IsPolyFront(int place, int x, int y, int z, float vx, float vy, float vz)
    void GenQuad(float *quadBuffer, int place, int x, int y, int z)
    Octree *AccessRecur(Octree *parent, int curx, int cury, int curz, int targetx, int targety, int targetz, int depth, int targetdepth)
    Octree *AccessOctreeWithXYZ(Octree * root, int x, int y, int z, int targetdepth)
    int CubeInFrustum(float x, float y, float z, double size, double frustum[6][4])
    void GenQuads(float *tV[64], float *tT[64], unsigned char *tC[64], int tIdx[64], int tLen[64], float *nsV[64], float *nsT[64], unsigned char *nsC[64], int nsIdx[64], int nsLen[64], float *aV[64], float *aT[64], unsigned char *aC[64], int aIdx[64], int aLen[64], float *iV[64], float *iT[64], unsigned char *iC[64], int iIdx[64], int iLen[64], Octree *root, Octree *parent, Chunk *chunk, Octree **octrees, Chunk **chunks, int pos[9][3], int depth, double frustum[6][4], int x, int y, int z, int ox, int oy, int oz, float vx, float vy, float vz, int lx, int ly, int lz, int updateCoords[64*3], int drawIdx, float sunx, float suny, float sunz)
    void GenIndexList(unsigned int *outIndexList, int *outIndexLen, float *quads, int quadLen, float vx, float vy, float vz)

cimport libc.stdio as stdio
cimport libc.math as cmath
import math
import numpy
import pickle
import random
cdef:
    int TEST_SIZE = 9
    enum OctreeFilledFlag:
        OT_FILLED = 1 << 0
        OT_HALFFILLED = 1 << 1
        OT_EMPTY = 1 << 2
        OT_COMPLETETRANSPARENT = 1 << 3
        OT_PARTTRANSPARENT = 1 << 4
        OT_XBLOCK = 1 << 5
        OT_YBLOCK = 1 << 6
        OT_ZBLOCK = 1 << 7
    enum BlockFlags:
        # 여기에 추가할 때 중간에 껴넣게 되면 맵 다 깨짐!
        # 총 256가지의 블럭종류들만이 가능하다.
        # 블럭에 컬러를 넣고 싶다면 또다른 확장 데이터가 필요함.
        # 뭐 컬러 버퍼라던지 그런 chunk.chunk를 또 만들면 된다.
        BLOCK_EMPTY
        BLOCK_WATER
        BLOCK_GLASS
        BLOCK_LAVA
        BLOCK_COBBLESTONE
        BLOCK_LOG
        BLOCK_WALL
        BLOCK_BRICK
        BLOCK_TNT
        BLOCK_STONE

        BLOCK_SAND
        BLOCK_GRAVEL
        BLOCK_WOOD
        BLOCK_LEAVES
        BLOCK_SILVER
        BLOCK_GOLD
        BLOCK_COALORE
        BLOCK_IRONORE
        BLOCK_DIAMONDORE
        BLOCK_IRON
        
        BLOCK_DIAMOND
        BLOCK_CPU
        BLOCK_CODE
        BLOCK_ENERGY
        BLOCK_KEYBIND
        BLOCK_PANELSWITCH
        BLOCK_LEVER
        BLOCK_WALLSWITCH
        BLOCK_NUMPAD
        BLOCK_TELEPORT

        BLOCK_JUMPER
        BLOCK_ELEVATOR
        BLOCK_ENGINECORE
        BLOCK_CONSTRUCTIONSITE
        BLOCK_AREASELECTOR
        BLOCK_GOLDORE
        BLOCK_SILVERORE
        BLOCK_WOOL
        BLOCK_GRASS
        BLOCK_DIRT
        BLOCK_INDESTRUCTABLE
        BLOCK_CHEST
        BLOCK_SPAWNER
        BLOCK_SILVERSLOT
        BLOCK_GOLDSLOT
        BLOCK_DIAMONDSLOT
        BLOCK_COLOR


    struct Vertex:
        float x,y,z
    struct Quad:
        Vertex v[4]

    int NUM_TREE = 4
    int MAX_DEPTH = 6
    int STREAM_BUFFER_LEN = 7*7
    int STREAM_BUFFER_SIZE = sizeof(Chunk *)*STREAM_BUFFER_LEN
    int SIZE_CHUNK = 128*128*128

#음. 옥트리를 쓰는 것 까지는 좋은데, 애초부터 최대 맵크기를 정해두고 해야한다.
# 블럭 한개가 50센티라고 치고....
# 12번 차일드를 까면 되나? 근데..... 음.......옥트리를 쓸 필요가 없이 걍 선형으로 해야하네. 높이는 128이 끝이니까. 음.....
# 아 그럼 쿼드트리 쓰면 되는구만 높이는 128개를 다 가지고 있거나 한다?
# 적어도 16개로 나눠서 최종레벨에서는 data가 16x16x16의 청크가 되게 한다. 16x16x16짜리가 8개 맨 아래 바닥부터 위까지 있도록 한다.
# 아. 청크사이즈를 2x2x2로 한 다음에 이걸 또 2x2x2로 묶고 또 묶고 이러면서 이걸 바로 Octree로 만들어야겠다.
# 2x2x2로 묶어도 4x4x4를 검사해야 한다.
# Traverse는 펑션포인터로 하도록 하자. 다시다시 복습하는 셈 치고.
# Octree 자체는 큐브를 가지고 있을 필요가 없다. 꽉찬건지 아닌지의 값만 가지고 있으면 된다.
# Octree의 루트가 여러개가 있고, 이것은 Quadtree에 의해 관리되도록 하게 하자.
# 128x128x128을 2x2x2가 될 때 까지 나눈 옥트리를 쓰도록 하자.
# 음.. 이걸 쿼드트리로 관리할 필요도 없다. 파일별로 관리하도록 하자. 청크가 되도록 하자. 그래. 용량도 2메가 밖에 안됨.
# 옥트리 자체도 매번 계산할 게 아니라 생성할 때 한 번 계산하고 그냥 저장해버리도록 하자.
#
#
# Torch등의 오브젝트는 따로 저장하겠군....
"""
bool SphereInFrustum( float x, float y, float z, float radius )
{
   int p;

   for( p = 0; p < 6; p++ )
      if( frustum[p][0] * x + frustum[p][1] * y + frustum[p][2] * z + frustum[p][3] <= -radius )
         return false;
   return true;
}
"""
class Vector2(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    def normalised(self):
        l = self.length()
        if l == 0.0:
            l = 1
        return Vector2(self.x / l, self.y / l)
    def __neg__(self):
        return Vector2(-self.x, -self.y)
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    def __radd__(self, other):
        return self.__add__(other)
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    def __rsub__(self, other):
        return self.__sub__(other)
    def __mul__(self, other):
        if type(other) in (int, float):
            return Vector2(self.x * other, self.y * other)
        else: # dot product
            return self.x * other.x + self.y * other.y
    def __rmul__(self, other):
        return self.__mul__(other)
    def __div__(self, other):
        return Vector2(self.x / other, self.y / other)
    def dotProduct(self, other):
        return self.x * other.x + self.y * other.y
    def __repr__(self):
        return str([self.x, self.y])

def tangent(a, b):
    return (a-b)/2.0
def CatmullRomSpline(p0, p1, p2, p3, resolution=0.1):

    m0 = tangent(p1, p0)
    m1 = tangent(p2, p0)
    m2 = tangent(p3, p1)
    m3 = tangent(p3, p2)
    t = 0.0
    a = []
    b = []
    c = []
    while t < 1.0:
        t_2 = t * t
        _1_t = 1 - t
        _2t = 2 * t
        h00 =  (1 + _2t) * (_1_t) * (_1_t)
        h10 =  t  * (_1_t) * (_1_t)
        h01 =  t_2 * (3 - _2t)
        h11 =  t_2 * (t - 1)

        result = Vector2(0.0,0.0)
        result.x = h00 * p0.x + h10 * m0.x + h01 * p1.x + h11 * m1.x
        result.y = h00 * p0.y + h10 * m0.y + h01 * p1.y + h11 * m1.y
        a.append(result)
        result = Vector2(0.0,0.0)
        result.x = h00 * p1.x + h10 * m1.x + h01 * p2.x + h11 * m2.x
        result.y = h00 * p1.y + h10 * m1.y + h01 * p2.y + h11 * m2.y
        b.append(result)
        result = Vector2(0.0,0.0)
        result.x = h00 * p2.x + h10 * m2.x + h01 * p3.x + h11 * m3.x
        result.y = h00 * p2.y + h10 * m2.y + h01 * p3.y + h11 * m3.y
        c.append(result)
        t+=resolution
    out = []

    for point in b:
        out.append(point)
    return out

cdef void *AllocExtra():
    cdef Extra *extra
    extra = <Extra*>malloc(sizeof(Extra))
    memset(extra, 0, sizeof(Extra))
    extra.torches = <Torch*>malloc(sizeof(Torch)*4)
    extra.torchLen = 4
    extra.chests = <Chest*>malloc(sizeof(Chest)*4)
    extra.chestLen = 4
    extra.items = <Item*>malloc(sizeof(Item)*4)
    extra.itemLen = 4
    return <void*>extra
cdef void FreeExtra(void *extra):
    free((<Extra*>extra).chests)
    free((<Extra*>extra).torches)
    free((<Extra*>extra).items)
    free(<Extra*>extra)

cdef Alloc(Octree *parent, int depth):
    parent.parent = NULL
    parent.children = NULL
    parent.filled = OT_EMPTY
    parent.extra = NULL
    if depth == 7:
        return
    else:
        parent.children = <Octree**>malloc(sizeof(Octree*)*8)
        for i in range(8):
            parent.children[i] = <Octree*>malloc(sizeof(Octree))
            Alloc(parent.children[i], depth+1)
            parent.children[i].parent = parent
    if depth == 5:
        parent.extra = AllocExtra()

cdef Octree *GenOctree():
    cdef Octree *root
    root = <Octree*>malloc(sizeof(Octree))

    Alloc(root, 1)
    return root

cdef FreeOctree(Octree *root):
    if root.children:
        for i in range(8):
            FreeOctree(root.children[i])
        free(root.children)
        root.children = NULL
        if root.extra:
            FreeExtra(root.extra)
            root.extra = NULL
    free(root)

import shutil, os

class Quaternion:
    def __init__(self, x = 0, y = 0, z = 0, w = 1):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def Length(self):
        return math.sqrt(self.x**2+self.y**2+self.z**2+self.w**2)

    def Normalized(self):
        len = self.Length()
        try:
            factor = 1.0/len
            x = self.x * factor
            y = self.y * factor
            z = self.z * factor
            w = self.w * factor
        except ZeroDivisionError:
            x = self.x
            y = self.y
            z = self.z
            w = self.w
        return Quaternion(x,y,z,w)


    def CreateFromAxisAngle(self, x, y, z, degrees):
        angle = (degrees / 180.0) * math.pi
        result = math.sin( angle / 2.0 )
        self.w = math.cos( angle / 2.0 )
        self.x = (x * result)
        self.y = (y * result)
        self.z = (z * result)

    def CreateMatrix(self):
        pMatrix = [0 for i in range(16)]
        
        # First row
        pMatrix[ 0] = 1.0 - 2.0 * ( self.y * self.y + self.z * self.z )
        pMatrix[ 1] = 2.0 * (self.x * self.y + self.z * self.w)
        pMatrix[ 2] = 2.0 * (self.x * self.z - self.y * self.w)
        pMatrix[ 3] = 0.0
        
        # Second row
        pMatrix[ 4] = 2.0 * ( self.x * self.y - self.z * self.w )
        pMatrix[ 5] = 1.0 - 2.0 * ( self.x * self.x + self.z * self.z )
        pMatrix[ 6] = 2.0 * (self.z * self.y + self.x * self.w )
        pMatrix[ 7] = 0.0

        # Third row
        pMatrix[ 8] = 2.0 * ( self.x * self.z + self.y * self.w )
        pMatrix[ 9] = 2.0 * ( self.y * self.z - self.x * self.w )
        pMatrix[10] = 1.0 - 2.0 * ( self.x * self.x + self.y * self.y )
        pMatrix[11] = 0.0

        # Fourth row
        pMatrix[12] = 0
        pMatrix[13] = 0
        pMatrix[14] = 0
        pMatrix[15] = 1.0
        return pMatrix


    def Conjugate(self):
        x = -self.x
        y = -self.y
        z = -self.z
        w = self.w
        return Quaternion(x,y,z,w)

    def __mul__(self, quat):
        x = self.w*quat.x + self.x*quat.w + self.y*quat.z - self.z*quat.y;
        y = self.w*quat.y - self.x*quat.z + self.y*quat.w + self.z*quat.x;
        z = self.w*quat.z + self.x*quat.y - self.y*quat.x + self.z*quat.w;
        w = self.w*quat.w - self.x*quat.x - self.y*quat.y - self.z*quat.z;
        return Quaternion(x,y,z,w)

    def __repr__(self):
        return str([self.w, [self.x,self.y,self.z]])
    
    def Dot(self, q):
        q = q.Normalized()
        self = self.Normalized()
        return self.x*q.x + self.y*q.y + self.z*q.z + self.w*q.w

    def Slerp(self, q, t):
        import math
        if t <= 0.0:
            return Quaternion(self.x, self.y, self.z, self.w)
        elif t >= 1.0:
            return Quaternion(q.x, q.y, q.z, q.w)

        cosOmega = self.Dot(q)
        if cosOmega < 0:
            cosOmega = -cosOmega
            q2 = Quaternion(-q.x, -q.y, -q.z, -q.w)
        else:
            q2 = Quaternion(q.x, q.y, q.z, q.w)
        
        if 1.0 - cosOmega > 0.00001:
            omega = math.acos(cosOmega)
            sinOmega = math.sin(omega)
            oneOverSinOmega = 1.0 / sinOmega

            k0 = math.sin((1.0 - t) * omega) / sinOmega
            k1 = math.sin(t * omega) / sinOmega
        else:
            k0 = 1.0 - t
            k1 = t
        return Quaternion(
                (k0 * self.x) + (k1 * q2.x),
                (k0 * self.y) + (k1 * q2.y),
                (k0 * self.z) + (k1 * q2.z),
                (k0 * self.w) + (k1 * q2.w))

import OpenGL.GL as GL
class MapGen:
    HEIGHTS = 0
    def __init__(self):
        self.map = {}
        self.generatedCoords = {}
        self.points = []
        try:
            self.chunkObjs = pickle.load(open("./map/patterns.pkl", "r"))
        except:
            self.chunkObjs = {}

    def GenMap(self, multX, multY): # x,y,z는 4096의 배수이다. 새로 생성할 때마다 주변청크가 있다면 겹치는 2048 영역에도 뭔가 이어서 만든다.
        # 음 또한 하여간에 이미 청크가 있는 영역만 안건드리면 된다.
        # 4096의 의미는 산맥의 전체 길이가 4096을 넘지 않는다는 것 밖에 의미하는 게 없다.
        # 호수 역시 넓어봐야 4096을 넘지 않는다.
        # 기본적으로 이 게임에 호수는 있어도 바다는 없다? 바다 처럼 보이는 해변가도 있지만 바다는 없다. 육지를 기반으로 호수가 잔뜩 있는 맵.
        # 바다를 기반으로 한 게 아님. 바다는 팔 수 없으니까.
        # 아하...........

        # 음. 아 무한맵 만드는 논문 읽어야함 ㅇㅇ
        # 음......맵은 일단 쿼드트리로 terrain을 생성하고
        # 현재 청크와 주변 8개 청크를 기준으로 쿼드트리를 생성한다.
        # 그러다가 옆으로 가게 되면 현재 루트 쿼드트리를 새로운 루트의 차일드 쿼드트리로 바꾸어두고
        # 새로운 맵을 생성.
        # 새로운 맵을 생성할 때에는 4개의 청크를 한번에 생성해서 땅속의 자연 동굴이 256x256의 넓이를 가질 수 있게 한다.
        # 또한, 자연동굴 같은 경우는 이어서 실시간으로 만드는 방법도 있을 것이다.
        # 산맥이나 절벽같은 것도 terrain과는 별개로 해야한다.
        # 아...생성하는 terrain은 128x128일 필요가 없다. 한번에 512x512의 heightmap을 만든다.
        # 산맥/동굴의 높이 값은 height맵을 기준으로 하여 뿌려지겠지만, 맵과는 별개로 만들고
        # 새로운 맵이 만들어질 때마다 랜덤 벡터로 계속 진행하게 한다.
        # overhang은 절벽 오브젝트가 있는 곳에다가 만들면 된다.
        # 절벽 오브젝트는 산이 있는 곳에다가 산의 옆에다가 딱 붙이면 된다.
        # 또는 산의 타입이 전부 절벽, 일부만 절벽 이런 속성을 가지게 하면 될 듯 하다.
        #
        # 아 맵 생성할 때 하잇맵 하지 말고, 산/구덩이 이런식으로 거시적 수준에서 한다.
        # 레이어를 두어서 3개의 레이어가 있는데, 첫번째는 크게 구덩이 파고 산 두고
        # 그 구덩이 판 상태에서 다시 구덩이 안에다가 산을 두거나, 산 위에다가 구덩이를 둘 수 있게 2번째 레이어를 깐다.
        # 3번째 레이어도 그렇게 하고 뭐 그런다.
        #
        # 일단 오브젝트들이 생성되면 그 부분은 더이상 새로운 오브젝트를 만들지 않는다.
        #
        # 음.......실시간 맵생성 뭐 이런거는....... 이미 마인크래프트에서 했자나?
        # 그냥 스태틱 맵으로 해서... 오블리비언 식의 게임을 만들까? 땅을 파는 오블리비언 ㅠㅠ
        # 땅 못파는 영역 몇개 두고 뭐 이래서.
        # 1년동안 열심히 만들어 보자.
        #
        # 음........게임상에서 맵을 수정하기가 쉽도록 하는 펑션들을 만들어야겠다.
        # 그래서 아예 게임상에서 맵을 생성하는 코드를 실행해서 게임 자체에서 맵 에디팅을...
        #
        # 청크단위로 맵을 생성하다 보면 동굴같은 게 두 청크에 이어져있는게 되지 않는다. 라지만,
        # 동굴을 현재 청크까지만 뚫어놓고 새로운 청크 있으면 거기서 이어서 하면 되겠구만? 아하...
        #
        # 특별히 오브젝트가 없어도 맵 가장자리에다가 어떤 동굴 이어짐 오브젝트, 산맥 이어짐 오브젝트를 두고 거기서 이어서 가도록 만들면 된다.
        # 다만, 이미 생성된 청크쪽으로는 갈 수 없다.
        #
        #
        # 그 전에 일단 간단하게 80 높이의 땅만 만들어 보자...;;
        #
        #
        #
        # 동굴:
        # 일단 점이 가진 넓이로 만든다.
        # 그럼 다음 점이 가진 넓이로 이어진다. 다음 점은 45도 이내의 각도이다. 0도로 그대로 이어질 가능성이 50%이다.
        # 밑으로도 내려가고 옆으로도 가고 뭐 이런다.
        #
        # 산:
        # spline을 이용해서 만든다.
        #
        # 일단 산 만들자.
        # 음 근데 gimp등으로 희안한 모양 만들어서 그라디에이션 뿌리면 한방인데 spline을 이용해서 만들 필요가 굳이 있을까 싶다.
        #
        # 미리 패턴들을 만들어두고 그걸 합쳐서 산맥을 만들던지
        # 그런 패턴 자체를 PIL로 만들어서 합치던디 뭐 이러면 될텐데.
        # spline으로 삼각형을 만들어서 그걸 그라디에이션으로 채우면 되는데?
        #
        # 여러 Y수준에서 스플라인을 만들면 기상천외한 모양의 산을 만들 수 있다.
        #
        # 원형이나 여러 형태의 스플라인 곡선들을 쌓아서 산을 만든다.
        # 점들을 어떻게 할까. 줄어드는 각도로 할까? 랜덤하게 줄어드는 각도로 하고 그러다보면 스파이럴이 되던지 만나던지 하겟지.

        q = Quaternion()
        org = Vector2(0.0, 0.0)
        v1 = Vector(1.0, 0.0, 0.0)
        angle = 5
        self.points = []
        self.points += [org]
        while angle <= 270:
            q.CreateFromAxisAngle(0.0,1.0,0.0, angle)
            matrix = q.CreateMatrix()
            v2 = v1.MultMatrix(matrix)
            v2 = Vector2(v2.x,v2.z) * (random.random()+1.0)
            self.points += [self.points[-1]+v2]
            angle += random.randint(5,10)
        # 이걸 float으로 만들어 fillmap에 전달하면 fillmap이 채우는 간단한코드
        #  이걸 C로 옮기면 땡 XX:
        #  음 청크 리스트 역시 뭔가 쿼드트리로 바꿔줘야 하지 않을지. XXX:
        #  너무 많이 로드하면 메모리 모자람 -_-;
        #  현재 한번에 3x3를 로드하는데 대충 4x4정도만 메모리에 가지고 있으면 됨. 더가면 어차피 로드
        #  돌아갈 가능성이 있으니 놔두고
        #
        #  자. 하여간에 그 다음엔 이 만든 산을 거꾸로 파느냐, 높이는 어디서 시작하느냐, 몇배로 늘리느냐, 위치 오프셋은 어디느냐에따라
        #  여러가지 지형이 가능할 것이고
        #  전부 풀땅으로만 채우지 말고 여러가지로 채우고, 밑으로 판 거에는 특히 물 등을 채우고 그러면 바다나 호수가 된다.
        if len(self.points) >= 4:
            1,2,3,4,5,6,7,8
            lines = []
            lines += CatmullRomSpline(self.points[0], self.points[1], self.points[2], self.points[3], 0.01)
            for i in range(len(self.points)-4):
                lines += CatmullRomSpline(self.points[i+1], self.points[i+2], self.points[i+3], self.points[i+4], 0.01)
            lines += CatmullRomSpline(self.points[-3], self.points[-2], self.points[-1] , self.points[0], 0.1)
            lines += CatmullRomSpline(self.points[-2], self.points[-1], self.points[0] , self.points[1], 0.1)
            lines += CatmullRomSpline(self.points[-1], self.points[0], self.points[1] , self.points[2], 0.1)
            #스케일 하고 정렬한다.
            leftMost = lines[0]
            rightMost = lines[0]
            topMost = lines[0]
            bottomMost = lines[0]
            for point in lines:
                if point.x > leftMost.x:
                    leftMost = point
            for point in lines:
                if point.y < topMost.y:
                    topMost = point
            for point in lines:
                if point.x < rightMost.x:
                    rightMost = point
            for point in lines:
                if point.y > bottomMost.y:
                    bottomMost = point
            xdif = leftMost.x
            ydif = bottomMost.y
            lenX = rightMost.x - leftMost.x
            lenY = topMost.y - bottomMost.y
            factorX = multX / lenX
            factorY = multY / lenY
            lines2 = []
            for point in lines:
                point.x -= xdif
                point.y -= ydif
                point.x *= factorX
                point.y *= factorY
                point.x = int(point.x)
                point.y = int(point.y)
                lines2 += [(point.x, point.y)]

            lines2 = list(set(lines2))

            def bubblesort(items):
                swapped = True
                while swapped:
                    swapped = False
                    for i in range(len(items)-1):
                        # 일단 y값이 커야바꾼다.
                        # y값이 같다면 x값으로 바꾼다.
                        if items[i][1] > items[i+1][1]:
                            items[i], items[i+1] = items[i+1], items[i]
                            swapped = True
                        elif items[i][1] == items[i+1][1] and items[i][0] > items[i+1][0]:
                            items[i], items[i+1] = items[i+1], items[i]
                            swapped = True
            bubblesort(lines2)
            mylines = []
            prevX,prevY = lines2[0]
            prevEndX = prevX
            mylines += [(prevX,prevY)]
            odd = False
            for point in lines2[1:]:
                if point[1] != prevY:
                    if len(mylines) >= 2:
                        diff = point[1] - prevY
                        offset = 1
                        a,b = mylines[-2]
                        c,d = mylines[-1]
                        while diff > 1: # diff>=2
                            mylines += [(a, b+offset), (c, d+offset)]
                            diff -= 1
                            offset += 1
                    if not odd:
                        mylines += [(prevX, prevY)]
                        mylines += [(point[0], point[1])]
                        prevEndX = prevX
                    else:
                        mylines += [(prevEndX, prevY)]
                        mylines += [(point[0], point[1])]
                prevX = point[0]
                prevY = point[1]
                odd = not odd
            if not odd: # if even, 근데 왜 안됨?
                mylines += [(prevEndX, prevY)]

            return mylines

        """
        이렇게 만들어진 곡선을 어떻게 렌더링하나?
        원 안에 스캔라인으로 채우는 방식으로 해야하나?
        청크 안에서 딱 맞춰져야 할텐데 이거참. 가장 left right top bottom점을 찾아서 청크에 맞춘 후에
        scale을 적용하고
        catmull로 나온 점들을 라인으로 간주하고는
        그 라인들을 기준으로 폴리곤을 채운다는 발상?
        가장 맨 위의 y값부터 1씩 증가하면서
        가장 왼쪽의 x값을 찾고 가장 오른쪽의 x값을 찾고 스캔라인
        x값은 어떻게 찾나? y값보다 작은 숫자중에 가장 큰 숫자, y값보다 큰 숫자중에 가장 작은 숫자
        그걸 linearinterpolation해서 x값을 얻는다.

        에이...pycairo쓰자^^
        아니다. 그냥 여기서 만든 shape를 맨 윗층에 깔고, 그 아래로 y값은 한칸씩 감소시키고 테두리의 두께를 1씩 증가시키면서 산을 만들면 된다!!!!
        http://www.cs.brown.edu/stc/summer/2ViewRender/2ViewRender_23.html
        X값들의 리스트를 1픽셀 수준에서 만든다.
        odd,even으로 폴리곤의 안쪽인지 바깥쪽인지 본다.
        """

        """
        if (x,y,z) not in self.map:
            self.generatedCoords[(x,y,z)] = None
            #x,y,z에 대해 여러가지 쉐이프라던가 땅의 높이라던가 그런 걸 결정한다.
            # x,y,z를 중심으로 여러가지 뭔가를 깔아두고, 만약 주변이 비어있다면 그 주변과 겹치는 부분에도 뭘 깔고,
            # 만약 주변이 이미 제네레이트 되어 있다면 그 주변과는 겹치게 하지 않는다.
            # 주변이라는 건 x,y,z 즉 Chunk를 각각 분리하는 좌표를 기준으로 한 주변 chunk 영역들.
            # 높이가 서로 다른 부분은 인터폴레이션 영역이 있어서 인터폴레이션 영역안에 있는 건 그 특정한 방법의 인터폴레이션을 사용해서 한다.
            # 음 일단 4방향 동서남북으로 서로 다른 인터폴레이션 방법을 쓰게 하거나, 산맥 같은 경우 산맵이 끝나는 끝지점에 특정한
            # 인터폴레이션 방법을 사용해서 쓴다. 나머지 부분은.... 그냥 1칸씩 점점 올라가는 방법으로 하자.
            size = 128
            self.map[(x,y,z)] = []
            heights = []
            while len(heights) < 8:
                # 바운더리가 생성되어있다면 제한하고 아니라면 제한 안해도 됨
                x,y,z = (random.randint(32,96),random.randint(64,120),random.randint(32,96),)
                rad = random.randint(64,96)
                if x-rad >= 0 and x+rad < 128 and y-rad >= 0 and y+rad < 128 and z-rad >= 0 and z+rad < 128:
                    self.map[(x,y,z)] += [(self.HEIGHTS, (x,y,z), rad)]

            mountains = []
            # 벡터로 진행을 시키면서 패턴들을 연결한다. 아...패턴 쓸 핑요도 없음,
            # rad와 랜덤벡터의 진행으로 한다.
            # 이미 생성된 부분은 피한다.
            # 마운틴은.... 사각형 안에 그냥 넣기엔 좀 그런 듯. 사각형을 완전 벗어남..
            #
            # 마운틴 레인지는 이런식으로 만들면 되겠고.
            # 일반 맵의 높이 등도 달라야 하겠는데 하잇맵 생성을 하자.

            doMts = random.randint(0,1)
            if doMts:
                while len(mountains) < 30:
                    rad = random.randint(10,40)
                    diffx = random.randint(4,32)
                    diffy = random.randint(4,32)
                    height = random.randint(16,32)
                    mountains += [(diffx, diffy, rad)]
        """



        return self.map
    def Save(self):
        pickle.dump(self.chunkObjs, open("./map/patterns.pkl", "w"))
class Vector:
    def __init__(self, x = 0, y = 0, z = 0, w=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def Length(self):
        import math
        return math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)

    def NormalizeByW(self):
        x,y,z,w = self.x,self.y,self.z,self.w
        w = float(w)
        if w == 0.0:
            w = 0.000001
        x /= w
        y /= w
        z /= w
        w = 1.0
        return Vector(x,y,z,w)

    def Normalized(self):
        try:
            newV = self.NormalizeByW()
            factor = 1.0/newV.Length()
            return newV.MultScalar(factor)
        except ZeroDivisionError:
            return Vector(self.x, self.y, self.z, self.w)

    def Cross(self, vector):
        newV = self.NormalizeByW()
        vector = vector.NormalizeByW()
        return Vector(*cross(newV.x,newV.y,newV.z,vector.x,vector.y,vector.z))

    def Dot(self, vector):
        newV = self.NormalizeByW()
        newV = newV.Normalized()
        vector = vector.NormalizeByW()
        vector = vector.Normalized()
        return newV.x*vector.x+newV.y*vector.y+newV.z*vector.z

    def __add__(self, vec):
        newV = self.NormalizeByW()
        vec = vec.NormalizeByW()
        a,b,c = newV.x,newV.y,newV.z
        x,y,z = vec.x,vec.y,vec.z
        return Vector(a+x,b+y,c+z)

    def __sub__(self, vec):
        newV = self.NormalizeByW()
        vec = vec.NormalizeByW()
        a,b,c = newV.x,newV.y,newV.z
        x,y,z = vec.x,vec.y,vec.z
        return Vector(a-x,b-y,c-z)

    def MultScalar(self, scalar):
        newV = self.NormalizeByW()
        return Vector(newV.x*scalar, newV.y*scalar, newV.z*scalar)
    def DivScalar(self, scalar):
        newV = self.NormalizeByW()
        return Vector(newV.x/scalar, newV.y/scalar, newV.z/scalar)
    def __repr__(self):
        return str([self.x, self.y, self.z, self.w])
    
    def MultMatrix(self, mat):
        tempVec = Vector()
        tempVec.x = self.x*mat[0] + self.y*mat[1] + self.z*mat[2] + self.w*mat[3]
        tempVec.y = self.x*mat[4] + self.y*mat[5] + self.z*mat[6] + self.w*mat[7]
        tempVec.z = self.x*mat[8] + self.y*mat[9] + self.z*mat[10] + self.w*mat[11]
        tempVec.w = self.x*mat[12] + self.y*mat[13] + self.z*mat[14] + self.w*mat[15]
        return tempVec

def normalize(x, y, z):
    factor = 1.0/math.sqrt(x**2+y**2+z**2)
    return x*factor, y*factor, z*factor
def cross(x,y,z,x2,y2,z2):
    return ((y*z2-z*y2),(z*x2-x*z2),(x*y2-y*x2))
def dot(x,y,z,x2,y2,z2):
    return x*x2+y*y2+z*z2


cdef class Chunks:
    cdef Chunk **chunks
    cdef Octree **octrees
    
   # cdef float quads[32768*4*3]
   # cdef float texs[32768*4*2]
   # cdef float normals[32768*4*3]
   # cdef unsigned char colors[32768*4*3]
   # cdef int curIdx
    cdef float *tV[64]
    cdef float *tT[64]
    cdef unsigned char *tC[64] # terrain
    cdef int tIdx[64]
    cdef int tLen[64]
    cdef float *nsV[64]
    cdef float *nsT[64]
    cdef unsigned char *nsC[64] # no sun
    cdef int nsIdx[64]
    cdef int nsLen[64]
    cdef float *aV[64]
    cdef float *aT[64]
    cdef unsigned char *aC[64] # alpha
    cdef int aIdx[64]
    cdef int aLen[64]
    cdef float *iV[64]
    cdef float *iT[64]
    cdef unsigned char *iC[64] # item
    cdef int iIdx[64]
    cdef int iLen[64]
    cdef unsigned int indexList[32768*4*3]
    cdef int updateCoords[64*3]
    cdef int lastX
    cdef int lastY
    cdef int lastZ
    mapgen = MapGen()
    curDrawnCoords = [[(-1,-1,-1) for i in range(64)]]
    cdef int curBlock
    def __cinit__(self):
        self.chunks = <Chunk**>malloc(sizeof(Chunk *)*STREAM_BUFFER_LEN)
        self.octrees = <Octree **>malloc(sizeof(Octree *)*STREAM_BUFFER_LEN)
        memset(self.chunks, 0, sizeof(Chunk *)*STREAM_BUFFER_LEN)
        memset(self.octrees, 0, sizeof(Octree *)*STREAM_BUFFER_LEN)
        memset(self.tIdx, 0, sizeof(int)*64)
        memset(self.nsIdx, 0, sizeof(int)*64)
        memset(self.aIdx, 0, sizeof(int)*64)
        memset(self.iIdx, 0, sizeof(int)*64)
        memset(self.tLen, 0, sizeof(int)*64)
        memset(self.nsLen, 0, sizeof(int)*64)
        memset(self.aLen, 0, sizeof(int)*64)
        memset(self.iLen, 0, sizeof(int)*64)
        self.lastX = -1
        self.lastY = -1
        self.lastZ = -1
        self.curBlock = -1

    def __dealloc__(self):
        for i in range(64):
            if self.tLen[i] != 0:
                free(self.tV[i])
                free(self.tT[i])
                free(self.tC[i])
            if self.nsLen[i] != 0:
                free(self.nsV[i])
                free(self.nsT[i])
                free(self.nsC[i])
            if self.aLen[i] != 0:
                free(self.aV[i])
                free(self.aT[i])
                free(self.aC[i])
            if self.iLen[i] != 0:
                free(self.iV[i])
                free(self.iT[i])
                free(self.iC[i])
        for i in range(STREAM_BUFFER_LEN):
            if self.chunks[i]:
                free(self.chunks[i])
                self.chunks[i] = NULL
                FreeOctree(self.octrees[i])
                self.octrees[i] = NULL
        free(self.chunks)
        free(self.octrees)
    def Save(self):
        self.mapgen.Save()
        for i in range(STREAM_BUFFER_LEN):
            if self.chunks[i] and self.octrees[i]:
                self.SaveToDisk(self.chunks[i])
                self.SaveToDiskColor(self.chunks[i])
                self.SaveItems(self.octrees[i], self.chunks[i].x, self.chunks[i].z)
                
    cdef void SaveItems(self, Octree *octree, int x,int z):
        self.SaveTorches(octree, x, z)
        self.SaveChests(octree, x, z)
        #self.SaveOthers(octree, x, z)

    """
    cdef SaveOthers(self, Octree *octree, int x, int z):
        cdef int *buffer
        cdef int bufferLen
        cdef int bufferIdx
        bufferLen = 4
        bufferIdx = 0
        buffer = <int *>malloc(sizeof(int)*bufferLen)
        cdef int xx[7]
        cdef int yy[7]
        cdef int zz[7]
        self.SaveOther(&buffer, &bufferLen, &bufferIdx, octree, xx,yy,zz, 1)

        cdef:
            char fnbuffer[256]
            char *path = "./map/%d/%d.others"
            char *path2 = "./map/%d/%d.otherslen"
            stdio.FILE *fp
        try:
            os.mkdir("./map/%d" % z)
        except:
            pass
        stdio.sprintf(fnbuffer, path, z, x)
        if bufferIdx != 0:
            fp = stdio.fopen(fnbuffer, "wb")
            if fp != NULL:
                stdio.fwrite(buffer, sizeof(int), bufferLen, fp)
                stdio.fclose(fp)

            stdio.sprintf(fnbuffer, path2, z, x)
            fp = stdio.fopen(fnbuffer, "wb")
            if fp != NULL:
                stdio.fwrite(&bufferIdx, sizeof(int), 1, fp)
                stdio.fclose(fp)

        free(buffer)
    """
    cdef SaveChests(self, Octree *octree, int x, int z):
        cdef int *buffer
        cdef int bufferLen
        cdef int bufferIdx
        bufferLen = 4
        bufferIdx = 0
        buffer = <int *>malloc(sizeof(int)*bufferLen)
        cdef int xx[7]
        cdef int yy[7]
        cdef int zz[7]
        self.SaveChest(&buffer, &bufferLen, &bufferIdx, octree, xx,yy,zz, 1)

        cdef:
            char fnbuffer[256]
            char *path = "./map/%d/%d.chests"
            char *path2 = "./map/%d/%d.chestslen"
            stdio.FILE *fp
        try:
            os.mkdir("./map/%d" % z)
        except:
            pass
        stdio.sprintf(fnbuffer, path, z, x)
        if bufferIdx != 0:
            fp = stdio.fopen(fnbuffer, "wb")
            if fp != NULL:
                stdio.fwrite(buffer, sizeof(int), bufferLen, fp)
                stdio.fclose(fp)

            stdio.sprintf(fnbuffer, path2, z, x)
            fp = stdio.fopen(fnbuffer, "wb")
            if fp != NULL:
                stdio.fwrite(&bufferIdx, sizeof(int), 1, fp)
                stdio.fclose(fp)

        free(buffer)
    cdef SaveTorches(self, Octree *octree, int x, int z):
        cdef int *buffer
        cdef int bufferLen
        cdef int bufferIdx
        bufferLen = 4
        bufferIdx = 0
        buffer = <int *>malloc(sizeof(int)*bufferLen)
        cdef int xx[7]
        cdef int yy[7]
        cdef int zz[7]
        self.SaveTorch(&buffer, &bufferLen, &bufferIdx, octree, xx,yy,zz, 1)

        cdef:
            char fnbuffer[256]
            char *path = "./map/%d/%d.torches"
            char *path2 = "./map/%d/%d.torcheslen"
            stdio.FILE *fp
        try:
            os.mkdir("./map/%d" % z)
        except:
            pass
        stdio.sprintf(fnbuffer, path, z, x)
        if bufferIdx != 0:
            fp = stdio.fopen(fnbuffer, "wb")
            if fp != NULL:
                stdio.fwrite(buffer, sizeof(int), bufferLen, fp)
                stdio.fclose(fp)

            stdio.sprintf(fnbuffer, path2, z, x)
            fp = stdio.fopen(fnbuffer, "wb")
            if fp != NULL:
                stdio.fwrite(&bufferIdx, sizeof(int), 1, fp)
                stdio.fclose(fp)

        free(buffer)
    cdef void LoadOther(self, int *bufferIdx, int **tbuffer, int x, int z):
        #f = open("%d_%d_%d", "rb")
        cdef:
            char buffer[256]
            char *path = "./map/%d/%d.others"
            char *path2 = "./map/%d/%d.otherslen"
            stdio.FILE *fp

        bufferIdx[0] = 0
        tbuffer[0] = NULL
        stdio.sprintf(buffer, path2, z, x)
        fp = stdio.fopen(buffer, "rb")
        if fp != NULL:
            stdio.fread(bufferIdx, sizeof(int), 1, fp);
            stdio.fclose(fp)
        else:
            return
        if bufferIdx[0]:
            tbuffer[0] = <int*>malloc(sizeof(int)*bufferIdx[0])
            stdio.sprintf(buffer, path, z, x)
            fp = stdio.fopen(buffer, "rb")
            if fp != NULL:
                stdio.fread(tbuffer[0], sizeof(int), bufferIdx[0], fp)
                stdio.fclose(fp)
            else:
                return
    cdef void LoadChest(self, int *bufferIdx, int **tbuffer, int x, int z):
        #f = open("%d_%d_%d", "rb")
        cdef:
            char buffer[256]
            char *path = "./map/%d/%d.chests"
            char *path2 = "./map/%d/%d.chestslen"
            stdio.FILE *fp

        bufferIdx[0] = 0
        tbuffer[0] = NULL
        stdio.sprintf(buffer, path2, z, x)
        fp = stdio.fopen(buffer, "rb")
        if fp != NULL:
            stdio.fread(bufferIdx, sizeof(int), 1, fp);
            stdio.fclose(fp)
        else:
            return
        if bufferIdx[0]:
            tbuffer[0] = <int*>malloc(sizeof(int)*bufferIdx[0])
            stdio.sprintf(buffer, path, z, x)
            fp = stdio.fopen(buffer, "rb")
            if fp != NULL:
                stdio.fread(tbuffer[0], sizeof(int), bufferIdx[0], fp)
                stdio.fclose(fp)
            else:
                return
    cdef void LoadTorch(self, int *bufferIdx, int **tbuffer, int x, int z):
        #f = open("%d_%d_%d", "rb")
        cdef:
            char buffer[256]
            char *path = "./map/%d/%d.torches"
            char *path2 = "./map/%d/%d.torcheslen"
            stdio.FILE *fp

        bufferIdx[0] = 0
        tbuffer[0] = NULL
        stdio.sprintf(buffer, path2, z, x)
        fp = stdio.fopen(buffer, "rb")
        if fp != NULL:
            stdio.fread(bufferIdx, sizeof(int), 1, fp);
            stdio.fclose(fp)
        else:
            return
        if bufferIdx[0]:
            tbuffer[0] = <int*>malloc(sizeof(int)*bufferIdx[0])
            stdio.sprintf(buffer, path, z, x)
            fp = stdio.fopen(buffer, "rb")
            if fp != NULL:
                stdio.fread(tbuffer[0], sizeof(int), bufferIdx[0], fp)
                stdio.fclose(fp)
            else:
                return



    cdef void GetByPos(self, Chunk * *dstChunk, Octree * *dstOctree, int x,int y,int z):
        for i in range(STREAM_BUFFER_LEN):
            if self.chunks[i]:
                if self.chunks[i].x == x and self.chunks[i].y == y and self.chunks[i].z == z:
                    dstChunk[0] = self.chunks[i]
                    dstOctree[0] = self.octrees[i]
                    return
        dstChunk[0] = NULL
        dstOctree[0] = NULL

    cdef Chunk **GetChunks(self):
        return self.chunks
    cdef Octree * *GetOctrees(self):
        return self.octrees
    cdef void Test1(self):
        cdef unsigned char *chunkData
        chunkData = <unsigned char*>malloc(sizeof(unsigned char)*SIZE_CHUNK)
        cdef Chunk chunk
        chunk.x = 0
        chunk.y = 0
        chunk.z = 0
        chunk.chunk = chunkData
        self.SaveToDisk(&chunk)

    cdef void Test2(self):
        cdef Octree *octree = GenOctree()
        cdef unsigned char *chunkData
        chunkData = <unsigned char*>malloc(sizeof(unsigned char)*SIZE_CHUNK)
        memset(chunkData, 1, sizeof(unsigned char)*SIZE_CHUNK)
        cdef Chunk chunk
        chunk.x = 0
        chunk.y = 0
        chunk.z = 0
        chunk.chunk = chunkData
        self.CalcFilled(&chunk, octree)
        print octree.filled

    cdef Octree * AccessRecur(self, Octree * parent, int curx, int cury, int curz, int targetx, int targety, int targetz, int depth, int targetdepth, int *outx, int *outy, int *outz):
        # target좌표나 curx좌표는 맵 좌표가 아닌 옥트리 로컬 좌표여야 한다. 기본적으로 2x2x2를 리턴하므로 targetx등을 포함하는 2x2x2를 가진 옥트리가 리턴된다.
        cdef int dx, dy, dz
        cdef int octx,octy,octz
        cdef int newx,newy,newz
        cdef int stride = 128
        for i in range(depth):
            stride /= 2

        if depth == targetdepth:
            outx[0] = curx
            outy[0] = cury
            outz[0] = curz
            return parent
        else:
            dx = targetx-curx
            dy = targety-cury
            dz = targetz-curz
            if dx >= stride:
                octx = 1
                newx = curx+stride
            else:
                octx = 0
                newx = curx

            if dy >= stride:
                octy = 1
                newy = cury+stride
            else:
                octy = 0
                newy = cury

            if dz >= stride:
                octz = 1
                newz = curz+stride
            else:
                octz = 0
                newz = curz
            return self.AccessRecur(parent.children[octz*2*2 + octy*2 + octx], newx,newy,newz, targetx,targety,targetz,depth+1,targetdepth, outx, outy, outz)
            #8개 좌표중에 하나를 선택하는 것이다.

    cdef Octree * AccessOctreeWithXYZ(self, Octree * root, int x, int y, int z, int targetdepth, int *newx, int *newy, int *newz):
        return self.AccessRecur(root, 0,0,0,x,y,z,1, targetdepth, newx, newy, newz)
        # 레벨0은 그냥 채우고
        # 레벨1은 for range8로 채우고
        # 레벨2부터는? 상위레벨 8*8번 채우는거네
        #
        # x[7]좌표를 가지고 버퍼에서의 좌표를 알아낼 수 있다면 이것이 가능하다. 어떻게 알아내는가?
        # 아. stride를 이용해서 최상위 stride는 0 그다음엔 1 그다음엔 8 이런식이다.
        # 아 근데......이거 계산하는 거 별로 안느리다. 그냥 로딩/생성시에 팍팍 계산하도록 하자.
    def GenCoords(self, ox,oz,w,h):
        coordsX = []
        coordsZ = []
        firstX = ox-(ox%128)
        firstZ = oz-(oz%128)
        while firstX < ox+w:
            coordsX += [firstX]
            firstX += 128
        while firstZ < oz+h:
            coordsZ += [firstZ]
            firstZ += 128
        return coordsX, coordsZ
    def GenObjs(self, x,y,z, numObjs, wmin, wmax, hmin, hmax, heimin, heimax, upward):
        prevObjs = len(self.mapgen.chunkObjs[(x,y,z)])
        while len(self.mapgen.chunkObjs[(x,y,z)])-prevObjs < numObjs:
            # 음 이렇게 10개 만들지 말고, 일단 한 청크를 다 먹는거 몇개
            # 청크 4개 먹는거 몇개
            # 작은거 몇개 이렇게 하자.
            # lwidth이런거를 청크 크기 나누기 높이로 해줘야함


            # 좌표 자체를 생성할 때 글로벌 좌표로 생성해서
            # 로컬엔 끼워맞추기.
            # 다른데랑 안겹치게 하기 위해 radiusX,Y를 GenMap에서 리턴해야 한다.
            # 그리고는 걍 오프셋 가지고 하면 됨.
            # 이미 있는지 없는지는 chunkObjs를 뒤져서 사각형 충돌로 해본다.
            # 사각형이 만들어내는 청크수준의 사각형들의 좌표가
            # 이미 chunkObjs안에 들어있다면 하지 않는다.
            # 한 번 만들어진 chunkObjs는 즉 계속 세이브파일에 저장된다는 이야기.
            # 음 이거 잘못하면 쓸데없이 시간 엄청 걸릴지도.
            ox, oz, w, h = random.randint(x,x+128), random.randint(z,z+128), random.randint(wmin,wmax), random.randint(hmin,hmax)
            height = random.randint(heimin,heimax)
            cX, cZ = self.GenCoords(ox,oz,w,h)
            found = False
            for cz in cZ:
                for cx in cX:
                    if (cx, 0, cz) in self.mapgen.chunkObjs.iterkeys() and (cx,0,cz) != (x,y,z):
                        found = True
                        break
                if found:
                    break
            if found:
                continue
            lines = self.mapgen.GenMap(w,h)
            self.mapgen.chunkObjs[(x,y,z)] += [(lines, ox,oz,w,h, height, upward)]

    cdef unsigned char * GenChunk(self, int x, int y,int z):
        # 어떤 벡터 기반의 맵 자체를 먼저 생성하고 맵을 기반으로 해서 청크들을 생성해야 한다.
        # 기본적으로 땅을 깔고
        # 산, 산맥, 구덩이, 동굴, 바다, 호수, 폭포 등을 만들고 나무를 뿌려야 한다.
        # 또한 평지인데 서로 다른 높이의 평지 뭐 해안가모래사장 뭐 그런 것들을 만들어야.
        # 
        # 일단 평지부터. 평지는 서로 다른 높이의 원 또는 다각형으로 구성되어 있다. 그걸 군데군데 뿌려서 인터폴레이션으로 높이를 맞춰주거나 기본 평지 레벨에
        # 위에 올리거나 아래로 파거나 이런다.
        # 음..... 원 또는 ellipse로 다 해도 됨. 어차피 구별 안감....
        # 원 ellipse, 변형된 5각형, 스타 모양 등등 여러가지 템플릿으로 한다.
        # Swirl알고리즘을 적용하려면 벡터가 래스터라이즈 되어야 한다. 그런 후에 픽셀 대 픽셀로 해결한다.
        #
        # 음흠 무한맵도 그냥 이 패턴을 까는 방법을 쓰면 계속 깔면서 하면 되겠군.
        #
        # 기본적으로 terrain레이어에 높이값을 가진 shape들
        # 땅속에 몇개의 레이어와 높이값을 가진 여러가지 오브젝트들로 이루어진다.
        # 그걸 기준으로 블럭들을 생성한다.

        cdef unsigned char *chunkData
        cdef int *points
        cdef int lenlines
        chunkData = <unsigned char*>malloc(sizeof(unsigned char)*SIZE_CHUNK)
        #memset(chunkData, 3, sizeof(unsigned char)*SIZE_CHUNK)
        self.mapgen.chunkObjs[(x,y,z)] = []

        print 'start'
            # 음 이렇게 10개 만들지 말고, 일단 한 청크를 다 먹는거 몇개
            # 청크 4개 먹는거 몇개
            # 작은거 몇개 이렇게 하자.
            # lwidth이런거를 청크 크기 나누기 높이로 해줘야함
            #
            # 큰거는 lwidth이런걸 조절
            # 산은 안조절
            # 큰거는 높이를 높게 쌓지 않음 그냥 땅 레벨 조절용임
            # 청크 생성 순서를 좀 잘 잡거나
            # 이전에 생각한 9x9수준으로 옵젝을 만들되, 미리 보이기 전에 생성해서 테두리에 겹치는 건 괜찮도록 한다던지
            # 지금 3x3을 생성하는데 이걸 5x5로만 늘려도 나머지 2x2는 겹쳐지는 부분을 만들거나 할 수 있다.
            # 지금 방법으로 하면 초반 가운데는 겹쳐지는 높낮이 조절이 잘 되는데 점점 넓어질수록...
            # 아 여러가지 방법이 있지만서도 역시 그냥 일단 하자.
            # 이 파는 방법은 바다용으로 적합하고 산같은건 그냥 heightmap이 좋은 것 같다.
            # heightmap연결해서 무한생성하는 방법은 뭐 쉽겠지.
            # 오브젝트 생성 루틴을 여기서 밖으로 조금만 빼도 내가 원하는 거 나온다. 내일 해보자.(무한한 자연스럽게 겹쳐지는 오브젝트들)
            # 4000x4000으로 생성하되 겹쳐지는1000만큼의 2000x2000을 중심으로 또 만들고 이러는거
            #
            # 산은 이정도로 하고 이제 바다, 광물 한 후에
            # 저장/로드 한다.


            # 좌표 자체를 생성할 때 글로벌 좌표로 생성해서
            # 로컬엔 끼워맞추기.
            # 다른데랑 안겹치게 하기 위해 radiusX,Y를 GenMap에서 리턴해야 한다.
            # 그리고는 걍 오프셋 가지고 하면 됨.
            # 이미 있는지 없는지는 chunkObjs를 뒤져서 사각형 충돌로 해본다.
            # 사각형이 만들어내는 청크수준의 사각형들의 좌표가
            # 이미 chunkObjs안에 들어있다면 하지 않는다.
            # 한 번 만들어진 chunkObjs는 즉 계속 세이브파일에 저장된다는 이야기.
            # 음 이거 잘못하면 쓸데없이 시간 엄청 걸릴지도.
        self.GenObjs(x,y,z,3, 64, 512, 64, 512, 2, 4, "Terrain")
        self.GenObjs(x,y,z,3, 64, 128, 64, 128, 20, 40, "Terrain")
        self.GenObjs(x,y,z,3, 64, 128, 64, 128, 4, 16, "Terrain")
        self.GenObjs(x,y,z,10, 8, 64, 8, 64, 4, 20, "Mountain")
        makeWater = random.random()
        if makeWater >= 0.5:
            self.GenObjs(x,y,z,2, 64, 128, 64, 128, 20, 40, "Sea")
        self.GenObjs(x,y,z,10, 8, 32, 8, 32, 1, 4, "Pond")
        """
        제네럴라이즈 하고 바다를 만들고 광물을 만들고
        끝낸다.
        그리고나서 땅파기와 인벤토리를 구현하고 아이템을 구현한다.
        그전에 나무를 구현한다.
        """

        FillMap(chunkData)
        extraLinCrd = []
        for xyz in self.mapgen.chunkObjs:
            if xyz != (x,y,z):
                for linesNcoords in self.mapgen.chunkObjs[xyz]:
                    lines, ox,oz,w,h, height, upward = linesNcoords
                    cX, cZ = self.GenCoords(ox,oz,w,h)
                    for cz in cZ:
                        for cx in cX:
                            if (cx, 0, cz) == (x,y,z):
                                extraLinCrd += [linesNcoords]

        for linesNcoords in self.mapgen.chunkObjs[(x,y,z)] + extraLinCrd:
            lines, ox,oz,w,h, height, type_ = linesNcoords
            lenlines = len(lines)
            lenlines *= 2
            points = <int*>malloc(sizeof(int)*lenlines)
            for i in range(lenlines/2):
                points[i*2] = lines[i][0]
                points[i*2+1] = lines[i][1]
            if type_ == "Terrain":
                FillTerrain(chunkData, points, lenlines, ox-x, 64, oz-z, 1, int(w/(height*2.5))+random.randint(0,3), int(w/(height*2.5))+random.randint(0,3), int(h/(height*2.5))+random.randint(0,3), int(h/(height*2.5))+random.randint(0,3), height, BLOCK_GRASS, BLOCK_DIRT, 0)
            elif type_ == "Mountain":
                FillTerrain(chunkData, points, lenlines, ox-x, 64, oz-z, 1, random.randint(1,4), random.randint(1,4), random.randint(1,4), random.randint(1,4), height, BLOCK_GRASS, BLOCK_DIRT, 0)
            free(points)
        for linesNcoords in self.mapgen.chunkObjs[(x,y,z)] + extraLinCrd:
            lines, ox,oz,w,h, height, type_ = linesNcoords
            lenlines = len(lines)
            lenlines *= 2
            points = <int*>malloc(sizeof(int)*lenlines)
            for i in range(lenlines/2):
                points[i*2] = lines[i][0]
                points[i*2+1] = lines[i][1]
            if type_ == "Pond":
                FillSea(chunkData, points, lenlines, ox-x, 63, oz-z, -1, int(w/(height*2.5))+random.randint(0,3), int(w/(height*2.5))+random.randint(0,3), int(h/(height*2.5))+random.randint(0,3), int(h/(height*2.5))+random.randint(0,3), height, BLOCK_WATER, BLOCK_DIRT, BLOCK_DIRT, 3)
            elif type_ == "Sea":
                FillSea(chunkData, points, lenlines, ox-x, 63, oz-z, -1, int(w/(height*2.5))+random.randint(0,3), int(w/(height*2.5))+random.randint(0,3), int(h/(height*2.5))+random.randint(0,3), int(h/(height*2.5))+random.randint(0,3), height, BLOCK_WATER, BLOCK_SAND, BLOCK_SAND, 20)
            free(points)

        
        # 이제 나무를 생성한다.
        # fillheight을 한 후에 랜덤한 점을 고르고 그게 grass면 그 위에 나무를 짓고 나무의 위치를 저장해서 나무가 겹치지 않게 한다.
        #
        #
        #
            # 이제 여기서 heightmap을 생성하고 FillMap에서 한번에 채운다.
            # 음 생성한 원을 바다로 쓸지 뭘로 쓸지는 어떻게 결정?
            # 또한.... 밑으로 팠는데 옆에 또 밑으로 판 놈이 있어서 뚫리면 그것도 바다가 될텐데.
            # 밑으로 파는 것들 중에서 겹치는게 있는지 없는지를 보고 바다를 잘 만들어야 한다.
            # 아하. 밑으로 파면 무조건 바다, 위로 쌓으면 무조건 산? 그건 아니지. 음...
            # 아 이러면 되겠다. 바다는 무조건 가장 나중에 만든다.
            # 두 개 이상의 원을 겹쳐서 바다를 만들 수도 있음.
        # 이 points가 다른 생성도지 않은 청크와 겹쳐지는 경우 저장해둔다. 파일로.
        # 그리고 생성될 때 쓰고는 생성이 끝나면 지운다. XXX:
        # 처음에 생각한대로 여러가지 산 골짜기를 겹치게 하고
        # 앞으로 생성할 청크들에 대한 맵 오브젝트만 만들 후에
        # 실시간 생성할 때마다 새롭게 맵 오브젝트를 더 생성한다.
        #
        # 일단 현재 생성하는 청크에 대한 오브젝트만 생성한다.
        # 다른 청크와 겹치는 부분은 저장해둔다.
        # 다음 청크가 할 때 이거와 겹치는 부분을 내 위치에도 그린다.
        # 이미 생성된 청크와 겹치는 부분은 절대 만들지 않는다.
        # 가장 높은 위치나 낮은 위치는 여기에서 계산해 낸다?
        # 아. height 계산하는걸 FillTerrain할 때마다 해야할지도.
        # 그래서 height값으로 가장 높거나 낮은 위치를 쿼드 사각형 내에서 검색해야 한다.
        # 하지만.. fill되지 않은 terrain에 대한 높이값은 어떻게 함?
        #
        # 아...... 이러지 말고 모든 terrain관련 업앤다운을 heightmap에 합친 후에
        # 그 heightmap을 최종적으로 블럭으로 렌더링하면 되겠구나.....
        # 3개의 맵을 겹쳤다면 grass밑에 dirt레벨이 3개 뭐 이런식으로 땅이 드러나지 않도록 할 수 있을 것 같다.
        # 돌산인 경우 상관없음
        # 원으로 height맵도 만들지만 원으로 영역표시도 하게 한다.
        # 표시가 안되면 grass
        # 돌이냐
        # 모래냐 정도만 있으면 될 것 같다.
        #
        #FillTerrain(chunkData, points, lenlines, 64, 63, 0, 1, 2, 1, 3, 3, 20)
        print 'end'
        return chunkData

    cdef unsigned char *LoadFromDiskColor(self, int x, int y, int z):
        #f = open("%d_%d_%d", "rb")
        cdef:
            char buffer[256]
            char *path = "./map/%d/%d.colors"
            unsigned char *chunkData
            stdio.FILE *fp
        chunkData = <unsigned char*>malloc(sizeof(unsigned char)*SIZE_CHUNK)
        if chunkData == NULL:
            assert False, "Not enough memory"
        stdio.sprintf(buffer, path, z, x)
        fp = stdio.fopen(buffer, "rb")
        if fp != NULL:
            stdio.fread(chunkData, sizeof(unsigned char), SIZE_CHUNK, fp);
            stdio.fclose(fp)
        else:
            return NULL
        return chunkData

    cdef unsigned char *LoadFromDisk(self, int x, int y, int z):
        #f = open("%d_%d_%d", "rb")
        cdef:
            char buffer[256]
            char *path = "./map/%d/%d"
            unsigned char *chunkData
            stdio.FILE *fp
        chunkData = <unsigned char*>malloc(sizeof(unsigned char)*SIZE_CHUNK)
        if chunkData == NULL:
            assert False, "Not enough memory"
        stdio.sprintf(buffer, path, z, x)
        fp = stdio.fopen(buffer, "rb")
        if fp != NULL:
            stdio.fread(chunkData, sizeof(unsigned char), SIZE_CHUNK, fp);
            stdio.fclose(fp)
        else:
            return NULL
        return chunkData

    cdef void SaveToDiskColor(self, Chunk * chunk):
        if not chunk:
            assert False, "NULL chunk detected"
        cdef:
            char buffer[256]
            char *path = "./map/%d/%d.colors"
            stdio.FILE *fp
        try:
            os.mkdir("./map/%d" % chunk.z)
        except:
            pass
        stdio.sprintf(buffer, path, chunk.z, chunk.x)
        fp = stdio.fopen(buffer, "wb")
        if fp != NULL:
            stdio.fwrite(chunk.colors, sizeof(unsigned char), SIZE_CHUNK, fp)
            stdio.fclose(fp)
    cdef void SaveToDisk(self, Chunk * chunk):
        if not chunk:
            assert False, "NULL chunk detected"
        cdef:
            char buffer[256]
            char *path = "./map/%d/%d"
            stdio.FILE *fp
        try:
            os.mkdir("./map/%d" % chunk.z)
        except:
            pass
        stdio.sprintf(buffer, path, chunk.z, chunk.x)
        fp = stdio.fopen(buffer, "wb")
        if fp != NULL:
            stdio.fwrite(chunk.chunk, sizeof(unsigned char), SIZE_CHUNK, fp)
            stdio.fclose(fp)

    cdef void UnloadChunkOctree(self, Chunk * chunk):
        if not chunk:
            assert False, "NULL chunk detected"
        free(chunk.chunk) # char * buffer
        free(chunk.colors) # char * buffer
        free(chunk.heights)
        for i in range(STREAM_BUFFER_LEN):
            if self.chunks[i] == chunk:
                free(self.chunks[i]) # chunk structure itself
                self.chunks[i] = NULL
                FreeOctree(self.octrees[i])
                self.octrees[i] = NULL
                return

    cdef void CalcFilled(self, Chunk * chunk, Octree *octree):
        CalcRecursive(chunk, octree, 0, 0, 0, 1)
        # 일단 옥트리의 가장 깊은 레벨로 가서 그 옥트리의 좌표에 맞는 2x2x2를 검사한다.

    cdef int IsOpaque(self, unsigned char block_id):
        if block_id == BLOCK_EMPTY:
            return False
        else:
            return True
    cdef int IsWaterGlass(self, unsigned char block_id):
        if block_id == BLOCK_WATER or block_id == BLOCK_GLASS:
            return True
        else:
            return False
    cdef void GetOctreesByViewpoint(self, int pos[9][3], Octree * outOctrees[9], Chunk * outChunks[9], int x, int y, int z):
        # 청크의 x=0,y=0,z=0에서 청크의 위치가 기록된다.
        cdef Chunk * chunk
        cdef Octree * octree
        cdef unsigned char *chunkData 
        cdef char treePoints[1000]
        cdef int *tbuffer
        cdef int bufferIdx
        self.GetOctreePositionsByVP(pos, x, y, z)
        vx = x-(x%128)
        vz = z-(z%128)

        # XXX: 여기서 현재 뷰포인트보다 3칸 차이나는 것들을 언로드하는 걸 구현한다.
        # X로 3칸 Z로3칸. 그리고 청크를 생성하면 바로 저장하는 것도 구현?
        stride = 4
        for i in range(STREAM_BUFFER_LEN):
            if self.chunks[i]:
                chunk = self.chunks[i]
                if chunk.x <= vx-stride*128:
                    self.SaveToDisk(self.chunks[i])
                    self.SaveToDiskColor(self.chunks[i])
                    self.SaveItems(self.octrees[i], self.chunks[i].x, self.chunks[i].z)
                    self.UnloadChunkOctree(chunk)
                elif chunk.x >= vx+stride*128:
                    self.SaveToDisk(self.chunks[i])
                    self.SaveToDiskColor(self.chunks[i])
                    self.SaveItems(self.octrees[i], self.chunks[i].x, self.chunks[i].z)
                    self.UnloadChunkOctree(chunk)
                elif chunk.z <= vz-stride*128:
                    self.SaveToDisk(self.chunks[i])
                    self.SaveToDiskColor(self.chunks[i])
                    self.SaveItems(self.octrees[i], self.chunks[i].x, self.chunks[i].z)
                    self.UnloadChunkOctree(chunk)
                elif chunk.z >= vz+stride*128:
                    self.SaveToDisk(self.chunks[i])
                    self.SaveToDiskColor(self.chunks[i])
                    self.SaveItems(self.octrees[i], self.chunks[i].x, self.chunks[i].z)
                    self.UnloadChunkOctree(chunk)


        for i in range(TEST_SIZE):
            self.GetByPos(&chunk, &octree, pos[i][0],0,pos[i][2])
            if chunk and octree:
                outChunks[i] = chunk
                outOctrees[i] = octree
            else:
                chunkData = self.LoadFromDisk(pos[i][0], 0, pos[i][2])
                if chunkData == NULL:
                    chunkData = self.GenChunk(pos[i][0], 0, pos[i][2])
                    chunk = <Chunk *>malloc(sizeof(Chunk))
                    chunk.chunk = chunkData
                    chunk.heights = <char*>malloc(sizeof(char)*128*128)
                    chunk.colors = <unsigned char*>malloc(sizeof(unsigned char)*128*128*128)
                    memset(chunk.colors, 0, sizeof(unsigned char)*128*128*128)
                    chunk.x = pos[i][0]
                    chunk.y = 0
                    chunk.z = pos[i][2]
                    FillHeights(chunk)
                    trees = self.GenTrees()
                    idx = 0;
                    for tree in trees:
                        treePoints[idx*2] = tree[0]
                        treePoints[idx*2+1] = tree[1]
                        idx += 1
                    FillTrees(chunk, treePoints)
                else:
                    chunk = <Chunk *>malloc(sizeof(Chunk))
                    chunk.chunk = chunkData
                    chunk.heights = <char*>malloc(sizeof(char)*128*128)
                    chunk.colors = self.LoadFromDiskColor(pos[i][0], 0, pos[i][2])
                    if chunk.colors == NULL:
                        chunk.colors = <unsigned char*>malloc(sizeof(unsigned char)*128*128*128)
                        memset(chunk.colors, 0, sizeof(unsigned char)*128*128*128)
                    chunk.x = pos[i][0]
                    chunk.y = 0
                    chunk.z = pos[i][2]

                octree = GenOctree()
                FillHeights(chunk)
                self.CalcFilled(chunk, octree)
                self.PutChunkIntoList(chunk, octree)


                self.LoadTorch(&bufferIdx, &tbuffer, pos[i][0], pos[i][2])
                if bufferIdx:
                    j = 0
                    while j < bufferIdx:
                        self.AddTorch2(octree, tbuffer[j], tbuffer[j+1], tbuffer[j+2], pos[i][0], 0, pos[i][2], tbuffer[j+3] )
                        j += 4
                    free(tbuffer)
                self.LoadChest(&bufferIdx, &tbuffer, pos[i][0], pos[i][2])
                if bufferIdx:
                    j = 0
                    while j < bufferIdx:
                        self.AddChest2(octree, tbuffer[j], tbuffer[j+1], tbuffer[j+2], pos[i][0], 0, pos[i][2], tbuffer[j+3] )
                        j += 4
                    free(tbuffer)

                outChunks[i] = chunk
                outOctrees[i] = octree

    def GenTrees(self):
        trees = []
        startZ = 4
        while startZ < 114:
            strideZ = random.randint(7,10)
            startX = 4
            while startX < 114:
                strideX = random.randint(7,10)
                newX = random.randint(startX+2,startX+strideX-2)
                newZ = random.randint(startZ+2,startZ+strideZ-2)
                trees += [(newX,newZ)]
                startX += strideX
            startZ += strideZ
        return trees

    """
    cdef void SaveOther(self, int **buffer, int *bufferLen, int *bufferIdx, Octree * parent, int x[7], int y[7], int z[7], int depth):
        cdef int stride = 128
        cdef int bufferOffset = 0
        cdef int bufferSize = 1
        cdef int depthOffset = 2**(depth-1)
        cdef int cx,cy,cz
        cdef Extra *extra
        for i in range(depth-1):
            bufferOffset += bufferSize
            bufferSize *= 8
        for i in range(depth-1):
            stride /= 2
        cx, cy, cz = 0, 0, 0
        for i in range(depth-1):
            cx += x[i]*2
            cy += y[i]*2
            cz += z[i]*2
        cdef int *save
        save = buffer[0]

        if depth == 5:
            extra = <Extra*>parent.extra
            for i in range(extra.itemIdx):
                if bufferIdx[0]+4 >= bufferLen[0]:
                    bufferLen[0] *= 2
                    buffer[0] = <int *>realloc(save, sizeof(int)*bufferLen[0])
                    save = buffer[0]
                save[bufferIdx[0]] = extra.items[i].type
                save[bufferIdx[0]+1] = extra.items[i].x
                save[bufferIdx[0]+2] = extra.items[i].y
                save[bufferIdx[0]+3] = extra.items[i].z
                save[bufferIdx[0]+4] = extra.items[i].idx
                bufferIdx[0] += 5
        if depth < 5:
            for k in range(2):
                for j in range(2):
                    for i in range(2):
                        x[depth] = i
                        y[depth] = j
                        z[depth] = k
                        self.SaveOther(buffer, bufferLen, bufferIdx, parent.children[k*2*2+j*2+i], x,y,z, depth+1)
    """

    cdef void SaveChest(self, int **buffer, int *bufferLen, int *bufferIdx, Octree * parent, int x[7], int y[7], int z[7], int depth):
        cdef int stride = 128
        cdef int bufferOffset = 0
        cdef int bufferSize = 1
        cdef int depthOffset = 2**(depth-1)
        cdef int cx,cy,cz
        cdef Extra *extra
        for i in range(depth-1):
            bufferOffset += bufferSize
            bufferSize *= 8
        for i in range(depth-1):
            stride /= 2
        cx, cy, cz = 0, 0, 0
        for i in range(depth-1):
            cx += x[i]*2
            cy += y[i]*2
            cz += z[i]*2
        cdef int *save
        save = buffer[0]

        if depth == 5:
            extra = <Extra*>parent.extra
            for i in range(extra.chestIdx):
                if bufferIdx[0]+3 >= bufferLen[0]:
                    bufferLen[0] *= 2
                    buffer[0] = <int *>realloc(save, sizeof(int)*bufferLen[0])
                    save = buffer[0]
                save[bufferIdx[0]] = extra.chests[i].x
                save[bufferIdx[0]+1] = extra.chests[i].y
                save[bufferIdx[0]+2] = extra.chests[i].z
                save[bufferIdx[0]+3] = extra.chests[i].frontFacing
                bufferIdx[0] += 4
        if depth < 5:
            for k in range(2):
                for j in range(2):
                    for i in range(2):
                        x[depth] = i
                        y[depth] = j
                        z[depth] = k
                        self.SaveChest(buffer, bufferLen, bufferIdx, parent.children[k*2*2+j*2+i], x,y,z, depth+1)

    cdef void SaveTorch(self, int **buffer, int *bufferLen, int *bufferIdx, Octree * parent, int x[7], int y[7], int z[7], int depth):
        cdef int stride = 128
        cdef int bufferOffset = 0
        cdef int bufferSize = 1
        cdef int depthOffset = 2**(depth-1)
        cdef int cx,cy,cz
        cdef Extra *extra
        for i in range(depth-1):
            bufferOffset += bufferSize
            bufferSize *= 8
        for i in range(depth-1):
            stride /= 2
        cx, cy, cz = 0, 0, 0
        for i in range(depth-1):
            cx += x[i]*2
            cy += y[i]*2
            cz += z[i]*2
        cdef int *save
        save = buffer[0]

        if depth == 5:
            extra = <Extra*>parent.extra
            for i in range(extra.torchIdx):
                if bufferIdx[0]+3 >= bufferLen[0]:
                    bufferLen[0] *= 2
                    buffer[0] = <int *>realloc(save, sizeof(int)*bufferLen[0])
                    save = buffer[0]
                save[bufferIdx[0]] = extra.torches[i].x
                save[bufferIdx[0]+1] = extra.torches[i].y
                save[bufferIdx[0]+2] = extra.torches[i].z
                save[bufferIdx[0]+3] = extra.torches[i].face
                bufferIdx[0] += 4
        if depth < 5:
            for k in range(2):
                for j in range(2):
                    for i in range(2):
                        x[depth] = i
                        y[depth] = j
                        z[depth] = k
                        self.SaveTorch(buffer, bufferLen, bufferIdx, parent.children[k*2*2+j*2+i], x,y,z, depth+1)

    cdef void SerializeOctree(self, unsigned char *buffer, Octree * parent, int x[7], int y[7], int z[7], int depth):
        cdef int stride = 128
        cdef int bufferOffset = 0
        cdef int bufferSize = 1
        cdef int depthOffset = 2**(depth-1)
        cdef int cx,cy,cz
        for i in range(depth-1):
            bufferOffset += bufferSize
            bufferSize *= 8
        for i in range(depth-1):
            stride /= 2
        cx, cy, cz = 0, 0, 0
        for i in range(depth-1):
            cx += x[i]*2
            cy += y[i]*2
            cz += z[i]*2

        buffer[bufferOffset + cz*depthOffset*depthOffset + cy*depthOffset + cz] = parent.filled
        if depth < 7:
            for k in range(2):
                for j in range(2):
                    for i in range(2):
                        x[depth] = i
                        y[depth] = j
                        z[depth] = k
                        self.SerializeOctree(buffer, parent.children[k*2*2+j*2+i], x,y,z, depth+1)

    cdef void LoadOctreeFromBuffer(self, unsigned char *buffer, Octree * parent, int x[7], int y[7], int z[7], int depth):
        cdef int stride = 128
        cdef int bufferOffset = 0
        cdef int bufferSize = 1
        cdef int depthOffset = 2**(depth-1)
        cdef int cx,cy,cz
        for i in range(depth-1):
            bufferOffset += bufferSize
            bufferSize *= 8
        for i in range(depth-1):
            stride /= 2
        cx, cy, cz = 0, 0, 0
        for i in range(depth-1):
            cx += x[i]*2
            cy += y[i]*2
            cz += z[i]*2

        parent.filled = <OctreeFilledFlag>buffer[bufferOffset + cz*depthOffset*depthOffset + cy*depthOffset + cz]
        if depth < 7:
            for k in range(2):
                for j in range(2):
                    for i in range(2):
                        x[depth] = i
                        y[depth] = j
                        z[depth] = k
                        self.LoadOctreeFromBuffer(buffer, parent.children[k*2*2+j*2+i], x,y,z, depth+1)

    cdef void GetOneOctreePositionsByVP(self, int outPos[3], int x, int y, int z):
        cdef int posx, posz
        posx = x - (x%128)
        posz = z - (z%128)
        outPos[0] = posx
        outPos[1] = 0
        outPos[2] = posz

    cdef void GetOctreePositionsByVP(self, int outPos[9][3], int x, int y, int z):
        cdef int posx, posz
        posx = x - (x%128)
        posz = z - (z%128)

        outPos[4][0] = posx-128
        outPos[4][1] = 0
        outPos[4][2] = posz-128

        outPos[0][0] = posx
        outPos[0][1] = 0
        outPos[0][2] = posz-128

        outPos[2][0] = posx+128
        outPos[2][1] = 0
        outPos[2][2] = posz-128

        outPos[3][0] = posx-128
        outPos[3][1] = 0
        outPos[3][2] = posz

        outPos[1][0] = posx
        outPos[1][1] = 0
        outPos[1][2] = posz

        outPos[5][0] = posx+128
        outPos[5][1] = 0
        outPos[5][2] = posz

        outPos[6][0] = posx-128
        outPos[6][1] = 0
        outPos[6][2] = posz+128

        outPos[7][0] = posx
        outPos[7][1] = 0
        outPos[7][2] = posz+128

        outPos[8][0] = posx+128
        outPos[8][1] = 0
        outPos[8][2] = posz+128

    cdef void CalcRecursive(self, Chunk * chunk, Octree *octree, int x, int y, int z, int depth):
        cdef int stride = 128
        for i in range(depth):
            stride /= 2
        cdef int notFilledFound = 0
        cdef int notFilledEmptyCount = 0
        cdef int waterGlassCount = 0
        cdef int partTrans = 0
        # 이제 여기서 좀 비어도 X쪽으로는 블럭, Y쪽으로는 블럭, Z쪽으로는 블럭 등을 검사한다.
        # 기본적으로 지그재그로 꽉차있으면 블럭이다.
        # xz평면에서 y값 무시하고 꽉차있으면 y축으로 블럭이다.
        # 투명값이 좀 있어도 막혀있으면 막힌거
        cdef int xblock[4] # 왼쪽에서 +z를 오른쪽에 두고 -y를 아래에 두고 바라볼 때
        # 앞에서 봤을 때 [0] 위뒤 [1]위앞 [2]아래뒤 [3]아래앞
        cdef int yblock[4] # 위에서 -z를 위에 두고 +x를 오른쪽에 두고 바라볼 때
        # 앞에서 봤을 땐 [0] 왼뒤 [1] 오른뒤 [2]왼앞 [3] 오른앞
        cdef int zblock[4] # 앞에서 +x오른 +y위
        # [0] 왼위 [1] 오른위 [2] 왼아래 [3] 오른아래
        for i in range(4):
            xblock[i] = 0
            yblock[i] = 0
            zblock[i] = 0

        cdef int xfound
        cdef int yfound
        cdef int zfound
        xfound = True
        yfound = True
        zfound = True
        cdef int xb[2][2]
        cdef int yb[2][2]
        cdef int zb[2][2]

        if depth >= 7:
            for k in range(2):
                for j in range(2):
                    for i in range(2):
                        if not self.IsOpaque(chunk.chunk[((z+k)*128*128) + (y+j)*128 + x+i]): # empty
                            # 물이나 유리도 투명하지만, 오로지 주변에 물이나 유리, 빈공간이 있을 경우에만 그린다.
                            # 으... 옥트리에서 이건 어떻게 표현하나?
                            # COMPLETEWATER?
                            # PARTWATER?
                            notFilledFound = 1
                            notFilledEmptyCount += 1
                        elif self.IsWaterGlass(chunk.chunk[((z+k)*128*128) + (y+j)*128 + x+i]): # transparent
                            waterGlassCount += 1
                        else: #opaque
                            if i == 0 and j == 0 and k == 0: # 왼쪽아래뒷면
                                xblock[2] = 1
                                yblock[0] = 1
                                zblock[2] = 1
                            elif i == 1 and j == 0 and k == 0: # 오른쪽아래뒷면
                                xblock[2] = 1
                                yblock[1] = 1
                                zblock[3] = 1
                            elif i == 0 and j == 1 and k == 0: #왼쪽위뒤
                                xblock[0] = 1
                                yblock[0] = 1
                                zblock[0] = 1
                            elif i == 0 and j == 0 and k == 1: #왼쪽아래앞
                                xblock[3] = 1
                                yblock[2] = 1
                                zblock[2] = 1
                            elif i == 1 and j == 1 and k == 0: # 오른쪽위뒤
                                xblock[0] = 1
                                yblock[1] = 1
                                zblock[1] = 1
                            elif i == 0 and j == 1 and k == 1: # 왼쪽위앞
                                xblock[1] = 1
                                yblock[2] = 1
                                zblock[0] = 1
                            elif i == 1 and j == 0 and k == 1: # 오른쪽아래앞
                                xblock[3] = 1
                                yblock[3] = 1
                                zblock[3] = 1
                            elif i == 1 and j == 1 and k == 1: # 오른쪽위앞
                                xblock[1] = 1
                                yblock[3] = 1
                                zblock[1] = 1

            if notFilledEmptyCount == 8:
                octree.filled = OT_EMPTY
            elif notFilledFound == 1:
                octree.filled = OT_HALFFILLED
            else:
                octree.filled = OT_FILLED

            if waterGlassCount == 8:
                octree.filled = OT_COMPLETETRANSPARENT
            elif waterGlassCount > 0:
                octree.filled |= OT_PARTTRANSPARENT

            for i in range(4):
                if xblock[i] == 0:
                    xfound = False
                if yblock[i] == 0:
                    yfound = False
                if zblock[i] == 0:
                    zfound = False
            if xfound:
                octree.filled |= OT_XBLOCK
            if yfound:
                octree.filled |= OT_YBLOCK
            if zfound:
                octree.filled |= OT_ZBLOCK
        else:
            for j in range(2):
                for i in range(2):
                    xb[i][j] = 0
                    yb[i][j] = 0
                    zb[i][j] = 0
            if octree.children: # 사실 이건 필요가 없음
                for k in range(2):
                    for j in range(2):
                        for i in range(2):
                            CalcRecursive(chunk, octree.children[k*2*2+j*2+i], x+(i*stride), y+(j*stride), z+(k*stride), depth+1)

                for k in range(2):
                    for j in range(2):
                        for i in range(2):
                            if octree.children[k*2*2+j*2+i].filled & OT_HALFFILLED:
                                notFilledFound = 1
                            if octree.children[k*2*2+j*2+i].filled & OT_EMPTY:
                                notFilledFound = 1
                                notFilledEmptyCount += 1
                            if octree.children[k*2*2+j*2+i].filled & OT_PARTTRANSPARENT:
                                partTrans = 1
                            if octree.children[k*2*2+j*2+i].filled & OT_COMPLETETRANSPARENT:
                                waterGlassCount += 1
                            if octree.children[k*2*2+j*2+i].filled & OT_FILLED:
                                pass
                            else:
                                notFilledFound = 1

                            # xblock이 각기 서로 다른 j,k값에서 다 나오기만 하면 된다.
                            if octree.children[k*2*2+j*2+i].filled & OT_XBLOCK:
                                xb[j][k] = 1
                            if octree.children[k*2*2+j*2+i].filled & OT_YBLOCK:
                                yb[i][k] = 1
                            if octree.children[k*2*2+j*2+i].filled & OT_ZBLOCK:
                                zb[i][j] = 1

                if notFilledEmptyCount == 8:
                    octree.filled = OT_EMPTY
                elif notFilledFound == 1:
                    octree.filled = OT_HALFFILLED
                else:
                    octree.filled = OT_FILLED

                if waterGlassCount == 8:
                    octree.filled = OT_COMPLETETRANSPARENT
                elif waterGlassCount > 0 or partTrans:
                    octree.filled |= OT_PARTTRANSPARENT

                for j in range(2):
                    for i in range(2):
                        if xb[i][j] == 0:
                            xfound = False
                        if yb[i][j] == 0:
                            yfound = False
                        if zb[i][j] == 0:
                            zfound = False

                if xfound:
                    octree.filled |= OT_XBLOCK
                if yfound:
                    octree.filled |= OT_YBLOCK
                if zfound:
                    octree.filled |= OT_ZBLOCK


    cdef void CalcOne(self, Chunk * chunk, Octree *octree, int x, int y, int z, int depth):
        cdef int stride = 128
        for i in range(depth):
            stride /= 2
        cdef int notFilledFound = 0
        cdef int notFilledEmptyCount = 0
        cdef int waterGlassCount = 0
        cdef int partTrans = 0
        # 이제 여기서 좀 비어도 X쪽으로는 블럭, Y쪽으로는 블럭, Z쪽으로는 블럭 등을 검사한다.
        # 기본적으로 지그재그로 꽉차있으면 블럭이다.
        # xz평면에서 y값 무시하고 꽉차있으면 y축으로 블럭이다.
        # 투명값이 좀 있어도 막혀있으면 막힌거
        cdef int xblock[4] # 왼쪽에서 +z를 오른쪽에 두고 -y를 아래에 두고 바라볼 때
        # 앞에서 봤을 때 [0] 위뒤 [1]위앞 [2]아래뒤 [3]아래앞
        cdef int yblock[4] # 위에서 -z를 위에 두고 +x를 오른쪽에 두고 바라볼 때
        # 앞에서 봤을 땐 [0] 왼뒤 [1] 오른뒤 [2]왼앞 [3] 오른앞
        cdef int zblock[4] # 앞에서 +x오른 +y위
        # [0] 왼위 [1] 오른위 [2] 왼아래 [3] 오른아래
        for i in range(4):
            xblock[i] = 0
            yblock[i] = 0
            zblock[i] = 0

        cdef int xfound
        cdef int yfound
        cdef int zfound
        xfound = True
        yfound = True
        zfound = True
        cdef int xb[2][2]
        cdef int yb[2][2]
        cdef int zb[2][2]

        if depth >= 7:
            for k in range(2):
                for j in range(2):
                    for i in range(2):
                        if not self.IsOpaque(chunk.chunk[((z+k)*128*128) + (y+j)*128 + x+i]): # empty
                            # 물이나 유리도 투명하지만, 오로지 주변에 물이나 유리, 빈공간이 있을 경우에만 그린다.
                            # 으... 옥트리에서 이건 어떻게 표현하나?
                            # COMPLETEWATER?
                            # PARTWATER?
                            notFilledFound = 1
                            notFilledEmptyCount += 1
                        elif self.IsWaterGlass(chunk.chunk[((z+k)*128*128) + (y+j)*128 + x+i]): # transparent
                            waterGlassCount += 1
                        else: #opaque
                            if i == 0 and j == 0 and k == 0: # 왼쪽아래뒷면
                                xblock[2] = 1
                                yblock[0] = 1
                                zblock[2] = 1
                            elif i == 1 and j == 0 and k == 0: # 오른쪽아래뒷면
                                xblock[2] = 1
                                yblock[1] = 1
                                zblock[3] = 1
                            elif i == 0 and j == 1 and k == 0: #왼쪽위뒤
                                xblock[0] = 1
                                yblock[0] = 1
                                zblock[0] = 1
                            elif i == 0 and j == 0 and k == 1: #왼쪽아래앞
                                xblock[3] = 1
                                yblock[2] = 1
                                zblock[2] = 1
                            elif i == 1 and j == 1 and k == 0: # 오른쪽위뒤
                                xblock[0] = 1
                                yblock[1] = 1
                                zblock[1] = 1
                            elif i == 0 and j == 1 and k == 1: # 왼쪽위앞
                                xblock[1] = 1
                                yblock[2] = 1
                                zblock[0] = 1
                            elif i == 1 and j == 0 and k == 1: # 오른쪽아래앞
                                xblock[3] = 1
                                yblock[3] = 1
                                zblock[3] = 1
                            elif i == 1 and j == 1 and k == 1: # 오른쪽위앞
                                xblock[1] = 1
                                yblock[3] = 1
                                zblock[1] = 1

            if notFilledEmptyCount == 8:
                octree.filled = OT_EMPTY
            elif notFilledFound == 1:
                octree.filled = OT_HALFFILLED
            else:
                octree.filled = OT_FILLED

            if waterGlassCount == 8:
                octree.filled = OT_COMPLETETRANSPARENT
            elif waterGlassCount > 0:
                octree.filled |= OT_PARTTRANSPARENT

            for i in range(4):
                if xblock[i] == 0:
                    xfound = False
                if yblock[i] == 0:
                    yfound = False
                if zblock[i] == 0:
                    zfound = False
            if xfound:
                octree.filled |= OT_XBLOCK
            if yfound:
                octree.filled |= OT_YBLOCK
            if zfound:
                octree.filled |= OT_ZBLOCK
        else:
            for j in range(2):
                for i in range(2):
                    xb[i][j] = 0
                    yb[i][j] = 0
                    zb[i][j] = 0
            for k in range(2):
                for j in range(2):
                    for i in range(2):
                        if octree.children[k*2*2+j*2+i].filled & OT_HALFFILLED:
                            notFilledFound = 1
                        if octree.children[k*2*2+j*2+i].filled & OT_EMPTY:
                            notFilledFound = 1
                            notFilledEmptyCount += 1
                        if octree.children[k*2*2+j*2+i].filled & OT_FILLED:
                            pass
                        else:
                            notFilledFound = 1
                        if octree.children[k*2*2+j*2+i].filled & OT_PARTTRANSPARENT:
                            partTrans = 1
                        if octree.children[k*2*2+j*2+i].filled & OT_COMPLETETRANSPARENT:
                            waterGlassCount += 1

                        # xblock이 각기 서로 다른 j,k값에서 다 나오기만 하면 된다.
                        if octree.children[k*2*2+j*2+i].filled & OT_XBLOCK:
                            xb[j][k] = 1
                        if octree.children[k*2*2+j*2+i].filled & OT_YBLOCK:
                            yb[i][k] = 1
                        if octree.children[k*2*2+j*2+i].filled & OT_ZBLOCK:
                            zb[i][j] = 1

            if notFilledEmptyCount == 8:
                octree.filled = OT_EMPTY
            elif notFilledFound == 1:
                octree.filled = OT_HALFFILLED
            else:
                octree.filled = OT_FILLED

            if waterGlassCount == 8:
                octree.filled = OT_COMPLETETRANSPARENT
            elif waterGlassCount > 0 or partTrans:
                octree.filled |= OT_PARTTRANSPARENT

            for j in range(2):
                for i in range(2):
                    if xb[i][j] == 0:
                        xfound = False
                    if yb[i][j] == 0:
                        yfound = False
                    if zb[i][j] == 0:
                        zfound = False

            if xfound:
                octree.filled |= OT_XBLOCK
            if yfound:
                octree.filled |= OT_YBLOCK
            if zfound:
                octree.filled |= OT_ZBLOCK



    def GetLocalCoordAndOffset(self, x_,y_,z_):
        xL = x_ % 128
        yL = y_ % 128
        zL = z_ % 128
        xO = x_ - xL
        yO = y_ - yL
        zO = z_ - zL
        return (xL,yL,zL), (xO,yO,zO)

    def RayQuadIntersect(self, p1, p2, pa, pb, pc, pd):
        inter, p = self.RayTryIntersect(p1, p2, pa, pb, pc)
        if inter:
            return p
        inter, p = self.RayTryIntersect(p1, p2, pc, pd, pa)
        if inter:
            return p
        return None
    def RayTryIntersect(self, p1, p2, pa, pb, pc):
        """
   Determine whether or not the line segment p1,p2
   Intersects the 3 vertex facet bounded by pa,pb,pc
   Return true/false and the intersection point p

   The equation of the line is p = p1 + mu (p2 - p1)
   The equation of the plane is a x + b y + c z + d = 0
                                n.x x + n.y y + n.z z + d = 0
        """
        cdef double d
        cdef double a1,a2,a3
        cdef double total,denom,mu
        n = Vector()
        pa1 = Vector()
        pa2 = Vector()
        pa3 = Vector()
        p = Vector()

        n.x = (pb.y - pa.y)*(pc.z - pa.z) - (pb.z - pa.z)*(pc.y - pa.y)
        n.y = (pb.z - pa.z)*(pc.x - pa.x) - (pb.x - pa.x)*(pc.z - pa.z)
        n.z = (pb.x - pa.x)*(pc.y - pa.y) - (pb.y - pa.y)*(pc.x - pa.x)
        n = n.Normalized()
        d = - n.x * pa.x - n.y * pa.y - n.z * pa.z

        denom = n.x * (p2.x - p1.x) + n.y * (p2.y - p1.y) + n.z * (p2.z - p1.z)
        if (abs(denom) < 0.001):
            return False, None
        mu = - (d + n.x * p1.x + n.y * p1.y + n.z * p1.z) / denom
        p.x = p1.x + mu * (p2.x - p1.x)
        p.y = p1.y + mu * (p2.y - p1.y)
        p.z = p1.z + mu * (p2.z - p1.z)
        if (mu < 0 or mu > 1):
            return False, None

        pa1.x = pa.x - p.x
        pa1.y = pa.y - p.y
        pa1.z = pa.z - p.z
        pa1 = pa1.Normalized()
        pa2.x = pb.x - p.x
        pa2.y = pb.y - p.y
        pa2.z = pb.z - p.z
        pa2 = pa2.Normalized()
        pa3.x = pc.x - p.x
        pa3.y = pc.y - p.y
        pa3.z = pc.z - p.z
        pa3 = pa3.Normalized()
        a1 = pa1.x*pa2.x + pa1.y*pa2.y + pa1.z*pa2.z
        a2 = pa2.x*pa3.x + pa2.y*pa3.y + pa2.z*pa3.z
        a3 = pa3.x*pa1.x + pa3.y*pa1.y + pa3.z*pa1.z

        convert = 360.0/(2*math.pi)
        total = (cmath.acos(a1) + cmath.acos(a2) + cmath.acos(a3)) * convert
        if (abs(total - 360.0) > 0.001):
            return False, None

        return True, p

    # 이제 충돌검사. 위치로 주변블럭을 가져와서
    # 앞으로 갔는데 막혔으면 빠꾸
    # 밑으로 떨어졌는데 막혔으면 가만히
    # 음... 이건 큐브/큐브 겹치는지 안겹치는지를 본다?
    # 아 RPG맵 짤때 하던거 하면 되겠구만 뭘..
    def AddOther(self, type_, x,y,z,idx):
        # 일단 x,y,z에 블럭이 없어야함.
        # facing은 2,3,4,5(-x,x,-z,z중에 하나
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        cdef Octree *curOctree
        cdef Extra *extra
        cdef int outx,outy,outz
        self.GetOctreesByViewpoint(pos, octrees, outchunks, x,y,z)
        (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x,y,z)

        for ii in range(9):
            if pos[ii][0] == A and pos[ii][2] == C:
                curOctree = self.AccessOctreeWithXYZ(octrees[ii], a,b,c, 5, &outx, &outy, &outz)
                extra = <Extra*>curOctree.extra
                for i in range(extra.itemIdx):
                    if extra.items[i].x == x and extra.items[i].y == y and extra.items[i].z == z:
                        return False
                if extra.itemIdx >= extra.itemLen:
                    extra.itemLen *= 2
                    extra.items = <Item*>realloc(<void*>extra.items, extra.itemLen*sizeof(Item))

                extra.items[extra.itemIdx].type = type_
                extra.items[extra.itemIdx].x = x
                extra.items[extra.itemIdx].y = y
                extra.items[extra.itemIdx].z = z
                extra.items[extra.itemIdx].idx = idx
                extra.itemIdx += 1
                return True
        return False
    def AddChest(self, x,y,z,facing):
        # 일단 x,y,z에 블럭이 없어야함.
        # facing은 2,3,4,5(-x,x,-z,z중에 하나
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        cdef Octree *curOctree
        cdef Extra *extra
        cdef int outx,outy,outz
        self.GetOctreesByViewpoint(pos, octrees, outchunks, x,y,z)
        (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x,y,z)

        for ii in range(9):
            if pos[ii][0] == A and pos[ii][2] == C:
                curOctree = self.AccessOctreeWithXYZ(octrees[ii], a,b,c, 5, &outx, &outy, &outz)
                extra = <Extra*>curOctree.extra
                for i in range(extra.chestIdx):
                    if extra.chests[i].x == x and extra.chests[i].y == y and extra.chests[i].z == z:
                        return False
                if extra.chestIdx >= extra.chestLen:
                    extra.chestLen *= 2
                    extra.chests = <Chest*>realloc(<void*>extra.chests, extra.chestLen*sizeof(Chest))

                extra.chests[extra.chestIdx].x = x
                extra.chests[extra.chestIdx].y = y
                extra.chests[extra.chestIdx].z = z
                extra.chests[extra.chestIdx].frontFacing = facing
                extra.chestIdx += 1
                return True
        return False
    def AddTorch(self, x,y,z,face):
        if face == 0:
            return
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        cdef Octree *curOctree
        cdef Extra *extra
        cdef int outx,outy,outz
        self.GetOctreesByViewpoint(pos, octrees, outchunks, x,y,z)
        (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x,y,z)
        for ii in range(9):
            if pos[ii][0] == A and pos[ii][2] == C:
                curOctree = self.AccessOctreeWithXYZ(octrees[ii], a,b,c, 5, &outx, &outy, &outz)
                extra = <Extra*>curOctree.extra
                for i in range(extra.torchIdx):
                    if extra.torches[i].x == x and extra.torches[i].y == y and extra.torches[i].z == z:
                        return False
                if extra.torchIdx >= extra.torchLen:
                    extra.torchLen *= 2
                    extra.torches = <Torch*>realloc(<void*>extra.torches, extra.torchLen*sizeof(Torch))
                extra.torches[extra.torchIdx].x = x
                extra.torches[extra.torchIdx].y = y
                extra.torches[extra.torchIdx].z = z
                extra.torches[extra.torchIdx].face = face
                extra.torchIdx += 1

                vx = x-(x%32)
                vy = y-(y%32)
                vz = z-(z%32)
                for i in range(64):
                    xx,yy,zz = self.curDrawnCoords[0][i]
                    if xx==vx and yy==vy and zz==vz:
                        self.curDrawnCoords[0][i] = (-1,-1,-1)

                if x-(x%32) > (x-8):
                    vx = x-(x%32)-32
                    vy = y-(y%32)
                    vz = z-(z%32)
                    for i in range(64):
                        xx,yy,zz = self.curDrawnCoords[0][i]
                        if xx==vx and yy==vy and zz==vz:
                            self.curDrawnCoords[0][i] = (-1,-1,-1)
                if y-(y%32) > (y-8):
                    vx = x-(x%32)
                    vy = y-(y%32)-32
                    vz = z-(z%32)
                    for i in range(64):
                        xx,yy,zz = self.curDrawnCoords[0][i]
                        if xx==vx and yy==vy and zz==vz:
                            self.curDrawnCoords[0][i] = (-1,-1,-1)
                if z-(z%32) > (z-8):
                    vx = x-(x%32)
                    vy = y-(y%32)
                    vz = z-(z%32)-32
                    for i in range(64):
                        xx,yy,zz = self.curDrawnCoords[0][i]
                        if xx==vx and yy==vy and zz==vz:
                            self.curDrawnCoords[0][i] = (-1,-1,-1)

                if x-(x%32)+32 < (x+8):
                    vx = x-(x%32)+32
                    vy = y-(y%32)
                    vz = z-(z%32)
                    for i in range(64):
                        xx,yy,zz = self.curDrawnCoords[0][i]
                        if xx==vx and yy==vy and zz==vz:
                            self.curDrawnCoords[0][i] = (-1,-1,-1)

                if y-(y%32)+32 < (y+8):
                    vx = x-(x%32)
                    vy = y-(y%32)+32
                    vz = z-(z%32)
                    for i in range(64):
                        xx,yy,zz = self.curDrawnCoords[0][i]
                        if xx==vx and yy==vy and zz==vz:
                            self.curDrawnCoords[0][i] = (-1,-1,-1)

                if z-(z%32)+32 < (z+8):
                    vx = x-(x%32)
                    vy = y-(y%32)
                    vz = z-(z%32)+32
                    for i in range(64):
                        xx,yy,zz = self.curDrawnCoords[0][i]
                        if xx==vx and yy==vy and zz==vz:
                            self.curDrawnCoords[0][i] = (-1,-1,-1)

                return True
                break
        return False
    cdef AddChest2(self, Octree *octree, int x,int y,int z,int ox,int oy, int oz, int facing):
        cdef Octree *curOctree
        cdef int outx,outy,outz
        cdef Extra *extra
        (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x,y,z)
        if A == ox and C == oz:
            curOctree = self.AccessOctreeWithXYZ(octree, a,b,c, 5, &outx, &outy, &outz)
            extra = <Extra*>curOctree.extra
            for i in range(extra.chestIdx):
                if extra.chests[i].x == x and extra.chests[i].y == y and extra.chests[i].z == z:
                    return
            if extra.chestIdx >= extra.chestLen:
                extra.chestLen *= 2
                extra.chests = <Chest*>realloc(<void*>extra.chests, extra.chestLen*sizeof(Chest))
            extra.chests[extra.chestIdx].x = x
            extra.chests[extra.chestIdx].y = y
            extra.chests[extra.chestIdx].z = z
            extra.chests[extra.chestIdx].frontFacing = facing
            extra.chestIdx += 1
        else:
            assert False
    cdef AddTorch2(self, Octree *octree, int x,int y,int z,int ox,int oy, int oz, int face):
        cdef Octree *curOctree
        cdef int outx,outy,outz
        cdef Extra *extra
        (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x,y,z)
        if A == ox and C == oz:
            curOctree = self.AccessOctreeWithXYZ(octree, a,b,c, 5, &outx, &outy, &outz)
            extra = <Extra*>curOctree.extra
            for i in range(extra.torchIdx):
                if extra.torches[i].x == x and extra.torches[i].y == y and extra.torches[i].z == z:
                    return
            if extra.torchIdx >= extra.torchLen:
                extra.torchLen *= 2
                extra.torches = <Torch*>realloc(<void*>extra.torches, extra.torchLen*sizeof(Torch))
            extra.torches[extra.torchIdx].x = x
            extra.torches[extra.torchIdx].y = y
            extra.torches[extra.torchIdx].z = z
            extra.torches[extra.torchIdx].face = face
            extra.torchIdx += 1
        else:
            assert False


    def InWater(self, vx,vy,vz):
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        self.GetOctreesByViewpoint(pos, octrees, outchunks, vx,64,vz)
        x,y,z = int(vx-0.5), int(vy), int(vz-0.5)
        for k in range(3):
            for j in range(1):
                for i in range(3):
                    (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x-1+i,y,z-1+k)
                    for ii in range(9):
                        if pos[ii][0] == A and pos[ii][2] == C:
                            if outchunks[ii].chunk[(c)*128*128+(b)*128+a] == BLOCK_WATER:
                                return True
                            break
        return False
    def DigBlock(self, x,y,z):
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        cdef unsigned char ocolor
        self.GetOctreesByViewpoint(pos, octrees, outchunks, x,0,z)
        block = self.ModifyBlock(pos, x, y, z, octrees, outchunks, BLOCK_EMPTY, 0, &ocolor)
        items = []
        if block == BLOCK_CHEST:
            ITEM_CHEST = 7
            self.RemoveChest(x,y,z)
            items += [ITEM_CHEST]# 여기에 XXX: 상자에 든 모든 아이템을 다 뿌린다.
        if self.GetTorch(x,y,z):
            ITEM_TORCH = 3
            items += [ITEM_TORCH]
            self.RemoveTorch(x,y,z)
        return block, items, ocolor
    def RemoveChest(self, x,y,z):
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        cdef Octree *curOctree
        cdef Extra *extra
        cdef int outx,outy,outz
        self.GetOctreesByViewpoint(pos, octrees, outchunks, x,y,z)
        (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x,y,z)
        for ii in range(9):
            if pos[ii][0] == A and pos[ii][2] == C:
                curOctree = self.AccessOctreeWithXYZ(octrees[ii], a,b,c, 5, &outx, &outy, &outz)
                extra = <Extra*>curOctree.extra
                for i in range(extra.chestIdx):
                    if extra.chests[i].x == x and extra.chests[i].y == y and extra.chests[i].z == z:
                        extra.chests[i] = extra.chests[extra.chestIdx-1]
                        extra.chestIdx -= 1
        return False
    def RemoveTorch(self, x,y,z):
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        cdef Octree *curOctree
        cdef Extra *extra
        cdef int outx,outy,outz
        self.GetOctreesByViewpoint(pos, octrees, outchunks, x,y,z)
        (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x,y,z)
        for ii in range(9):
            if pos[ii][0] == A and pos[ii][2] == C:
                curOctree = self.AccessOctreeWithXYZ(octrees[ii], a,b,c, 5, &outx, &outy, &outz)
                extra = <Extra*>curOctree.extra
                for i in range(extra.torchIdx):
                    if extra.torches[i].x == x and extra.torches[i].y == y and extra.torches[i].z == z:
                        extra.torches[i] = extra.torches[extra.torchIdx-1]
                        extra.torchIdx -= 1
        return False
    def GetTorch(self, x,y,z):
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        cdef Octree *curOctree
        cdef Extra *extra
        cdef int outx,outy,outz
        self.GetOctreesByViewpoint(pos, octrees, outchunks, x,y,z)
        (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x,y,z)
        for ii in range(9):
            if pos[ii][0] == A and pos[ii][2] == C:
                curOctree = self.AccessOctreeWithXYZ(octrees[ii], a,b,c, 5, &outx, &outy, &outz)
                extra = <Extra*>curOctree.extra
                for i in range(extra.torchIdx):
                    if extra.torches[i].x == x and extra.torches[i].y == y and extra.torches[i].z == z:
                        return True
        return False

    def LookAtBlock(self, vp, dirV, level, bound, mat):
        # level은 3,5,7,9까지 가능하다. 3이면 1칸 이내에서만 가능, 5면 2칸 7이면 3칸 9면 4칸이내에서 파기/쌓기 가능
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        self.GetOctreesByViewpoint(pos, octrees, outchunks, vp.x,64,vp.z)
        cdef XYZ pickVP
        cdef XYZ pickDirV
        cdef int outCoords[3]
        cdef int outFace
        cdef int picked
        pickVP.x = vp.x
        pickVP.y = vp.y
        pickVP.z = vp.z
        pickDirV.x = dirV.x
        pickDirV.y = dirV.y
        pickDirV.z = dirV.z

        outFace = 0
        outCoords[0] = 0
        outCoords[1] = 0
        outCoords[2] = 0
        cdef float viewmat[16]
        viewmat[0] = mat[0][0]
        viewmat[1] = mat[1][0]
        viewmat[2] = mat[2][0]
        viewmat[3] = mat[3][0]
        viewmat[4] = mat[0][1]
        viewmat[5] = mat[1][1]
        viewmat[6] = mat[2][1]
        viewmat[7] = mat[3][1]
        viewmat[8] = mat[0][2]
        viewmat[9] = mat[1][2]
        viewmat[10] = mat[2][2]
        viewmat[11] = mat[3][2]
        viewmat[12] = mat[0][3]
        viewmat[13] = mat[1][3]
        viewmat[14] = mat[2][3]
        viewmat[15] = mat[3][3]
        """
        viewmat[0] = mat[0][0]
        viewmat[1] = mat[0][1]
        viewmat[2] = mat[0][2]
        viewmat[3] = mat[0][3]
        viewmat[4] = mat[1][0]
        viewmat[5] = mat[1][1]
        viewmat[6] = mat[1][2]
        viewmat[7] = mat[1][3]
        viewmat[8] = mat[2][0]
        viewmat[9] = mat[2][1]
        viewmat[10] = mat[2][2]
        viewmat[11] = mat[2][3]
        viewmat[12] = mat[3][0]
        viewmat[13] = mat[3][1]
        viewmat[14] = mat[3][2]
        viewmat[15] = mat[3][3]
        """

        picked = PickWithMouse(pickVP, pickDirV, pos, octrees, outchunks, outCoords, &outFace, level, 0, viewmat)
        if picked:
            (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(outCoords[0],outCoords[1],outCoords[2])
            block = 0
            for ii in range(9):
                if pos[ii][0] == A and pos[ii][2] == C:
                    block = outchunks[ii].chunk[c*128*128+b*128+a]
                    break

            if block:
                return outCoords[0], outCoords[1], outCoords[2], outFace, block
            else:
                return None
        else:
            return None
    def CheckCollide(self, x,y,z,pos,bound):
        return CheckCollide(x,y,z, pos.x, pos.y, pos.z, bound[0], bound[1], bound[2], 0)
    def ModBlock(self, vp, dirV, level, block, bound, ydiff, mat, color=0):
        # level은 3,5,7,9까지 가능하다. 3이면 1칸 이내에서만 가능, 5면 2칸 7이면 3칸 9면 4칸이내에서 파기/쌓기 가능
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        self.GetOctreesByViewpoint(pos, octrees, outchunks, vp.x,64,vp.z)
        cdef XYZ pickVP
        cdef XYZ pickDirV
        cdef int outCoords[3]
        cdef int outFace
        cdef int picked
        pickVP.x = vp.x
        pickVP.y = vp.y
        pickVP.z = vp.z
        pickDirV.x = dirV.x
        pickDirV.y = dirV.y
        pickDirV.z = dirV.z

        outFace = 0
        outCoords[0] = 0
        outCoords[1] = 0
        outCoords[2] = 0
        cdef unsigned char ocolor
        cdef float viewmat[16]
        viewmat[0] = mat[0][0]
        viewmat[1] = mat[1][0]
        viewmat[2] = mat[2][0]
        viewmat[3] = mat[3][0]
        viewmat[4] = mat[0][1]
        viewmat[5] = mat[1][1]
        viewmat[6] = mat[2][1]
        viewmat[7] = mat[3][1]
        viewmat[8] = mat[0][2]
        viewmat[9] = mat[1][2]
        viewmat[10] = mat[2][2]
        viewmat[11] = mat[3][2]
        viewmat[12] = mat[0][3]
        viewmat[13] = mat[1][3]
        viewmat[14] = mat[2][3]
        viewmat[15] = mat[3][3]
        picked = PickWithMouse(pickVP, pickDirV, pos, octrees, outchunks, outCoords, &outFace, level, ydiff, viewmat)
        if picked:
            x,y,z = 0,0,0
            face = outFace
            if block != 0:
                if face == 0:
                    y -= 1
                elif face == 1:
                    y += 1
                elif face == 2:
                    x -= 1
                elif face == 3:
                    x += 1
                elif face == 4:
                    z -= 1
                elif face == 5:
                    z += 1
                if not CheckCollide(float(outCoords[0]+x), float(outCoords[1]+y+1), float(outCoords[2]+z), vp.x, vp.y, vp.z, bound[0], bound[1], bound[2], ydiff):
                    result = self.ModifyBlock(pos, outCoords[0]+x, outCoords[1]+y, outCoords[2]+z, octrees, outchunks, block, color, &ocolor)
                    return result
            else:
                result = self.ModifyBlock(pos, outCoords[0], outCoords[1], outCoords[2], octrees, outchunks, block, color, &ocolor)
                return result
        return False

        """

        # 요 아래부터 PickWithMouse가 된다능
        x,y,z = vp.x, vp.y, vp.z
        x = int(x)
        y = int(y)
        z = int(z)
        x -= 2
        y -= 2
        z -= 2
        blocks = []
        for k in range(5):
            for j in range(5):
                for i in range(5):
                    (a,b,c), (A,B,C) = self.GetLocalCoordAndOffset(x + i, y + j, z + k)
                    print a,b,c,A,B,C, "aaa"
                    for ii in range(9):
                        if pos[ii][0] == A and pos[ii][1] == B and pos[ii][2] == C:
                            blocks += [outchunks[ii].chunk[c*128*128+b*128+a]]
                            break
        dirV = dirV.Normalized()
        dirV = dirV.MultScalar(10.0)
        dirV += vp
        # 01234
        # 67890
        # 12345
        # 67890
        # 12345
        #ray sphere test를 한다.
        #가까운데 있는 블럭부터 해야하니까 주변 3x3x3블럭, 5x5x5블럭 등을 검사한다. 3블럭 이상 떨어졌는데 그걸 파겠다고? 안되지.
        # 아 근데...3블럭 이상 떨어졌어도 집 지을 땐 필요함.. 음....
        # blocks는 x,y,z가 가장 작은 값부터 가장 큰 값까지
        # 2,2,2가 오리진.
        # 
        # 아...주변 3x3x3블럭을 어떻게 검사한담? ^^;;;;
        # 아. 오리진에서부터 1 떨어진 놈들을 검사하면 된다.
        found = []
        makeCube = [ # 위아래왼쪽오른쪽앞뒤, 아래왼쪽뒤가 원점
                [[-0.5, 0.5, -0.5], [0.5, 0.5, -0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]],
                [[-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, -0.5, 0.5], [-0.5, -0.5, 0.5]],
                [[-0.5, 0.5, -0.5], [-0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, -0.5, -0.5]],
                [[0.5, 0.5, -0.5], [0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [0.5, -0.5, -0.5]],
                [[-0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [-0.5, -0.5, 0.5]],
                [[-0.5, 0.5, -0.5], [0.5, 0.5, -0.5], [0.5, -0.5, -0.5], [-0.5, -0.5, -0.5]],]
        for k in range(3):
            for j in range(3):
                for i in range(3):
                    if blocks[(k+1)*5*5+(j+1)*5+(i+1)] != 0: # 여기를 고치면 여러가지 블럭(물, 다른거) 등에 대해 다른 연산을 할 수 있다.
                        spx = x+i+1+0.5
                        spy = y+j+1+0.5
                        spz = z+k+1+0.5
                        # 육면으로 한다. 음 깨는것도 그렇다. 깨는것도 정확하게 큐브로 한다.
                        # 일단 한 블럭당 6개의 인터섹션을 얻을 것이다.
                        # 그 인터섹션 점들 중에서 뷰포인트와 가장 가까운 것이 찾은 블럭이다.
                        # 아놔... 일단 느리고(C로하면 됨), 잘 못잡네?
                        # 뭔가 멀면 잘 못잡는 것 같다.
                        idx = 0
                        for cube in makeCube:
                            a = Vector(spx+cube[0][0], spy+cube[0][1], spz+cube[0][2])
                            b = Vector(spx+cube[1][0], spy+cube[1][1], spz+cube[1][2])
                            c = Vector(spx+cube[2][0], spy+cube[2][1], spz+cube[2][2])
                            d = Vector(spx+cube[3][0], spy+cube[3][1], spz+cube[3][2])
                            p = self.RayQuadIntersect(vp, dirV, a,b,c,d)
                            if p:
                                print vp, dirV, a,b,c,d
                                spx = x+i+1
                                spy = y+j+1
                                spz = z+k+1
                                found += [(idx, p, (spx,spy,spz))]
                            idx += 1

        if found:
            # 기본적으로 pos, octrees, outchunks, found, idx만 리턴할 수 있으면 된다. C로 해서...
            lowest = found[0]
            for tup_ in found[1:]:
                whichFace, point, coord = tup_
                oldPoint = lowest[1]
                if (oldPoint-vp).Length() > (point-vp).Length():
                    lowest = tup_

            found = lowest[2]
            print found
            self.RemoveBlock(pos, found[0], found[1], found[2], octrees, outchunks)
            return

        for k in range(5):
            for j in range(5):
                for i in range(5):
                    if blocks[(k)*5*5+(j)*5+(i)] != 0:
                        spx = x+i+0.5
                        spy = y+j+0.5
                        spz = z+k+0.5
                        idx = 0
                        for cube in makeCube:
                            a = Vector(spx+cube[0][0], spy+cube[0][1], spz+cube[0][2])
                            b = Vector(spx+cube[1][0], spy+cube[1][1], spz+cube[1][2])
                            c = Vector(spx+cube[2][0], spy+cube[2][1], spz+cube[2][2])
                            d = Vector(spx+cube[3][0], spy+cube[3][1], spz+cube[3][2])
                            p = self.RayQuadIntersect(vp, dirV, a,b,c,d)
                            if p:
                                spx = x+i
                                spy = y+j
                                spz = z+k
                                found += [(idx, p, (spx,spy,spz))]
                            idx += 1

        if found:
            lowest = found[0]
            for tup_ in found[1:]:
                whichFace, point, coord = tup_
                oldPoint = lowest[1]
                if (oldPoint-vp).Length() > (point-vp).Length():
                    lowest = tup_
            found = lowest[2]
            print found, 2
            self.RemoveBlock(pos, found[0], found[1], found[2], octrees, outchunks)
            return


        #이렇게 하고 Radius 1, 2, 3, 4, 5, 6, 7, 8, 9까지 해서 9단계로 Ray/Sphere 충돌검사를 한 후에
        # 가장 먼저 걸리는 블럭의 pos를 구한다.
        """

    def FixPos(self, oldpos, newpos, boundingBoxLen): # 땅 위에 떠있으면 떨어지고, 블럭과 겹쳐지면 원래 자리로 돌아가거나 아...
        cdef Octree * octrees[9]
        cdef Chunk * chunks[9]
        cdef int pos[9][3]
        cdef float fx,fy,fz

        self.GetOctreesByViewpoint(pos, octrees, chunks, newpos.x,64,newpos.z)
        FixPos(&fx, &fy,&fz, oldpos.x,oldpos.y,oldpos.z,newpos.x,newpos.y,newpos.z,boundingBoxLen[0],boundingBoxLen[1],boundingBoxLen[2], octrees, chunks, pos)
        return fx,fy,fz
    cdef int CheckIfAble(self, int pos[9][3], Chunk *chunks[9], int x,int y,int z):
        cdef int nxa[6]
        cdef int nya[6]
        cdef int nza[6]
        nxa[0] = 0
        nya[0] = -1
        nza[0] = 0

        nxa[1] = 0
        nya[1] = 1
        nza[1] = 0

        nxa[2] = -1
        nya[2] = 0
        nza[2] = 0

        nxa[3] = 1
        nya[3] = 0
        nza[3] = 0

        nxa[4] = 0
        nya[4] = 0
        nza[4] = -1

        nxa[5] = 0
        nya[5] = 0
        nza[5] = 1

        disallowedBlocks = [
                BLOCK_EMPTY,BLOCK_WATER,BLOCK_LAVA,BLOCK_CHEST
                # empty 라바, 물
                ]
        # 또한 여기서 인벤토리 등의 블락이 아닌 툴 등 역시 검사해봐야 한다.
        # 아 근데 툴은 좀 괜찮지 않나? 툴 쌓아두고 말이지. 괜찮을 듯. 나무도 괜찮음 라바 물만 아니면 됨
        for i in range(6):
            (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x+nxa[i],y+nya[i],z+nza[i])
            for ii in range(9):
                if pos[ii][0] == A and pos[ii][2] == C:
                    block = chunks[ii].chunk[c*128*128+b*128+a]
                    if block not in disallowedBlocks:
                        return True
        return False

    cdef int CheckIfDestructable(self, unsigned char block):
        disallowedBlocks = [
                BLOCK_EMPTY,BLOCK_WATER,BLOCK_LAVA,BLOCK_INDESTRUCTABLE
                ]
        if block in disallowedBlocks:
            return False
        return True
    def IsBlockThere(self, x,y,z):
        cdef int pos[9][3]
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        self.GetOctreesByViewpoint(pos, octrees, outchunks, x,y,z)
        (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x,y,z)
        retBlock = 0
        for ii in range(9):
            if pos[ii][0] == A and pos[ii][2] == C:
                if outchunks[ii].chunk[c*128*128+b*128+a]:
                    return True
        return False

    cdef int ModifyBlock(self, int pos[9][3], int x, int y, int z, Octree *octrees[9], Chunk *chunks[9], unsigned char block, unsigned char color, unsigned char *outColor):
        # face -> 위 아래 왼쪽 오른쪽 앞 뒤 0 1 2 3 4 5
        # 즉... x,y,z에서 어느 좌표를 -1 +1 해줄것인가를 결정
        #
        # 음 이제 여기에서... 블럭을 넣을 때 viewpos와 충돌나는지 안나는지를 보면 된다.
        #
        cdef int outx
        cdef int outy
        cdef int outz
        cdef Octree *curOctree
        (a,b,c),(A,B,C) = self.GetLocalCoordAndOffset(x,y,z)
        retBlock = 0
        for ii in range(9):
            if pos[ii][0] == A and pos[ii][2] == C:
                if block == 0 and self.CheckIfDestructable(chunks[ii].chunk[c*128*128+b*128+a]):
                    retBlock = chunks[ii].chunk[c*128*128+b*128+a]
                    chunks[ii].chunk[c*128*128+b*128+a] = block
                    outColor[0] = chunks[ii].colors[c*128*128+b*128+a]
                    for i in range(127):
                        if chunks[ii].chunk[c*128*128+(127-i)*128+a] != 0:
                            chunks[ii].heights[c*128+a] = 127-i
                            break
                    self.UpdateChunks(octrees[ii], chunks[ii], a,b,c)
                elif chunks[ii].chunk[c*128*128+b*128+a] == 0 and self.CheckIfAble(pos, chunks, x,y,z):
                    retBlock = -1
                    chunks[ii].chunk[c*128*128+b*128+a] = block
                    chunks[ii].colors[c*128*128+b*128+a] = color
                    if chunks[ii].heights[c*128+a] < b and b != BLOCK_COLOR and b != BLOCK_WATER and b != BLOCK_GLASS:
                        chunks[ii].heights[c*128+a] = b
                    self.UpdateChunks(octrees[ii], chunks[ii], a,b,c)
                break
        if retBlock != 0:
            vx = x-(x%32)
            vy = y-(y%32)
            vz = z-(z%32)
            for i in range(64):
                xx,yy,zz = self.curDrawnCoords[0][i]
                if xx==vx and yy==vy and zz==vz:
                    self.curDrawnCoords[0][i] = (-1,-1,-1)

            if not(x % 32):
                vx = x-(x%32)-32
                vy = y-(y%32)
                vz = z-(z%32)
                for i in range(64):
                    xx,yy,zz = self.curDrawnCoords[0][i]
                    if xx==vx and yy==vy and zz==vz:
                        self.curDrawnCoords[0][i] = (-1,-1,-1)
            if not(y % 32):
                vx = x-(x%32)
                vy = y-(y%32)-32
                vz = z-(z%32)
                for i in range(64):
                    xx,yy,zz = self.curDrawnCoords[0][i]
                    if xx==vx and yy==vy and zz==vz:
                        self.curDrawnCoords[0][i] = (-1,-1,-1)
            if not(z % 32):
                vx = x-(x%32)
                vy = y-(y%32)
                vz = z-(z%32)-32
                for i in range(64):
                    xx,yy,zz = self.curDrawnCoords[0][i]
                    if xx==vx and yy==vy and zz==vz:
                        self.curDrawnCoords[0][i] = (-1,-1,-1)

            if x % 32 == 31:
                vx = x-(x%32)+32
                vy = y-(y%32)
                vz = z-(z%32)
                for i in range(64):
                    xx,yy,zz = self.curDrawnCoords[0][i]
                    if xx==vx and yy==vy and zz==vz:
                        self.curDrawnCoords[0][i] = (-1,-1,-1)

            if y % 32 == 31:
                vx = x-(x%32)
                vy = y-(y%32)+32
                vz = z-(z%32)
                for i in range(64):
                    xx,yy,zz = self.curDrawnCoords[0][i]
                    if xx==vx and yy==vy and zz==vz:
                        self.curDrawnCoords[0][i] = (-1,-1,-1)

            if z % 32 == 31:
                vx = x-(x%32)
                vy = y-(y%32)
                vz = z-(z%32)+32
                for i in range(64):
                    xx,yy,zz = self.curDrawnCoords[0][i]
                    if xx==vx and yy==vy and zz==vz:
                        self.curDrawnCoords[0][i] = (-1,-1,-1)

        return retBlock

    cdef void UpdateChunks(self, Octree *octree, Chunk *chunk, a,b,c):
        cdef int outx
        cdef int outy
        cdef int outz
        cdef Octree *curOctree
        curOctree = self.AccessOctreeWithXYZ(octree, a,b,c, 7, &outx, &outy, &outz)
        #self.CalcFilled(chunk, octree)
        for i in range(7):
            #self.AccessOctreeWithXYZ(octrees[ii], a,b,c, 7-i, &outx, &outy, &outz) outx는 마지막 레벨에서만 사용하기 때문에 바꿀 필요가 없음
            self.CalcOne(chunk, curOctree, outx,outy,outz, 7-i)
            curOctree = curOctree.parent

    def RaySphereIntersect(self, p1, p2, sc, r):
        dp = Vector()
        dp.x = p2.x - p1.x
        dp.y = p2.y - p1.y
        dp.z = p2.z - p1.z
        a = dp.x * dp.x + dp.y * dp.y + dp.z * dp.z
        b = 2 * (dp.x * (p1.x - sc.x) + dp.y * (p1.y - sc.y) + dp.z * (p1.z - sc.z))
        c = sc.x * sc.x + sc.y * sc.y + sc.z * sc.z
        c += p1.x * p1.x + p1.y * p1.y + p1.z * p1.z
        c -= 2 * (sc.x * p1.x + sc.y * p1.y + sc.z * p1.z)
        c -= r * r
        bb4ac = b * b - 4 * a * c
        if abs(a) < 0.001 or bb4ac < 0:
            mu1 = 0
            mu2 = 0
            return False

        mu1 = (-b + cmath.sqrt(bb4ac)) / (2 * a)
        mu2 = (-b - cmath.sqrt(bb4ac)) / (2 * a)

        return True
    def LoadRegion(self, name, dstpos):

        #f = open("%d_%d_%d", "rb")
        cdef:
            char fbuffer[256]
            char *path = "./map/%s.region"
            char *path2 = "./map/%s.len"
            stdio.FILE *fp
            char *nameStr = name
            int whl[3]

        stdio.sprintf(fbuffer, path2, nameStr)
        fp = stdio.fopen(fbuffer, "rb")
        if fp != NULL:
            stdio.fread(whl, sizeof(int), 3, fp);
            stdio.fclose(fp)
        else:
            return
        w,h,l = whl[0],whl[1],whl[2]
        cdef unsigned char *buffer
        buffer = <unsigned char*>malloc(sizeof(unsigned char)*w*h*l)

        stdio.sprintf(fbuffer, path, nameStr)
        fp = stdio.fopen(fbuffer, "rb")
        if fp != NULL:
            stdio.fread(buffer, sizeof(unsigned char), w*h*l, fp);
            stdio.fclose(fp)
        else:
            return

        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        cdef int pos[9][3]
        x,y,z = dstpos
        xx,yy,zz = x+w,y+h,z+l
        if yy-y > 128:
            yy -= yy-y-128
        if y < 0:
            y = 0
        if y >= 128:
            y = 127
        if yy < 0:
            yy = 0
        if yy >= 128:
            yy = 127

        self.GetOctreesByViewpoint(pos, octrees, outchunks, x,y,z)
        # 9개의 버퍼중 현재 좌표에 맞는 부분을 찾아야 한다.
        # 최대 4개의 버퍼가 필요하므로 그 4개의 좌표를 찾는다.
        x2 = xx-(xx%128)
        z2 = zz-(zz%128)
        w2 = xx-x2
        l2 = zz-z2
        if x-(x%128) == x2:
            w2 = 0
            w = xx-x
        else:
            w = x2-x

        if z-(z%128) == z2:
            l2 = 0
            l = zz-z
        else:
            l = z2-z

        for ii in range(9):
            if pos[ii][0] == x-(x%128) and pos[ii][2] == z-(z%128):
                for k in range(l):
                    for j in range(h):
                        memcpy(&outchunks[ii].chunk[(k+(z%128))*128*128+(y+j)*128+(x%128)], &buffer[k*h*(w+w2)+j*(w+w2)], w)

                self.CalcFilled(outchunks[ii], octrees[ii])


            elif pos[ii][0] == x-(x%128) and pos[ii][2] == z2:
                if l2:
                    for k in range(l2):
                        for j in range(h):
                            memcpy(&outchunks[ii].chunk[(k)*128*128+(y+j)*128+(x%128)], &buffer[(k+l)*h*(w+w2)+j*(w+w2)], w)
                    self.CalcFilled(outchunks[ii], octrees[ii])
            elif pos[ii][0] == x2 and pos[ii][2] == z-(z%128):
                if w2:
                    for k in range(l):
                        for j in range(h):
                            memcpy(&outchunks[ii].chunk[(k+(z%128))*128*128+(y+j)*128], &buffer[k*h*(w+w2)+j*(w+w2)+w], w2)
                    self.CalcFilled(outchunks[ii], octrees[ii])
            elif pos[ii][0] == x2 and pos[ii][2] == z2:
                if w2 and l2:
                    for k in range(l2):
                        for j in range(h):
                            memcpy(&outchunks[ii].chunk[(k)*128*128+(y+j)*128], &buffer[(k+l)*h*(w+w2)+j*(w+w2)+w],  w2)
                    self.CalcFilled(outchunks[ii], octrees[ii])
        for k in range(((l+l2)/32)+2):
            for j in range(128/32):
                for i in range(((w+w2)/32)+2):
                    vx = x-(x%32)+i*32
                    vy = j*32
                    vz = z-(z%32)+k*32
                    for iii in range(64):
                        xxx,yyy,zzz = self.curDrawnCoords[0][iii]
                        if xxx==vx and yyy==vy and zzz==vz:
                            self.curDrawnCoords[0][iii] = (-1,-1,-1)


        free(buffer)

    def SaveRegion(self, name, min, max):
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        cdef int pos[9][3]
        x,y,z = min
        xx,yy,zz = max
        if xx-x > 128:
            xx -= xx-x-128
        if yy-y > 128:
            yy -= yy-y-128
        if zz-z > 128:
            zz -= zz-z-128
        if y < 0:
            y = 0
        if y >= 128:
            y = 127
        if yy < 0:
            yy = 0
        if yy >= 128:
            yy = 127
        if xx-x == 0 or yy-y == 0 or zz-z == 0 or xx < x or yy < y or zz < z:
            assert False, "Wrong min max"
        w,h,l = xx-x, yy-y, zz-z
        self.GetOctreesByViewpoint(pos, octrees, outchunks, x,y,z)
        cdef unsigned char *buffer
        buffer = <unsigned char*>malloc(sizeof(unsigned char)*w*h*l)
        # 9개의 버퍼중 현재 좌표에 맞는 부분을 찾아야 한다.
        # 최대 4개의 버퍼가 필요하므로 그 4개의 좌표를 찾는다.
        x2 = xx-(xx%128)
        z2 = zz-(zz%128)
        w2 = xx-x2
        l2 = zz-z2
        if x-(x%128) == x2:
            w2 = 0
            w = xx-x
        else:
            w = x2-x

        if z-(z%128) == z2:
            l2 = 0
            l = zz-z
        else:
            l = z2-z

        # 제대로 안된다. 뭔가 점 이상하네여~~~~~~
        for ii in range(9):
            if pos[ii][0] == x-(x%128) and pos[ii][2] == z-(z%128):
                for k in range(l):
                    for j in range(h):
                        memcpy(&buffer[k*h*(w+w2)+j*(w+w2)], &outchunks[ii].chunk[(k+(z%128))*128*128+(y+j)*128+(x%128)], w)
            elif pos[ii][0] == x-(x%128) and pos[ii][2] == z2:
                if l2:
                    for k in range(l2):
                        for j in range(h):
                            memcpy(&buffer[(k+l)*h*(w+w2)+j*(w+w2)], &outchunks[ii].chunk[(k)*128*128+(y+j)*128+(x%128)], w)
            elif pos[ii][0] == x2 and pos[ii][2] == z-(z%128):
                if w2:
                    for k in range(l):
                        for j in range(h):
                            memcpy(&buffer[k*h*(w+w2)+j*(w+w2)+w], &outchunks[ii].chunk[(k+(z%128))*128*128+(y+j)*128], w2)
            elif pos[ii][0] == x2 and pos[ii][2] == z2:
                if w2 and l2:
                    for k in range(l2):
                        for j in range(h):
                            memcpy(&buffer[(k+l)*h*(w+w2)+j*(w+w2)+w], &outchunks[ii].chunk[(k)*128*128+(y+j)*128], w2)

        cdef:
            char fbuffer[256]
            char *path = "./map/%s.region"
            char *path2 = "./map/%s.len"
            stdio.FILE *fp
            char *nameStr = name
            int whl[3]
        whl[0] = w+w2
        whl[1] = h
        whl[2] = l+l2
        try:
            os.mkdir("./map")
        except:
            pass

        stdio.sprintf(fbuffer, path, nameStr)
        fp = stdio.fopen(fbuffer, "wb")
        if fp != NULL:
            stdio.fwrite(buffer, sizeof(unsigned char), (w+w2)*h*(l+l2), fp)
            stdio.fclose(fp)

        stdio.sprintf(fbuffer, path2, nameStr)
        fp = stdio.fopen(fbuffer, "wb")
        if fp != NULL:
            stdio.fwrite(whl, sizeof(int), 3, fp)
            stdio.fclose(fp)

    def GetNewPos(self, oldPos):
        newPos = oldPos
        # 여기서 충돌검사를 하여 새로운 위치를 얻는다.?
        # 아예 좌우이동 할 때 위아래로는 못가게 하고 여기서는 y값만 변경시키도록 하자.
        return newPos
    def GenVerts(self, frustum, viewpoint, updateFrame, tooltex, blocktex):
        cdef double frustumC[6][4]
        cdef double rad
        for i in range(6):
            for j in range(4):
                frustumC[i][j] = frustum[i][j]

        # 일단 뷰포인트로 주변 4개의 옥트리의 위치를 얻어온다. (4개 이상은 가져올 필요가 없을 것. 매우 크니까 1개 청크가)
        # 그중 어떤 옥트리들이 프러스텀에 힛하는지 스피어테스트를 한다. 루트128*128이 청크 스피어의 radius
        # 그 다음 옥트리 레벨을 내려가면서 어느 옥트리가 힛하는지 본다.
        # 그 다음에 육면검사를 한다.(옥트리이용)
        # 그 다음에 폴리곤 생성하면서 뷰포인트를 이용하여 삼각형의 한 점을 기준으로 노멀, 뷰포인트의 벡터를 dot해서 음수면 폴리곤 생성
        # 양수면 스킵한다.
        # 폴리곤 덩어리를 그린다.
        # 음....4개만 가져오는 게 아니라 9개를 가져와야 하지 않을까 싶다. 흠.....
        # 9개 아니면 1개이지 4개는 좀 아닌 듯.
        cdef int vx,vy,vz
        cdef int ox,oy,oz
        vx,vy,vz = int(viewpoint[0]), int(viewpoint[1]), int(viewpoint[2])
        cdef Octree * octrees[9]
        cdef Chunk * outchunks[9]
        cdef int pos[9][3]
        cdef int cx,cy,cz
        # -x, +x, -y, +y, -z, +y 순서로 6면에 대한 정보
        # empty일 경우에 1 아닐 경우 0
        # 잠깐. 이 정보는 필요가 없다. empty일 경우 좌표와 함께 아....
        cdef int indexLen=0
        self.GetOctreesByViewpoint(pos, octrees, outchunks, vx,64,vz)
        updated = False
        if updateFrame:
            # 여기서도 현재 뷰포인트를 기준으로 128*128*128만큼만 그리도록 고치고
            # updateCoords를 백업해 둔 후에
            # 사람이 이동을 했다면
            # updateCoords백업한거랑 현재거랑 비교해서
            # 바뀐 부분을 updateCoords에 넣고, 안바꿀 부분은 -1-1-1로만 하고
            # 바뀌어진 updateCoords를 백업해두고
            # 업뎃을 실행한다.
            # 백업은 파이썬 리스트로 한다.
            # 현재 그릴 리스트는 128/4인 32x32x32수준으로 viewpoint를 변환해서 얻어온다.
            #
            # 이제 만들어진 걸로 indexedList를 만들어서 그리면 금상첨화.
            # 프러스텀 컬링과 앞면검사를 한다.
            curToDrawList = [] # 이것과 drawnList를 검사해서 다르다면 updateCoords에 넣고 업뎃을 한다.
            # 이하를 C로 옮기고
            # 청크의 크기를 32x32x32에서 16x16x16으로 좀 바꾸면 빨라질지도....
            sightLen = 64
            curCX = vx-(vx%32)-32*2
            curCY = 0
            curCZ = vz-(vz%32)-32*2
            for z in range(4):
                for y in range(4):
                    for x in range(4):
                        curToDrawList += [(curCX+32*x, curCY+32*y, curCZ+32*z)]

            matchedCoords = []
            for i in range(sightLen):
                if self.curDrawnCoords[0][i] in curToDrawList:
                        matchedCoords += [self.curDrawnCoords[0][i]]

            rad = 16.0#math.sqrt(16.0*16.0+16.0*16.0)+3.0
            if len(matchedCoords) != sightLen:
                unmatchedIdx = []
                for i in range(sightLen):
                    if self.curDrawnCoords[0][i] not in matchedCoords:
                        unmatchedIdx += [i]
                updatedDrawList = []
                for i in range(sightLen):
                    if curToDrawList[i] not in matchedCoords:
                        updatedDrawList += [curToDrawList[i]]
                """
                for i in range(sightLen):
                    self.updateCoords[i*3+0] = self.curDrawnCoords[0][i][0]
                    self.updateCoords[i*3+1] = self.curDrawnCoords[0][i][1]
                    self.updateCoords[i*3+2] = self.curDrawnCoords[0][i][2]
                """
                memset(self.updateCoords, -1, sizeof(int)*64*3)
                idx = 0
                for i in range(sightLen):
                    if i in unmatchedIdx:
                        curx,cury,curz = updatedDrawList[idx]
                        if self.CubeInFrustum(curx+16.0,cury+16.0,curz+16.0, rad, frustumC):
                            self.updateCoords[i*3+0] = updatedDrawList[idx][0]
                            self.updateCoords[i*3+1] = updatedDrawList[idx][1]
                            self.updateCoords[i*3+2] = updatedDrawList[idx][2]
                            self.curDrawnCoords[0][i] = updatedDrawList[idx]
                            updated = True
                        else:
                            self.curDrawnCoords[0][i] = (-1,-1,-1)
                        self.tIdx[i] = 0
                        self.aIdx[i] = 0
                        self.iIdx[i] = 0
                        self.nsIdx[i] = 0
                        idx += 1
                # 다 하면 메모리 모자라지 않게 5x5x5만 남겨두고 나머지는 다 octrees 리스트에서 free하는 코드를 짠다.
                # Z,X쪽으로 현재 뷰포인트에서 3칸째 떨어진 놈들은 무조건 FREE한다.
                # 음...옥트리를 쓸 때는 프러스텀 컬링이 쉬웠는데? 아 이거 할 때도 쉽다. updateCoords를 가지고 컬링하고
                # 컬링 안된놈들 중에서는 앞면검사를 한다.
                # 컬링과 앞면검사를 하고나서 속도를 보자. 보통 몹없으면 60FPS 몹있으면 45FPS, 맵그리면 7FPS가 나온다.
                # 맵이 꽤 느리다는 이야기.
                # 일단 간단한 프러스텀 컬링부터
                if updated:
                    for i in range(TEST_SIZE):
                        ox,oy,oz = pos[i][0], 0, pos[i][2]
                        oy = 0
                        self.GenQuads(self.tV, self.tT, self.tC, self.tIdx, self.tLen, self.nsV, self.nsT, self.nsC, self.nsIdx, self.nsLen, self.aV, self.aT, self.aC, self.aIdx, self.aLen, self.iV, self.iT, self.iC, self.iIdx, self.iLen, octrees[i], octrees[i], outchunks[i], octrees, outchunks, pos, 1, frustumC, 0,0,0, ox,0,oz, viewpoint[0],viewpoint[1],viewpoint[2], self.lastX, self.lastY, self.lastZ, self.updateCoords, -1, 0.0, -1.0, 0.0)
        

        if True:
            GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
            GL.glEnableClientState(GL.GL_TEXTURE_COORD_ARRAY)
            GL.glEnableClientState(GL.GL_COLOR_ARRAY)
            GL.glEnable(GL.GL_CULL_FACE)
            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glDisable(GL.GL_BLEND)
            # XXX: 프러스텀은 했으니 뒷면검사도 그냥 한번 해본다.
            # 이러니까 렌더링 자체가 느리다.
            # 뒷면검사 안하면 그리는게 느리고 뒷면검사 하면 검사하는게 느려서 속도가 비슷비슷하다.
            # 뒷면검사 자체를 OpenGL에서 하느냐 아니면 여기서 하느냐의 정도의 차이인 것 같다.
            # 그나저나 프러스텀 줄여도 느린건 무슨심보지....
            # 4x4x4중에서 2x2x2만 그려질텐데말야...
            # 즉 캐슁을 해도 느리다?
            # 하지만 전처럼 0프레임은 안나온다. 빠르긴 빠른데, 전보다 더 빠르지는 않다 이건가.
            # 아님 컴터가 이상해서 그럴수도;; 40프레임도 나와봤으니까!
            # 앞면검사만 좀 더 빠르다면...... 인덱스 생성.
            for i in range(64):
                curx,cury,curz = self.curDrawnCoords[0][i]
                if self.tIdx[i] != 0 and self.CubeInFrustum(curx+16.0,cury+16.0,curz+16.0, rad, frustumC):
                    indexLen = 0
                    GenIndexList(self.indexList, &indexLen, self.tV[i], self.tIdx[i], viewpoint[0], viewpoint[1], viewpoint[2])
                    glVertexPointer( 3, GL.GL_FLOAT, 0, <void*>self.tV[i]) 
                    glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.tT[i]) 
                    glColorPointer(3, GL.GL_UNSIGNED_BYTE, 0, <void*>self.tC[i]) 
                    #glDrawArrays(GL.GL_QUADS, 0, self.tIdx[i]*4)
                    glDrawElements(GL.GL_QUADS, indexLen, GL.GL_UNSIGNED_INT, self.indexList)

            """
            self.curIdx = 0
            for i in range(64):
                curx,cury,curz = self.curDrawnCoords[0][i]
                if self.tIdx[i] != 0 and self.CubeInFrustum(curx+16.0,cury+16.0,curz+16.0, rad, frustumC):
                    if self.curIdx+self.tIdx[i] < 32768:
                        memcpy(&self.quads[self.curIdx*4*3], self.tV[i], sizeof(float)*self.tIdx[i]*4*3)
                        memcpy(&self.texs[self.curIdx*4*2], self.tT[i], sizeof(float)*self.tIdx[i]*4*2)
                        memcpy(&self.normals[self.curIdx*4*3], self.tN[i], sizeof(float)*self.tIdx[i]*4*3)
                        self.curIdx += self.tIdx[i]

            indexLen = 0
            GenIndexList(self.indexList, &indexLen, self.quads, self.curIdx, viewpoint[0], viewpoint[1], viewpoint[2])
            glVertexPointer( 3, GL.GL_FLOAT, 0, <void*>self.quads) 
            glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.texs) 
            glNormalPointer(GL.GL_FLOAT, 0, <void*>self.normals) 
            #glDrawArrays(GL.GL_QUADS, 0, self.tIdx[i]*4)
            glDrawElements(GL.GL_QUADS, indexLen, GL.GL_UNSIGNED_INT, self.indexList)
            """




            GL.glBindTexture(GL.GL_TEXTURE_2D, tooltex)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
            GL.glTexEnvf(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_MODULATE)

            for i in range(64):
                curx,cury,curz = self.curDrawnCoords[0][i]
                if self.iIdx[i] != 0 and self.CubeInFrustum(curx+16.0,cury+16.0,curz+16.0, rad, frustumC):
                    indexLen = 0
                    GenIndexList(self.indexList, &indexLen, self.iV[i], self.iIdx[i], viewpoint[0], viewpoint[1], viewpoint[2])
                    glVertexPointer( 3, GL.GL_FLOAT, 0, <void*>self.iV[i]) 
                    glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.iT[i]) 
                    glColorPointer(3, GL.GL_UNSIGNED_BYTE, 0, <void*>self.iC[i]) 
                    #glDrawArrays(GL.GL_QUADS, 0, self.iIdx[i]*4)
                    glDrawElements(GL.GL_QUADS, indexLen, GL.GL_UNSIGNED_INT, self.indexList)



            GL.glBindTexture(GL.GL_TEXTURE_2D, blocktex)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
            GL.glTexEnvf(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_MODULATE)

            for i in range(64):
                curx,cury,curz = self.curDrawnCoords[0][i]
                if self.nsIdx[i] != 0 and self.CubeInFrustum(curx+16.0,cury+16.0,curz+16.0, rad, frustumC):
                    indexLen = 0
                    GenIndexList(self.indexList, &indexLen, self.nsV[i], self.nsIdx[i], viewpoint[0], viewpoint[1], viewpoint[2])
                    glVertexPointer( 3, GL.GL_FLOAT, 0, <void*>self.nsV[i]) 
                    glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.nsT[i]) 
                    glColorPointer(3, GL.GL_UNSIGNED_BYTE, 0, <void*>self.nsC[i]) 
                    #glDrawArrays(GL.GL_QUADS, 0, self.nsIdx[i]*4)
                    glDrawElements(GL.GL_QUADS, indexLen, GL.GL_UNSIGNED_INT, self.indexList)
            #GL.glDisable(GL.GL_CULL_FACE)
            #GL.glDisable(GL.GL_DEPTH_TEST)

            GL.glEnable(GL.GL_BLEND)
            #GL.glDisable(GL.GL_DEPTH_TEST) 이걸 해버리면 산 뒤에있는 transparent오브젝트까지 렌더링된다.
            #폴리곤을... 현재 뷰포인트에서 X정렬, Y정렬, Z정렬을 하고 뷰포인트가 X의 -쪽이면 X의 -부터 그리고 Y의 -쪽이면 Y의 -부터 그리고
            # 뭐 이런식으로 인덱스 버퍼를 정렬하면 될 것 같은데. XXX

            for i in range(64):
                curx,cury,curz = self.curDrawnCoords[0][i]
                if self.aIdx[i] != 0 and self.CubeInFrustum(curx+16.0,cury+16.0,curz+16.0, rad, frustumC):
                    indexLen = 0
                    GenIndexList(self.indexList, &indexLen, self.aV[i], self.aIdx[i], viewpoint[0], viewpoint[1], viewpoint[2])
                    glVertexPointer( 3, GL.GL_FLOAT, 0, <void*>self.aV[i]) 
                    glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.aT[i]) 
                    glColorPointer(3, GL.GL_UNSIGNED_BYTE, 0, <void*>self.aC[i]) 
                    #glDrawArrays(GL.GL_QUADS, 0, self.aIdx[i]*4)
                    glDrawElements(GL.GL_QUADS, indexLen, GL.GL_UNSIGNED_INT, self.indexList)

            


           # 음 OpenGL컨텍스트는 Pygame쓸 수 있지만 OpenGL명령어 자체는 라이브러리가 다르기 때문에 뭔가 따로 쓰면 안될 것 같기도 하다.
            # glew를 써야 하더라도 그냥 Cython에서 GL코드를 부르자.
            #print self.quadIdx, 'quadIdx'
                # 생성을 다하면 한번에 그린다.
                #cx,cy,cz = octreePos[j][0], octreePos[j][1], octreePos[j][2]
                    # outchunks[i].chunk[cz*128*128+cy*128+cx]
                    # 이제 여기서 레벨6,7의 empty를 파악하고 empty가 아니라면 주변 6개 octree를 읽어와서 empty인지 filled인지 notfilled인지를 파악한다.
                    # 그렇게 해서 주변이 empty인 6면들 중 한 면들만 가져온다.
                    # 즉, 여기서 바로 버텍스를 생성하는 거임
                    # 120개의 옥트리가 있는 경우 최대 6만개를 검사하니까 36만개를 검사해야 한다. 36만번 루프를 돌아보고 빠른지 보자.
                    # 음..... filled인데 주변이 다 filled인 경우도 무시 가능하고 그러니까 꽤 빠를 거 같기도 하고.
                    #
                    # 음.... 뷰포인트에서 벽에 가려진 경우 벽 뒤에 있는 건 아예 그릴 필요가 없는데 이것도 알아내는 방법이 있을 거 같은데?
                    # 0.5벡터씩 뷰벡터에서 디렉션 벡터로 증가시키면서 그 스캔라인 면과 접촉하는 모든 블럭을 가져와서 그 블럭이 완벽하게 꽉 차 있을
                    # 경우 그 뒷면은 다 무시한다던가?
                    # 그걸 옥트리 레벨에서 하면.. 땅속에 있을 때 굉장히 빠를 것이다.
                    # 하튼 즉 오클루젼 컬링을 어느정도 구현해야 한다.
                    # 여기서 이게 하기 좋은 이유는 "폴리곤"이 아니라 "바운딩박스"로만 이루어져있기 때문이다.
                    # 예를들어, 프러스텀 내의 8x8x8안에 있는 포지션을 전부 트랜슬레이트 하고,
                    # 그걸로 오클루젼 Z소팅 테스트를 해서 앞에 가려지는 게 있으면 그거만 그리도록 하고.
                    # 이건 시간이 좀 걸릴 것 같기도 하다.
                    # 오클루젼 말고 6면검사만 해도 빠르지 않을까 하지만 6면검사 자체가 느리면 어쩌지? 60000개를 다 육면검사
                    # 아 그래서 옥트리로 2x2x2수준에서 검사해도 많다. 하지만 1x1x1수준으로 하는 것보다는 빠르다.
                    # 레벨 5의 옥트리를 가지고 있으니까 일단 레벨 5의 수준에서 6면의 8x8x8 꽉찬거에 완벽하게 둘러쌓인 놈은 다 제외하고
                    # 그 다음 남은걸로 레벨 6에서 또 비슷하게 검사하고
                    # 거기서 남은걸로 레벨7에서 비슷하게 검사하고
                    # 마지막으로 거기서 남은걸로 1x1x1수준에서 검사해서
                    # 남은걸로 전부 6면검사 하면서 다른 블럭이 없는 면만 버텍스를 생성한다.
                    # 그러다가 쿼드 갯수가 32768을 넘어서면 아예 멈춰버린다.
                    # 음 애초에 5레벨에서 검사할 때에도 큐브단위가 아닌 "면"단위로 데이터를 저장해두면 다음 레벨에서도 그쪽 면만 검사하면 된다는
                    # 아 그리고 주변이 FILLED가 아닌 경우 무조건 추가. 음 그러고보니 그냥 프러스텀 검사할 때 면검사도 같이 하면 되는구만?
                    # 레벨 5까지는 프러스텀 검사를 하고, 레벨 6부터는 면검사를 한다.
                    # ㄱㄱㄱ
                    
                # 이게 굉장히 느림. 어쩌지.... ㅡㅡ;;;;
                #
                #그렇다면 이제 옥트리별 스피어 검사와 육면검사를 한다.
                #어떤 리스트에다가 프러스텀 안에 있는 옥트리를 전부 넣어서 그 옥트리들만 쓰게 한다? 특히, 상위 옥트리는 empty가 아닌 이상은 필요가 없지 않을까?
                #즉, 상위 옥트리가 empty이거나 filled인데 주변역시 filled인 것들만 빼고 프러스텀 안에 있다면 다 넣는다.
                #음.....
                # 아놔 근데 상위 옥트리들은.... empty인 것들만 빼놓고, empty가 아니면 일단 최하위 레벨까지 들어가서 일단 프러스텀 안에 있다면 넣는다.
                # 상위 옥트리는 frustum안에 완벽하게 없는 것들만 뺀다.
                # 즉, 추가되는 건 무조건 최하위 옥트리들. 진짜 많을텐데 음....
                # 레벨 6짜리로 할까? 간단하게?
                # 32768개에 4x4x4니까 꽤 그럴싸하다.
                # 레벨 5짜리
                # 8x8x8도 꽤 그럴싸함. 4096개밖에 안되고.
                # 레벨 5로 하자.
                
    cdef GenQuads(self, float *tV[64], float *tT[64], unsigned char *tC[64], int tIdx[64], int tLen[64], float *nsV[64], float *nsT[64], unsigned char *nsC[64], int nsIdx[64], int nsLen[64], float *aV[64], float *aT[64], unsigned char *aC[64], int aIdx[64], int aLen[64], float *iV[64], float *iT[64], unsigned char *iC[64], int iIdx[64], int iLen[64], Octree *root, Octree *parent, Chunk *chunk, Octree **octrees, Chunk **chunks, int pos[9][3], int depth, double frustum[6][4], int x, int y, int z, int ox, int oy, int oz, float vx, float vy, float vz, int lx, int ly, int lz, int updateCoords[64*3], int drawIdx, float sunx, float suny, float sunz):
        GenQuads(tV, tT, tC, tIdx, tLen, nsV, nsT, nsC, nsIdx, nsLen, aV, aT, aC, aIdx, aLen, iV, iT, iC, iIdx, iLen, root, parent, chunk, octrees, chunks, pos, depth, frustum, x, y, z, ox, oy, oz, vx, vy, vz, lx, ly, lz, updateCoords, drawIdx, sunx,suny,sunz)

    cdef void GetNeighboringOctrees(self, Octree * neighbors[6], Octree * octree):
        pass
    def HitBoundingBox(self, min, max, origin, dir_):
        cdef float minB[3]
        cdef float maxB[3]
        cdef float origina[3]
        cdef float dira[3]
        cdef float coorda[3]
        
        for i in range(3):
            minB[i] = min[i]
        for i in range(3):
            maxB[i] = max[i]
        for i in range(3):
            origina[i] = origin[i]
        for i in range(3):
            dira[i] = dir_[i]
        intersects = HitBoundingBox(minB,maxB, origina, dira,coorda)
        coord = coorda[0], coorda[1], coorda[2]
        return intersects, coord
    def SphereInFrustumPy(self, x, y, z, radius, frustum):
        for p in range(6):
            if frustum[p][0] * x + frustum[p][1] * y + frustum[p][2] * z + frustum[p][3] <= -radius:
                return False
        return True
    cdef int SphereInFrustum(self, double x, double y, double z, double radius, double frustum[6][4]):
        for p in range(6):
            if frustum[p][0] * x + frustum[p][1] * y + frustum[p][2] * z + frustum[p][3] <= -radius:
                return False
        return True

    def CubeInFrustumPy(self, x, y, z, size, frustum):
        cdef int p
        cdef int c
        cdef int c2
        c2 = 0

        for p in range(6):
            c = 0
            if (frustum[p][0] * (x - size) + frustum[p][1] * (y - size) + frustum[p][2] * (z - size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x + size) + frustum[p][1] * (y - size) + frustum[p][2] * (z - size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x - size) + frustum[p][1] * (y + size) + frustum[p][2] * (z - size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x + size) + frustum[p][1] * (y + size) + frustum[p][2] * (z - size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x - size) + frustum[p][1] * (y - size) + frustum[p][2] * (z + size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x + size) + frustum[p][1] * (y - size) + frustum[p][2] * (z + size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x - size) + frustum[p][1] * (y + size) + frustum[p][2] * (z + size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x + size) + frustum[p][1] * (y + size) + frustum[p][2] * (z + size) + frustum[p][3]) >= 0 :
                c += 1
            if c == 0:
                return 0
            if c == 8:
                c2 += 1
        if c2 == 6:
            return 2
        else:
            return 1
    cdef int CubeInFrustum(self, float x, float y, float z, double size, double frustum[6][4]):
        cdef int p
        cdef int c
        cdef int c2
        c2 = 0

        for p in range(6):
            c = 0
            if (frustum[p][0] * (x - size) + frustum[p][1] * (y - size) + frustum[p][2] * (z - size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x + size) + frustum[p][1] * (y - size) + frustum[p][2] * (z - size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x - size) + frustum[p][1] * (y + size) + frustum[p][2] * (z - size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x + size) + frustum[p][1] * (y + size) + frustum[p][2] * (z - size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x - size) + frustum[p][1] * (y - size) + frustum[p][2] * (z + size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x + size) + frustum[p][1] * (y - size) + frustum[p][2] * (z + size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x - size) + frustum[p][1] * (y + size) + frustum[p][2] * (z + size) + frustum[p][3]) >= 0 :
                c += 1
            if (frustum[p][0] * (x + size) + frustum[p][1] * (y + size) + frustum[p][2] * (z + size) + frustum[p][3]) >= 0 :
                c += 1
            if c == 0:
                return 0
            if c == 8:
                c2 += 1
        if c2 == 6:
            return 2
        else:
            return 1

    cdef void PutChunkIntoList(self, Chunk * chunk, Octree * octree):
        for i in range(STREAM_BUFFER_LEN):
            if self.chunks[i] == NULL:
                self.chunks[i] = chunk
                self.octrees[i] = octree
                # CalcFilled 또는 저장된 Filled데이터를 가져옴
                # Filled데이터는 어떻게 정렬할까?
                # 바이너리힙처럼 하면 되겠네 뭐...
                # 1,8,64,512,4096,32768,262144개의 서브트리? 용량이 꽤 되는데. 파일로는 300K밖에 안되네 이제보니;
                # 청크 128x128x128을 음..... 대충 메모리에 3메가 정도 먹을 거 같다.
                return
        assert False, "Not enough space"

        
# 음 뷰 프러스텀은 결국 세로 길이의 일정한 청크들이 뷰프러스텀 좌우앞뒤 안에 있는가 없는가만 보면 되겠다. 위아래검사는 맨 마지막 트리에서만
# 오로지 위아래검사만 한다.(이미 부모트리가 좌우앞뒤트리 안에 있으므로)



def Test():
    chunks = Chunks()
    chunks.Test2()



"""
옥트리
타일정의 char배열 3차원배열
z/y/x순서로 정렬.
아 아놔...

트리 자체가 필요가 없다. 그냥 청크로 나누면 된다!
------
만약 뷰포인트에서 사각형의 4 점으로 가는 벡터를 기준으로 클리핑 플레인을 5개 만들어서 그 안에 박스가 있으면 안그리는 그런 걸 이용한다면?
그러면 트렌슬레이션 없이 최적화가 가능하다.
음 인터넷 뒴져볼까...

아 근데...폴리곤이 한개일 때에는 한번의 InPlane검사로 되지만서도, 폴리곤이 많으니까-_- 그 모든 폴리곤에 대한 Plane을 다 만들어서 검사하면;;
ㄷㄷㄷ 되니까;;
6면검사가 가장 좋다.
-------------
옥트리에 폴리곤의 인덱스를 넣고, 폴리곤 버퍼를 만들어서 메모리에 저장해두고, 인덱스를 이용해서 쓴다.
청크의 가장자리는 육면검사를 안하는데, 하게한다.

육면검사를 안하는 게 더 빠를 수도 있으니 옵션에 육면검사를 안하는 것도 넣는다.
--------
매 프레임에 폴리곤을 생성하는 게 아니라, 뭐 3프레임에 1번씩만 업뎃하거나 이래도 확실히 잘된다.
-------
자. 만약 청크가 X축으로 완벽하게 막는지, Y축쪽으로 완벽하게 막는지, Z축쪽으로 완벽하게 막는지를 안다면
6면검사할 때 완벽하게 차있지 않아도 그쪽 면에 막는다면 안그려도 된다. ㅎㅎㅎ
이걸 OT_XBLOCK 등으로 하자.
-- DONE

---------------
음 이제 neighbor청크와의 6면검사를 하도록 한다면 된다. 그 다음에 맵 생성을 하자.
그 다음은 옥트리와 청크를 실제로 저장하도록 한다. 그런 다음 다음번에는 로드를 함
네이버 청크를 해결하면 한층 빨라진다.
-----------
glew 비주얼 C++용을 쓰면 mingw32안써도 된다. pysoy의 gl.pxd쓰면 된다.
--------
자............ 모든 코드를 다 C로 바꾸자. (...........)
아...로딩도 50초에서 5초로 줄었음 ㅡㅡ;;
전부 다 바꾸자.............
---------
앞뒷면 검사가 좀 틀린 것 같기도 함. 지금으로는 잘 몰겠지만 -- 아닐 수도 있음 거의 아님
------------------------
음 이제 맵 생성은 그냥 파이썬으로 하고, 큐브로 바꾸는 부분은 C로 해야겠다.
------------------
음 기본적으로..... 유져는 큐브의 3가지 면만 보게 된다. 이걸 이용해 좀 더 최적화 하는 방법은 없을까?
뭐 일단 충분히 빠르니까. 하지만.. 300fps 이정도로  나왔었으면 더 좋을 뻔 했다. 
--------
아 뭥미? .........................
뭔가 Z축이 반대로 파지는데여....
왜 그러는지 모르겠음;;
해결
------------
음 이제 뭐 한 블럭에 3개 쌓는 패널 계단 같은거는
블럭 구조 그대로 두고
투명으로 취급하고
충돌검사에서만 3단으로 취급하고
플래그값을 따로 둬서 바이너리로 100,010,001,110,011,111 등으로 뭐..... 해서 그릴 때만 신경쓰면 되도록 한다.
다른 블럭들도 모두 이런식으로 블럭으로 취급하면서도 플래그값만 따로 두도록 한다.
Torch같은 것도 역시 이런식으로 취급한다. 투명이면서 플래그값이 다르고 충돌검사/렌더링만 다르게 하고 뭐 그런식.
--------------
윗부분이 YBLOCK일 경우 햇빛을 완전히 차단한다.

아. 청크를 따라서 가장 위에 그리고 상위레벨에 있는 YBLOCK하는 청크를 찾아 depth와 position을 기록해 둔다.
그 아래에 있는 옥트리 그리고 하위옥트리는 모두 햇빛을 받지 않는다.

음.... 일단 청크마다 최상위 YBlock에 관한 정보를 만약 모든 옥트리가 가지고 있다면 정말 느릴 것이니 따로 저장.
최상위 YBlock에 관한 정보를 미리 계산해 둔 후에, 그 YBlock자체는 태양광과 함께 렌더링 하고(최상위 블럭들만)
그 미만들은 모두 횃불이나 용암등으로만 수동 라이팅을 한다.

즉, 128x128수준으로 Y값을 기록해 두면 가장 편하겠군? 아...YBlock값을 이용할 필요도 없지 않나 싶다. 블럭을 렌더링 할 때 그냥 높이값만 일겅오면 되니...
즉, 그냥 최상위 블럭들 Y값들만 다 기록해서 Height맵을 만들고, 팔 때마다 업뎃하고 뭐 이러면 된다.
그래서 그 아래 블럭들(최상위 블럭의 아랫면들도)은 태양의 영향을 받지 않는다.

에 근데 이러면 일렬로 위로 주욱 쌓은 놈들은?? ㅡㅡ;
아. 이래서 주변블락이 필요. 주변 약... 9x9블럭의 Y값을 읽어와서 그것들이 다 현재 블럭의 Y값보다 높다면 태양을 완전히 차단
그중에 하나씩 비어있을수록 점점 태양의 영향을 많이 받음.
----------
CalcOne 할 때에도 이거 높이 계산하는 거 넣어야 한다.
------
확실히 마우스 피킹할 때 엉뚱한거 나올 때 있다. 아하. 바로 앞에 있는 것보다 옆에 있는 게 vector상에서 더 가까울 때 이런 결과가 나온다.
또한 CalcFilled를 해도 제대로 안될 때가 있다. 뭥미...
-------------------
음. 주변 청크 값을 꼭 얻어와야 한다. Lighting.....
--------
라이팅 제대로 안됨(개선)
마우스 피킹 가끔 삑사리(바로 앞에있는 거보다 벡터길이가 더 가까운 리스트 내의 사각형. 이게 어떻게 충돌을 해서 그런지는 몰겠지만)
프러스텀 에러: 높이가 일정 이하로 떨어지면(바닥으로 가면) 안보인다.

음....프러스텀 에러는 에러라기 보다는 뭔가... 특별히 구현해 줘야 하는게 이쓴ㄴ 건지. 땅속에서부터 안파고 제대로 파면 그런 에러가 없었다.
좀 더 테스트해보고..

가끔 바닥이 안보이는 건 "너무 멀어서" 즉 프러스텀 밖이라서 그런 것.
------------
------------------
if 블럭을 넣지 말고, Computer라는 블럭을 넣고 컴퓨터에 프로그래밍을 간단하게 하고 더 어드벤스드 된 코딩은 서버 마스터만 할 수 있게 하거나 허락
받은 사람만 하게 하고
컴퓨터와 여러가지를 연결해서 여러가지를 만든다.
----------
지금은 실시간으로 quad를 만드는데 이건 캐슁의 여지가 항상 있다.
옥트리 수준으로 이미 quad가 만들어질 대로 다 만들어진 옥트리는 건드리지 않고
뭐 그럴 수도 있겠다만.... 결국 quad가 그려지는 수가 적으냐(GL오버헤드) 아니면 chunk를 순회하는 수가 적으냐 그차이.
------------
음..............................................................
"""
