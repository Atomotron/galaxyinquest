#!/usr/bin/env python
from pygame.locals import *
from pygame import Rect

from util import vfloat,vfloor

class Button(object):
   BUTTON_RECTS = {

   }
   ALPHA_CUTOFF = 16 # A pixel on the button sprite must have at least this much alpha to receive clicks
   def __init__(self,pos,sheet,on,off,visible=True,sticky=True,sound=None,mutually_exclusive=[]):
      self.pos = pos
      self.sheet = sheet
      self.on = on
      self.off = off
      self.sound = sound
      self.mutually_exclusive = mutually_exclusive
      self.sticky = sticky
      self.activated = False
      self.visible = visible
      
   @property
   def sprite(self):
      return self.sheet.subsurface(self.BUTTON_RECTS[self.on] if self.activated else self.BUTTON_RECTS[self.off])
      
   def contains(self,pos):
      rel_pos = (pos[0]-self.pos[0],pos[1]-self.pos[1])
      sprite = self.sprite
      if sprite.get_rect().collidepoint(rel_pos):
         if sprite.get_at(rel_pos)[3] > self.ALPHA_CUTOFF:
            return True
      return False
      
   def handle_event(self,event):
      '''Returns true if we want to consume the event.'''
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
      
   def draw(self,screen,camera):
      if self.visible:
         return screen.blit(self.sprite,self.pos)

class UI(object):
   CARGO_BUTTONS = [
      ('red_on','red_off',(0,0))
   ]
   def __init__(self,universe,sounds,button_sheet=None):
      self.buttons = []
      self.sounds = sounds
      self.button_sheet = button_sheet
   def handle_event(self,event):
      for button in self.buttons:
         if button.handle_event(event):
            return
      if event.type == MOUSEBUTTONDOWN and event.button == 1:
         self.sounds['engine'].play(loops=-1,fade_ms=100)
         self.sounds['engine_start'].play()
      elif event.type == MOUSEBUTTONUP and event.button == 1:
         self.sounds['engine'].fadeout(100)
         self.sounds['engine_stop'].play()
      elif event.type == KEYDOWN and event.key == K_SPACE:
         self.sounds['abusalehbreaks'].play()
