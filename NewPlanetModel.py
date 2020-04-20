#!/usr/bin/env python
import numpy as np

class PlanetModel(object):
   SPEED = 0.002 # average change to parameters each milisecond
   PULL_TO_CENTER = 0.0002
   def __init__(self,string = "Hi",stringcolour = (255,255,255)):
      # Choose random starting values
      self.string = string
      self.stringColour = stringcolour
      self.sea = np.random.uniform(-0.3,0.3)
      self.temp = np.random.uniform(-0.3,0.3)
      self.pop = np.random.uniform(0.0,1.0)
      self.tech = np.random.uniform(0.0,1.0)
      self.maxPop = 1
      self.ticks = 0
   def tick(self,dt):
       self.ticks += 1*dt
       self.temp += -self.sea*dt*0.0001
       self.temp = np.clip(self.temp,-1,1)
       self.sea += self.temp*dt*0.0001
       self.sea = np.clip(self.sea, -1, 1)
       self.pop = np.clip(self.pop, 0, 1)
       if -0.3 < self.temp < 0.3 and -0.3 < self.sea < 0.3:
           self.pop += 0.0001
       else:
           self.pop -= 0.0001

