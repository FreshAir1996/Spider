#!/usr/bin/env python
from distutils.core import setup, Extension
MOD = 'FFmpeg'
source = 'ffmpeg.c'
setup(name=MOD, ext_modules=[Extension(MOD, sources=[source],library_dirs=['./lib'],libraries=['avcodec','avformat','avutil'])])
