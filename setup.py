import os
import sys
import subprocess

from setuptools import setup

from distutils.command.build_py import build_py as _build_py
from distutils.command.clean import clean as _clean
from distutils.spawn import find_executable

# Find the Protocol Compiler.
if 'PROTOC' in os.environ and os.path.exists(os.environ['PROTOC']):
  protoc = os.environ['PROTOC']
elif os.path.exists('../bazel-bin/protoc'):
  protoc = '../bazel-bin/protoc'
elif os.path.exists('../bazel-bin/protoc.exe'):
  protoc = '../bazel-bin/protoc.exe'
elif os.path.exists('protoc'):
  protoc = '../protoc'
elif os.path.exists('protoc.exe'):
  protoc = '../protoc.exe'
elif os.path.exists('../vsprojects/Debug/protoc.exe'):
  protoc = '../vsprojects/Debug/protoc.exe'
elif os.path.exists('../vsprojects/Release/protoc.exe'):
  protoc = '../vsprojects/Release/protoc.exe'
else:
  protoc = find_executable('protoc')

def GenProto(source, require=True):
  """Generates a _pb2.py from the given .proto file.
  Does nothing if the output already exists and is newer than the input.
  Args:
      source: the .proto file path.
      require: if True, exit immediately when a path is not found.
  """

  if not require and not os.path.exists(source):
    return

  output = source.replace('.proto', '_pb2.py').replace('../src/', '')

  if (not os.path.exists(output) or
      (os.path.exists(source) and
       os.path.getmtime(source) > os.path.getmtime(output))):
    print('Generating %s...' % output)

    if not os.path.exists(source):
      sys.stderr.write("Can't find required file: %s\n" % source)
      sys.exit(-1)

    if protoc is None:
      sys.stderr.write(
          'protoc is not installed nor found in ../src.  Please compile it '
          'or install the binary package.\n')
      sys.exit(-1)

    protoc_command = [protoc, '-I../src', '-I.', '--python_out=.', source]
    if subprocess.call(protoc_command) != 0:
      sys.exit(-1)

class CleanCmd(_clean):
  """Custom clean command for building the protobuf extension."""

  def run(self):
    # Delete generated files in the code tree.
    for (dirpath, unused_dirnames, filenames) in os.walk('.'):
      for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        if (filepath.endswith('_pb2.py') or filepath.endswith('.pyc') or
            filepath.endswith('.so') or filepath.endswith('.o')):
          os.remove(filepath)
    # _clean is an old-style class, so super() doesn't work.
    _clean.run(self)

src = ['src/proto/message.proto']

class BuildPyCmd(_build_py):
  """Custom build_py command for building the protobuf runtime."""

  def run(self):
    for f in src:
        GenProto(f)
    _build_py.run(self)

setup(
    name='protobuf_parser',
    version='1.0.0',
    description='Разбор потока length-prefixed Protobuf сообщений на Python',
    zip_safe=False,
    packages=['src.proto', 'src.parser', 'tests'],
    cmdclass={
          'clean': CleanCmd,
          'build_py': BuildPyCmd
    },
    test_suite="tests"
)