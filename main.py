#!/usr/bin/env python
import pygame
from pygame.locals import *
import numpy as np

from util import vfloor,vfloat
import planet
import widgets
from models import PlanetModel

class Planet(object):
   '''A model of the evolution of a planet. Set to randomly increase and decrease parameters kind of like the stock market.'''
   REFRESH_TIME = 1000/2 # refresh no fewer than 2 times per second
   TITLE_OFFSET = 130 # The distance above the planet that the title is drawn
   def __init__(self,universe,planet_sprite,pos,mass,radius):
      self.universe = universe
      self.universe.things.append(self) # we want to receive ticks
      universe.gravitators.append(self)
      universe.camera_targets.append(self)
      universe.sprites.append(self)
      self.planet_sprite = planet_sprite
      self.pos = pos
      self.mass = mass
      self.radius = radius
      self.staleness = 0 # a counter for time
      self.refresh_time = 0
      self.model = PlanetModel()
      self.name = planet.generate_name()
      self.title_small = self.universe.fonts[0].render(self.name,True,(255,255,255))
      self.title_large = self.universe.fonts[1].render(self.name,True,(255,255,255))

   def tick(self,dt):
      self.model.tick(dt)
      # Update the sprite if we have gone too long without doing so
      self.planet_sprite.set_parameters(self.model.sea,self.model.temp,self.model.pop,self.model.tech)
      if self.staleness > self.refresh_time:
         self.refresh_time = np.random.uniform(0.0,self.REFRESH_TIME)
         self.staleness = 0
         self.planet_sprite.update()
      self.staleness += dt

   def draw(self,screen,camera):
      title_pos = vfloor(camera.cam(self.pos-np.array((0.0,self.TITLE_OFFSET))))
      title_pos = (title_pos[0]-self.title_small.get_width()//2,title_pos[1]-self.title_small.get_height()//2)
      return screen.blit(self.title_small,title_pos)

class Player(object):
   RADIUS = 32 # radius for physics purposes
   G = 0.25 # The strength of the force of gravity
   THRUST = 0.00025
   BOUNCE_DAMP = 0.6
   ABUSALEHBREAKS = 0.005 # I will put this in properly tomorrow
   BOUNCE_VOLUME = 0.5
   PLANET_CONNECTION_RADIUS = 160 # How many units we can be off the surface of the planet for us to count as "orbiting"
   BOUNDARIES = (
      (-5000,5000),
      (-5000,5000)
   )
   def __init__(self,universe,spritesheet,rects,sounds,pos,angle=0,vel=(0,0)):
      self.universe = universe
      self.sprites = {k:spritesheet.subsurface(rects[k]) for k in rects}
      self.rects = rects
      self.sounds = sounds
      self.pos = vfloat(pos)
      self.initial_pos = vfloat(pos)# for teleporting home
      self.vel = vfloat(vel)
      self.initial_vel = vfloat(vel) # for teleporting home
      self.acc = np.array((0.0,0.0)) # we want to keep around last frame's acceleration for velocity verlet
      self.angle = angle
      self.thrusting = False
      self.connected_planet = None # The planet we're within range of
      universe.sprites.append(self)
      universe.things.append(self)
      universe.camera_targets.append(self)
      universe.player = self
         
   def gravity_at(self,pos):
      '''Computes the acceleration due to gravity due to a body.'''
      g = np.array((0.0,0.0))
      gravitators = [self.connected_planet] if self.connected_planet else self.universe.gravitators
      for gravitator in gravitators:
         r = gravitator.pos - self.pos
         r_mag_raised_to_three = np.power(np.sum(np.square(r)),3/2)
         g += self.G*gravitator.mass*r / r_mag_raised_to_three
      return g
   
   
   def start_thrusting(self):
      '''Called by the UI on a mousebuttondown after it has verified that you're not clicking a button.'''
      self.thrusting = True
   
   @property
   def abu_saleh_breaking(self):
      '''Determines whether or not we will need to take our car to abu saleh later today.'''
      return pygame.key.get_pressed()[K_SPACE]
   
   def thrust(self):
      '''Computes how much we should be thrusting based on our controls.'''
      self.thrusting = self.thrusting and pygame.mouse.get_pressed()[0]
      if self.abu_saleh_breaking:
         return -self.vel*self.ABUSALEHBREAKS
      elif self.thrusting:
         return np.array((
            self.THRUST*np.cos(self.angle),
            self.THRUST*np.sin(self.angle),
         ))         
      else:
         return np.array((0.0,0.0))
      
   def collide(self):
      '''Check if we're inside a planet, and get us out if we are.'''
      nearest_r_mag = None
      nearest_gravitator = None
      for gravitator in self.universe.gravitators:
         r = gravitator.pos - self.pos
         r_mag = np.sqrt(np.sum(np.square(r)))
         if not nearest_r_mag or nearest_r_mag > r_mag:
            nearest_gravitator = gravitator
            nearest_r_mag = r_mag
         if r_mag < self.RADIUS+gravitator.radius:
            r_hat = r/r_mag
            v_dot_r_hat = np.sum(self.vel*r_hat)
            if v_dot_r_hat > 0.1:
               self.sounds['bounce'].set_volume(v_dot_r_hat*self.BOUNCE_VOLUME) # Quiet sound for tiny bounce
               self.sounds['bounce'].play()
            v_proj_r_hat = v_dot_r_hat*r_hat # project velocity on to radial vector
            self.vel -= (2-self.BOUNCE_DAMP)*v_proj_r_hat # elastic colission
            self.pos = gravitator.pos - r_hat*(self.RADIUS+gravitator.radius) # put us back on the surface
      if nearest_r_mag < self.PLANET_CONNECTION_RADIUS+nearest_gravitator.radius:
         self.connected_planet = nearest_gravitator
      else:
         self.connected_planet = None
         
   def warp_home(self):
      if self.pos[0] < self.BOUNDARIES[0][0] or self.pos[0] > self.BOUNDARIES[0][1] or \
         self.pos[1] < self.BOUNDARIES[1][0] or self.pos[1] > self.BOUNDARIES[1][1]:
         self.pos = self.initial_pos
         self.vel = self.initial_vel
         self.sounds['warp_home'].play()
         
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
      self.warp_home()
      
   def draw(self,screen,camera):
      axis = np.array((np.cos(self.angle),np.sin(self.angle))) * camera.zoom
      pos = camera.cam(self.pos)
      postfix = "_glow" if self.thrusting else ""
      rotated_U = pygame.transform.rotozoom(
         self.sprites["U"+postfix],
         -self.angle*(180/np.pi)-90,
         camera.zoom
      )
      scaled_orb_small = pygame.transform.rotozoom(
         self.sprites["orb_small"+postfix],
         0,
         camera.zoom
      )
      scaled_orb_large = pygame.transform.rotozoom(
         self.sprites["orb_large"+postfix],
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
   CAMERA_SPEED = 0.01 # The rate at which the camera approaches the target values
   MARGIN = 100
   def __init__(self,planet_factory,background,shadow,fonts):
      self.planet_factory = planet_factory
      self.background = background
      self.wrapping_rect = background.get_rect() # if wrapping_rect is null, use the background rect
      self.sprites = [] # things that need to have draw(screen) called on them
      self.things = [] # things that need to have tick(dt) called on them
      self.gravitators = [] # things that create gravitational fields    
      self.camera_targets = [] # Things that the camera should try to display  
      self.dirty_rects = [background.get_rect()] # patches of the background that will need to be redrawn
      self.player = None
      self.shadow = shadow
      self.scaled_shadow = shadow
      self.zoom = 1
      self.camera = np.array((0.0,0.0))
      self.camera_urgency = 1
      self.target_zoom = 1
      self.target_camera = np.array((0.0,0.0))
      self.rect_offset = vfloat(self.wrapping_rect.size)/2 # To move the origin from the top left to the center of the screen
      self.age = 0
      self.fonts = fonts
      
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
      if self.player.connected_planet:
         self.target_zoom = 1
         self.target_camera = self.player.connected_planet.pos
         self.camera_urgency = 0.1
      else:
         min_x = min([o.pos[0] for o in self.camera_targets]) - self.MARGIN
         max_x = max([o.pos[0] for o in self.camera_targets]) + self.MARGIN
         min_y = min([o.pos[1] for o in self.camera_targets]) - self.MARGIN
         max_y = max([o.pos[1] for o in self.camera_targets]) + self.MARGIN
         self.target_zoom = min(
            self.wrapping_rect.width/(max_x-min_x),
            self.wrapping_rect.height/(max_y-min_y),
            1 # Never zoom closer than 1
         )
         self.target_camera = np.array((
            (max_x+min_x)/2,(max_y+min_y)/2
         ))
         self.camera_urgency = 1
      self.camera += (self.target_camera-self.camera)*self.CAMERA_SPEED*dt*self.camera_urgency
      self.zoom += (self.target_zoom-self.zoom)*self.CAMERA_SPEED*dt*self.camera_urgency
      for thing in self.things:
         thing.tick(dt)
         
   def add_planet(self,pos,mass):
      Planet(self,self.planet_factory.make_planet(self,pos),pos,mass,80)

   def populate(self):
      self.add_planet((-300,300),20)
      self.add_planet((800,0),20)
      self.add_planet((-300,-300),20)

if __name__ == "__main__":
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
   font = pygame.font.Font("fonts/monodb_.ttf",24)
   font_big = pygame.font.Font("fonts/monodb_.ttf",48)
   universe = Universe(
      planet_factory,
      pygame.image.load("img/nebula.jpg").convert(),
      pygame.image.load("img/shadow_outline.png").convert_alpha(),
      (font,font_big),
   )
   universe.populate()
   Player(
      universe,pygame.image.load("img/ship58h.png").convert_alpha(),
      {
         'U': Rect(0,0,52,58),
         'orb_small': Rect(57,44,10,10),
         'orb_large': Rect(52,10,28,29),
         'U_glow': Rect(0,58,52,58),
         'orb_small_glow': Rect(52,97,19,19),
         'orb_large_glow': Rect(52,68,28,29),
      },
      {
         'bounce':pygame.mixer.Sound("sounds/bounce_planet_short.ogg"),
         'warp_home':pygame.mixer.Sound("sounds/error.ogg"),
      },
      (0,0),0,(0.0,0)
   )
   pygame.mixer.Sound("sounds/space_ambient.ogg").play(loops=-1,fade_ms=1000)
   sounds = {
      'engine' :  pygame.mixer.Sound("sounds/sfx_engine_loop.ogg"),
      'engine_start' :  pygame.mixer.Sound("sounds/sfx_engine_initial.ogg"),
      'engine_stop'  :  pygame.mixer.Sound("sounds/sfx_engine_off.ogg"),
      'abusalehbreaks'  :  pygame.mixer.Sound("sounds/abubreak.ogg")
   }
   ui = widgets.UI(universe,sounds)    
   while True:
        dt = clock.tick(60)  # If we go faster than 60fps, stop and wait.
        for event in pygame.event.get():  # Get everything that's happening
            if event.type == QUIT:  # If someone presses the X button
                pygame.quit()  # Shuts down the window
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()
            elif event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP or event.type == KEYDOWN:
               ui.handle_event(event)
        universe.tick(dt)
        pygame.display.update(universe.draw(screen)) # Only push out the stuff we changed to the OS
