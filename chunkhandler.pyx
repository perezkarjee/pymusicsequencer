import OpenGL.GL as GL
from OpenGL.arrays import ArrayDatatype as ADT

class VBOs(object):
    def __init__(self):
        self.vbos = []
class VertexBuffer(object):

  def __init__(self, data, usage=GL.GL_STATIC_DRAW):
    self.buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffer)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, ADT.arrayByteCount(data), ADT.voidDataPointer(data), usage)
    self.reload = False

  def __del__(self):
    if not self.reload:
      GL.glDeleteBuffers(1, GL.GLuint(self.buffer))

  def bind(self):
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffer)

  def bind_colors(self, size, type, stride=0):
    self.bind()
    GL.glColorPointer(size, type, stride, None)

  def bind_edgeflags(self, stride=0):
    self.bind()
    GL.glEdgeFlagPointer(stride, None)

  def bind_indexes(self, type, stride=0):
    self.bind()
    GL.glIndexPointer(type, stride, None)

  def bind_normals(self, type, stride=0):
    self.bind()
    GL.glNormalPointer(type, stride, None)

  def bind_texcoords(self, size, type, stride=0):
    self.bind()
    GL.glTexCoordPointer(size, type, stride, None)

  def bind_vertexes(self, size, type, stride=0):
    self.bind()
    GL.glVertexPointer(size, type, stride, None)

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

cdef extern from "cpart.h":
    struct tTile:
        float height
        int tileData
    struct tChunk:
        tTile *tiles
        int x,y,z
    ctypedef tChunk Chunk
    ctypedef tTile Tile
    cdef int ReadInt(char *str)
    cdef char HitBoundingBox(float minB[3],float maxB[3], float origin[3], float dir[3],float coord[3])



cdef void FreeChunk(Chunk* chunk):
    free(chunk.tiles)
    free(chunk)

NUMCHUNKS = 1
SIZE_CHUNK = 8
import random

SW = 1024
SH = 768
cdef class GUIBGRenderer(object):
    vbos = VBOs()
    cdef float *quad
    cdef float *texcs
    def __cinit__(self):
        texupx = 0
        texupy = 0
        x = 0
        y = SH-256
        w = SW
        h = 256


        self.quad = <float*>malloc(sizeof(float)*4*3)
        self.texcs = <float*>malloc(sizeof(float)*4*2)
        # x,y,z,  x,y,z  x,y,z,  x,y,z * 5
        self.quad[0] = float(x)
        self.quad[1] = -float(y+h)
        self.quad[2] = 100.0
        self.quad[3] = float(x+w)
        self.quad[4] = -float(y+h)
        self.quad[5] = 100.0
        self.quad[6] = float(x+w)
        self.quad[7] =  -float(y)
        self.quad[8] =  100.0
        self.quad[9] = float(x)
        self.quad[10] =  -float(y)
        self.quad[11] = 100.0
        self.texcs[0] = texupx
        self.texcs[1] = texupy+1.0
        self.texcs[2] = texupx+1.0
        self.texcs[3] = texupy+1.0
        self.texcs[4] = texupx+1.0
        self.texcs[5] = texupy
        self.texcs[6] = texupx
        self.texcs[7] = texupy

    def __dealloc__(self):
        free(self.texcs)
        free(self.quad)

    def Regen(self):

        cdef char *quad
        cdef char *texcs

        if self.vbos.vbos:
            self.vbos.vbos[0].reload = True
            self.vbos.vbos[1].reload = True
            del self.vbos.vbos[0]
            del self.vbos.vbos[0]
        quad = <char*>self.quad
        texcs = <char*>self.texcs
        self.vbos.vbos += [0,0]
        self.vbos.vbos[0] = VertexBuffer(quad[:4*3*sizeof(float)])
        self.vbos.vbos[1] = VertexBuffer(texcs[:4*2*sizeof(float)])



    def Render(self):
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glDisable(GL.GL_TEXTURE_1D)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_TEXTURE_COORD_ARRAY)

        self.vbos.vbos[0].bind()
        GL.glVertexPointer( 3, GL.GL_FLOAT, 0, None)#<void*>self.verts) 
        self.vbos.vbos[1].bind()
        GL.glTexCoordPointer( 2, GL.GL_FLOAT, 0, None)#<void*>self.verts) 

        glDrawArrays(GL.GL_QUADS, 0, 4*3)

        GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_TEXTURE_1D)
