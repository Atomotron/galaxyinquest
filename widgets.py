#!/usr/bin/env python
from sys import exit
import pygame
from pygame.locals import *
from pygame import Rect
import numpy as np
from collections import deque
from util import vfloat,vfloor
import random
CARGO_RECTS = {
   'off_full_r':Rect(0,12,30,112),
   'off_full_g':Rect(30,12,30,112),
   'off_full_b':Rect(60,12,30,112),
   'off_empty_r':Rect(0,12+124,30,112),
   'off_empty_g':Rect(30,12+124,30,112),
   'off_empty_b':Rect(60,12+124,30,112),
   'on_full_r':Rect(0,12+124*2,30,112),
   'on_full_g':Rect(30,12+124*2,30,112),
   'on_full_b':Rect(60,12+124*2,30,112),
   'on_empty_r':Rect(0,12+124*3,30,112),
   'on_empty_g':Rect(30,12+124*3,30,112),
   'on_empty_b':Rect(60,12+124*3,30,112),
}
PLANET_RECTS = {
   'full_e':Rect(152,0,157,21),
   'empty_e':Rect(152,21,157,21),
   'off_full_r':Rect(152,42,157,25),
   'off_empty_r':Rect(152,42+25,157,25),
   'on_full_r':Rect(152,42+25*2,157,25),
   'on_empty_r':Rect(152,42+25*3,157,25),
   'off_full_g':Rect(152,42+25*4,157,25),
   'off_empty_g':Rect(152,42+25*5,157,25),
   'on_full_g':Rect(152,42+25*6,157,25),
   'on_empty_g':Rect(152,42+25*7,157,25),
   'off_full_b':Rect(152,42+25*8,157,25),
   'off_empty_b':Rect(152,42+25*9,157,25),
   'on_full_b':Rect(152,42+25*10,157,25),
   'on_empty_b':Rect(152,42+25*11,157,25),
}

class BarButton(object):
   '''Combines a bar and a button in to one big honkin' class.'''
   ALPHA_CUTOFF = 0 # A pixel on the button sprite must have more than this much alpha to receive clicks
   def __init__(self,ui,pos,sheet,sounds,off_full,off_empty,on_full,on_empty,early_cut,value=0.5,responsive=True,visible=True,sticky=False):
      self.ui = ui
      self.pos = pos
      self.sheet = sheet
      self.off_full = off_full
      self.off_empty = off_empty
      self.on_full = on_full
      self.on_empty = on_empty
      self.value = value
      self.responsive = responsive
      self.early_cut = early_cut # for when 100% full corresponds to a slice short of 100% of the full image
      self.sounds = sounds
      self.mutually_exclusive = [] # None, by default
      self.sticky = sticky
      self.activated = False
      self.visible = visible
      ui.widgets.append(self)
      
   @property
   def full_sprite(self):
      return self.sheet.subsurface(self.on_full if self.activated else self.off_full)
   @property
   def empty_sprite(self):
      return self.sheet.subsurface(self.on_empty if self.activated else self.off_empty)      
   
   def sprite_contains(self,rel_pos):
      sprite = self.full_sprite
      return sprite.get_rect().collidepoint(rel_pos) and sprite.get_at(rel_pos)[3] > self.ALPHA_CUTOFF
   
   def contains(self,pos):
      return False
      
   def handle_event(self,event):
      '''Returns true if we want to consume the event.'''
      if not self.responsive or not self.visible:
         return False

      if event.type == KEYDOWN:
          return False
      if event.button != 1:
         return False
      if event.type == MOUSEBUTTONDOWN:
         if self.contains(event.pos):
            if not self.activated:
               self.activated = True
               self.sounds['select'].play()
               for me in self.mutually_exclusive:
                  me.activated = False
            return True
      elif event.type == MOUSEBUTTONUP and self.activated and not self.sticky:
         self.activated = False
         return True
      return False
      
   def draw(self,surface,camera):
      pass

