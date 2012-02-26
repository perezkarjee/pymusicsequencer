from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("chunkhandler", ["chunkhandler.pyx"], libraries = ['opengl32', 'genquads'])]

setup(
  name = 'DigDig Chunk Handler',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)

