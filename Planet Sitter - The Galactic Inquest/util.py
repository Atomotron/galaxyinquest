#!/usr/bin/env python
import numpy as np

def vfloor(x):
   '''Converts a numpy array to an int tuple, useful for sending
      coordinates to pygame drawing.'''
   return (int(x[0]),int(x[1]))
def vfloat(x):
   '''Builds a numpy floating point array from a tuple of something else.
      Useful for putting pygame numbers into numpy.'''
   return np.array(x,dtype=np.float64)
