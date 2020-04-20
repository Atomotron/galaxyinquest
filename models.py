#!/usr/bin/env python
import numpy as np

class SineModel(object):
   SPEED = 0.002 # average change to parameters each milisecond
   PULL_TO_CENTER = 0.0002
   def __init__(self,string = "Hi",stringcolour = (255,255,255)):
      # Choose random starting values
      self.string = string
      self.stringColour = stringcolour
      self.sea = np.random.uniform(-0.8,0.8)
      self.temp = np.random.uniform(-0.8,0.8)
      self.pop = np.random.uniform(0.0,1.0)
      self.tech = np.random.uniform(0.0,1.0)
      self.maxPop = 1
      self.ticks = 0
      self.isEnlightened = False

   def isEnlightened(self):
        return self.isEnlightened

   def tick(self,dt):
        if not self.isEnlightened:
            self.ticks += 1*dt
            self.temp += -self.sea*dt*0.0001
            self.temp = np.clip(self.temp,-1,1)
            self.sea += self.temp*dt*0.0001
            self.sea = np.clip(self.sea, -1, 1)
            self.pop = np.clip(self.pop, 0, 1)
            self.tech = np.clip(self.tech, 0, 1)
            if -0.3 < self.temp < 0.3 and -0.3 < self.sea < 0.3:
                 self.pop += 0.0001
            else:
                 self.pop -= 0.0001
            if 0.3 < self.pop < 0.8:
                self.tech += 0.0001 - (0.55-self.pop)*0.0001
            #Yeah this fixes a bug where there's only 1 guy and he keeps rebuilding society lol
            if self.pop <= 0.001:
                self.pop = 0
            if self.pop == 0:
                self.tech = 0
        if self.tech >= 1:
            self.isEnlightened = True
            self.temp = self.temp

class StochasticModel(object):
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

PlanetModel = SineModel # Select the sine model
