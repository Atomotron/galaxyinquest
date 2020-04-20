#!/usr/bin/env python
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
   def __init__(self,ui,pos,sheet,off_full,off_empty,on_full,on_empty,
   value=0.5,sound=None,vertical=True,visible=True,sticky=True,responsive=True,follow_camera=None,
   early_cut=0,mutually_exclusive=[]):
      self.ui = ui
      self.pos = pos
      self.sheet = sheet
      self.off_full = off_full
      self.off_empty = off_empty
      self.on_full = on_full
      self.on_empty = on_empty
      self.vertical = vertical
      self.value = value
      self.responsive = responsive
      self.early_cut = early_cut # for when 100% full corresponds to a slice short of 100% of the full image
      self.sound = sound
      self.mutually_exclusive = mutually_exclusive
      self.sticky = sticky
      self.activated = False
      self.follow_camera = follow_camera
      self.visible = visible
      ui.widgets.append(self)
      
   @property
   def full_sprite(self):
      return self.sheet.subsurface(self.on_full if self.activated else self.off_full)
   @property
   def empty_sprite(self):
      return self.sheet.subsurface(self.on_empty if self.activated else self.off_empty)      
   
   def contains(self,pos):
      if self.follow_camera is None:
         rel_pos = (pos[0]-self.pos[0],pos[1]-self.pos[1])
      else:
         rel_pos = vfloor(self.ui.universe.uncam(vfloat(pos)) - self.pos-self.follow_camera)
      sprite = self.full_sprite
      if sprite.get_rect().collidepoint(rel_pos):
         if sprite.get_at(rel_pos)[3] > self.ALPHA_CUTOFF:
            return True
      return False
      
   def handle_event(self,event):
      '''Returns true if we want to consume the event.'''
      if not self.responsive or not self.visible:
         return False
      if (event.type == MOUSEBUTTONUP or event.type == MOUSEBUTTONDOWN) and event.button == 1:
         if self.contains(event.pos):
            if event.type == MOUSEBUTTONDOWN and not self.activated:
               self.activated = True
               if self.sound: self.sound.play()
               for me in self.mutually_exclusive:
                  me.activated = False
            elif event.type == MOUSEBUTTONUP and self.activated and not self.sticky:
               self.activated = False
            return True
      return False
      
   def draw(self,surface,camera):
      if not self.visible:
         return None
      if self.follow_camera is None:
         pos = self.pos
      else:
         pos = vfloor(camera.cam(self.pos) + self.follow_camera)
      empty_sprite = self.empty_sprite
      full_sprite = self.full_sprite
      if self.vertical:
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
      else:
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
            

class UI(object):
   def __init__(self,universe,sounds,sheet):
      self.sounds = sounds
      self.universe = universe
      self.universe.ui = self
      self.sheet = sheet
      self.widgets = []
      # Create cargo bar
      self.cargo_bars = {}
      cargo_bar_pos = (1024 - 120,768-140)
      for i,c in enumerate('rgb'):
         self.cargo_bars[c] = BarButton(
            self,(i*CARGO_RECTS['off_full_'+c].width+cargo_bar_pos[0],cargo_bar_pos[1]),sheet,
            CARGO_RECTS['off_full_'+c],CARGO_RECTS['off_empty_'+c],CARGO_RECTS['on_full_'+c],CARGO_RECTS['on_empty_'+c],
            value=random.uniform(0,1),sound=sounds['select'],
         )
      self.cargo_bars['r'].mutually_exclusive = [self.cargo_bars['g'],self.cargo_bars['b']]
      self.cargo_bars['g'].mutually_exclusive = [self.cargo_bars['b'],self.cargo_bars['r']]
      self.cargo_bars['b'].mutually_exclusive = [self.cargo_bars['r'],self.cargo_bars['g']]
      # Create cargo bar
      self.planet_bars = {}
      planet_bar_offset = (140,-50)
      self.planet_bars['e'] = BarButton(
            self,(0,0),sheet,
            PLANET_RECTS['full_e'],PLANET_RECTS['empty_e'],PLANET_RECTS['full_e'],PLANET_RECTS['empty_e'],
            value=random.uniform(0,1),sound=None,vertical=False,visible=False,sticky=False,responsive=False,follow_camera = np.array(planet_bar_offset),
      )
      for i,c in enumerate('rgb'):
         self.planet_bars[c] = BarButton(
            self,(0,0),sheet,
            PLANET_RECTS['off_full_'+c],PLANET_RECTS['off_empty_'+c],PLANET_RECTS['on_full_'+c],PLANET_RECTS['on_empty_'+c],
            value=random.uniform(0,1),sound=sounds['select'],vertical=False,visible=False,sticky=False,follow_camera = np.array((0.0,25.0*i+25.0)+np.array(planet_bar_offset)),
            responsive = True,early_cut=34
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
         elif event.type == KEYDOWN and event.key == K_SPACE:
            self.sounds['abusalehbreaks'].play()
   def draw(self,screen,camera):
      return [r for r in [widget.draw(screen,camera) for widget in self.widgets] if r]
   def tick(self,dt):
      if self.universe.player and self.universe.player.connected_planet:
         for p in self.planet_gui:
            p.visible = True
         self.planet_bars['e'].value = self.universe.player.connected_planet.model.tech
         self.planet_bars['r'].value = self.universe.player.connected_planet.model.temp/2 + 0.5
         self.planet_bars['g'].value = self.universe.player.connected_planet.model.pop
         self.planet_bars['b'].value = self.universe.player.connected_planet.model.sea/2 + 0.5
         self.planet_bars['e'].pos = self.universe.player.connected_planet.pos
         self.planet_bars['r'].pos = self.universe.player.connected_planet.pos
         self.planet_bars['g'].pos = self.universe.player.connected_planet.pos
         self.planet_bars['b'].pos = self.universe.player.connected_planet.pos
      else:
         for p in self.planet_gui:
            p.visible = False
      if self.next_track_in <= 0:
         track = self.sequence.pop()
         self.sounds[track].play(fade_ms=3000)
         self.sequence.appendleft(track)
         self.next_track_in = 1000*60 * 4
      else:
         self.next_track_in -= dt
      