class Tex:
    def __init__(self):
        self.tex = []

class Element:
    def __init__(self):
        self.ele = None
        self.ele2 = None

FACE_X = 0
FACE_Z = 1
NOWALL = 2
cdef struct WallTile:
    int facing
    int frontTile
    int backTile


# 벽은 한 타일에 2개씩 있다.
# x=0,z=0쪽에 있음.
# 음................................................
# 걍 귀찮으니 타일구조로 하고 벽이 있는지 없는지만 표현

cdef struct Walls:
    WallTile *wallsX
    WallTile *wallsZ
    int x
    int y
    int z

"""
울온처럼 평평한 땅에만 지을 수 있다.
평평한 땅을 만들면 거기에 타일의 높낮이 조절 불가능하게 해야함
걍 map인스턴스를 여러개를 만들어서 렌더링을 한다. 아 안되넹 vbos가 공유가 되버려서';;;;;
걍 Map클래스 내부에서 잘 처리되도록 한다.
"""
class Buffer:
    def __init__(self):
        self.vbos = VBOs()
        self.tex = Tex()
        self.ele = Element()
        self.coord = (0,0)
class Buffers:
    def __init__(self):
        self.buffers = {}
cdef class Map:
    cdef Chunk **chunks
    cdef float *quads
    cdef float *topquads
    cdef float *texcs
    cdef Walls **wallChunks
    cdef int **eles
    cdef int **eles2
    cdef int tileData
    cdef int prevX
    buffers = Buffers()
    cdef int prevZ
    cdef int idx
    def __cinit__(self, idx, coord):
        self.idx = idx
        self.buffers.buffers[idx] = Buffer()
        self.buffers.buffers[idx].coord = coord
        self.wallChunks = <Walls**>malloc(sizeof(Walls*)*NUMCHUNKS)
        memset(self.wallChunks, 0, sizeof(Walls*)*NUMCHUNKS)
        self.wallChunks[0] = <Walls*>malloc(sizeof(Walls))
        self.wallChunks[0].wallsX = <WallTile*>malloc(sizeof(WallTile)*SIZE_CHUNK*SIZE_CHUNK)
        self.wallChunks[0].wallsZ = <WallTile*>malloc(sizeof(WallTile)*SIZE_CHUNK*SIZE_CHUNK)
        self.wallChunks[0].x = 0
        self.wallChunks[0].y = 0
        self.wallChunks[0].z = 0
        for i in range(SIZE_CHUNK*SIZE_CHUNK):
            self.wallChunks[0].wallsX[i].facing = NOWALL
            self.wallChunks[0].wallsX[i].frontTile = 0
            self.wallChunks[0].wallsX[i].backTile = 0
            self.wallChunks[0].wallsZ[i].facing = NOWALL
            self.wallChunks[0].wallsZ[i].frontTile = 0
            self.wallChunks[0].wallsZ[i].backTile = 0

        self.chunks = <Chunk**>malloc(sizeof(Chunk*)*NUMCHUNKS)
        memset(self.chunks, 0, sizeof(Chunk*)*NUMCHUNKS)
        self.chunks[0] = <Chunk*>malloc(sizeof(Chunk))
        self.chunks[0].tiles = <Tile*>malloc(sizeof(Tile)*SIZE_CHUNK*SIZE_CHUNK)
        self.chunks[0].x = 0
        self.chunks[0].y = 0
        self.chunks[0].z = 0
        for i in range(SIZE_CHUNK*SIZE_CHUNK):
            self.chunks[0].tiles[i].height = 0.0#+float(random.randint(0,10))
            self.chunks[0].tiles[i].tileData = 0#+float(random.randint(0,10))

        self.quads = <float*>0
        self.topquads = <float*>0
        self.texcs = <float*>0
        self.eles = <int**>0
        self.eles2 = <int**>0


    def AddWall(self, x, y, z):
        x = int(x)
        z = -int(z)
    def SetTile(self, tile):
        self.tileData = tile
    def ClickTile(self, mode, part, position):
        x,y,z = position
        x = int(x)
        z = -int(z)
        if self.prevX == x and self.prevZ == z and self.chunks[0].tiles[z*SIZE_CHUNK+x].tileData == self.tileData:
            return
        self.prevX = x
        self.prevZ = z
        LEFTTOP = 0
        RIGHTTOP = 1
        LEFTBOT = 2
        RIGHTBOT = 3
        #self.chunks[0].tiles[z*SIZE_CHUNK+x].height += 1
        self.chunks[0].tiles[z*SIZE_CHUNK+x].tileData = self.tileData
        self.Regen(*self.buffers.buffers[self.idx].tex.tex)
    def Regen(self, *textures):
        self.buffers.buffers[self.idx].tex.tex = textures
        cdef char *topquads
        cdef char *quads
        cdef char *texcs
        if self.topquads:
            free(self.topquads)
        if self.texcs:
            free(self.texcs)
        if self.quads:
            free(self.quads)
        if self.eles:
            for i in range(len(textures)):
                free(self.eles[i])
            free(self.eles)
        if self.eles2:
            for i in range(len(textures)):
                free(self.eles2[i])
            free(self.eles2)
        self.quads = <float*>malloc(sizeof(float)*3*SIZE_CHUNK*SIZE_CHUNK*4*4) # xyz, width, height, verts*4=quad, quads
        self.topquads = <float*>malloc(sizeof(float)*3*SIZE_CHUNK*SIZE_CHUNK*4) # xyz, width, height, verts*4=quad, quads
        self.texcs = <float*>malloc(sizeof(float)*2*SIZE_CHUNK*SIZE_CHUNK*4) # xyz, width, height, verts*4=quad, quads
        # x,y,z,  x,y,z  x,y,z,  x,y,z * 5

        xx = 0.0
        yy = 0.0
        zz = 0.0
        # 텍스쳐별로 vbo를 만들던지 아니면 한 vbo로 하되 오프셋을 다르게 하여 텍스쳐를 다르게 적용시킨다?
        # 아 엘레멘트버퍼를 만들어서 그걸루 나누자.

        """
        for y in range(SIZE_CHUNK):
            for x in range(SIZE_CHUNK):
                self.chunks[0].tiles[y*SIZE_CHUNK+x].tileData = random.randint(0,1)
                #self.chunks[0].tiles[y*SIZE_CHUNK+x].height = random.randint(0,1)
        """
        self.buffers.buffers[self.idx].ele.ele = [[] for i in range(len(textures))]
        ii = 0
        for y in range(SIZE_CHUNK):
            for x in range(SIZE_CHUNK):
                height = self.chunks[0].tiles[y*SIZE_CHUNK+x].height
                for kkk in range(len(textures)):
                    if self.chunks[0].tiles[y*SIZE_CHUNK+x].tileData == kkk:
                        self.buffers.buffers[self.idx].ele.ele[kkk] += [ii,ii+1,ii+2,ii+3]
                        # 여기에 엘레멘트버퍼를 추가
                ii += 4
                i=0
                # top
                self.topquads[y*SIZE_CHUNK*4*3+i+x*4*3] = xx
                self.topquads[y*SIZE_CHUNK*4*3+1+i+x*4*3] = float(height)*0.25
                self.topquads[y*SIZE_CHUNK*4*3+2+i+x*4*3] = zz

                self.topquads[y*SIZE_CHUNK*4*3+3+i+x*4*3] = xx+1.0
                self.topquads[y*SIZE_CHUNK*4*3+4+i+x*4*3] = float(height)*0.25
                self.topquads[y*SIZE_CHUNK*4*3+5+i+x*4*3] = zz

                self.topquads[y*SIZE_CHUNK*4*3+6+i+x*4*3] = xx+1.0
                self.topquads[y*SIZE_CHUNK*4*3+7+i+x*4*3] = float(height)*0.25
                self.topquads[y*SIZE_CHUNK*4*3+8+i+x*4*3] = zz-1.0

                self.topquads[y*SIZE_CHUNK*4*3+9+i+x*4*3] = xx
                self.topquads[y*SIZE_CHUNK*4*3+10+i+x*4*3] = float(height)*0.25
                self.topquads[y*SIZE_CHUNK*4*3+11+i+x*4*3] = zz-1.0


                self.texcs[y*SIZE_CHUNK*4*2+i+0+x*4*2] = 0.0
                self.texcs[y*SIZE_CHUNK*4*2+i+1+x*4*2] = 0.0
                self.texcs[y*SIZE_CHUNK*4*2+i+2+x*4*2] = 1.0
                self.texcs[y*SIZE_CHUNK*4*2+i+3+x*4*2] = 0.0
                self.texcs[y*SIZE_CHUNK*4*2+i+4+x*4*2] = 1.0
                self.texcs[y*SIZE_CHUNK*4*2+i+5+x*4*2] = 1.0
                self.texcs[y*SIZE_CHUNK*4*2+i+6+x*4*2] = 0.0
                self.texcs[y*SIZE_CHUNK*4*2+i+7+x*4*2] = 1.0


                xx += 1.0
            zz -= 1.0
            xx = 0.0
        self.eles = <int**>malloc(sizeof(int*)*len(textures))
        for i in range(len(textures)):
            self.eles[i] = <int*>malloc(sizeof(int)*len(self.buffers.buffers[self.idx].ele.ele[i])+1)
            for j in range(len(self.buffers.buffers[self.idx].ele.ele[i])):
                self.eles[i][j] = self.buffers.buffers[self.idx].ele.ele[i][j]

        self.buffers.buffers[self.idx].ele.ele2 = [[] for i in range(len(textures))]
        xx = 0.0
        yy = 0.0
        zz = 0.0
        ii = 0
        for y in range(SIZE_CHUNK):
            for x in range(SIZE_CHUNK):
                height = self.chunks[0].tiles[y*SIZE_CHUNK+x].height

                for kkk in range(len(textures)):
                    if self.chunks[0].tiles[y*SIZE_CHUNK+x].tileData == kkk:
                        for jjj in range(4*4):
                            self.buffers.buffers[self.idx].ele.ele2[kkk] += [ii+jjj]
                        # 여기에 엘레멘트버퍼를 추가
                ii += 4*4
                i=0
                # front
                self.quads[y*SIZE_CHUNK*4*4*3+i+x*4*4*3] = xx # top left
                self.quads[y*SIZE_CHUNK*4*4*3+1+i+x*4*4*3] = float(height)*0.25
                self.quads[y*SIZE_CHUNK*4*4*3+2+i+x*4*4*3] = zz

                self.quads[y*SIZE_CHUNK*4*4*3+3+i+x*4*4*3] = xx
                self.quads[y*SIZE_CHUNK*4*4*3+4+i+x*4*4*3] = -100.0
                self.quads[y*SIZE_CHUNK*4*4*3+5+i+x*4*4*3] = zz

                self.quads[y*SIZE_CHUNK*4*4*3+6+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+7+i+x*4*4*3] = -100.0
                self.quads[y*SIZE_CHUNK*4*4*3+8+i+x*4*4*3] = zz

                self.quads[y*SIZE_CHUNK*4*4*3+9+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+10+i+x*4*4*3] = float(height)*0.25
                self.quads[y*SIZE_CHUNK*4*4*3+11+i+x*4*4*3] = zz
                i += 12

                # back
                self.quads[y*SIZE_CHUNK*4*4*3+i+x*4*4*3] = xx # top left
                self.quads[y*SIZE_CHUNK*4*4*3+1+i+x*4*4*3] = float(height)*0.25
                self.quads[y*SIZE_CHUNK*4*4*3+2+i+x*4*4*3] = zz-1.0

                self.quads[y*SIZE_CHUNK*4*4*3+3+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+4+i+x*4*4*3] = float(height)*0.25
                self.quads[y*SIZE_CHUNK*4*4*3+5+i+x*4*4*3] = zz-1.0

                self.quads[y*SIZE_CHUNK*4*4*3+6+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+7+i+x*4*4*3] = -100.0
                self.quads[y*SIZE_CHUNK*4*4*3+8+i+x*4*4*3] = zz-1.0

                self.quads[y*SIZE_CHUNK*4*4*3+9+i+x*4*4*3] = xx
                self.quads[y*SIZE_CHUNK*4*4*3+10+i+x*4*4*3] = -100.0
                self.quads[y*SIZE_CHUNK*4*4*3+11+i+x*4*4*3] = zz-1.0
                i += 12

                # left
                self.quads[y*SIZE_CHUNK*4*4*3+i+x*4*4*3] = xx # top left
                self.quads[y*SIZE_CHUNK*4*4*3+1+i+x*4*4*3] = float(height)*0.25
                self.quads[y*SIZE_CHUNK*4*4*3+2+i+x*4*4*3] = zz

                self.quads[y*SIZE_CHUNK*4*4*3+3+i+x*4*4*3] = xx
                self.quads[y*SIZE_CHUNK*4*4*3+4+i+x*4*4*3] = float(height)*0.25
                self.quads[y*SIZE_CHUNK*4*4*3+5+i+x*4*4*3] = zz-1.0

                self.quads[y*SIZE_CHUNK*4*4*3+6+i+x*4*4*3] = xx
                self.quads[y*SIZE_CHUNK*4*4*3+7+i+x*4*4*3] = -100.0
                self.quads[y*SIZE_CHUNK*4*4*3+8+i+x*4*4*3] = zz-1.0

                self.quads[y*SIZE_CHUNK*4*4*3+9+i+x*4*4*3] = xx
                self.quads[y*SIZE_CHUNK*4*4*3+10+i+x*4*4*3] = -100.0
                self.quads[y*SIZE_CHUNK*4*4*3+11+i+x*4*4*3] = zz
                i += 12

                # right
                self.quads[y*SIZE_CHUNK*4*4*3+i+x*4*4*3] = xx+1.0 # top right
                self.quads[y*SIZE_CHUNK*4*4*3+1+i+x*4*4*3] = float(height)*0.25
                self.quads[y*SIZE_CHUNK*4*4*3+2+i+x*4*4*3] = zz

                self.quads[y*SIZE_CHUNK*4*4*3+3+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+4+i+x*4*4*3] = -100.0
                self.quads[y*SIZE_CHUNK*4*4*3+5+i+x*4*4*3] = zz

                self.quads[y*SIZE_CHUNK*4*4*3+6+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+7+i+x*4*4*3] = -100.0
                self.quads[y*SIZE_CHUNK*4*4*3+8+i+x*4*4*3] = zz-1.0

                self.quads[y*SIZE_CHUNK*4*4*3+9+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+10+i+x*4*4*3] = float(height)*0.25
                self.quads[y*SIZE_CHUNK*4*4*3+11+i+x*4*4*3] = zz-1.0
                i += 12

                xx += 1.0
            zz -= 1.0
            xx = 0.0
        self.eles2 = <int**>malloc(sizeof(int*)*len(textures))
        for i in range(len(textures)):
            self.eles2[i] = <int*>malloc(sizeof(int)*len(self.buffers.buffers[self.idx].ele.ele2[i])+1)
            for j in range(len(self.buffers.buffers[self.idx].ele.ele2[i])):
                self.eles2[i][j] = self.buffers.buffers[self.idx].ele.ele2[i][j]

        if self.buffers.buffers[self.idx].vbos.vbos:
            self.buffers.buffers[self.idx].vbos.vbos[0].reload = True
            self.buffers.buffers[self.idx].vbos.vbos[1].reload = True
            self.buffers.buffers[self.idx].vbos.vbos[2].reload = True
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
        quads = <char*>self.quads
        topquads = <char*>self.topquads
        texcs = <char*>self.texcs
        self.buffers.buffers[self.idx].vbos.vbos += [0,0,0]
        self.buffers.buffers[self.idx].vbos.vbos[0] = VertexBuffer(topquads[:SIZE_CHUNK*SIZE_CHUNK*4*3*sizeof(float)])
        self.buffers.buffers[self.idx].vbos.vbos[1] = VertexBuffer(quads[:SIZE_CHUNK*SIZE_CHUNK*4*4*3*sizeof(float)])
        self.buffers.buffers[self.idx].vbos.vbos[2] = VertexBuffer(texcs[:SIZE_CHUNK*SIZE_CHUNK*4*2*sizeof(float)])


    def Render(self):
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glDisable(GL.GL_TEXTURE_1D)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        #GL.glEnableClientState(GL.GL_NORMAL_ARRAY)
        GL.glEnableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        #GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        self.buffers.buffers[self.idx].vbos.vbos[0].bind()
        GL.glVertexPointer( 3, GL.GL_FLOAT, 0, None)#<void*>self.verts) 
        self.buffers.buffers[self.idx].vbos.vbos[2].bind()
        GL.glTexCoordPointer( 2, GL.GL_FLOAT, 0, None)#<void*>self.verts) 

        for i in range(len(self.buffers.buffers[self.idx].tex.tex)):
            if len(self.buffers.buffers[self.idx].ele.ele[i]):
                GL.glBindTexture(GL.GL_TEXTURE_2D, self.buffers.buffers[self.idx].tex.tex[i][0])
                #GL.glNormalPointer(GL.GL_FLOAT, 0, None) 
                #glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.tT[i]) 
                #glColorPointer(3, GL.GL_UNSIGNED_BYTE, 0, <void*>self.tC[i]) 

                glDrawElements(GL.GL_QUADS, len(self.buffers.buffers[self.idx].ele.ele[i]), GL.GL_UNSIGNED_INT, <void*>self.eles[i])
                #glDrawArrays(GL.GL_QUADS, 0, SIZE_CHUNK*SIZE_CHUNK*4)
        GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)

        GL.glDisable(GL.GL_TEXTURE_2D)
        self.buffers.buffers[self.idx].vbos.vbos[1].bind()
        GL.glVertexPointer( 3, GL.GL_FLOAT, 0, None)#<void*>self.verts) 
        #glDrawArrays(GL.GL_QUADS, 0, SIZE_CHUNK*SIZE_CHUNK*4*4)
        for i in range(len(self.buffers.buffers[self.idx].tex.tex)):
            if len(self.buffers.buffers[self.idx].ele.ele2[i]):
                GL.glColor4ub(*self.buffers.buffers[self.idx].tex.tex[i][1])
                glDrawElements(GL.GL_QUADS, len(self.buffers.buffers[self.idx].ele.ele2[i]), GL.GL_UNSIGNED_INT, <void*>self.eles2[i])
        #glDrawElements(GL.GL_TRIANGLES, self.indNum, GL.GL_UNSIGNED_INT, <void*>self.inds)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        #GL.glDisableClientState(GL.GL_NORMAL_ARRAY)
        #GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        #GL.glDisableClientState(GL.GL_COLOR_ARRAY)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_TEXTURE_1D)
    def __dealloc__(self):
        for i in range(NUMCHUNKS):
            if self.chunks[i]:
                FreeChunk(self.chunks[i])
        free(self.chunks)
        if self.topquads:
            free(self.topquads)
        if self.texcs:
            free(self.texcs)
        if self.quads:
            free(self.quads)
        if self.eles:
            for i in range(len(self.buffers.buffers[self.idx].tex.tex)):
                free(self.eles[i])
            free(self.eles)
        if self.eles2:
            for i in range(len(self.buffers.buffers[self.idx].tex.tex)):
                free(self.eles2[i])
            free(self.eles2)


