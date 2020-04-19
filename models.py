#!/usr/bin/env python
import numpy as np

class PlanetModel(object):
   SPEED = 0.002 # average change to parameters each milisecond
   PULL_TO_CENTER = 0.0002
   def __init__(self):
      # Choose random starting values
      self.sea = np.random.uniform(-1.0,1.0)
      self.temp = np.random.uniform(-1.0,1.0)
      self.pop = np.random.uniform(0.0,1.0)
      self.tech = np.random.uniform(0.0,1.0)
   def random_delta(self,dt,value,off_center):
      step = np.random.uniform(-1.0,1.0)*self.SPEED*dt
      restoration = - self.PULL_TO_CENTER*off_center*dt
      return value + step + restoration
   def tick(self,dt):
      # Randomly increase or decrease parameters, but keep them bounded
      self.sea = np.clip(self.random_delta(dt,self.sea,self.sea), -1,1)
      self.temp = np.clip(self.random_delta(dt,self.temp,self.temp), -1,1)
      self.pop = np.clip(self.random_delta(dt,self.pop,self.pop-0.5), 0,1)
      self.tech = np.clip(self.random_delta(dt,self.tech,self.tech-0.5), 0,1)
