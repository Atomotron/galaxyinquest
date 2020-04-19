import pygame, math
import numpy as np
import random
from pygame.locals import *
import time
from main import *

# Initialize Window
pygame.init()

screenWidth = 1024
screenHeight = 768
screen = pygame.display.set_mode((screenWidth, screenHeight))

# Load Pictures
background = pygame.image.load("../img/wow.png").convert_alpha()
player_sheet = pygame.image.load("../img/spritecolor_v2.png").convert_alpha()
spritesheet = pygame.image.load("../img/sprites.png").convert_alpha()
source_rects = {
    'man': Rect((0, 0), (48 * 2, 48 * 3)),
    'turret': Rect((48 * 2, 0), (48 * 2, 48 * 3)),
    'dragon': Rect((48 * 4, 0), (48 * 2, 48 * 3)),
    'sword': Rect((48 * 6, 0), (48 * 2, 48 * 3)),
    'axe': Rect((48 * 8, 0), (48 * 2, 48 * 3)),
    'hammer': Rect((48 * 10, 0), (48 * 2, 48 * 3)),
    'werewolf': Rect((48 * 12, 0), (48 * 4, 48 * 3)),
    'warrior': Rect((48 * 16, 0), (48 * 2, 48 * 3)),
    'royal': Rect((48 * 18, 0), (48 * 2, 48 * 3)),
    'apple': Rect((0, 48 * 3), (48 * 2, 48 * 2)),
    'cherry': Rect((48 * 2, 48 * 3), (48 * 2, 48 * 2)),
    'poultry': Rect((48 * 4, 48 * 3), (48 * 2, 48 * 2)),
    'meat': Rect((48 * 6, 48 * 3), (48 * 2, 48 * 2)),
    'lake': Rect((48 * 8, 48 * 3), (48 * 8, 48 * 2)),
    'angel': Rect((48 * 16, 48 * 3), (48 * 2, 48 * 3)),
    'devil': Rect((48 * 18, 48 * 3), (48 * 2, 48 * 3)),
    'flame': Rect((0, 48 * 5), (48 * 4, 48 * 2)),
    'jet': Rect((48 * 4, 48 * 5), (48 * 5, 48 * 2)),
    'fire': Rect((48 * 9, 48 * 5), (48 * 2, 48 * 3)),
    'fir': Rect((48 * 11, 48 * 5), (48 * 2, 48 * 3)),
    'oak': Rect((48 * 13, 48 * 5), (48 * 2, 48 * 3)),
    'flower': Rect((48 * 15, 48 * 6), (48, 48 * 2)),
    'shrub': Rect((48 * 16, 48 * 6), (48 * 2, 48 * 2)),
    'block': Rect((48 * 18, 48 * 6), (48 * 2, 48 * 2)),
    'tallgrass1': Rect((0, 48 * 9), (48, 48 * 2)),
    'tallgrass2': Rect((48, 48 * 9), (48 * 2, 48 * 2)),
    'castle': Rect((48 * 3, 48 * 8), (48 * 8, 48 * 4)),
    'rock': Rect((48 * 12, 48 * 9), (48 * 3, 48 * 2)),
    'boulder': Rect((48 * 15, 48 * 8), (48 * 3, 48 * 3)),
    'outcrop': Rect((48 * 18, 48 * 8), (48 * 2, 48 * 3)),
    'widegrass': Rect((48 * 13, 48 * 11), (48 * 5, 48 * 1)),
    'grass': Rect((48 * 18, 48 * 11), (48 * 2, 48 * 1)),
}


class World(object):
    def __init__(self, background, screen_rect):
        # Foreground drawing
        self.things = []
        # Background drawing
        self.dirty_rects = [screen_rect]  # We must draw the whole background on startup
        self.background = background

    def draw(self, screen):
        for rect in self.dirty_rects:
            screen.blit(self.background, (0, 0), rect)
        for thing in self.things:
            thing.draw(screen)