class PlanetBar(BarButton):
   def __init__(self,ui,pos,offset,sheet,sounds,off_full,off_empty,on_full,on_empty,early_cut=0,value=0.5,responsive=True,visible=False):
      super().__init__(ui,pos,sheet,sounds,off_full,off_empty,on_full,on_empty,early_cut,value,responsive,visible,sticky=False)
      self.offset = vfloat(offset)
   
   def contains(self,pos):
      rel_pos = vfloor(self.ui.universe.uncam(vfloat(pos)) - self.pos - self.offset)
      return self.sprite_contains(rel_pos)

   def draw(self,surface,camera):
      if not self.visible:
         return None
      pos = vfloor(camera.cam(self.pos) + self.offset)
      empty_sprite = self.empty_sprite
      full_sprite = self.full_sprite
      cut = int( self.value*(full_sprite.get_width()-self.early_cut) )
      full_pos = pos
      full_rect = Rect((0,0),
         (cut,
          full_sprite.get_height())
      )
      empty_pos = (
         pos[0] + cut,
         pos[1]
      )
      empty_rect = Rect((cut,0),
         (empty_sprite.get_width() - cut,
          empty_sprite.get_height())
      )
      r = surface.blit(full_sprite,full_pos,full_rect)
      return r.union(surface.blit(empty_sprite,empty_pos,empty_rect))

class InventoryBar(BarButton):
   def __init__(self,ui,pos,sheet,sounds,off_full,off_empty,on_full,on_empty,early_cut=0,value=0.5,responsive=True,visible=True):
                       #ui,pos,sheet,sounds,off_full,off_empty,on_full,on_empty,early_cut,value=0.5,responsive=True,visible=True,sticky=False
      super().__init__(ui,pos,sheet,sounds,off_full,off_empty,on_full,on_empty,early_cut,value,responsive,visible,sticky=True)

   def contains(self,pos):
      rel_pos = (pos[0]-self.pos[0],pos[1]-self.pos[1])
      return self.sprite_contains(rel_pos)

   def draw(self,surface,camera):
      if not self.visible:
         return None
      pos = self.pos
      empty_sprite = self.empty_sprite
      full_sprite = self.full_sprite
      cut = int( (1-self.value)*(empty_sprite.get_height()-self.early_cut) )
      empty_pos = pos
      empty_rect = Rect((0,0),
         (empty_sprite.get_width(),
         cut)
      )
      full_pos = (
         pos[0],
         pos[1] + cut
      )
      full_rect = Rect((0,cut),
         (full_sprite.get_width(),
          full_sprite.get_height() - cut)
      )
      r = surface.blit(full_sprite,full_pos,full_rect)
      return r.union(surface.blit(empty_sprite,empty_pos,empty_rect))

