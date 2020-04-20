#!/usr/bin/env python
from pygame.locals import *
from pygame import Rect
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

class BarButton(object):
   '''Combines a bar and a button in to one big honkin' class.'''
   ALPHA_CUTOFF = 0 # A pixel on the button sprite must have more than this much alpha to receive clicks
   def __init__(self,ui,pos,sheet,off_full,off_empty,on_full,on_empty,
   value=0.5,sound=None,vertical=True,visible=True,sticky=True,responsive=True,
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
      self.visible = visible
      ui.widgets.append(self)
      
   @property
   def full_sprite(self):
      return self.sheet.subsurface(self.on_full if self.activated else self.off_full)
   @property
   def empty_sprite(self):
      return self.sheet.subsurface(self.on_empty if self.activated else self.off_empty)      
   
   def contains(self,pos):
      rel_pos = (pos[0]-self.pos[0],pos[1]-self.pos[1])
      sprite = self.full_sprite
      if sprite.get_rect().collidepoint(rel_pos):
         if sprite.get_at(rel_pos)[3] > self.ALPHA_CUTOFF:
            return True
      return False
      
   def handle_event(self,event):
      '''Returns true if we want to consume the event.'''
      if not self.responsive:
         return
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
         return
      empty_sprite = self.empty_sprite
      full_sprite = self.full_sprite
      if self.vertical:
         cut = int( (1-self.value)*(empty_sprite.get_height()-self.early_cut) )
         empty_pos = self.pos
         empty_rect = Rect((0,0),
            (empty_sprite.get_width(),
            cut)
         )
         full_pos = (
            self.pos[0],
            self.pos[1] + cut
         )
         full_rect = Rect((0,cut),
            (full_sprite.get_width(),
             full_sprite.get_height() - cut)
         )
      else:
         cut = int( self.value*(full_sprite.get_width()-self.early_cut) )
         full_pos = self.pos
         full_rect = Rect((0,0),
            (cut,
             full_sprite.get_height())
         )
         empty_pos = (
            self.pos[0] + cut,
            self.pos[1]
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
      return [widget.draw(screen,camera) for widget in self.widgets]
   def tick(self,dt):
      if self.next_track_in <= 0:
         track = self.sequence.pop()
         self.sounds[track].play(fade_ms=3000)
         self.sequence.appendleft(track)
         self.next_track_in = 1000*60 * 4
      else:
         self.next_track_in -= dt
      
