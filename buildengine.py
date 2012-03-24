from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("simple3DGamePYX", ["simple3DGamePYX.pyx"], libraries = [])]

setup(
  name = 'DigDig Chunk Handler',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)

