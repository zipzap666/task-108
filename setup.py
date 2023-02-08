import os
import sys
import subprocess
from setuptools import setup
from distutils.command.build_py import build_py as _build_py
from distutils.spawn import find_executable

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
    author='Zvega Alexandr',
    author_email='zipzap666@mail.ru',
    url='https://github.com/zipzap666/task-108',
    description='Разбор потока length-prefixed Protobuf сообщений на Python',
    zip_safe=False,
    include_package_data=True,
    cmdclass={
        'build_py': BuildPyCmd
    }
)
