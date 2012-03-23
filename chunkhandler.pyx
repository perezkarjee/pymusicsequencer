import OpenGL.GL as GL
import cPickle
from OpenGL.arrays import ArrayDatatype as ADT

class VBOs(object):
    def __init__(self):
        self.vbos = []
class ElementBuffer(object):
    def __init__(self, data):
        self.reload = False
        self.buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffer)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, ADT.arrayByteCount(data), ADT.voidDataPointer(data), GL.GL_STATIC_DRAW)
    def __del__(self):
        if not self.reload:
            GL.glDeleteBuffers(1, GL.GLuint(self.buffer))

    def bind(self):
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffer)
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
    cdef int ReadInt(char *str)
    cdef char HitBoundingBox(float minB[3],float maxB[3], float origin[3], float dir[3],float coord[3])




NUMCHUNKS = 1
SIZE_CHUNK = 128
import random

SW = 1024
SH = 768
def CubeInFrustum(x, y, z, size, frustum):
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

cdef class GUIBGRenderer(object):
    vbos = VBOs()
    cdef float *quad
    cdef float *texcs
    def __cinit__(self):
        texupx = 0
        texupy = 0
        x = 0
        y = SH-128
        w = SW
        h = 128


        self.quad = <float*>malloc(sizeof(float)*4*3)
        self.texcs = <float*>malloc(sizeof(float)*4*2)
        # x,y,z,  x,y,z  x,y,z,  x,y,z * 5
        self.quad[0] = float(x)
        self.quad[1] = -float(y+h)
        self.quad[2] = 25.0
        self.quad[3] = float(x+w)
        self.quad[4] = -float(y+h)
        self.quad[5] = 25.0
        self.quad[6] = float(x+w)
        self.quad[7] =  -float(y)
        self.quad[8] =  25.0
        self.quad[9] = float(x)
        self.quad[10] =  -float(y)
        self.quad[11] = 25.0
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
        self.tex2 = []

class Element:
    def __init__(self):
        self.ele = None
        self.ele2 = None
        self.ele3 = None

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


