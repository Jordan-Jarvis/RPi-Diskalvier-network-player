from os import getcwd
from ctypes import *
so_file=getcwd() + "/metamidi.so"
my_functions = CDLL(so_file)

print(my_functions.main(argc=2, argv=["",'--help']))