#!/usr/bin/env python3
import pygame
from pygame.locals import *
import pygame.surfarray as surfarray
import numpy as np

screen = pygame.display.set_mode((256,256))

def load(tfile,pfile):
   terrain = pygame.image.load(tfile).convert_alpha()
   biomes = pygame.image.load(pfile).convert_alpha()
   terrain_map = surfarray.array3d(terrain)
   biome_array = surfarray.array2d(biomes)
   # Disassemble
   shifts = biomes.get_shifts()
   r = np.bitwise_and(np.right_shift(biome_array,shifts[0]),0xff)
   g = np.bitwise_and(np.right_shift(biome_array,shifts[1]),0xff)
   b = np.bitwise_and(np.right_shift(biome_array,shifts[2]),0xff)
   a = np.bitwise_and(np.right_shift(biome_array,shifts[3]),0xff)
   print(r[0,0],b[0,0],g[0,0],a[0,0],biome_array[128,128])
   planet_surface = pygame.Surface(biomes.get_rect().size,SRCALPHA,32)
   return terrain_map,planet_surface,a,g,r
   
def update(templevel,sealevel,temperatures,elevations,alpha,terrain_map,planet_surface):
   shifts = planet_surface.get_shifts()
   planet_array = pygame.surfarray.pixels2d(planet_surface)
   colors = terrain_map[np.clip(temperatures+templevel,0,127),np.clip(elevations+sealevel,0,127)]
   a = np.array(colors[:,:,0],dtype=np.uint32) << shifts[0]
   b = a | (np.array(colors[:,:,1],dtype=np.uint32) << shifts[1])
   c = b | (np.array(colors[:,:,2],dtype=np.uint32) << shifts[2])
   d = c | (np.array(alpha,dtype=np.uint32) << shifts[3])
   planet_array[:] = np.array(d,dtype=np.uint32)

terrain_map,planet_surface,alpha,temperatures,elevations = load("terrain.png","planet.png")

#merge = terrain_pixels[base[:,:,0],base[:,:,1]]
#target = pygame.surfarray.make_surface(merge)
#print(planet_array,planet_alpha)
#print(merge,merge.shape)
clock = pygame.time.Clock()

while True:
   dt = clock.tick(30)
   for event in pygame.event.get():
      if event.type == QUIT:
         pygame.quit()
         exit()
      elif event.type == KEYDOWN:
         if event.key == K_ESCAPE:
            pygame.quit()
            exit()
         if event.key == K_SPACE:
            terrain_map,planet_surface,alpha,temperatures,elevations = load("terrain.png","planet.png")
   templevel,sealevel = pygame.mouse.get_pos()
   templevel = templevel - 128
   sealevel = sealevel - 128
   screen.fill((0,0,0))
   update(templevel,sealevel,temperatures,elevations,alpha,terrain_map,planet_surface)
   screen.blit(planet_surface,(0,0))
   pygame.display.flip()
   
