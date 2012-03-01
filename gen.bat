del cpart.o
del libcpart.a
gcc -O2 -march=pentium4 -msse3 -c cpart.c -o cpart.o
ar rcs libcpart.a cpart.o
del C:\MinGW\lib\libcpart.a
copy libcpart.a C:\MinGW\lib\
