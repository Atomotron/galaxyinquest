#!/usr/bin/env python

class Button(object):
   def __init__(self,pos,sheet,on_rect,off_rect,behavior='',sound=None,mutually_exclusive=[]):
      self.pos = pos
      self.sheet = sheet
      self.on_rect = on_rect
      self.off_rect = off_rect
      self.sound = sound
      self.mutually_exclusive = mutually_exclusive
      self.activated = False
   def interact(self,event):
      pass
