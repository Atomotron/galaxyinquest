#!/usr/bin/env python
import pygame
from pygame.locals import *
import numpy as np

from util import vfloor,vfloat
import planet

class PlanetModel(object):
   '''A model of the evolution of a planet. Set to randomly increase and decrease parameters kind of like the stock market.'''
   REFRESH_TIME = 1000/2 # refresh no fewer than 2 times per second
   SPEED = 0.002 # average change to parameters each milisecond
   PULL_TO_CENTER = 0.0002
   def __init__(self,universe,planet_sprite):
      self.universe = universe
      self.universe.things.append(self) # we want to receive ticks
      self.planet_sprite = planet_sprite
      self.staleness = 0 # a counter for time
      self.refresh_time = 0
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
      # Update the sprite if we have gone too long without doing so
      self.planet_sprite.set_parameters(self.sea,self.temp,self.pop,self.tech)
      if self.staleness > self.refresh_time:
         self.refresh_time = np.random.uniform(0.0,self.REFRESH_TIME)
         self.staleness = 0
         self.planet_sprite.update()
      self.staleness += dt

class Gravitator(object):
   def __init__(self,universe,pos,mass,radius):
      universe.gravitators.append(self)
      #universe.sprites.append(self) # debug drawing
      self.pos = vfloat(pos) # convert to numpy array for that sweet operator overloading
      self.mass = mass
      self.radius = radius
   def draw(self,screen,camera):
      return pygame.draw.circle(
         screen,
         (min(255,max(0,int(self.mass))),
          min(255,max(0,int(self.mass*255))),
          min(255,max(0,int(np.log(self.mass))))),
         vfloor(camera.cam(self.pos)),
         int(self.radius*camera.zoom),
         1,
      ).inflate(1,0) # return impacted pixels

class Player(object):
   RADIUS = 24 # radius for physics purposes
   G = 0.1 # The strength of the force of gravity
   THRUST = 0.001
   BOUNCE_DAMP = 0.4
   ABUSALEHBREAKS = 0.005 # I will put this in properly tomorrow
   BOUNCE_VOLUME = 0.5
   def __init__(self,universe,spritesheet,rects,sounds,pos,angle=0,vel=(0,0)):
      self.universe = universe
      self.sprites = {k:spritesheet.subsurface(rects[k]) for k in rects}
      self.rects = rects
      self.sounds = sounds
      self.pos = vfloat(pos)
      self.vel = vfloat(vel)
      self.acc = np.array((0.0,0.0)) # we want to keep around last frame's acceleration for velocity verlet
      self.angle = angle
      universe.sprites.append(self)
      universe.things.append(self)
      universe.player = self
         
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
      return (np.array((
         self.THRUST*np.cos(self.angle),
         self.THRUST*np.sin(self.angle),
      )) if pygame.mouse.get_pressed()[0] else np.array((0.0,0.0)))
      
   def collide(self):
      '''Check if we're inside a planet, and get us out if we are.'''
      for gravitator in self.universe.gravitators:
         r = gravitator.pos - self.pos
         r_mag = np.sqrt(np.sum(np.square(r)))
         if r_mag < self.RADIUS+gravitator.radius:
            r_hat = r/r_mag
            v_dot_r_hat = np.sum(self.vel*r_hat)
            if v_dot_r_hat > 0.1:
               self.sounds['bounce'].set_volume(v_dot_r_hat*self.BOUNCE_VOLUME) # Quiet sound for tiny bounce
               self.sounds['bounce'].play()
            v_proj_r_hat = v_dot_r_hat*r_hat # project velocity on to radial vector
            self.vel -= (2-self.BOUNCE_DAMP)*v_proj_r_hat # elastic colission
            self.pos = gravitator.pos - r_hat*(self.RADIUS+gravitator.radius) # put us back on the surface
            
   def tick(self,dt):
      # Point at the mouse
      delta_to_mouse = self.universe.uncam(vfloat(pygame.mouse.get_pos())) - self.pos
      self.angle = np.arctan2(delta_to_mouse[1],delta_to_mouse[0]) 
      # Collide with planets
      self.collide()
      # Update velocity
      self.pos = self.pos + self.vel*dt + 0.5*self.acc*(dt*dt)
      new_acc = self.gravity_at(self.pos) + self.thrust()
      self.vel = self.vel + 0.5*dt*(self.acc + new_acc)
      self.acc = new_acc # save acceleration for next frame
      
   def draw(self,screen,camera):
      axis = np.array((np.cos(self.angle),np.sin(self.angle))) * camera.zoom
      pos = camera.cam(self.pos)
      rotated_U = pygame.transform.rotozoom(
         self.sprites["U"],
         -self.angle*(180/np.pi)-90,
         camera.zoom
      )
      scaled_orb_small = pygame.transform.rotozoom(
         self.sprites["orb_small"],
         0,
         camera.zoom
      )
      scaled_orb_large = pygame.transform.rotozoom(
         self.sprites["orb_large"],
         0,
         camera.zoom
      )
      r = screen.blit(
         scaled_orb_small,
         vfloor(pos - vfloat(scaled_orb_small.get_size())/2 - axis*28)
      )
      r = r.union(screen.blit(
         scaled_orb_large,
         vfloor(pos - vfloat(scaled_orb_large.get_size())/2- axis*3)
      ))
      return r.union(screen.blit(
         rotated_U,
         vfloor(pos - vfloat(rotated_U.get_size())/2)
      ))
      