REGENX = 9
REGENZ = 9
OFFSETX = 18
OFFSETZ = 18
"""
울온처럼 평평한 땅에만 지을 수 있다.
평평한 땅을 만들면 거기에 타일의 높낮이 조절 불가능하게 해야함
걍 map인스턴스를 여러개를 만들어서 렌더링을 한다. 아 안되넹 vbos가 공유가 되버려서';;;;;
걍 Map클래스 내부에서 잘 처리되도록 한다.
"""
class Files:
    def __init__(self):
        self.files = {}
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
    cdef float *quads
    cdef float *wallquads
    cdef float *walltexs
    cdef float *topquads
    cdef float *texcs
    cdef int **eles
    cdef int **eles2
    cdef int **eles3
    cdef int **eleFloor2
    cdef int **eleFloor3
    cdef int **eleFloor4
    cdef int **eleWall2
    cdef int **eleWall3
    cdef int **weles
    cdef int tileData
    cdef int prevX
    buffers = Buffers()
    cdef int prevZ
    cdef int idx
    cdef int prevGenX
    cdef int prevGenZ
    files = Files()
    walls = Files()
    walls2 = Files()
    walls3 = Files()
    floor2 = Files()
    floor3 = Files()
    floor4 = Files()
    def GetXZ(self):
        x,z = self.buffers.buffers[self.idx].coord
        return x*8.0,z*8.0
    def __cinit__(self, idx):
        self.prevGenX = 0
        self.prevGenZ = 0
        self.idx = idx
        self.buffers.buffers[idx] = Buffer()
        self.files.files[idx] = {}

        self.quads = <float*>0
        self.topquads = <float*>0
        self.texcs = <float*>0
        self.eles = <int**>0
        self.eles2 = <int**>0
        self.eles3 = <int**>0
        self.wallquads = <float*>0
        self.walltexs = <float*>0

        self.files.files[self.idx] = {}
        self.walls.files[self.idx] = {}
        # 벽은 8x8맵의 범위안에 있다.
        # 음 파일의 수가 엄청 많아지면 좀 곤란한데?
        # 맵이 작으니까 괜찮다. 맵 커봤자 타일구존데 뭐....

        self.quads = <float*>malloc(sizeof(float)*3*SIZE_CHUNK*SIZE_CHUNK*4*4) # xyz, width, height, verts*4=quad, quads
        self.topquads = <float*>malloc(sizeof(float)*3*SIZE_CHUNK*SIZE_CHUNK*4) # xyz, width, height, verts*4=quad, quads
        self.texcs = <float*>malloc(sizeof(float)*2*SIZE_CHUNK*SIZE_CHUNK*4) # xyz, width, height, verts*4=quad, quads




    def DelWall(self,x,y,z, tile, facing, floor=1):
        x=int(x)
        z=-int(z)
        if (x,z) in self.walls.files[self.idx][self.GetWallFileName(int(x),int(z))].iterkeys():
            try:
                self.walls.files[self.idx][self.GetWallFileName(int(x),int(z))][(x,z)].remove([facing,tile])
                self.Regen(self.buffers.buffers[self.idx].tex.tex, self.buffers.buffers[self.idx].tex.tex2, False, True)
            except:
                pass
    def GetWall(self, x,z, floor=1):
        result = []
        if (x,z) in self.walls.files[self.idx][self.GetWallFileName(int(x),int(z))]:
            walls = self.walls.files[self.idx][self.GetWallFileName(int(x),int(z))]
            for wall in walls[(x,z)]:
                facing,tile = wall
                result += [(x,z,facing,tile)]
            return result
        else:
            return []
    def AddWall(self, x, y, z, tile, facing, floor=1):
        x = int(x)
        z = -int(z)
        LEFTTOP = 0
        RIGHTTOP = 1
        LEFTBOT = 2
        RIGHTBOT = 3

        xxx,zzz = self.GetLocalCoord(int(x),int(z))
        if (x,z) not in self.walls.files[self.idx][self.GetWallFileName(int(x),int(z))]:
            self.walls.files[self.idx][self.GetWallFileName(int(x),int(z))][(x,z)] = []
        if [facing,tile] not in self.walls.files[self.idx][self.GetWallFileName(int(x),int(z))][(x,z)]:
            self.walls.files[self.idx][self.GetWallFileName(int(x),int(z))][(x,z)] += [[facing,tile]]
            self.Regen(self.buffers.buffers[self.idx].tex.tex, self.buffers.buffers[self.idx].tex.tex2, False, True)
    def SetTile(self, tile):
        self.tileData = tile
    def GetHeight(self, x,z):
        xxx,zzz = self.GetLocalCoord(int(x),int(z))
        height = self.files.files[self.idx][self.GetFileName(int(x),int(z))][zzz*8+xxx][0]
        return height
    def ClickTile(self, mode, part, position, floor=1):
        x,y,z = position
        x = int(x)
        z = -int(z)
        xxx,zzz = self.GetLocalCoord(int(x),int(z))
        if self.prevX == x and self.prevZ == z and self.files.files[self.idx][self.GetFileName(int(x),int(z))][zzz*8+xxx][1] == self.tileData:
            return
        self.prevX = x
        self.prevZ = z
        LEFTTOP = 0
        RIGHTTOP = 1
        LEFTBOT = 2
        RIGHTBOT = 3
        #self.chunks[0].tiles[z*SIZE_CHUNK+x].height += 1

        self.files.files[self.idx][self.GetFileName(int(x),int(z))][zzz*8+xxx][1] = self.tileData
        #self.chunks[0].tiles[z*SIZE_CHUNK+x].tileData = self.tileData
        self.Regen(self.buffers.buffers[self.idx].tex.tex, self.buffers.buffers[self.idx].tex.tex2, False, True)

    def PosUpdate(self, x,y,z):
        if (abs(self.prevGenX-x) >= REGENX) or (abs(self.prevGenZ-z) >= REGENZ):
            self.prevGenX = x
            self.prevGenZ = z
            self.Regen(self.buffers.buffers[self.idx].tex.tex, self.buffers.buffers[self.idx].tex.tex2, False)

    cdef GetLocalCoord(self, int x,int z):
        x = x%8
        z = z%8
        return x,z

    cdef GetFloor2Name(self, int x,int z):
        x = x-(x%8)
        z = z-(z%8)
        fileN = "./maps/%d_%d.floor2" % (x,z)
        return fileN
    cdef GetFloor3Name(self, int x,int z):
        x = x-(x%8)
        z = z-(z%8)
        fileN = "./maps/%d_%d.floor3" % (x,z)
        return fileN
    cdef GetFloor4Name(self, int x,int z):
        x = x-(x%8)
        z = z-(z%8)
        fileN = "./maps/%d_%d.floor4" % (x,z)
        return fileN
    cdef GetFileName(self, int x,int z):
        x = x-(x%8)
        z = z-(z%8)
        fileN = "./maps/%d_%d.map" % (x,z)
        return fileN
    cdef GetWallFileName(self, int x, int z):
        x = x-(x%8)
        z = z-(z%8)
        fileN = "./maps/%d_%d.wall" % (x,z)
        return fileN
    cdef GetWall2FileName(self, int x, int z):
        x = x-(x%8)
        z = z-(z%8)
        fileN = "./maps/%d_%d.wall2" % (x,z)
        return fileN
    cdef GetWall3FileName(self, int x, int z):
        x = x-(x%8)
        z = z-(z%8)
        fileN = "./maps/%d_%d.wall3" % (x,z)
        return fileN
    def Save(self, fileN, fileContents):
        cPickle.dump(fileContents, open(fileN, "wb"))
    def LoadWall(self, fileN):
        try:
            return cPickle.load(open(fileN, "rb"))
        except:
            return {}
    def Load(self, fileN):
        try:
            return cPickle.load(open(fileN, "rb"))
        except:
            return [[0,0] for i in range(8*8)]
    def Regen(self, textures, textures2, regen=True, changeTile=False):
        if not changeTile:
            xLeft = self.prevGenX-OFFSETX
            xOrg = xLeft
            xRight = xLeft+OFFSETX*2+8
            zLeft = self.prevGenZ-OFFSETZ
            zRight = zLeft+OFFSETZ*2+8
            fileNames = []
            fileNames3 = []
            fileNamesFloor2 = []
            fileNamesFloor3 = []
            fileNamesFloor4 = []
            while zLeft <= zRight:
                while xLeft <= xRight:
                    fileNames += [self.GetFileName(xLeft,zLeft)]
                    if self.GetFileName(xLeft,zLeft) not in self.files.files[self.idx].iterkeys():
                        self.files.files[self.idx][self.GetFileName(xLeft,zLeft)] = self.Load(self.GetFileName(xLeft, zLeft))
                    fileNames3 += [self.GetWallFileName(xLeft,zLeft)]
                    if self.GetWallFileName(xLeft,zLeft) not in self.walls.files[self.idx].iterkeys():
                        self.walls.files[self.idx][self.GetWallFileName(xLeft,zLeft)] = self.LoadWall(self.GetWallFileName(xLeft, zLeft))

                    """
                    fileNamesFloor2 += [self.GetFloor2Name(xLeft,zLeft)]
                    if self.GetFloor2Name(xLeft,zLeft) not in self.floor2.files[self.idx].iterkeys():
                        self.floor2.files[self.idx][self.GetFloor2Name(xLeft,zLeft)] = self.LoadWall(self.GetFloor2Name(xLeft, zLeft))

                    fileNamesFloor3 += [self.GetFloor3Name(xLeft,zLeft)]
                    if self.GetFloor3Name(xLeft,zLeft) not in self.floor3.files[self.idx].iterkeys():
                        self.floor3.files[self.idx][self.GetFloor3Name(xLeft,zLeft)] = self.LoadWall(self.GetFloor3Name(xLeft, zLeft))

                    fileNamesFloor4 += [self.GetFloor4Name(xLeft,zLeft)]
                    if self.GetFloor4Name(xLeft,zLeft) not in self.floor4.files[self.idx].iterkeys():
                        self.floor4.files[self.idx][self.GetFloor4Name(xLeft,zLeft)] = self.LoadWall(self.GetFloor4Name(xLeft, zLeft))
                    """

                    xLeft += 8
                zLeft += 8
                xLeft = xOrg

            files = self.files.files[self.idx]
            fileNames2 = self.files.files[self.idx].keys()
            for fileN in fileNames2:
                if fileN not in fileNames:
                    self.Save(fileN, files[fileN])
                    del self.files.files[self.idx][fileN]

            files2 = self.walls.files[self.idx]
            fileNames4 = self.walls.files[self.idx].keys()
            for fileN in fileNames4:
                if fileN not in fileNames3:
                    self.Save(fileN, files2[fileN])
                    del self.walls.files[self.idx][fileN]

            """
            files2 = self.floor2.files[self.idx]
            fileNames4 = self.floor2.files[self.idx].keys()
            for fileN in fileNames4:
                if fileN not in fileNamesFloor2:
                    self.Save(fileN, files2[fileN])
                    del self.floor2.files[self.idx][fileN]

            files2 = self.floor3.files[self.idx]
            fileNames4 = self.floor3.files[self.idx].keys()
            for fileN in fileNames4:
                if fileN not in fileNamesFloor3:
                    self.Save(fileN, files2[fileN])
                    del self.floor3.files[self.idx][fileN]

            files2 = self.floor4.files[self.idx]
            fileNames4 = self.floor4.files[self.idx].keys()
            for fileN in fileNames4:
                if fileN not in fileNamesFloor4:
                    self.Save(fileN, files2[fileN])
                    del self.floor4.files[self.idx][fileN]
            """


        self.buffers.buffers[self.idx].tex.tex = textures
        self.buffers.buffers[self.idx].tex.tex2 = textures2

        cdef char *topquads
        cdef char *wallquads
        cdef char *walltexs
        cdef char *quads
        cdef char *texcs
        if self.wallquads:
            free(self.wallquads)
        if self.walltexs:
            free(self.walltexs)
        walls = self.walls.files[self.idx]
        numwalls = 0
        for fileN in walls.iterkeys():
            for coord in walls[fileN].iterkeys():
                for wall in walls[fileN][coord]:
                    numwalls += 1
        self.wallquads = <float*>malloc(sizeof(float)*3*numwalls*4) # xyz, width, height, verts*4=quad, quads
        self.walltexs = <float*>malloc(sizeof(float)*2*numwalls*4) # xyz, width, height, verts*4=quad, quads
        # x,y,z,  x,y,z  x,y,z,  x,y,z * 5
        wallIdx = 0
        self.buffers.buffers[self.idx].ele.ele3 = [[] for i in range(len(textures2))]
        for fileN in walls.iterkeys():
            for coord in walls[fileN].iterkeys():

                x,z = coord
                for wall in walls[fileN][coord]:
                    xxx,zzz = self.GetLocalCoord(int(x),int(z))
                    height = self.files.files[self.idx][self.GetFileName(int(x),int(z))][zzz*8+xxx][0]
                    height *=0.25
                    facing, tile = wall
                    for kkk in range(len(textures2)):
                        if tile == kkk:
                            ii = wallIdx*4
                            self.buffers.buffers[self.idx].ele.ele3[kkk] += [ii,ii+1,ii+2,ii+3]
                            # 여기에 엘레멘트버퍼를 추가

                    if facing == 0:
                        self.wallquads[wallIdx*4*3+0] = x
                        self.wallquads[wallIdx*4*3+1] = height+2.0
                        self.wallquads[wallIdx*4*3+2] = z

                        self.wallquads[wallIdx*4*3+3] = x+1.0
                        self.wallquads[wallIdx*4*3+4] = height+2.0
                        self.wallquads[wallIdx*4*3+5] = z

                        self.wallquads[wallIdx*4*3+6] = x+1.0
                        self.wallquads[wallIdx*4*3+7] = height
                        self.wallquads[wallIdx*4*3+8] = z

                        self.wallquads[wallIdx*4*3+9] = x
                        self.wallquads[wallIdx*4*3+10] = height
                        self.wallquads[wallIdx*4*3+11] = z

                    if facing == 1:
                        self.wallquads[wallIdx*4*3+0] = x
                        self.wallquads[wallIdx*4*3+1] = height+2.0
                        self.wallquads[wallIdx*4*3+2] = z

                        self.wallquads[wallIdx*4*3+3] = x
                        self.wallquads[wallIdx*4*3+4] = height+2.0
                        self.wallquads[wallIdx*4*3+5] = z+1.0

                        self.wallquads[wallIdx*4*3+6] = x
                        self.wallquads[wallIdx*4*3+7] = height
                        self.wallquads[wallIdx*4*3+8] = z+1.0

                        self.wallquads[wallIdx*4*3+9] = x
                        self.wallquads[wallIdx*4*3+10] = height
                        self.wallquads[wallIdx*4*3+11] = z

                    self.walltexs[wallIdx*4*2+0] = 0.0
                    self.walltexs[wallIdx*4*2+1] = 1.0

                    self.walltexs[wallIdx*4*2+2] = 1.0
                    self.walltexs[wallIdx*4*2+3] = 1.0

                    self.walltexs[wallIdx*4*2+4] = 1.0
                    self.walltexs[wallIdx*4*2+5] = 0.0

                    self.walltexs[wallIdx*4*2+6] = 0.0
                    self.walltexs[wallIdx*4*2+7] = 0.0



                    wallIdx += 1

        if self.eles3:
            for i in range(len(textures2)):
                free(self.eles3[i])
            free(self.eles3)

        self.eles3 = <int**>malloc(sizeof(int*)*len(textures2))
        for i in range(len(textures2)):
            self.eles3[i] = <int*>malloc(sizeof(int)*len(self.buffers.buffers[self.idx].ele.ele3[i])+1)

        for i in range(len(textures2)):
            for j in range(len(self.buffers.buffers[self.idx].ele.ele3[i])):
                self.eles3[i][j] = self.buffers.buffers[self.idx].ele.ele3[i][j]


        xx = self.prevGenX-OFFSETX
        yy = 0.0
        zz = self.prevGenZ+OFFSETZ
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
                xxx,zzz = self.GetLocalCoord(int(xx),int(zz))
                height = self.files.files[self.idx][self.GetFileName(int(xx),int(zz))][zzz*8+xxx][0]
                #height = self.chunks[0].tiles[y*SIZE_CHUNK+x].height
                tileData = self.files.files[self.idx][self.GetFileName(int(xx),int(zz))][zzz*8+xxx][1]
                for kkk in range(len(textures)):
                    #if self.chunks[0].tiles[y*SIZE_CHUNK+x].tileData == kkk:
                    if tileData == kkk:
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
            xx = self.prevGenX-OFFSETX

        if self.eles:
            for i in range(len(textures)):
                free(self.eles[i])
            free(self.eles)
        self.eles = <int**>malloc(sizeof(int*)*len(textures))
        for i in range(len(textures)):
            self.eles[i] = <int*>malloc(sizeof(int)*len(self.buffers.buffers[self.idx].ele.ele[i])+1)

        for i in range(len(textures)):
            for j in range(len(self.buffers.buffers[self.idx].ele.ele[i])):
                self.eles[i][j] = self.buffers.buffers[self.idx].ele.ele[i][j]

        self.buffers.buffers[self.idx].ele.ele2 = [[] for i in range(len(textures))]
        xx = self.prevGenX-OFFSETX
        yy = 0.0
        zz = self.prevGenZ+OFFSETZ
        ii = 0
        for y in range(SIZE_CHUNK):
            for x in range(SIZE_CHUNK):
                xxx,zzz = self.GetLocalCoord(int(xx),int(zz))
                height = self.files.files[self.idx][self.GetFileName(int(xx),int(zz))][zzz*8+xxx][0]
                #height = self.chunks[0].tiles[y*SIZE_CHUNK+x].height
                tileData = self.files.files[self.idx][self.GetFileName(int(xx),int(zz))][zzz*8+xxx][1]
                #height = self.chunks[0].tiles[y*SIZE_CHUNK+x].height

                for kkk in range(len(textures)):
                    #if self.chunks[0].tiles[y*SIZE_CHUNK+x].tileData == kkk:
                    if tileData == kkk:
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
                self.quads[y*SIZE_CHUNK*4*4*3+4+i+x*4*4*3] = -25.0
                self.quads[y*SIZE_CHUNK*4*4*3+5+i+x*4*4*3] = zz

                self.quads[y*SIZE_CHUNK*4*4*3+6+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+7+i+x*4*4*3] = -25.0
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
                self.quads[y*SIZE_CHUNK*4*4*3+7+i+x*4*4*3] = -25.0
                self.quads[y*SIZE_CHUNK*4*4*3+8+i+x*4*4*3] = zz-1.0

                self.quads[y*SIZE_CHUNK*4*4*3+9+i+x*4*4*3] = xx
                self.quads[y*SIZE_CHUNK*4*4*3+10+i+x*4*4*3] = -25.0
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
                self.quads[y*SIZE_CHUNK*4*4*3+7+i+x*4*4*3] = -25.0
                self.quads[y*SIZE_CHUNK*4*4*3+8+i+x*4*4*3] = zz-1.0

                self.quads[y*SIZE_CHUNK*4*4*3+9+i+x*4*4*3] = xx
                self.quads[y*SIZE_CHUNK*4*4*3+10+i+x*4*4*3] = -25.0
                self.quads[y*SIZE_CHUNK*4*4*3+11+i+x*4*4*3] = zz
                i += 12

                # right
                self.quads[y*SIZE_CHUNK*4*4*3+i+x*4*4*3] = xx+1.0 # top right
                self.quads[y*SIZE_CHUNK*4*4*3+1+i+x*4*4*3] = float(height)*0.25
                self.quads[y*SIZE_CHUNK*4*4*3+2+i+x*4*4*3] = zz

                self.quads[y*SIZE_CHUNK*4*4*3+3+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+4+i+x*4*4*3] = -25.0
                self.quads[y*SIZE_CHUNK*4*4*3+5+i+x*4*4*3] = zz

                self.quads[y*SIZE_CHUNK*4*4*3+6+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+7+i+x*4*4*3] = -25.0
                self.quads[y*SIZE_CHUNK*4*4*3+8+i+x*4*4*3] = zz-1.0

                self.quads[y*SIZE_CHUNK*4*4*3+9+i+x*4*4*3] = xx+1.0
                self.quads[y*SIZE_CHUNK*4*4*3+10+i+x*4*4*3] = float(height)*0.25
                self.quads[y*SIZE_CHUNK*4*4*3+11+i+x*4*4*3] = zz-1.0
                i += 12

                xx += 1.0
            zz -= 1.0
            xx = self.prevGenX-OFFSETX



        if self.eles2:
            for i in range(len(textures)):
                free(self.eles2[i])
            free(self.eles2)

        self.eles2 = <int**>malloc(sizeof(int*)*len(textures))
        for i in range(len(textures)):
            self.eles2[i] = <int*>malloc(sizeof(int)*len(self.buffers.buffers[self.idx].ele.ele2[i])+1)

        for i in range(len(textures)):
            for j in range(len(self.buffers.buffers[self.idx].ele.ele2[i])):
                self.eles2[i][j] = self.buffers.buffers[self.idx].ele.ele2[i][j]

        if self.buffers.buffers[self.idx].vbos.vbos:
            self.buffers.buffers[self.idx].vbos.vbos[0].reload = regen
            self.buffers.buffers[self.idx].vbos.vbos[1].reload = regen
            self.buffers.buffers[self.idx].vbos.vbos[2].reload = regen
            for vbo in self.buffers.buffers[self.idx].vbos.vbos[3]:
                vbo.reload = regen
            for vbo in self.buffers.buffers[self.idx].vbos.vbos[4]:
                vbo.reload = regen
            self.buffers.buffers[self.idx].vbos.vbos[5].reload = regen
            for vbo in self.buffers.buffers[self.idx].vbos.vbos[6]:
                vbo.reload = regen
            self.buffers.buffers[self.idx].vbos.vbos[7].reload = regen
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
        quads = <char*>self.quads
        topquads = <char*>self.topquads
        texcs = <char*>self.texcs
        wallquads = <char*>self.wallquads
        walltexs = <char*>self.walltexs
        self.buffers.buffers[self.idx].vbos.vbos += [0,0,0,0,0,0,0,0]
        self.buffers.buffers[self.idx].vbos.vbos[0] = VertexBuffer(topquads[:SIZE_CHUNK*SIZE_CHUNK*4*3*sizeof(float)])
        self.buffers.buffers[self.idx].vbos.vbos[0].bind_vertexes(3, GL.GL_FLOAT)
        self.buffers.buffers[self.idx].vbos.vbos[1] = VertexBuffer(quads[:SIZE_CHUNK*SIZE_CHUNK*4*4*3*sizeof(float)])
        self.buffers.buffers[self.idx].vbos.vbos[1].bind_vertexes(3, GL.GL_FLOAT)
        self.buffers.buffers[self.idx].vbos.vbos[2] = VertexBuffer(texcs[:SIZE_CHUNK*SIZE_CHUNK*4*2*sizeof(float)])
        self.buffers.buffers[self.idx].vbos.vbos[2].bind_texcoords(2, GL.GL_FLOAT)
        self.buffers.buffers[self.idx].vbos.vbos[3] = []
        self.buffers.buffers[self.idx].vbos.vbos[4] = []
        self.buffers.buffers[self.idx].vbos.vbos[5] = VertexBuffer(wallquads[:4*3*numwalls*sizeof(float)])
        self.buffers.buffers[self.idx].vbos.vbos[5].bind_vertexes(3, GL.GL_FLOAT)
        self.buffers.buffers[self.idx].vbos.vbos[6] = []
        self.buffers.buffers[self.idx].vbos.vbos[7] = VertexBuffer(walltexs[:4*2*numwalls*sizeof(float)])
        self.buffers.buffers[self.idx].vbos.vbos[7].bind_texcoords(2, GL.GL_FLOAT)

        cdef char *ele1
        cdef char *ele2
        cdef char *ele3
        for i in range(len(textures)):
            ele1 = <char*>self.eles[i]
            self.buffers.buffers[self.idx].vbos.vbos[3] += [ElementBuffer(ele1[:len(self.buffers.buffers[self.idx].ele.ele[i])*sizeof(int)])]
        for i in range(len(textures)):
            ele2 = <char*>self.eles2[i]
            self.buffers.buffers[self.idx].vbos.vbos[4] += [ElementBuffer(ele2[:len(self.buffers.buffers[self.idx].ele.ele2[i])*sizeof(int)])]
        for i in range(len(textures2)):
            ele3 = <char*>self.eles3[i]
            self.buffers.buffers[self.idx].vbos.vbos[6] += [ElementBuffer(ele3[:len(self.buffers.buffers[self.idx].ele.ele3[i])*sizeof(int)])]


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
                self.buffers.buffers[self.idx].vbos.vbos[3][i].bind()
                #GL.glNormalPointer(GL.GL_FLOAT, 0, None) 
                #glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.tT[i]) 
                #glColorPointer(3, GL.GL_UNSIGNED_BYTE, 0, <void*>self.tC[i]) 

                glDrawElements(GL.GL_QUADS, len(self.buffers.buffers[self.idx].ele.ele[i]), GL.GL_UNSIGNED_INT, <void*>0)
                #glDrawArrays(GL.GL_QUADS, 0, SIZE_CHUNK*SIZE_CHUNK*4)

        GL.glDisable(GL.GL_CULL_FACE)
        self.buffers.buffers[self.idx].vbos.vbos[5].bind()
        GL.glVertexPointer( 3, GL.GL_FLOAT, 0, None)#<void*>self.verts) 
        self.buffers.buffers[self.idx].vbos.vbos[7].bind()
        GL.glTexCoordPointer( 2, GL.GL_FLOAT, 0, None)#<void*>self.verts) 

        for i in range(len(self.buffers.buffers[self.idx].tex.tex2)):
            if len(self.buffers.buffers[self.idx].ele.ele3[i]):
                GL.glBindTexture(GL.GL_TEXTURE_2D, self.buffers.buffers[self.idx].tex.tex2[i])
                self.buffers.buffers[self.idx].vbos.vbos[6][i].bind()
                #GL.glNormalPointer(GL.GL_FLOAT, 0, None) 
                #glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.tT[i]) 
                #glColorPointer(3, GL.GL_UNSIGNED_BYTE, 0, <void*>self.tC[i]) 

                glDrawElements(GL.GL_QUADS, len(self.buffers.buffers[self.idx].ele.ele3[i]), GL.GL_UNSIGNED_INT, <void*>0)
                #glDrawArrays(GL.GL_QUADS, 0, SIZE_CHUNK*SIZE_CHUNK*4)

        GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        GL.glEnable(GL.GL_CULL_FACE)


        GL.glDisable(GL.GL_TEXTURE_2D)
        self.buffers.buffers[self.idx].vbos.vbos[1].bind()
        GL.glVertexPointer( 3, GL.GL_FLOAT, 0, None)#<void*>self.verts) 
        #glDrawArrays(GL.GL_QUADS, 0, SIZE_CHUNK*SIZE_CHUNK*4*4)
        for i in range(len(self.buffers.buffers[self.idx].tex.tex)):
            if len(self.buffers.buffers[self.idx].ele.ele2[i]):
                self.buffers.buffers[self.idx].vbos.vbos[4][i].bind()
                GL.glColor4ub(*self.buffers.buffers[self.idx].tex.tex[i][1])
                glDrawElements(GL.GL_QUADS, len(self.buffers.buffers[self.idx].ele.ele2[i]), GL.GL_UNSIGNED_INT, <void*>0)
        #glDrawElements(GL.GL_TRIANGLES, self.indNum, GL.GL_UNSIGNED_INT, <void*>self.inds)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        #GL.glDisableClientState(GL.GL_NORMAL_ARRAY)
        #GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        #GL.glDisableClientState(GL.GL_COLOR_ARRAY)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_TEXTURE_1D)
    def SaveFiles(self):
        files = self.files.files[self.idx]
        for fileN in files.iterkeys():
            self.Save(fileN, files[fileN])
        files = self.walls.files[self.idx]
        for fileN in files.iterkeys():
            self.Save(fileN, files[fileN])

    def __dealloc__(self):
        self.SaveFiles()

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
        if self.eles3:
            for i in range(len(self.buffers.buffers[self.idx].tex.tex)):
                free(self.eles3[i])
            free(self.eles3)