# This is my class :D


class Player(object):
    # So pos,vel, and acc ALL have 0 and 1 , e.g: pos[0] is X coordinates, so on.
    def __init__(self, sprite, screen, pos, velocity, acc, planetList):
        self.sprite = pygame.transform.rotate(sprite, -90)
        self.pos = pos
        self.velocity = velocity
        self.acc = acc
        self.screen = screen
        self.MaxVelocity = 5
        self.rotation = 0
        self.sprite2 = pygame.transform.rotate(sprite, -90)
        self.mass = 1
        self.centerPos = (
        self.pos[0] - self.sprite.get_rect().width // 2, self.pos[1] - self.sprite.get_rect().height // 2)
        self.planetList = planetList
        self.angularmom = 0

        
        
    def draw(self):
        screen.blit(self.sprite, (self.centerPos[0], self.centerPos[1]))

    def move(self,dt):
        dt = dt/14
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            self.velocity[1] -= 0.1 * np.cos(self.rotation * 3.14 / 180) *dt
            self.velocity[0] -= 0.1 * np.sin(self.rotation * 3.14 / 180) *dt
        if (self.velocity[0] <= (-1 * self.MaxVelocity)):
            self.velocity[0] = (-1 * self.MaxVelocity)
        if (self.velocity[1] <= (-1 * self.MaxVelocity)):
            self.velocity[1] = (-1 * self.MaxVelocity)
        if (self.velocity[0] >= self.MaxVelocity):
            self.velocity[0] = self.MaxVelocity
        if (self.velocity[1] >= self.MaxVelocity):
            self.velocity[1] = self.MaxVelocity
        if pressed[pygame.K_d]:
            self.rotation -= 3 *dt
            self.sprite = pygame.transform.rotate(self.sprite2, self.rotation)
        if pressed[pygame.K_a]:
            self.rotation += 3 *dt
            self.sprite = pygame.transform.rotate(self.sprite2, self.rotation)
        if pressed[pygame.K_q]:
            self.angularmom += 0.05 *dt
        if pressed[pygame.K_e]:
            self.angularmom -= 0.05 *dt
        self.velocity[0] += self.acc[0] *dt
        self.velocity[1] += self.acc[1] *dt
        self.pos[1] += self.velocity[1] *dt
        self.pos[0] += self.velocity[0] *dt
        self.rotation += self.angularmom * dt
        
        
        
    def isThrusting(self):
        return self.thrust
    
    def isKillingThrusting(self):
        return self.killThrust

    def move2(self,dt):
        
        dt = dt/14
        pressed = pygame.mouse.get_pressed()


        if pressed[0]:      
            self.velocity[1] -= 0.1 * np.cos(self.rotation * 3.14 / 180) *dt
            self.velocity[0] -= 0.1 * np.sin(self.rotation * 3.14 / 180) *dt
            
            
        if (self.velocity[0] <= (-1 * self.MaxVelocity)):
            self.velocity[0] = (-1 * self.MaxVelocity)
        if (self.velocity[1] <= (-1 * self.MaxVelocity)):
            self.velocity[1] = (-1 * self.MaxVelocity)
        if (self.velocity[0] >= self.MaxVelocity):
            self.velocity[0] = self.MaxVelocity
        if (self.velocity[1] >= self.MaxVelocity):
            self.velocity[1] = self.MaxVelocity
        X,Y = pygame.mouse.get_pos()
        self.rotation = -math.atan2(Y-self.pos[1],X-self.pos[0]) * (180/3.14) - 90
        self.velocity[0] += self.acc[0] *dt
        self.velocity[1] += self.acc[1] *dt
        self.pos[1] += self.velocity[1] *dt
        self.pos[0] += self.velocity[0] *dt
        self.rotation += self.angularmom * dt
        self.sprite = pygame.transform.rotate(self.sprite2, self.rotation)
    def abuSalehBreaks(self,dt):
        dt = dt / 14
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_s] and (abs(self.velocity[0]) > 0 or abs(self.velocity[1]) > 0):
            if abs(self.velocity[0]) <= 0.06:
                self.velocity[0] = 0
            if abs(self.velocity[1]) <= 0.06:
                self.velocity[1] = 0
            if self.velocity[0] > 0:
                self.velocity[0] -= 0.1 *dt
            elif self.velocity[0] < 0:
                self.velocity[0] += 0.1 *dt
            if self.velocity[1] > 0:
                self.velocity[1] -= 0.1 *dt
            elif self.velocity[1] < 0:
                self.velocity[1] += 0.1 *dt
            self.acc[0] = 0
            self.acc[1] = 0
            self.angularmom = 0
    def gravityUpdater(self, X):
        planetAcc = [0, 0]
        xself = self.pos[0]
        yself = self.pos[1]
        xplanet = X.centerPos[0]
        yplanet = X.centerPos[1]
        dist = np.sqrt(((xplanet - xself) ** 2) + ((yplanet - yself) ** 2))
        cos = (xplanet - xself) / dist
        sin = (yplanet - yself) / dist
        planetAcc[0] = cos * (X.mass / (dist*dist))
        planetAcc[1] = sin * (X.mass / (dist*dist))
        return planetAcc

    def accUpdater(self,dt):
        dt = dt / 14
        self.acc[0] = 0
        self.acc[1] = 0
        for i in range (len(self.planetList)):
            planetAcc = self.gravityUpdater(self.planetList[i])
            self.acc[0] += planetAcc[0] * dt
            self.acc[1] += planetAcc[1] * dt

    def wrapAround(self):

        if (self.pos[0] >= (screenWidth + 40)):
            self.pos[0] = -40
        elif (self.pos[0] <= -40):
            self.pos[0] = screenWidth + 40
        if (self.pos[1] >= (screenHeight + 40)):
            self.pos[1] = -40
        elif (self.pos[1] <= -40):
            self.pos[1] = screenHeight + 40
    def collide(self):
        collided = False
        for i in range (len(self.planetList)):
            xself = self.pos[0]
            yself = self.pos[1]
            xplanet = self.planetList[i].centerPos[0]
            yplanet = self.planetList[i].centerPos[1]
            dist = np.sqrt(((xplanet - xself) ** 2) + ((yplanet - yself) ** 2))
            cos = (xplanet - xself) / dist
            sin = (yplanet - yself) / dist
            if dist < self.planetList[i].radius:
                collided = True
                distx = (xplanet - xself)/dist
                disty = (yplanet - yself) / dist
                bounce = distx*self.velocity[0] + disty*self.velocity[1]
                V2x = bounce*distx
                V2y = bounce*disty
                self.velocity[0] -=2*V2x
                self.velocity[1] -=2*V2y
        return collided
    def update(self,dt):
        
        pressed = pygame.key.get_pressed()
        collided = self.collide()
        self.draw()
        self.abuSalehBreaks(dt)
        self.wrapAround()
        if not(pressed[pygame.K_s]) and not collided:
            self.accUpdater(dt)
        self.move2(dt)
        self.centerPos = (
        self.pos[0] - self.sprite.get_rect().width // 2, self.pos[1] - self.sprite.get_rect().height // 2)
        if pressed[pygame.K_f]:
            print(self.planetList)
            print(self.gravityUpdater(self.planetList[0]))
        self.sprite = pygame.transform.rotate(self.sprite2, self.rotation)
class Planet(object):
    def __init__(self, sprite, radius, mass, pos):
        self.sprite = sprite
        self.radius = radius
        self.mass = mass
        self.pos = pos
        self.centerPos = (
        self.pos[0] + self.sprite.get_rect().width // 2, self.pos[1] + self.sprite.get_rect().height // 2)

    def draw(self):
        screen.blit(self.sprite, self.pos)

    def update(self):
        self.draw()
        

        
class PlanetSpriteLoader(object):
    
    def __init__(self,tfile,pfile,cindex,bindex,population=0,tech=0,sealevel = 0,templevel = 0):
        
        self.tfile = tfile
        self.pfile = pfile
        self.cindex = cindex
        self.bindex = bindex
        self.population = population
        self.tech = tech
        self.sealevel= sealevel
        self.templevel = templevel

    
    def load(self):
        color_sheet = pygame.image.load(self.tfile).convert_alpha()
        biomes_sheet = pygame.image.load(self.pfile).convert_alpha()
        shadow = pygame.image.load("shadow.png").convert_alpha()
        city = pygame.image.load("cityscapes.png").convert_alpha()
        cmap = ColorMap(color_sheet,pygame.Rect(self.cindex*ColorMap.SHEET_SIZE,0,ColorMap.SHEET_SIZE,ColorMap.SHEET_SIZE))
        bmap = BiomeMap(biomes_sheet,pygame.Rect(self.bindex*160,0,160,160))
        psprite = PlanetSprite((128,128),bmap,cmap,city,shadow)
        return psprite
  
    
    def update(self,psprite,dt):           

        psprite.tick(dt)
        psprite.set_parameters(self.sealevel,self.templevel,self.population,self.tech) 
        psprite.draw(screen)
        

   
        
if __name__ == "__main__":

    planetSprite = pygame.image.load("../img/planetTest.png").convert_alpha()
    mainSoundChannel = pygame.mixer.Channel(0)
    #mainSoundChannel.play(pygame.mixer.Sound("../sounds/space_ambient.ogg"),loops=-1)
    mainSoundChannel.set_volume(0.6)
    
    thrustSounds = pygame.mixer.Channel(1)
    loopedThrust = pygame.mixer.Sound("../sounds/sfx_engine_loop.ogg")
    initThrust = pygame.mixer.Sound("../sounds/sfx_engine_initial.ogg")
    killThrust = pygame.mixer.Sound("../sounds/sfx_engine_off.ogg")

    

    clock = pygame.time.Clock()  # A clock to keep track of time
    world = World(background, screen.get_rect())
    planet = Planet(planetSprite.subsurface(pygame.Rect((0, 0), (190, 194))), 100, 600, (screenWidth / 2, screenHeight / 2))
    #planet2 = Planet(planetSprite.subsurface(pygame.Rect((0, 0), (190, 194))), 100, 600, (500, 20))
    player = Player(spritesheet.subsurface(source_rects["jet"]), screen, [(screenWidth / 2) - 25, screenHeight / 2],
                    [(0), (0)], [0, 0], [planet])



    planetSpriteLoader = PlanetSpriteLoader("terrain.png","planet.png",0,1,0.5,0.5)
    
    psprite = planetSpriteLoader.load()
    cindex = 0
    bindex = 1
    report = "Colormap {}, biome map {}".format(cindex,bindex)
    font = pygame.font.Font('LiberationSans-Regular.ttf', 12)  
    text = font.render(report, True, (255,255,255))
   
    
    
    while True:
        dt = clock.tick(60)  # If we go faster than 60fps, stop and wait.
        for event in pygame.event.get():  # Get everything that's happening
            if event.type == QUIT:  # If someone presses the X button
                pygame.quit()  # Shuts down the window
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()
                
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                thrustSounds.stop()
                thrustSounds.queue(initThrust)
                thrustSounds.queue(loopedThrust)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                thrustSounds.stop()
                thrustSounds.queue(killThrust)


        world.draw(screen)
        
        planetSpriteLoader.update(psprite,dt)
        
        planet.update()
        #planet2.update()
        player.update(dt)
        
        

        pygame.display.set_caption(
            'Velocity:' + str(player.velocity[1]))

        pygame.display.flip()