#!/usr/bin/env python3
import pygame
from pygame.locals import *
import pygame.surfarray as surfarray
import numpy as np
import random
from util import vfloor,vfloat

NAME_PREFIXES = [
   'Al','Aub','Bor','Bro','Cor','Co','Di','Do','Ea','Ear','Ee','For','Fre','Gor',
   'Gon','Hi','Hu','Hal','Io','Incan','Ju','Jov','Kor','Kan','Li','Lu','Moo',
   'Mer','Mar','Nige','Nitro','Nep','Oor','Opu','Plu','Poo','Quo','Qua','Qui',
   'Rig','Roto','Ron','Sat','Su','Tib','Tro','Uvo','Ura','Vex','Val','Ven',
   'Woo','Wig','Wab','Xi','Xu','Xeno','Zet','Zon','Zorb','Zran'  
]
NAME_MIDDLES = [
   'oo','max','aur','ax','ain','ep','ephre','mig','ing','aul','too','min','ph','quo','qua','li',
   'lu','moo','mar','ige',
]
NAME_ENDINGS = [
   'is','ars','une','nus','toh','tune','th','-alpha',
]
def generate_name():
   middle_count = random.choice([0,0,0,0,1,1,1,1,2])
   middle = ""
   for i in range(middle_count):
      middle += random.choice(NAME_MIDDLES)
   return random.choice(NAME_PREFIXES)+middle+random.choice(NAME_ENDINGS)+'-'+str(random.randrange(0,100))+random.choice('ABCDGXZ')

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
   def dynamic_range(self,x):
      """Scale and clamp a floating point value between -1.0 and 1.0 to be between -SHEET_SIZE and SHEET_SIZE"""
      return min(ColorMap.SHEET_SIZE,max(-ColorMap.SHEET_SIZE, #clamp
         int(x * ColorMap.SHEET_SIZE)
      ))
   def stamp(self,sealevel,templevel,colormap,surface):
      """Writes the planet sprite onto the given surface. Sealevel and templevel have dynamic range from -1.0 to 1.0"""
      sealevel = self.dynamic_range(sealevel)
      templevel = self.dynamic_range(-templevel) # invert templevel
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

