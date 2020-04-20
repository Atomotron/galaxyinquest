#!/usr/bin/env python
import pygame
import random
from sys import exit
from pygame.locals import *

class Resources(object):
   LOADING_BAR_HEIGHT = 32
   FONT_HEIGHT = 32
   def __init__(self,screen,images,sounds,fonts):
      self.image_names = images
      self.sound_names = sounds
      self.font_names = fonts
      self.sound = {}
      self.image = {}
      self.font = {}
      # Take over mainloop while loading
      to_load = [(name,sounds[name],'sound') for name in sounds]
      to_load += [(name,images[name],'image') for name in images]
      to_load += [(name,fonts[name],'font') for name in fonts]
      loading_screen = pygame.image.load("img/loadingscreen.png")
      font = pygame.font.Font('fonts/LiberationSans-Regular.ttf', self.FONT_HEIGHT)
      screen.blit(loading_screen,(0,0))
      
      # Skully: use pygame to load loading screen image assets here.
      # loading_screen = pygame.image.load(...)
      for i,(name,filename,kind) in enumerate(to_load):
         # We have to check the events or else the OS will crash the game.
         for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()
         # Skully: replace this for whatever you'd like to use to draw loading progress to the screen
         # progress ranges from 0.0 to slightly less than 1.0
         # we never want to show a full loading bar because when it's full, we move on and quit loading!
         progress = i / (len(to_load))
         text = font.render("Loading "+str(filename), True, (233,83,50))
         text_pos = (0,screen.get_height() - self.FONT_HEIGHT - self.LOADING_BAR_HEIGHT)
         screen.blit(text,text_pos)
         pygame.draw.rect(
            screen,
            (233,83,50),
            pygame.Rect(0,screen.get_height() - self.LOADING_BAR_HEIGHT,int(progress*screen.get_width()),self.LOADING_BAR_HEIGHT)
         )
         pygame.display.update(screen.get_rect())
         pygame.draw.rect(
            screen,
            (0,0,0),
            text.get_rect().move(text_pos)
         )
         # actually load the resource
         if kind == 'sound':
            self.sound[name] = pygame.mixer.Sound(filename)
         elif kind == 'image':
            self.image[name] = pygame.image.load(filename).convert_alpha()
         elif kind == 'font':
            self.font[name] = pygame.font.Font(filename[0],filename[1])
