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

cdef class Map:
    cdef Chunk **chunks
    def __cinit__(self):
        self.chunks = <Chunk**>malloc(sizeof(Chunk*)*9)

    def __dealloc__(self):
        for i in range(9):
            if self.chunks[i]:
                free(self.chunks[i])
        free(self.chunks)

"""
from OpenGL.GL import *
from OpenGL.raw import GL
from OpenGL.arrays import ArrayDatatype as ADT


class VertexBuffer(object):

  def __init__(self, data, usage):
    self.buffer = GL.GLuint(0)
    glGenBuffers(1, self.buffer)
    self.buffer = self.buffer.value
    glBindBuffer(GL_ARRAY_BUFFER_ARB, self.buffer)
    glBufferData(GL_ARRAY_BUFFER_ARB, ADT.arrayByteCount(data), ADT.voidDataPointer(data), usage)

  def __del__(self):
    glDeleteBuffers(1, GL.GLuint(self.buffer))

  def bind(self):
    glBindBuffer(GL_ARRAY_BUFFER_ARB, self.buffer)

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