class UI(object):
   def __init__(self,res,universe):
      self.res = res
      self.sounds = res.sound
      self.universe = universe
      self.universe.ui = self
      self.sheet = res.image['ui']
      self.widgets = []
      self.overlay_image = None
      self.after_overlay = None
      self.overlay_message = None
      # Create cargo bar
      self.cargo_bars = {}
      cargo_bar_pos = (1024 - 120,768-140)
      for i,c in enumerate('rgb'):
         self.cargo_bars[c] = InventoryBar(
            self,(i*CARGO_RECTS['off_full_'+c].width+cargo_bar_pos[0],cargo_bar_pos[1]),self.sheet,self.sounds,
            CARGO_RECTS['off_full_'+c],CARGO_RECTS['off_empty_'+c],CARGO_RECTS['on_full_'+c],CARGO_RECTS['on_empty_'+c],
            value=random.uniform(0,1),
         )
      self.cargo_bars['r'].mutually_exclusive = [self.cargo_bars['g'],self.cargo_bars['b']]
      self.cargo_bars['g'].mutually_exclusive = [self.cargo_bars['b'],self.cargo_bars['r']]
      self.cargo_bars['b'].mutually_exclusive = [self.cargo_bars['r'],self.cargo_bars['g']]
      # Create cargo bar
      self.planet_bars = {}
      planet_bar_offset = (140,-50)
      self.planet_bars['e'] = PlanetBar(
            self,(0,0),np.array(planet_bar_offset),self.sheet,self.sounds,
            PLANET_RECTS['full_e'],PLANET_RECTS['empty_e'],PLANET_RECTS['full_e'],PLANET_RECTS['empty_e'],
            value=random.uniform(0,1),visible=False,responsive=False,
      )
      for i,c in enumerate('rgb'):
         self.planet_bars[c] = PlanetBar(
            self,(0,0),np.array((0.0,25.0*i+25.0)+np.array(planet_bar_offset)),self.sheet,self.sounds,
            PLANET_RECTS['off_full_'+c],PLANET_RECTS['off_empty_'+c],PLANET_RECTS['on_full_'+c],PLANET_RECTS['on_empty_'+c],
            value=random.uniform(0,1),visible=False,
            early_cut=34
         )
      self.planet_gui = [self.planet_bars[k] for k in self.planet_bars]
      
      # Init sound
      self.next_track_in = 1000*40
      self.sequence = deque(['song2','song1'])
   def handle_event(self,event):
      for widget in self.widgets:
         if widget.handle_event(event):
            return
      if self.universe.player:
         if event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.sounds['engine'].play(loops=-1,fade_ms=100)
            self.sounds['engine_start'].play()
            self.universe.player.start_thrusting()
         elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.sounds['engine'].fadeout(100)
            self.sounds['engine_stop'].play()
         if event.type == MOUSEBUTTONDOWN and event.button == 3:
            self.universe.player.start_firing()
         elif event.type == KEYDOWN and event.key == K_SPACE:
            self.sounds['abusalehbreaks'].play()
   def draw(self,screen,camera):
      dirty = [r for r in [widget.draw(screen,camera) for widget in self.widgets] if r]
      if self.overlay_image:
         self.universe.skip_next_tick = True
         screen.blit(self.overlay_image,(0,0))
         rect = self.overlay_image.get_rect()
         if self.overlay_message:
            print(self.overlay_message)
            y = 0
            for line in self.overlay_message.splitlines():
               text = self.res.font['huge'].render(line, True, (255,255,255))
               screen.blit(text,
                  (rect.width//2 - text.get_width()//2,
                   rect.height//2 - text.get_height()//2 + y,)
               )
               y += text.get_height()
         pygame.display.update([rect])
         looping = True
         while looping:
            clock = pygame.time.Clock()
            for event in pygame.event.get():
               if event.type == QUIT:
                   pygame.quit()
                   exit()
               elif event.type == KEYDOWN and event.key == K_ESCAPE:
                   pygame.quit()
                   exit()
               elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                  looping = False
         self.overlay_message = None
         self.overlay_image = None
         if self.after_overlay:
            l = self.after_overlay
            self.after_overlay = None
            l()
         return [rect]
      return dirty
   def tick(self,dt):
      if self.universe.player and self.universe.player.connected_planet:
         for p in self.planet_gui:
            p.visible = True
         player = self.universe.player
         planet = self.universe.player.connected_planet
         model = planet.model
         self.planet_bars['e'].value = min(1.0,max(0.0,(model.tech)))
         self.planet_bars['r'].value = min(1.0,max(0.0,(model.temp/2 + 0.5)))
         self.planet_bars['g'].value = min(1.0,max(0.0,(model.pop)))
         self.planet_bars['b'].value = min(1.0,max(0.0,(model.sea/2 + 0.5)))
         self.planet_bars['e'].pos = planet.pos
         self.planet_bars['r'].pos = planet.pos
         self.planet_bars['g'].pos = planet.pos
         self.planet_bars['b'].pos = planet.pos
         for k in 'rgb':
            if self.planet_bars[k].activated and player.inventory[k] < player.INVENTORY_CAPACITY:
               delta = 0
               if k == 'r':
                  new = max(-1.0,model.temp - dt*player.SUCK_SPEED)
                  delta = new - model.temp
                  model.temp = new
               if k == 'g':
                  new = max(0.0,model.pop - dt*player.SUCK_SPEED/2)
                  delta = new - model.pop
                  model.pop = new
               if k == 'b':
                  new = max(-1.0,model.sea - dt*player.SUCK_SPEED)
                  delta = new - model.sea
                  model.sea = new
               player.inventory[k] = min(player.INVENTORY_CAPACITY, player.inventory[k] - delta)
      else:
         for p in self.planet_gui:
            p.visible = False
            p.activated = False
      if self.universe.player:
         for k in 'rgb':
            if self.cargo_bars[k].activated:
               self.universe.player.selected_slot = k
            self.cargo_bars[k].value = self.universe.player.inventory[k]
      if self.next_track_in <= 0:
         track = self.sequence.pop()
         self.sounds[track].play(fade_ms=3000)
         self.sequence.appendleft(track)
         self.next_track_in = 1000*60 * random.uniform(3+1,3+4)
      else:
         self.next_track_in -= dt
   def overlay(self,name,after=None,message=None):
      if name in self.res.image:
         self.overlay_image = self.res.image[name]
      else:
         self.overlay_image = pygame.image.load(name).convert_alpha()
      self.after_overlay = after
      self.overlay_message = message
      
