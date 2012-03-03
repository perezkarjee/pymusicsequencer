del cpart.o
del libcpart.a
gcc -std=c99 -O3 -march=pentium4 -msse4.1 -c cpart.c -o cpart.o
ar rcs libcpart.a cpart.o
del C:\MinGW\lib\libcpart.a
copy libcpart.a C:\MinGW\lib\
