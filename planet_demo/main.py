#!/usr/bin/env python3
import pygame
from pygame.locals import *
import pygame.surfarray as surfarray
import numpy as np

screen = pygame.display.set_mode((256,256))

class ColorMap(object):
   SHEET_SIZE = 128
   def __init__(self,sheet,rect):
      assert rect.width == self.SHEET_SIZE
      assert rect.height == self.SHEET_SIZE
      get_rid_of_alpha = ~(0xff << sheet.get_shifts()[3])
      self.colors = np.bitwise_and(subsurface.array2d(sheet.subsurface(rect)),get_rid_of_alpha)

class BiomeMap(object):
   def __init__(self,sheet,rect):
      subsurface = sheet.subsurface(rect)
      data = surfarray.array2d(subsurface)
      self.shifts = subsurface.get_shifts()
      self.elevation = self.isolate_and_divide(data,self.shifts[0])
      self.temperature = self.isolate_and_divide(data,self.shifts[1])
      self.alpha = np.bitwise_and(data,0xff << self.shifts[3])
      self.scratch = data.copy()
      self.altered_temp = self.temperature.copy()
      self.altered_elevation = self.elevation.copy()
   def isolate_and_divide(self,array,shift):
      """Isolates a byte (setting other bytes to zero), and divides it by SHEET_SIZE_FRACTION"""
      output = array.copy()
      np.right_shift(output,shift,out=output)
      np.bitwise_and(output,0xff,out=output)
      np.floor_divide(output,256//ColorMap.SHEET_SIZE,out=output)
      return output
      #np.bitwise_and(np.right_shift(subsurface,shifts[0]),0xff)
   def dynamic_range(self,x):
      """Scale and clamp a floating point value between -1.0 and 1.0 to be between -SHEET_SIZE and SHEET_SIZE"""
      return min(ColorMap.SHEET_SIZE,max(-ColorMap.SHEET_SIZE, #clamp
         int(x * 256 * SHEET_SIZE_FRACTION)
      ))
   def stamp(self,sealevel,templevel,colormap,surface):
      """Writes the planet sprite onto the given surface. Sealevel and templevel have dynamic range from -1.0 to 1.0"""
      sealevel = dynamic_range(sealevel)
      templevel = dynamic_range(templevel)
      data = surfarray.pixels2d(surface)
      np.copyto(data,self.alpha) # A clean slate
      # Temperature
      np.sub(self.temperature,templevel,out=self.altered_temp)
      np.clip(self.altered_temp,0,ColorMap.SHEET_SIZE,out=self.altered_temp)
      np.sub(self.elevation,sealevel,out=self.altered_elevation)
      np.clip(self.altered_elevation,0,ColorMap.SHEET_SIZE,out=self.altered_elevation)
      self.scratch[:] = colormap.colors[self.altered_elevation,self.altered_temp]
      np.bitwise_or(self.scratch,data,out=data)
   def make_surface(self):
      """Makes a surface ready to receive pixel data from stamp."""
      size = self.alpha.shape
      return pygame.Surface(size,SRCALPHA,32)
      
class PlanetSprite(object):
   CANVAS_SIZE = (256,256)
   def __init__(self,pos,biomemap,colormap,scale=1,omega=1,theta=0):
      self.pos = pos
      self.theta = theta
      self.omega = omega
      self.scale = scale
      self.colormap = colormap
      self.biomemap = biomemap
      
      self.day_canvas = pygame.Surface(self.CANVAS_SIZE,SRCALPHA,32)
      self.night_canvas = pygame.Surface(self.CANVAS_SIZE,SRCALPHA,32)
      self.planet_sprite = biomemap.make_surface()
   def tick(self,dt):
      self.theta += self.omega * dt
   def blit_centered(self,dst,src,src_rect):
      dst.blit(src,(dst.get_width()//2 - src_rect.width//2,dst.get_height()//2 - src_rect.height//2),src_rect)
   def set_parameters(self,sealevel,templevel):
      self.biomemap.stamp(sealevel,templevel,self.colormap,self.planet_sprite)
      # Day
      self.blit_centered(self.day_canvas,self.planet_sprite,self.planet_sprite.get_rect())
      # Night
      self.night_canvas.fill((255,0,0))
      self.blit_centered(self.night_canvas,self.planet_sprite,self.planet_sprite.get_rect())
   def draw(self,surface):
      day = pygame.transform.rotozoom(self.day_canvas,self.theta,self.scale)
      night = pygame.transform.rotozoom(self.night_canvas,self.theta,self.scale)
      day_pos = (
         self.pos[0] - day.get_width()//2,
         self.pos[1] - day.get_height()//2,
      )
      surface.blit(day,day_pos,pygame.Rect(0,0,day.get_width()//2,day.get_height()) )
      night_pos = (
         self.pos[0],
         self.pos[1] - night.get_height()//2,
      )
      surface.blit(night,night_pos,pygame.Rect(day.get_width()//2,0,day.get_width()//2,day.get_height()) )

def load(tfile,pfile):
   terrain = pygame.image.load(tfile).convert_alpha()
   biomes = pygame.image.load(pfile).convert_alpha()
   BiomeMap(biomes,biomes.get_rect())
   terrain_map = surfarray.array3d(terrain)
   biome_array = surfarray.array2d(biomes)
   # Disassemble
   shifts = biomes.get_shifts()
   r = np.bitwise_and(np.right_shift(biome_array,shifts[0]),0xff) // 2
   g = np.bitwise_and(np.right_shift(biome_array,shifts[1]),0xff) // 2
   b = np.bitwise_and(np.right_shift(biome_array,shifts[2]),0xff) // 2
   a = np.bitwise_and(np.right_shift(biome_array,shifts[3]),0xff)
   print(r[0,0],b[0,0],g[0,0],a[0,0],biome_array[128,128])
   planet_surface = pygame.Surface(biomes.get_rect().size,SRCALPHA,32)
   return terrain_map,planet_surface,a,g,r
   
def update(templevel,sealevel,temperatures,elevations,alpha,terrain_map,planet_surface):
   shifts = planet_surface.get_shifts()
   planet_array = pygame.surfarray.pixels2d(planet_surface)
   colors = terrain_map[np.clip(temperatures-templevel,0,127),np.clip(elevations-sealevel,0,127)]
   a = np.array(colors[:,:,0],dtype=np.uint32) << shifts[0]
   b = a | (np.array(colors[:,:,1],dtype=np.uint32) << shifts[1])
   c = b | (np.array(colors[:,:,2],dtype=np.uint32) << shifts[2])
   d = c | (np.array(alpha,dtype=np.uint32) << shifts[3])
   planet_array[:] = np.array(d,dtype=np.uint32)

terrain_map,planet_surface,alpha,temperatures,elevations = load("terrain.png","planet.png")
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
   sealevel,templevel = pygame.mouse.get_pos()
   templevel = templevel - 128
   sealevel = sealevel - 128
   screen.fill((0,0,0))
   update(templevel,sealevel,temperatures,elevations,alpha,terrain_map,planet_surface)
   screen.blit(planet_surface,(0,0))
   pygame.display.flip()
   
