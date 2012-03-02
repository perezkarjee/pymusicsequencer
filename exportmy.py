
#Lines 30 through 379 belong to an jrpg.py made by PhaethonH, Bob Holcomb, Damien McGinnes, and/or Robert (Tr3B) Beckebans.
#This jrpg.py had to be merged with my exporter because Blender tries to load it as another exporter.

#Lines 9,10,11,12,18,304,523,524,525,542,544,545,557,558,661,662,692 #Drek
#Updates for Blender 2.60a

bl_info = {
    "name": "JRPG (+shaders)",#Drek
    "author": "Drek, Xembie, PhaethonH, Bob Holcomb, Damien McGinnes, Robert (Tr3B) Beckebans",#Drek
    "version": (1,5),#Drek
    "blender": (2, 6, 0),#Drek
    "api": 36991,
    "location": "File > Export > Jin'sRPG (.jrpg)",
    "description": "Export mesh Jin'sRPG (.jrpg)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",#Drek
    "category": "Import-Export"}

import bpy, struct, math, os, time

MAX_QPATH = 64

JRPG_IDENT = "IDP3"
JRPG_VERSION = 15
JRPG_MAX_TAGS = 16
JRPG_MAX_SURFACES = 32
JRPG_MAX_FRAMES = 1024
JRPG_MAX_SHADERS = 256
JRPG_MAX_VERTICES = 4096
JRPG_MAX_TRIANGLES = 8192
JRPG_XYZ_SCALE = 64.0

class JRPGHeader:
	# header structure

    def __init__(self):
        """
    * JRPG3D
        * version 4bytes
        * numverts 4bytes
        * lentypename 4bytes
        * typename
        * numanims
            
        """
        self.binaryFormat1="<6siiii%dsi"
        self.ident = b"JRPG3D"
        self.version = 1
        self.numverts = 0
        self.numIndices = 0
        self.typename = "default"
        self.numanims = 0
    def Save(self, file):
        fmt = self.binaryFormat1 % len(self.typename)
        header1 = struct.pack(fmt, self.ident, self.version, self.numverts, self.numIndices, len(self.typename), bytes(self.typename,'ascii'), self.numanims)
        print len(self.typename)
        file.write(header1)
class jrpgAnimatedMeshHeader:
    """
        * lenanimname
        * animname
        * lenanim
        * verts*lenanim, texcs*lenanim, normals*lenanim

    """
    def __init__(self):
        self.packFmt = "<i%dsi"
        self.animname = ""
        self.lenanim= 0
        """
        self.verts = None
        self.texcs = None
        self.normals = None
        """
    def Save(self, file):
        fmt = self.packFmt % len(self.animname)
        header = struct.pack(fmt, len(self.animname), bytes(self.animname,'ascii'), self.lenanim)
        file.write(header)


class jrpgMesh:
    def __init__(self):
        self.verts = {}
        self.uvs = {}
        self.normals = {}
        self.indices = []

    def GetNumVerts(self):
        return len(self.verts.keys())

    def Save(self, file):
        for vertidx in range(len(self.verts.keys())):
            data = struct.pack("<3f", self.verts[vertidx][0], self.verts[vertidx][1], self.verts[vertidx][2])
            file.write(data)
        for vertidx in range(len(self.uvs.keys())):
            data = struct.pack("<2f", self.uvs[vertidx][0], self.uvs[vertidx][1])
            file.write(data)
        for vertidx in range(len(self.normals.keys())):
            data = struct.pack("<3f", self.normals[vertidx][0], self.normals[vertidx][1], self.normals[vertidx][2])
            file.write(data)
        for vertidx in range(len(self.indices)):
            data = struct.pack("<i", self.indices[vertidx])
            file.write(data)

def message(log,msg):
  if log:
    log.write(msg + "\n")
  else:
    print(msg)

class jrpgSettings:
  def __init__(self,
               savepath,
               name,
               scale=1.0,
               offsetx=0.0,
               offsety=0.0,
               offsetz=0.0):
    self.savepath = savepath
    self.name = name
    #self.logtype = logtype
    #self.dumpall = dumpall
    #self.ignoreuvs = ignoreuvs
    self.scale = scale
    self.offsetx = offsetx
    self.offsety = offsety
    self.offsetz = offsetz


