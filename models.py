#!/usr/bin/env python
import numpy as np
import random

class Model(object):
   DEFAULT_SPEED = 0.001 # dt multiplier
   def __init__(self,sea=0.0,temp=0.0,pop=0.0,tech=0.0,speed=1):
      self.sea = sea
      self.temp = temp
      self.pop = pop
      self.tech = tech
      self.speed = speed*self.DEFAULT_SPEED
      self.enlightened = False
      self.event_warnings = [] # A list of events that have yet to be acknowledged by the game engine
   
   def tick(self,dt):
      pass
   
   def start_event(self,name):
      '''Called by the model when we would like to trigger an event.'''
      print("Starting event",name)
      self.event_warnings.append(name)
   
   def execute_event(self,name):
      '''Called by the game engine some time after start_event, when it is time
         for the event to actually happen.'''
      pass

class SineModel(Model):
   SEA_SPEED = 0.1
   TEMP_SPEED = 0.1
   POP_SPEED = 0.01
   TECH_SPEED = 0.01
   
   # The range of temp and sea values required for pop growth
   GOOD_TEMP_ZONE = 0.3
   GOOD_SEA_ZONE = 0.3
   GOOD_POP_ZONE = 0.25 # width around 0.5 pop for tech growth
   
   EVENT_DELTA = { # dsea,dtemp,pop factor,dtech
      'world_war' : (0.0,0.3,0.05,0.0),
      'war'       : (0.0,0.2,0.5,0.0),
      'plauge'    : (0.0,0.0,1,0.0),
      'monsoon'   : (0.3,-0.3,1,0.0),
      'sandstorm'   : (-0.3,0.3,1,0.0),
   }
   EVENT_PERIOD = 10
   def __init__(self):
      # Choose random starting values
      super().__init__(
         sea=np.random.uniform(-self.GOOD_SEA_ZONE,self.GOOD_SEA_ZONE),
         temp=np.random.uniform(-self.GOOD_TEMP_ZONE,self.GOOD_TEMP_ZONE),
         pop=0.1,tech=0.0
      )
      self.event_timer = 0

   def tick(self,dt):
      ds = self.speed * dt
      # Maybe start an event
      if self.event_timer > self.EVENT_PERIOD:
         self.event_timer = 0
         self.start_event(random.choice(list(self.EVENT_DELTA)))
      self.event_timer += ds
      # Handle behavior
      if not self.enlightened:
         self.temp += -self.sea*ds*self.TEMP_SPEED
         self.sea += self.temp*ds*self.SEA_SPEED
         if -self.GOOD_TEMP_ZONE < self.temp < self.GOOD_TEMP_ZONE and \
            -self.GOOD_SEA_ZONE < self.sea < self.GOOD_SEA_ZONE:
            self.pop += self.POP_SPEED*ds
         else:
             self.pop -= self.POP_SPEED*ds
         if 0.5-self.GOOD_POP_ZONE < self.pop < 0.5+self.GOOD_POP_ZONE:
             self.tech += (1-0.5+self.pop)*ds*self.TECH_SPEED
         #Yeah this fixes a bug where there's only 1 guy and he keeps rebuilding society lol
         if self.pop <= 0.001:
             self.pop = 0
         if self.pop == 0:
             self.tech = 0
      if self.tech >= 1:
         self.enlightened = True
      self.pop = np.clip(self.pop, 0, 1)
      self.tech = np.clip(self.tech, 0, 1)
      
   def execute_event(self,name):
      dsea,dtemp,dpop,dtech = self.EVENT_DELTA[name]
      self.sea = self.sea+dsea
      self.temp = self.temp+dtemp
      self.pop = np.clip(self.pop*dpop,0,1)
      self.tech = np.clip(self.tech+dtech,0,1)

class StochasticModel(Model):
   SPEED = 0.002 # average change to parameters each milisecond
   PULL_TO_CENTER = 0.0002
   def __init__(self):
      super().__init__(
         np.random.uniform(-1.0,1.0),
         np.random.uniform(-1.0,1.0),
         np.random.uniform(0.0,1.0),
         np.random.uniform(0.0,1.0)
      )
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