class Universe(object):
   def __init__(self,planet_factory,background,shadow,wrapping_rect=None):
      self.planet_factory = planet_factory
      self.background = background
      self.wrapping_rect = wrapping_rect or background.get_rect() # if wrapping_rect is null, use the background rect
      self.sprites = [] # things that need to have draw(screen) called on them
      self.things = [] # things that need to have tick(dt) called on them
      self.gravitators = [] # things that create gravitational fields      
      self.dirty_rects = [background.get_rect()] # patches of the background that will need to be redrawn
      self.player = None
      self.planets = []
      self.shadow = shadow
      self.scaled_shadow = shadow
      self.zoom = 1
      self.camera = np.array((0.0,0.0))
      self.rect_offset = vfloat(self.wrapping_rect.size)/2 # To move the origin from the top left to the center of the screen
      self.age = 0
      
   def cam(self,pos):
      '''Adjusts a position to take in to account our camera and zoom.'''
      return (pos-self.camera)*self.zoom + self.rect_offset
   
   def uncam(self,pos):
      '''Inverse of cam: takes screen space to world space'''
      return (pos-self.rect_offset)/self.zoom + self.camera
   
   def draw(self,screen):
      bg_rect = self.background.get_rect()
      for rect in self.dirty_rects:
         screen.blit(self.background,rect.topleft,rect.clip(bg_rect))
      touched_rects = self.dirty_rects
      self.dirty_rects = []
      self.scaled_shadow = pygame.transform.rotozoom(self.shadow,0,self.zoom)
      for sprite in self.sprites:
         rect = sprite.draw(screen,self)
         if rect: # If the draw function has created a dirty rect
            self.dirty_rects.append(rect)
            touched_rects.append(rect)
      return touched_rects

   def tick(self,dt):
      self.age += 0.001*dt
      self.zoom = np.sin(self.age)*0.4 + 0.6
      self.camera = 400 * np.array((np.sin(3/10*self.age+np.pi/2),np.cos(4/10*self.age)))
      for thing in self.things:
         thing.tick(dt)
         
   def add_planet(self,pos,mass):
      PlanetModel(self,self.planet_factory.make_planet(self,pos))
      Gravitator(self,pos,mass,80)

   def populate(self):
      self.add_planet((-300,300),20)
      self.add_planet((300,0),20)
      self.add_planet((-300,-300),20)

if __name__ == "__main__":
   pygame.mixer.pre_init(44100, -16, 2, 512)
   pygame.mixer.pre_init(44100, -16, 2, 1024)
   pygame.init()
   screen_size = (1024,768)
   screen = pygame.display.set_mode(screen_size)
   clock = pygame.time.Clock()
   planet_factory = planet.PlanetSpriteFactory(
      pygame.image.load("img/terrain.png").convert_alpha(),
      pygame.image.load("img/planet.png").convert_alpha(),
      pygame.image.load("img/cityscapes.png").convert_alpha(),
      pygame.image.load("img/atmosphere_color.png").convert_alpha(),
      pygame.image.load("img/AtmosphereWhite.png").convert_alpha(),
      pygame.image.load("img/Clouds.png").convert_alpha(),
   )
   universe = Universe(
      planet_factory,
      pygame.image.load("img/nebula.jpg").convert(),
      pygame.image.load("img/shadow_outline.png").convert_alpha()
   )
   universe.populate()
   Player(
      universe,pygame.image.load("img/ship58h.png").convert_alpha(),
      {
         'U': Rect(0,0,52,58),
         'orb_small': Rect(52,0,10,10),
         'orb_large': Rect(52,10,28,29),
      },
      {
         'bounce':pygame.mixer.Sound("sounds/bounce_planet_short.ogg"),
      },
      (0,0),0,(0.0,0)
   )
   pygame.mixer.Sound("sounds/space_ambient.ogg").play(loops=-1,fade_ms=1000)
   engine_sound = pygame.mixer.Sound("sounds/sfx_engine_loop.ogg")
   engine_start_sound = pygame.mixer.Sound("sounds/sfx_engine_initial.ogg")
   engine_stop_sound = pygame.mixer.Sound("sounds/sfx_engine_off.ogg")

   while True:
        dt = clock.tick(60)  # If we go faster than 60fps, stop and wait.
        for event in pygame.event.get():  # Get everything that's happening
            if event.type == QUIT:  # If someone presses the X button
                pygame.quit()  # Shuts down the window
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
               engine_sound.play(loops=-1,fade_ms=100)
               engine_start_sound.play()
            elif event.type == MOUSEBUTTONUP and event.button == 1:
               engine_sound.fadeout(100)
               engine_stop_sound.play()
        universe.tick(dt)
        pygame.display.update(universe.draw(screen)) # Only push out the stuff we changed to the OS