def save_jrpg(settings):
  starttime = time.clock()#start timer
  bpy.ops.object.mode_set(mode='OBJECT')
  jrpgHeader = JRPGHeader()

  for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
      mymesh = jrpgMesh()
      bpy.context.scene.frame_set(bpy.context.scene.frame_start)
      nobj = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
      UVImage = nobj.uv_textures[0] #Drek; Thanks to adam450 @ blender artists
      texCoords = UVImage.data #Drek
      #nsurface = jrpgSurface() #Drek
      #nsurface.name = obj.name
      #nsurface.ident = JRPG_IDENT
      
      #ignoreuvs = False
      #nshader = jrpgShader()
      #Add only 1 shader per surface/object
      #try:
        #Using custom properties allows a longer string
      #  nshader.name = obj["jrpgshader"]
      #except:#we should add a blank as a placeholder
      #  ignoreuvs = True
      #  nshader.name = "NULL"
      """
      nsurface.shaders.append(nshader)
      nsurface.numShaders = 1
      """
 
      myInt = 0 #Drek
      vertlist = []
      for f,face in enumerate(nobj.faces):
        faceTexCoords = texCoords[myInt] #Drek
        myInt = myInt + 1 #Drek

        if len(face.vertices) != 3:
          continue

        for v,vert_index in enumerate(face.vertices):
          uv_u = round(faceTexCoords.uv[v][0],5)#Drek
          uv_v = round(faceTexCoords.uv[v][1],5)#Drek
          mymesh.uvs[vert_index] = (uv_u,uv_v)
          vertlist += [vert_index]
      bpy.data.meshes.remove(nobj)

      fobj = obj.to_mesh(bpy.context.scene,True,'PREVIEW')
      for vi in vertlist:
          vert = fobj.vertices[vi]
          mymesh.verts[vi] = vert.co * obj.matrix_world
          mymesh.verts[vi][0] = round(((mymesh.verts[vi][0] + obj.matrix_world[3][0]) * settings.scale) + settings.offsetx,5)
          mymesh.verts[vi][1] = round(((mymesh.verts[vi][1] + obj.matrix_world[3][1]) * settings.scale) + settings.offsety,5)
          mymesh.verts[vi][2] = round(((mymesh.verts[vi][2] + obj.matrix_world[3][2]) * settings.scale) + settings.offsetz,5)
          mymesh.normals[vi] = vert.normal
      bpy.data.meshes.remove(fobj)
      """
                self.binaryFormat1="<6siii%dsi"
		self.ident = "JRPG3D"
		self.version = 1
                self.numverts = 0
		self.typename = ""
                self.numanims = 0
     """
      mymesh.indices = vertlist
      jrpgHeader.numverts = mymesh.GetNumVerts()
      jrpgHeader.numIndices = len(vertlist)
      jrpgHeader.typename = str(settings.name)
      jrpgHeader.numanims = 1
      file = open(settings.savepath, "wb")
      jrpgHeader.Save(file)
      header = jrpgAnimatedMeshHeader()
      header.animname = "Test"
      header.lenanim = 1
      header.Save(file)
      mymesh.Save(file)
      file.close()


from bpy.props import *

class ExportJRPG(bpy.types.Operator):
  '''Export to Jin'sRPG (.jrpg)'''
  bl_idname = "export.jrpg"
  bl_label = 'Export JRPG'
  
  logenum = [("console","Console","log to console"),
             ("append","Append","append to log file"),
             ("overwrite","Overwrite","overwrite log file")]

  filepath = StringProperty(subtype = 'FILE_PATH',name="File Path", description="Filepath for exporting", maxlen= 1024, default= "")
  jrpgname = StringProperty(name="JRPG Type", description="JRPG header name / skin path (64 bytes)",maxlen=64,default="")
  #jrpglogtype = EnumProperty(name="Save log", items=logenum, description="File logging options",default = 'overwrite')#Drek; Changed default from 'console'
  #jrpgdumpall = BoolProperty(name="Dump all", description="Dump all data for jrpg to log",default=True)#Drek; Changed default from False
  #jrpgignoreuvs = BoolProperty(name="Ignore UVs", description="Ignores uv influence on mesh generation. Use if uv map not made.",default=False)
  jrpgscale = FloatProperty(name="Scale", description="Scale all objects from world origin (0,0,0)",default=1.0,precision=5)
  jrpgoffsetx = FloatProperty(name="Offset X", description="Transition scene along x axis",default=0.0,precision=5)
  jrpgoffsety = FloatProperty(name="Offset Y", description="Transition scene along y axis",default=0.0,precision=5)
  jrpgoffsetz = FloatProperty(name="Offset Z", description="Transition scene along z axis",default=0.0,precision=5)

  def execute(self, context):
   settings = jrpgSettings(savepath = self.properties.filepath,
                          name = self.properties.jrpgname,
                          #logtype = self.properties.jrpglogtype,
                          #dumpall = self.properties.jrpgdumpall,
                          #ignoreuvs = self.properties.jrpgignoreuvs,
                          scale = self.properties.jrpgscale,
                          offsetx = self.properties.jrpgoffsetx,
                          offsety = self.properties.jrpgoffsety,
                          offsetz = self.properties.jrpgoffsetz)
   save_jrpg(settings)
   return {'FINISHED'}

  def invoke(self, context, event):
    wm = context.window_manager
    wm.fileselect_add(self)
    return {'RUNNING_MODAL'}

  @classmethod
  def poll(cls, context):
    return context.active_object != None

def menu_func(self, context):
  self.layout.operator(ExportJRPG.bl_idname, text="JRPG (+shaders)", icon='BLENDER')#Drek
  
def register():
  bpy.utils.register_class(ExportJRPG)
  bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
  bpy.utils.unregister_class(ExportJRPG)
  bpy.types.INFO_MT_file_export.remove(menu_func)
if __name__ == '__main__':
    register()
