#!/usr/bin/env python3
import pygame
from pygame.locals import *
import pygame.surfarray as surfarray
import numpy as np

screen = pygame.display.set_mode((128,128))

terrain = pygame.image.load("terrain.png")
planet = pygame.image.load("planet.png")
terrain_pixels = surfarray.pixels3d(terrain)
planet_array = surfarray.pixels3d(planet)[:,:,:2]

base = planet_array // 2
print(base[:,:,1])
merge = terrain_pixels[base[:,:,0],base[:,:,1]]
target = pygame.surfarray.make_surface(merge)
print(merge)
#print(merge,merge.shape)
clock = pygame.time.Clock()
while True:
   dt = clock.tick(30)
   for event in pygame.event.get():
      if event.type == QUIT:
         pygame.quit()
         exit()
      elif event.type == KEYDOWN and event.key == K_ESCAPE:
         pygame.quit()
         exit()
   
   templevel,sealevel = pygame.mouse.get_pos()
   templevel = max(0,min(127,templevel))
   sealevel = max(0,min(127,sealevel))
   screen.fill((0,0,0))
   planet = np.clip(base - np.array([templevel,sealevel]),0,127)
   surfarray.blit_array(target, terrain_pixels[planet[:,:,0],planet[:,:,1]])
   screen.blit(target,(0,0))
   pygame.display.flip()
   
