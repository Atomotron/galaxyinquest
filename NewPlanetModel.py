#!/usr/bin/env python
import numpy as np

class PlanetModel(object):
   SPEED = 0.002 # average change to parameters each milisecond
   PULL_TO_CENTER = 0.0002
   def __init__(self,string = "Hi",stringcolour = (255,255,255)):
      # Choose random starting values
      self.string = string
      self.stringColour = stringcolour
      self.sea = np.random.uniform(-1.0,1.0)
      self.temp = np.random.uniform(-1.0,1.0)
      self.pop = np.random.uniform(0.0,1.0)
      self.tech = np.random.uniform(0.0,1.0)
      self.dSea = 0
      self.dPop = 0
      self.dTech = 0
      self.dTemp = 0
      self.maxPop = 1
   def random_delta(self,dt,value,off_center):
      step = np.random.uniform(-1.0,1.0)*self.SPEED*dt
      restoration = - self.PULL_TO_CENTER*off_center*dt
      return value + step + restoration
   def tick(self,dt):
       self.dPop = (self.pop * (2.7 ** 0.0001)) - self.pop
       self.dTemp += (self.pop - 0.5) * 0.0000001
       self.dSea -= (self.temp - 0.5) * 0.0000001
       if (self.temp > 0.65 or self.temp < 0.35):
           self.dPop = -self.dPop
           optTemp = False
       else:
           optTemp = True
       if (self.sea > 0.65):
           self.maxPop = 1 - ((self.sea - 0.65) * 2)
           self.dTemp -= (self.sea - 0.5) * 0.0000001
           optSea = False
       elif (self.sea < 0.35):
           self.maxPop = 1 - ((0.35 - self.sea) * 2)
           self.dTemp += (self.sea - 0.5) * 0.0000001
           optSea = False
       else:
           optSea = True
       if (optSea and optTemp):
           self.dTech = 0.00001
       else:
           self.dTech = 0
       self.sea += self.dSea
       self.temp += self.dTemp
       self.tech += self.dTech
       self.pop += self.dPop
       if self.pop > self.maxPop:
           self.pop = self.maxPop