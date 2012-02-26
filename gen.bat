del genquads.o
del libgenquads.a
gcc -O2 -march=pentium4 -msse3 -c genquads.c -o genquads.o
ar rcs libgenquads.a genquads.o
del C:\MinGW\lib\libgenquads.a
copy libgenquads.a C:\MinGW\lib\