cdef class Model:
    cdef char *verts
    cdef char *texcs
    cdef char *normals
    cdef char *inds
    cdef int num
    cdef int indNum
    cdef int lX,lY,lZ,hX,hY,hZ
    vbo = VBOs()
    def __cinit__(self, fileName):
        cdef char *lentypenameChar
        cdef char *versionChar
        cdef char *numvertsChar
        cdef char *numanimsChar
        cdef char *lenanimnameChar
        cdef char *lenanimChar
        cdef char *numindChar
        cdef char *v
        cdef char *t
        cdef char *n
        cdef char *i
        cdef float *vbound

        f = open(fileName, "rb")

        header = f.read(6)
        if header == "JRPG3D":
            """
         * JRPG3D
         * version 4bytes
         * numverts 4bytes
         * lentypename 4bytes
         * typename
         * numanims

            """
            versionStr = f.read(4)
            versionChar = versionStr
            version = ReadInt(versionChar)
            free(versionChar)

            numvertsStr = f.read(4)
            numvertsChar = numvertsStr
            numverts = ReadInt(numvertsChar)
            free(numvertsChar)

            numindStr = f.read(4)
            numindChar = numindStr
            numind = ReadInt(numindChar)
            free(numindChar)

            lentypenameStr = f.read(4)
            lentypenameChar = lentypenameStr
            lentypename = ReadInt(lentypenameChar)
            free(lentypenameChar)

            typename = f.read(lentypename)

            numanimsStr = f.read(4)
            numanimsChar = numanimsStr
            numanims = ReadInt(numanimsChar)
            free(numanimsChar)

            lenanimnameStr = f.read(4)
            lenanimnameChar = lenanimnameStr
            lenanimname = ReadInt((lenanimnameChar))
            free(lenanimnameChar)

            animname = f.read(lenanimname)

            lenanimStr = f.read(4)
            lenanimChar = lenanimStr
            lenanim = ReadInt((lenanimChar))
            free(lenanimChar)
            vertsStr = f.read(numverts*4*3)
            texcsStr = f.read(numverts*4*2)
            normsStr = f.read(numverts*4*3)
            indsStr = f.read(numind*4)
            v = vertsStr
            t = texcsStr
            n = normsStr
            i = indsStr

            self.verts = <char*>malloc(numverts*4*3)
            memcpy(self.verts, v, numverts*4*3)
            free(v)

            self.texcs = <char*>malloc(numverts*4*2)
            memcpy(self.texcs, t, numverts*4*2)
            free(t)

            self.normals = <char*>malloc(numverts*4*3)
            memcpy(self.normals, n, numverts*4*3)
            free(n)

            self.inds = <char*>malloc(numind*4)
            memcpy(self.inds, i, numind*4)
            free(i)
            self.num = numverts
            self.indNum = numind

            vbound = <float*>v
            lowestX = vbound[0]
            lowestY = vbound[1]
            lowestZ = vbound[2]
            highestX = lowestX
            highestY = lowestY
            highestZ = lowestZ
            curX = 0
            curY = 0
            curZ = 0
            for ii in range(numverts):
                curX = vbound[ii*3]
                curY = vbound[ii*3+1]
                curZ = vbound[ii*3+2]
                if lowestX > curX:
                    lowestX = curX
                if lowestY > curY:
                    lowestY = curY
                if lowestZ > curZ:
                    lowestZ = curZ

                if highestX < curX:
                    highestX = curX
                if highestY < curY:
                    highestY = curY
                if highestX < curZ:
                    highestZ = curZ

            self.lX = lowestX
            self.lY = lowestY
            self.lZ = lowestZ
            self.hX = highestX
            self.hY = highestY
            self.hZ = highestZ



            


        """
         * JRPG3D
         * version 4bytes
         * numverts 4bytes
         * lentypename 4bytes
         * typename
         * numanims
         * 
         * lenanimname
         * animname
         * lenanim
         * verts*lenanim, texcs*lenanim, normals*lenanim
         * 
         * lenanimname
         * animname
         * lenanim
         * verts*lenanim, texcs*lenanim, normals*lenanim
         * ...
        
        """
        pass
    def __dealloc__(self):
        free(self.verts)
        free(self.texcs)
        free(self.normals)
        free(self.inds)
    def GetNum(self):
        return self.num
    def GetBounds(self):
        return [(self.lX,self.lY,self.lZ), (self.hX,self.hY,self.hZ)]
    def Regen(self):
        if self.vbo.vbos:
            self.vbo.vbos[0].reload = True
            self.vbo.vbos[1].reload = True
            del self.vbo.vbos[0]
            del self.vbo.vbos[0]
        self.vbo.vbos += [0,0]
        self.vbo.vbos[0] = VertexBuffer(self.verts[:self.num*4*3])
        self.vbo.vbos[1] = VertexBuffer(self.normals[:self.num*4*3])
    def Draw(self):
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_NORMAL_ARRAY)
        #GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        self.vbo.vbos[0].bind()
        GL.glVertexPointer( 3, GL.GL_FLOAT, 0, None)#<void*>self.verts) 
        GL.glNormalPointer(GL.GL_FLOAT, 0, None) 
        #glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.tT[i]) 
        #glColorPointer(3, GL.GL_UNSIGNED_BYTE, 0, <void*>self.tC[i]) 
        #glDrawArrays(GL.GL_TRIANGLES, 0, self.num)
        glDrawElements(GL.GL_TRIANGLES, self.indNum, GL.GL_UNSIGNED_INT, <void*>self.inds)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_NORMAL_ARRAY)
        #GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        #GL.glDisableClientState(GL.GL_COLOR_ARRAY)

