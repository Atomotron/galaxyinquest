#!/usr/bin/env python3
import pygame
from pygame.locals import *
import pygame.surfarray as surfarray
import numpy as np

class ColorMap(object):
   SHEET_SIZE = 128
   def __init__(self,sheet,rect):
      assert rect.width == self.SHEET_SIZE
      assert rect.height == self.SHEET_SIZE
      get_rid_of_alpha = ~(0xff << sheet.get_shifts()[3])
      self.colors = np.bitwise_and(surfarray.array2d(sheet.subsurface(rect)),get_rid_of_alpha)

class BiomeMap(object):
   SHEET_SIZE = 160
   def __init__(self,sheet,rect):
      subsurface = sheet.subsurface(rect)
      data = surfarray.array2d(subsurface)
      self.shifts = subsurface.get_shifts()
      self.elevation = self.isolate_and_divide(data,self.shifts[0]).astype(dtype=np.int64,casting="unsafe",copy=False)
      self.temperature = self.isolate_and_divide(data,self.shifts[1]).astype(dtype=np.int64,casting="unsafe",copy=False)
      self.alpha = np.bitwise_and(data,0xff << self.shifts[3]).astype(dtype=np.uint32,casting="unsafe",copy=False)
      self.scratch = data.copy()
      self.altered_temp = self.temperature.astype(dtype=np.int64,casting="unsafe")
      self.altered_elevation = self.elevation.astype(dtype=np.int64,casting="unsafe")
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
         int(x * ColorMap.SHEET_SIZE)
      ))
   def stamp(self,sealevel,templevel,colormap,surface):
      """Writes the planet sprite onto the given surface. Sealevel and templevel have dynamic range from -1.0 to 1.0"""
      sealevel = self.dynamic_range(sealevel)
      templevel = self.dynamic_range(templevel)
      data = surfarray.pixels2d(surface)
      np.copyto(data,self.alpha) # A clean slate
      # Temperature
      np.subtract(self.temperature,templevel,out=self.altered_temp)
      np.clip(self.altered_temp,0,ColorMap.SHEET_SIZE-1,out=self.altered_temp)
      np.subtract(self.elevation,sealevel,out=self.altered_elevation)
      np.clip(self.altered_elevation,0,ColorMap.SHEET_SIZE-1,out=self.altered_elevation)
      self.scratch[:] = colormap.colors[self.altered_temp,self.altered_elevation]
      np.bitwise_or(self.scratch.astype(dtype=np.uint32,casting="unsafe",copy=False),data,out=data)
   def make_surface(self):
      """Makes a surface ready to receive pixel data from stamp."""
      size = self.alpha.shape
      return pygame.Surface(size,SRCALPHA,32)

