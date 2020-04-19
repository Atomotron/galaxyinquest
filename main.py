#!/usr/bin/env python
import pygame
from pygame.locals import *
import numpy as np

import planet

class Player(object):
   RADIUS = 16 # radius for physics purposes
   def __init__(self,universe,sprite,pos,vel=(0,0)):
      self.universe = universe
      self.sprite = sprite
      self.pos = np.array(pos,dtype=np.float64) # convert to numpy array for that sweet operator overloading
      self.vel = np.array(vel,dtype=np.float64)

class Universe(object):
   def __init__(self,background,wrapping_rect=None):
      self.background = background
      self.wrapping_rect = wrapping_rect or background.get_rect() # if wrapping_rect is null, use the background rect
      self.sprites = [] # things that need to have draw(screen) called on them
      self.things = [] # things that need to have tick(dt) called on them
      self.dirty_rects = [background.get_rect()] # patches of the background that will need to be redrawn
      self.player = None
      self.planets = []
   def draw(self,screen):
      bg_rect = self.background.get_rect()
      for rect in self.dirty_rects:
         screen.blit(self.background,rect.topleft,rect.clip(bg_rect))
      for sprite in self.sprites:
         rect = sprite.draw(screen)
         if rect: # If the draw function has created a dirty rect
            self.dirty_rects.append(rect)
   def tick(self,dt):
      for thing in self.things:
         thing.tick(dt)

if __name__ == "__main__":
   pygame.init()
   screen_size = (1024,768)
   screen = pygame.display.set_mode(screen_size)
   clock = pygame.time.Clock()
   universe = Universe(pygame.image.load("img/nebula.jpg").convert())
   while True:
        dt = clock.tick(60)  # If we go faster than 60fps, stop and wait.
        for event in pygame.event.get():  # Get everything that's happening
            if event.type == QUIT:  # If someone presses the X button
                pygame.quit()  # Shuts down the window
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()
        universe.tick(dt)
        universe.draw(screen)
        pygame.display.flip()
