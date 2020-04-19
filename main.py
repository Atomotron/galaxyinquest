#!/usr/bin/env python
import pygame
from pygame.locals import *
import numpy as np

from util import vfloor,vfloat
import planet


class Gravitator(object):
   def __init__(self,universe,pos,mass,radius):
      universe.gravitators.append(self)
      universe.sprites.append(self) # debug drawing
      self.pos = vfloat(pos) # convert to numpy array for that sweet operator overloading
      self.mass = mass
      self.radius = radius
   def draw(self,screen):
      return pygame.draw.circle(
         screen,
         (min(255,max(0,int(self.mass))),
          min(255,max(0,int(self.mass*255))),
          min(255,max(0,int(np.log(self.mass))))),
         vfloor(self.pos),
         int(self.radius),
         2,
      ) # return impacted pixels

class Player(object):
   RADIUS = 16 # radius for physics purposes
   G = 1 # The strength of the force of gravity
   THRUST = 0.001
   BOUNCE_DAMP = 0.1
   def __init__(self,universe,sprite,pos,angle=0,vel=(0,0)):
      self.universe = universe
      self.sprite = sprite
      self.pos = vfloat(pos)
      self.vel = vfloat(vel)
      self.acc = np.array((0.0,0.0)) # we want to keep around last frame's acceleration for velocity verlet
      self.angle = angle
      universe.sprites.append(self)
      universe.things.append(self)
      universe.player = self
   def wrap(self):
      '''Enforce toroidal geometry'''
      if self.pos[1] > self.universe.wrapping_rect.bottom + self.RADIUS:
         self.pos[1] = self.universe.wrapping_rect.top-self.RADIUS
      elif self.pos[1] < self.universe.wrapping_rect.top-self.RADIUS:
         self.pos[1] = self.universe.wrapping_rect.bottom + self.RADIUS
      
      if self.pos[0] > self.universe.wrapping_rect.right + self.RADIUS:
         self.pos[0] = self.universe.wrapping_rect.left-self.RADIUS
      elif self.pos[0] < self.universe.wrapping_rect.left-self.RADIUS:
         self.pos[0] = self.universe.wrapping_rect.right + self.RADIUS
   def gravity_at(self,pos):
      '''Computes the acceleration due to gravity due to a body.'''
      g = np.array((0.0,0.0))
      for gravitator in self.universe.gravitators:
         r = gravitator.pos - self.pos
         r_mag_raised_to_three = np.power(np.sum(np.square(r)),3/2)
         g += self.G*gravitator.mass*r / r_mag_raised_to_three
      return g
   def thrust(self):
      '''Computes how much we should be thrusting based on our controls.'''
      return np.array((
         self.THRUST*np.cos(self.angle),
         self.THRUST*np.sin(self.angle),
      )) if pygame.mouse.get_pressed()[0] else np.array((0.0,0.0))
   def collide(self):
      '''Check if we're inside a planet, and get us out if we are.'''
      for gravitator in self.universe.gravitators:
         r = gravitator.pos - self.pos
         r_mag = np.sqrt(np.sum(np.square(r)))
         if r_mag < self.RADIUS+gravitator.radius:
            r_hat = r/r_mag
            v_proj_r_hat = np.sum(self.vel*r_hat)*r_hat # project velocity on to radial vector
            self.vel -= (2-self.BOUNCE_DAMP)*v_proj_r_hat # elastic colission
            self.pos = gravitator.pos - r_hat*(self.RADIUS+gravitator.radius) # put us back on the surface
   def tick(self,dt):
      # Point at the mouse
      delta_to_mouse = vfloat(pygame.mouse.get_pos()) - self.pos
      self.angle = np.arctan2(delta_to_mouse[1],delta_to_mouse[0]) 
      # Collide with planets
      self.collide()
      # Update velocity
      self.pos = self.pos + self.vel*dt + 0.5*self.acc*(dt*dt)
      new_acc = self.gravity_at(self.pos) + self.thrust()
      self.vel = self.vel + 0.5*dt*(self.acc + new_acc)
      self.acc = new_acc # save acceleration for next frame
      # Enforce toroidal geometry
      self.wrap()
   def draw(self,screen):
      rotated_sprite = pygame.transform.rotozoom(self.sprite,-self.angle*(180/np.pi)-90,1)
      pos = vfloor(self.pos - vfloat(rotated_sprite.get_size())/2)
      return screen.blit(
         rotated_sprite,
         pos
      ) # Returns impacted pixels

class Universe(object):
   def __init__(self,background,wrapping_rect=None):
      self.background = background
      self.wrapping_rect = wrapping_rect or background.get_rect() # if wrapping_rect is null, use the background rect
      self.sprites = [] # things that need to have draw(screen) called on them
      self.things = [] # things that need to have tick(dt) called on them
      self.gravitators = [] # things that create gravitational fields      
      self.dirty_rects = [background.get_rect()] # patches of the background that will need to be redrawn
      self.player = None
      self.planets = []
   def draw(self,screen):
      bg_rect = self.background.get_rect()
      for rect in self.dirty_rects:
         screen.blit(self.background,rect.topleft,rect.clip(bg_rect))
      touched_rects = self.dirty_rects
      self.dirty_rects = []
      for sprite in self.sprites:
         rect = sprite.draw(screen)
         if rect: # If the draw function has created a dirty rect
            self.dirty_rects.append(rect)
            touched_rects.append(rect)
      return touched_rects
   def tick(self,dt):
      for thing in self.things:
         thing.tick(dt)
   def populate(self):
      Gravitator(self,(500,500),100,80)

if __name__ == "__main__":
   pygame.init()
   screen_size = (1024,768)
   screen = pygame.display.set_mode(screen_size)
   clock = pygame.time.Clock()
   universe = Universe(pygame.image.load("img/nebula.jpg").convert())
   Player(universe,pygame.image.load("img/sprite_grave.png").convert_alpha(),(500,300),0,(0.7,0))
   universe.populate()
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
        pygame.display.update(universe.draw(screen)) # Only push out the stuff we changed to the OS
