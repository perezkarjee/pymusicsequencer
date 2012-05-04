
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

class Bone:
  def __init__(self, skeleton, parent, name, mat, theboneobj):
    self.parent = parent #Bone
    self.name   = name   #string
    self.children = []   #list of Bone objects
    self.theboneobj = theboneobj #Blender.Armature.Bone
    # HACK: this flags if the bone is animated in the one animation that we export
    self.is_animated = 0  # = 1, if there is an ipo that animates this bone

    self.matrix = mat
    if parent:
      parent.children.append(self)
    
    self.skeleton = skeleton
    self.id = skeleton.next_bone_id
    skeleton.next_bone_id += 1
    skeleton.bones.append(self)
    
    BONES[name] = self


  def to_md5mesh(self):
    buf= "\t\"%s\"\t" % (self.name)
    parentindex = -1
    if self.parent:
        parentindex=self.parent.id
    buf=buf+"%i " % (parentindex)
    
    pos1, pos2, pos3= self.matrix[3][0], self.matrix[3][1], self.matrix[3][2]
    buf=buf+"( %f %f %f ) " % (pos1*scale, pos2*scale, pos3*scale)
    #qx, qy, qz, qw = matrix2quaternion(self.matrix)
    #if qw<0:
    #    qx = -qx
    #    qy = -qy
    #    qz = -qz
    m = self.matrix
#    bquat = self.matrix.to_quat()  #changed from matrix.toQuat() in blender 2.4x script
    bquat = self.matrix.to_quaternion()  #changed from to_quat in 2.57 -mikshaw
    bquat.normalize()
    qx = bquat.x
    qy = bquat.y
    qz = bquat.z
    if bquat.w > 0:
        qx = -qx
        qy = -qy
        qz = -qz
    buf=buf+"( %f %f %f )\t\t// " % (qx, qy, qz)
    if self.parent:
        buf=buf+"%s" % (self.parent.name)    
    
    buf=buf+"\n"
    return buf


class Skeleton:
  def __init__(self, MD5Version = 10, commandline = ""):
    self.bones = []
    self.MD5Version = MD5Version
    self.commandline = commandline
    self.next_bone_id = 0
    

  def to_md5mesh(self, numsubmeshes):
    buf = "MD5Version %i\n" % (self.MD5Version)
    buf = buf + "commandline \"%s\"\n\n" % (self.commandline)
    buf = buf + "numJoints %i\n" % (self.next_bone_id)
    buf = buf + "numMeshes %i\n\n" % (numsubmeshes)
    buf = buf + "joints {\n"
    for bone in self.bones:
      buf = buf + bone.to_md5mesh()
    buf = buf + "}\n\n"
    return buf

BONES = {}

