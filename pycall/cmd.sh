#!bin/sh
rm ./build/lib.linux-x86_64-2.7/FFmpeg.so
rm FFmpeg.so
python setup.py build
cp ./build/lib.linux-x86_64-2.7/FFmpeg.so .
LD_LIBRARY_PATH=./lib/ python pycall.py 
