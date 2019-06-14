#!/usr/bin/python
from operator import add, mul
import sys

##print 'Number of arguments:', len(sys.argv), 'arguments.'
##print 'Argument List:', str(sys.argv[2])
def sum_squares2(x,y):
	return add(mul(x,x),mul(y,y))
#sum_squares2(4,5)
#print(sum_squares2((int)(sys.argv[1]),(int)(sys.argv[2])))