def save_jrpg(settings):
  starttime = time.clock()#start timer
  bpy.ops.object.mode_set(mode='OBJECT')
  jrpgHeader = JRPGHeader()

  bpy.context.scene.frame_set(bpy.context.scene.frame_start)
  thearmature = None
  w_matrix = None
  skeleton = Skeleton(10, "Exported from Blender by io_export_md5.py by Paul Zirkle")
  for obj in bpy.context.selected_objects:
    if obj.type == 'ARMATURE':
      #skeleton.name = obj.name
      thearmature = obj
      w_matrix = obj.matrix_world
      
      #define recursive bone parsing function
      def treat_bone(b, parent = None):
        if (parent and not b.parent.name==parent.name):
          return #only catch direct children
        
        mat =  mathutils.Matrix(w_matrix) * mathutils.Matrix(b.matrix_local)  #reversed order of multiplication from 2.4 to 2.5!!! ARRRGGG
        
        bone = Bone(skeleton, parent, b.name, mat, b)
        
        if( b.children ):
          for child in b.children: treat_bone(child, bone)
          
      for b in thearmature.data.bones:
        if( not b.parent ): #only treat root bones'
          print( "root bone: " + b.name )
          treat_bone(b)
    
      break #only pull one skeleton out
  ANIMATIONS = {}


  arm_action = thearmature.animation_data.action
  rangestart = 0
  rangeend = 0
  if arm_action:
    animation = ANIMATIONS[arm_action.name] = MD5Animation(skeleton)

    rangestart = int( bpy.context.scene.frame_start ) # int( arm_action.frame_range[0] )
    rangeend = int( bpy.context.scene.frame_end ) #int( arm_action.frame_range[1] )
    currenttime = rangestart
    while currenttime <= rangeend: 
      bpy.context.scene.frame_set(currenttime)
      time = (currenttime - 1.0) / 24.0 #(assuming default 24fps for md5 anim)
      pose = thearmature.pose

      for bonename in thearmature.data.bones.keys():
        posebonemat = mathutils.Matrix(pose.bones[bonename].matrix ) # @ivar poseMatrix: The total transformation of this PoseBone including constraints. -- different from localMatrix

        try:
          bone  = BONES[bonename] #look up md5bone
        except:
          print( "found a posebone animating a bone that is not part of the exported armature: " + bonename )
          continue
        if bone.parent: # need parentspace-matrix
          parentposemat = mathutils.Matrix(pose.bones[bone.parent.name].matrix ) # @ivar poseMatrix: The total transformation of this PoseBone including constraints. -- different from localMatrix
#          posebonemat = parentposemat.invert() * posebonemat #reverse order of multiplication!!!
          parentposemat.invert() # mikshaw
          posebonemat = parentposemat * posebonemat # mikshaw
        else:
          posebonemat = thearmature.matrix_world * posebonemat  #reverse order of multiplication!!!
        loc = [posebonemat[3][0],
            posebonemat[3][1],
            posebonemat[3][2],
            ]
#        rot = posebonemat.to_quat().normalize()
        rot = posebonemat.to_quaternion() # changed from to_quat in 2.57 -mikshaw
        rot.normalize() # mikshaw
        rot = [rot.w,rot.x,rot.y,rot.z]
        
        animation.addkeyforbone(bone.id, time, loc, rot)
      currenttime += 1

  if True:#( settings.exportMode == "mesh & anim" or settings.exportMode == "anim only" ):
    md5anim_filename = settings.savepath + ".md5anim"

    #save animation file
    if len(ANIMATIONS)>0:
      anim = ANIMATIONS.popitem()[1] #ANIMATIONS.values()[0]
      print( str( anim ) )
      try:
        file = open(md5anim_filename, 'w')
      except IOError:
        errmsg = "IOError " #%s: %s" % (errno, strerror)
      objects = []
      for submesh in meshes[0].submeshes:
        if len(submesh.weights) > 0:
          obj = None
          for sob in bpy.context.selected_objects:
              if sob and sob.type == 'MESH' and sob.name == submesh.name:
                obj = sob
          objects.append (obj)
      generateboundingbox(objects, anim, [rangestart, rangeend])
      buffer = anim.to_md5anim()
      file.write(buffer)
      file.close()
      print( "saved anim to " + md5anim_filename )
    else:
      print( "No md5anim file was generated." )
 

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
          weightlist
      bpy.data.meshes.remove(nobj)

      fobj = obj.to_mesh(bpy.context.scene,True,'PREVIEW')
      for vi in vertlist:
          vert = fobj.vertices[vi]
          mymesh.verts[vi] = vert.co * obj.matrix_world
          mymesh.verts[vi][0] = round(((mymesh.verts[vi][0] + obj.matrix_world[3][0]) * settings.scale) + settings.offsetx,5)
          mymesh.verts[vi][1] = round(((mymesh.verts[vi][1] + obj.matrix_world[3][1]) * settings.scale) + settings.offsety,5)
          mymesh.verts[vi][2] = round(((mymesh.verts[vi][2] + obj.matrix_world[3][2]) * settings.scale) + settings.offsetz,5)
          mymesh.normals[vi] = vert.normal
          mymesh.weights[vi] = vert.
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