class Atmosphere(object):
   def __init__(self,colormap,atmosphere,enlightened_atmosphere):
      self.colormap = surfarray.array3d(colormap)
      self.atmosphere = atmosphere
      self.enlightened_atmosphere = enlightened_atmosphere
      self.mult_canvas = pygame.Surface(atmosphere.get_size(),SRCALPHA,32)
      self.canvas = pygame.Surface(atmosphere.get_size(),SRCALPHA,32)
   def draw_at(self,surface,pos,scale,sealevel,templevel,tech):
      color = self.colormap[
         min(self.colormap.shape[0]-1,max(0,int((templevel/2+0.5)*self.colormap.shape[0]))),
         min(self.colormap.shape[0]-1,max(0,int((sealevel/2+0.5)*self.colormap.shape[1])))
      ]
      self.mult_canvas.fill(color)
      self.canvas.fill((0,0,0,0))
      self.canvas.blit(self.atmosphere,(0,0))
      self.canvas.blit(self.mult_canvas,(0,0),special_flags=BLEND_RGBA_MULT)
      if tech >= 1.0:
         self.canvas.blit(self.enligtened_atmosphere,(0,0))
      scaled = pygame.transform.rotozoom(self.canvas,0,scale)
      center_pos = (pos[0]-scaled.get_width()//2,pos[1]-scaled.get_height()//2)
      return surface.blit(scaled,center_pos)

class PlanetSprite(object):
   CANVAS_SIZE = (256,256)
   ROTATION_SPEED = 0.0002
   def __init__(self,universe,pos,biomemap,colormap,city_spritesheet,atmosphere,clouds):
      self.universe = universe
      if universe:
         universe.things.append(self)
         universe.sprites.append(self)
      self.pos = vfloat(pos)
      self.theta = np.random.uniform(0,360)
      self.cloud_theta = np.random.uniform(0,360)
      self.omega = np.random.uniform(-1.0,1.0)*self.ROTATION_SPEED
      self.cloud_omega = np.random.uniform(-1.0,1.0)*self.ROTATION_SPEED + self.omega
      self.scale = 1
      self.colormap = colormap
      self.biomemap = biomemap
      self.cityscape = Cityscape(city_spritesheet)
      self.atmosphere = atmosphere
      self.clouds = clouds
      self.day_canvas = pygame.Surface(self.CANVAS_SIZE,SRCALPHA,32)
      self.night_canvas = pygame.Surface(self.CANVAS_SIZE,SRCALPHA,32)
      self.planet_sprite = biomemap.make_surface()
      self.parameters = [0,0,0,0]
      self.update()
   def tick(self,dt):
      self.theta += self.omega * dt
      self.cloud_theta += self.cloud_omega * dt
   def blit_centered(self,dst,src,src_rect):
      dst.blit(src,(dst.get_width()//2 - src_rect.width//2,dst.get_height()//2 - src_rect.height//2),src_rect)
   def set_parameters(self,sealevel,templevel,population,tech):
      self.parameters = [sealevel,templevel,population,tech]
   def update(self):
      sealevel,templevel,population,tech = self.parameters
      '''Update sprite to match parameters'''
      self.biomemap.stamp(sealevel,templevel,self.colormap,self.planet_sprite)
      # Day
      self.day_canvas.fill((0,0,0,0))
      self.cityscape.stamp(self.day_canvas,True,population,tech)
      self.blit_centered(self.day_canvas,self.planet_sprite,self.planet_sprite.get_rect())
      # Night
      self.night_canvas.fill((0,0,0,0))
      self.cityscape.stamp(self.night_canvas,False,population,tech)
      self.blit_centered(self.night_canvas,self.planet_sprite,self.planet_sprite.get_rect())
   def draw(self,surface,camera):
      angle = self.theta * 180 / np.pi
      scale = camera.zoom*self.scale
      pos = vfloor(camera.cam(self.pos))
      if pos[0] < -self.CANVAS_SIZE[0]//2 or \
         pos[0] > surface.get_width()+self.CANVAS_SIZE[0]//2 or \
         pos[1] < -self.CANVAS_SIZE[1]//2 or \
         pos[1] > surface.get_height()+self.CANVAS_SIZE[1]//2:
         return None         
      day = pygame.transform.rotozoom(self.day_canvas,angle,scale)
      night = pygame.transform.rotozoom(self.night_canvas,angle,scale)
      clouds = pygame.transform.rotozoom(self.clouds,self.cloud_theta*180/np.pi,scale)
      r = self.atmosphere.draw_at(surface,pos,scale,self.parameters[0],self.parameters[1],self.parameters[2])
      r = r.union(surface.blit(
         clouds,
         (pos[0] - clouds.get_width()//2,pos[1] - clouds.get_height()//2)
      ))
      r = r.union(surface.blit(
         day,
         (pos[0],pos[1] - night.get_height()//2),
         pygame.Rect(day.get_width()//2,0,day.get_width()//2,day.get_height()) 
      ))
      r = r.union(surface.blit(
         night,
         (pos[0] - night.get_width()//2,pos[1] - night.get_height()//2),
         pygame.Rect(0,0,night.get_width()//2,night.get_height()) 
      ))
      return r.union(surface.blit(
         camera.scaled_shadow,
         (pos[0] - camera.scaled_shadow.get_width()//2,pos[1] - camera.scaled_shadow.get_height()//2)
      ))

class PlanetSpriteFactory(object):
   def __init__(self,res):
      self.biome_maps = [
         BiomeMap(res.image['biomemaps'],pygame.Rect(i*BiomeMap.SHEET_SIZE,0,BiomeMap.SHEET_SIZE,BiomeMap.SHEET_SIZE))
         for i in range(0,res.image['biomemaps'].get_width()//BiomeMap.SHEET_SIZE)
      ]
      self.color_maps = [
         ColorMap(res.image['colormaps'],pygame.Rect(i*ColorMap.SHEET_SIZE,0,ColorMap.SHEET_SIZE,ColorMap.SHEET_SIZE))
         for i in range(0,res.image['colormaps'].get_width()//ColorMap.SHEET_SIZE)
      ]
      self.city_spritesheet = res.image['cityscapes']
      self.atmosphere = Atmosphere(res.image['atmosphere_colormap'],res.image['atmosphere'],res.image['enlightened_atmosphere'])
      self.clouds = res.image['clouds']
   def make_planet(self,universe,pos,bindex=None,cindex=None):
      bindex = bindex or np.random.randint(1,len(self.biome_maps)) # start at 1 because 0 is my thing
      cindex = cindex or np.random.randint(0,len(self.color_maps))
      return PlanetSprite(
         universe,
         pos,
         self.biome_maps[bindex%len(self.biome_maps)],
         self.color_maps[cindex%len(self.color_maps)],
         self.city_spritesheet,
         self.atmosphere,
         self.clouds
      )

if __name__ == "__main__":
   for i in range(0,100):
      print(generate_name())
   pygame.init()
   screen = pygame.display.set_mode((256,256))
   clock = pygame.time.Clock()
   def load(cindex,bindex):
      planet_factory = PlanetSpriteFactory(
         pygame.image.load("img/terrain.png").convert_alpha(),
         pygame.image.load("img/planet.png").convert_alpha(),
         pygame.image.load("img/cityscapes.png").convert_alpha(),
         pygame.image.load("img/atmosphere_color.png").convert_alpha(),
         pygame.image.load("img/AtmosphereWhite.png").convert_alpha(),
         pygame.image.load("img/Clouds.png").convert_alpha(),
      )
      return planet_factory.make_planet(None,(128,128),bindex,cindex)
   class DummyCamera(object):
      def __init__(self):
         self.zoom = 1
         self.scaled_shadow = pygame.image.load("img/shadow_outline.png").convert_alpha()
      def cam(self,pos):
         return pos
   psprite = load(0,1)
   cindex = 0
   bindex = 1
   report = "Colormap {}, biome map {}".format(cindex,bindex)
   font = pygame.font.Font('img/LiberationSans-Regular.ttf', 12)  
   text = font.render(report, True, (255,255,255))
   population = 0.5
   tech = 0.5
   camera = DummyCamera()
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
               psprite = load(cindex,bindex)
            elif event.key == K_UP:
               cindex = (cindex+1) % 16
               psprite = load(cindex,bindex)
            elif event.key == K_DOWN:
               cindex = (cindex-1) % 16
               psprite = load(cindex,bindex)
            elif event.key == K_LEFT:
               bindex = (bindex-1) % 5
               psprite = load(cindex,bindex)
            elif event.key == K_RIGHT:
               bindex = (bindex+1) % 5
               psprite = load(cindex,bindex)
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
      psprite.update()
      psprite.draw(screen,camera)
      pygame.draw.circle(screen,(255,0,255),(int(population*256),int(tech*256)),4)
      screen.blit(text,(0,0))
      pygame.display.flip()
   
