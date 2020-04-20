#!/usr/bin/env python
import pygame
from pygame import Rect
import random

from util import vfloor,vfloat

class Effect(object):
   FRAME_TIME = 100
   RECTS = {
      'world_war' : [Rect(160*i,0,160,160) for i in range(0,7)],
      'war'       : [Rect(160*i,160,160,160) for i in range(0,7)],
      'plauge'    : [Rect(160*i,160*2,160,160) for i in range(0,7)],
      'monsoon'   : [Rect(160*i,160*3,160,160) for i in range(0,7)],
   }
   def __init__(self,res,universe,pos,name,loops=1):
      self.sheet = res.image['effects']
      self.universe = universe
      self.frames = self.RECTS[name]
      self.time = 0
      self.loops = loops
      self.pos = vfloat(pos)
      
   @property
   def frame(self):
      return int(self.time/self.FRAME_TIME)
      
   def tick(dt):
      self.time += dt
      if self.frame >= len(self.frames):
         if self.loops > 0:
            self.loops -= 1
         if self.loops == 0: # if loops starts out negative we'll loop forever
            universe.effects.remove(self)
         
   def draw(self,screen,camera):
      rect = self.frames[frame]
      pos = vfloor(camera.cam(self.pos - vfloat(rect.size)))
      scaled_sprite = pygame.transform.rotozoom(self.sheet.subsurface(rect),0,camera.zoom)
      return surface.blit(scaled_sprite,pos)