cdef class Model:
    """
    이거 element array 쓰게 고치고 idx넣어야 한다.
    """
    cdef char *verts
    cdef char *texcs
    cdef char *normals
    cdef char *inds
    cdef int num
    cdef int indNum
    cdef int lX,lY,lZ,hX,hY,hZ
    cdef int idx
    buffers = Buffers()
    
    
    def __cinit__(self, fileName, idx):
        self.idx = idx
        self.buffers.buffers[idx] = Buffer()
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
        if self.buffers.buffers[self.idx].vbos.vbos:
            self.buffers.buffers[self.idx].vbos.vbos[0].reload = True
            self.buffers.buffers[self.idx].vbos.vbos[1].reload = True
            self.buffers.buffers[self.idx].vbos.vbos[2].reload = True
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
            del self.buffers.buffers[self.idx].vbos.vbos[0]
        self.buffers.buffers[self.idx].vbos.vbos += [0,0,0]
        self.buffers.buffers[self.idx].vbos.vbos[0] = VertexBuffer(self.verts[:self.num*4*3])
        self.buffers.buffers[self.idx].vbos.vbos[1] = VertexBuffer(self.normals[:self.num*4*3])
        self.buffers.buffers[self.idx].vbos.vbos[2] = ElementBuffer(self.inds[:self.indNum*4])
    def Draw(self):
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_NORMAL_ARRAY)
        #GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        self.buffers.buffers[self.idx].vbos.vbos[0].bind()
        GL.glVertexPointer( 3, GL.GL_FLOAT, 0, None)#<void*>self.verts) 
        self.buffers.buffers[self.idx].vbos.vbos[1].bind()
        GL.glNormalPointer(GL.GL_FLOAT, 0, None) 
        #glTexCoordPointer( 2, GL.GL_FLOAT, 0, <void*>self.tT[i]) 
        #glColorPointer(3, GL.GL_UNSIGNED_BYTE, 0, <void*>self.tC[i]) 
        #glDrawArrays(GL.GL_TRIANGLES, 0, self.num)
        self.buffers.buffers[self.idx].vbos.vbos[2].bind()
        glDrawElements(GL.GL_TRIANGLES, self.indNum, GL.GL_UNSIGNED_INT, <void*>0)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_NORMAL_ARRAY)
        #GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        #GL.glDisableClientState(GL.GL_COLOR_ARRAY)
"""
기본적으로 컬링이 필요없을 것 같다. 걍 범위안의 타일을 모조리 렌더링하면 됨
음 근데 vbo를 1개만 쓰고 한번에 렌더링을 해야하니까 64x64만큼 로드하고 맵을 새로 로드해야하니 음...

"""