class Cityscape(object):
   SPRITE_SIZE = (20,50)
   BASE_HEIGHT = 80-3
   NUM_SLOTS = 360//10
   def __init__(self,spritesheet):
      self.spritesheet = spritesheet
      n_sprites = spritesheet.get_width() // self.SPRITE_SIZE[0]
      self.n_techs = spritesheet.get_height() // (self.SPRITE_SIZE[1]*2)
      self.sprite_indices = np.random.randint(0,n_sprites,self.NUM_SLOTS)
      self.pop_bias = self.gen_bias()
      self.tech_bias = self.gen_bias()
     
   def gen_bias(self,maximum=1.0):
      a = np.random.uniform(0,1.0,self.NUM_SLOTS)
      # blur
      b = a.copy()
      b += 0.5*np.roll(b,1)
      b += 0.5*np.roll(b,-1)
      b -= np.min(b) # lowest should be 0
      b *= maximum/np.max(b) # highest should be 1
      return b
      
   def stamp_building(self,surface,theta,index,day,tech):
      rect = pygame.Rect(
         (index*self.SPRITE_SIZE[0],tech*self.SPRITE_SIZE[1]*2 + (0 if day else self.SPRITE_SIZE[1])),
         self.SPRITE_SIZE
         )
      radius = self.BASE_HEIGHT + self.SPRITE_SIZE[1]/2
      dx = (int(radius*np.cos(theta * 0.017453293)),int(radius*np.sin(theta*0.017453293)))
      rotated_image = pygame.transform.rotozoom(self.spritesheet.subsurface(rect),-theta-90,1)
      surface.blit(
         rotated_image,
         (surface.get_width()//2 + dx[0] - rotated_image.get_width()//2,
          surface.get_height()//2 + dx[1] - rotated_image.get_height()//2)
      )
   def stamp(self,surface,day=True,population=0,tech=0):
      dtheta = 360 / self.NUM_SLOTS
      for i,index in enumerate(self.sprite_indices):
         if self.pop_bias[i] >= population:
            continue
         theta = dtheta*i
         tech_index = max(min(int(np.floor(self.tech_bias[i] + tech*(self.n_techs-1))),self.n_techs-1),0)
         self.stamp_building(surface,theta,index,day,tech_index)
         

class PlanetSprite(object):
   CANVAS_SIZE = (256,256)
   def __init__(self,universe,pos,biomemap,colormap,city_spritesheet,shadow,scale=1,omega=0.005,theta=None):
      self.universe = universe
      if universe:
         universe.things.append(self)
         universe.sprites.append(self)
      self.pos = pos
      self.theta = theta or np.random.uniform(0,360)
      self.omega = omega
      self.scale = scale
      self.colormap = colormap
      self.biomemap = biomemap
      self.cityscape = Cityscape(city_spritesheet)
      self.shadow = shadow
      
      self.day_canvas = pygame.Surface(self.CANVAS_SIZE,SRCALPHA,32)
      self.night_canvas = pygame.Surface(self.CANVAS_SIZE,SRCALPHA,32)
      self.planet_sprite = biomemap.make_surface()
      self.set_parameters(0,0,0,0)
   def tick(self,dt):
      self.theta += self.omega * dt
   def blit_centered(self,dst,src,src_rect):
      dst.blit(src,(dst.get_width()//2 - src_rect.width//2,dst.get_height()//2 - src_rect.height//2),src_rect)
   def set_parameters(self,sealevel,templevel,population,tech):
      self.biomemap.stamp(sealevel,templevel,self.colormap,self.planet_sprite)
      # Day
      self.day_canvas.fill((0,0,0,0))
      self.cityscape.stamp(self.day_canvas,True,population,tech)
      self.blit_centered(self.day_canvas,self.planet_sprite,self.planet_sprite.get_rect())
      # Night
      self.night_canvas.fill((0,0,0,0))
      self.cityscape.stamp(self.night_canvas,False,population,tech)
      self.blit_centered(self.night_canvas,self.planet_sprite,self.planet_sprite.get_rect())
   def draw(self,surface):
      day = pygame.transform.rotozoom(self.day_canvas,self.theta,self.scale)
      night = pygame.transform.rotozoom(self.night_canvas,self.theta,self.scale)
      r = surface.blit(
         day,
         (self.pos[0],self.pos[1] - night.get_height()//2),
         pygame.Rect(day.get_width()//2,0,day.get_width()//2,day.get_height()) 
      )
      r = r.union(surface.blit(
         night,
         (self.pos[0] - night.get_width()//2,self.pos[1] - night.get_height()//2),
         pygame.Rect(0,0,day.get_width()//2,day.get_height()) 
      ))
      return r.union(surface.blit(
         self.shadow,
         (self.pos[0] - self.shadow.get_width()//2,self.pos[1] - self.shadow.get_height()//2)
      ))

class PlanetSpriteFactory(object):
   def __init__(self,color_sheet,biomes_sheet,city_spritesheet,shadow):
      self.biome_maps = [
         BiomeMap(biomes_sheet,pygame.Rect(i*BiomeMap.SHEET_SIZE,0,BiomeMap.SHEET_SIZE,BiomeMap.SHEET_SIZE))
         for i in range(0,biomes_sheet.get_width()//BiomeMap.SHEET_SIZE)
      ]
      self.color_maps = [
         ColorMap(color_sheet,pygame.Rect(i*ColorMap.SHEET_SIZE,0,ColorMap.SHEET_SIZE,ColorMap.SHEET_SIZE))
         for i in range(0,color_sheet.get_width()//ColorMap.SHEET_SIZE)
      ]
      self.city_spritesheet = city_spritesheet
      self.shadow = shadow
   def make_planet(self,universe,pos,bindex=None,cindex=None):
      bindex = bindex or np.random.randint(1,len(self.biome_maps)) # start at 1 because 0 is my thing
      cindex = cindex or np.random.randint(0,len(self.color_maps))
      print("Making planet with",bindex,cindex)
      return PlanetSprite(
         universe,
         pos,
         self.biome_maps[bindex%len(self.biome_maps)],
         self.color_maps[cindex%len(self.color_maps)],
         self.city_spritesheet,
         self.shadow
      )

if __name__ == "__main__":
   pygame.init()
   screen = pygame.display.set_mode((256,256))
   clock = pygame.time.Clock()
   def load(tfile,pfile,cindex,bindex):
      color_sheet = pygame.image.load(tfile).convert_alpha()
      biomes_sheet = pygame.image.load(pfile).convert_alpha()
      shadow = pygame.image.load("img/shadow_outline.png").convert_alpha()
      city = pygame.image.load("img/cityscapes.png").convert_alpha()
      cmap = ColorMap(color_sheet,pygame.Rect(cindex*ColorMap.SHEET_SIZE,0,ColorMap.SHEET_SIZE,ColorMap.SHEET_SIZE))
      bmap = BiomeMap(biomes_sheet,pygame.Rect(bindex*160,0,160,160))
      psprite = PlanetSprite(None,(128,128),bmap,cmap,city,shadow)
      return psprite
   psprite = load("img/terrain.png","img/planet.png",0,1)
   cindex = 0
   bindex = 1
   report = "Colormap {}, biome map {}".format(cindex,bindex)
   font = pygame.font.Font('img/LiberationSans-Regular.ttf', 12)  
   text = font.render(report, True, (255,255,255))
   population = 0.5
   tech = 0.5
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
            elif event.key == K_SPACE:
               psprite = load("img/terrain.png","img/planet.png",cindex,bindex)
            elif event.key == K_UP:
               cindex = (cindex+1) % 16
               psprite = load("img/terrain.png","img/planet.png",cindex,bindex)
            elif event.key == K_DOWN:
               cindex = (cindex-1) % 16
               psprite = load("img/terrain.png","img/planet.png",cindex,bindex)
            elif event.key == K_LEFT:
               bindex = (bindex-1) % 5
               psprite = load("img/terrain.png","img/planet.png",cindex,bindex)
            elif event.key == K_RIGHT:
               bindex = (bindex+1) % 5
               psprite = load("img/terrain.png","img/planet.png",cindex,bindex)
            report = "Colormap {}, biome map {}".format(cindex,bindex)
            text = font.render(report, True, (255,255,255))
      pressed = pygame.key.get_pressed()
      if pressed[K_w]:
         population += 0.001*dt
      if pressed[K_s]:
         population -= 0.001*dt
      if pressed[K_a]:
         tech -= 0.001*dt
      if pressed[K_d]:
         tech += 0.001*dt
      psprite.tick(dt)
      sealevel,templevel = pygame.mouse.get_pos()
      templevel = (templevel - 128) / 128
      sealevel = (sealevel - 128) / 128
      screen.fill((0,0,0))
      psprite.set_parameters(sealevel,templevel,population,tech) 
      psprite.draw(screen)
      pygame.draw.circle(screen,(255,0,255),(int(population*256),int(tech*256)),4)
      screen.blit(text,(0,0))
      pygame.display.flip()
   