"""
from OpenGL.GL import *
from OpenGL.raw import GL


from OpenGL.arrays import ArrayDatatype as ADT
class VertexBuffer(object):

  def __init__(self, data, usage):
    self.buffer = GL.GLuint(0)
    glGenBuffers(1, self.buffer)
    self.buffer = self.buffer.value
    glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
    glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(data), ADT.voidDataPointer(data), usage)

  def __del__(self):
    glDeleteBuffers(1, GL.GLuint(self.buffer))

  def bind(self):
    glBindBuffer(GL_ARRAY_BUFFER, self.buffer)

  def bind_colors(self, size, type, stride=0):
    self.bind()
    glColorPointer(size, type, stride, None)

  def bind_edgeflags(self, stride=0):
    self.bind()
    glEdgeFlagPointer(stride, None)

  def bind_indexes(self, type, stride=0):
    self.bind()
    glIndexPointer(type, stride, None)

  def bind_normals(self, type, stride=0):
    self.bind()
    glNormalPointer(type, stride, None)

  def bind_texcoords(self, size, type, stride=0):
    self.bind()
    glTexCoordPointer(size, type, stride, None)

  def bind_vertexes(self, size, type, stride=0):
    self.bind()
    glVertexPointer(size, type, stride, None)

"""
"""
기본적으로 컬링이 필요없을 것 같다. 걍 범위안의 타일을 모조리 렌더링하면 됨
"""
