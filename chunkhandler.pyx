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

# 렌더링할 때 캐슁을 이용하여 실시간으로 삼각형을 생성하여 렌더링한다.
# 삼각형을 생성할 때 CatMull을 이용하여 스무딩을 한다.
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
cdef void FreeChunk(Chunk* chunk):
    free(chunk.tiles)
    free(chunk)
NUMCHUNKS = 1
cdef class Map:
    cdef Chunk **chunks
    def __cinit__(self):
        self.chunks = <Chunk**>malloc(sizeof(Chunk*)*NUMCHUNKS)
        memset(self.chunks, 0, sizeof(Chunk*)*NUMCHUNKS)
        self.chunks[0] = <Chunk*>malloc(sizeof(Chunk))
        self.chunks[0].tiles = <Tile*>malloc(sizeof(Tile)*32*32)
        for i in range(32*32):
            self.chunks[0].tiles[i].height = 0.0
    def Render(self):
        pass
    def __dealloc__(self):
        for i in range(NUMCHUNKS):
            if self.chunks[i]:
                FreeChunk(self.chunks[i])
        free(self.chunks)

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
            del self.vbo.vbos[0]
        self.vbo.vbos += [0]
        self.vbo.vbos[0] = VertexBuffer(self.verts[:self.num*4*3])
    def Draw(self):
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        #GL.glEnableClientState(GL.GL_NORMAL_ARRAY)
        #GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        self.vbo.vbos[0].bind()
        GL.glVertexPointer( 3, GL.GL_FLOAT, 0, None)#<void*>self.verts) 
        #glNormalPointer(GL.GL_FLOAT, 0, <void*>self.normals) 
        #glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.tT[i]) 
        #glColorPointer(3, GL.GL_UNSIGNED_BYTE, 0, <void*>self.tC[i]) 
        #glDrawArrays(GL.GL_TRIANGLES, 0, self.num)
        glDrawElements(GL.GL_TRIANGLES, self.indNum, GL.GL_UNSIGNED_INT, <void*>self.inds)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        #GL.glDisableClientState(GL.GL_NORMAL_ARRAY)
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
