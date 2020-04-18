import pygame,math
import numpy as np
import random
from pygame.locals import *
import time
#Initialize Window
pygame.init()

screenWidth=1024
screenHeight=768
screen = pygame.display.set_mode((screenWidth,screenHeight))
#Load Pictures
background = pygame.image.load("../img/PyBgrd1_Plains.png").convert_alpha()
player_sheet = pygame.image.load("../img/spritecolor_v2.png").convert_alpha()
spritesheet = pygame.image.load("../img/sprites.png").convert_alpha()
source_rects = {
    'man'   : Rect((0,0),(48*2,48*3)),
    'turret': Rect((48*2,0),(48*2,48*3)),
    'dragon': Rect((48*4,0),(48*2,48*3)),
    'sword' : Rect((48*6,0),(48*2,48*3)),
    'axe'   : Rect((48*8,0),(48*2,48*3)),
    'hammer': Rect((48*10,0),(48*2,48*3)),
    'werewolf':Rect((48*12,0),(48*4,48*3)),
    'warrior':Rect((48*16,0),(48*2,48*3)),
    'royal' : Rect((48*18,0),(48*2,48*3)),
    'apple' : Rect((0,48*3),(48*2,48*2)),
    'cherry': Rect((48*2,48*3),(48*2,48*2)),
    'poultry':Rect((48*4,48*3),(48*2,48*2)),
    'meat'  : Rect((48*6,48*3),(48*2,48*2)),
    'lake'  : Rect((48*8,48*3),(48*8,48*2)),
    'angel' : Rect((48*16,48*3),(48*2,48*3)),
    'devil' : Rect((48*18,48*3),(48*2,48*3)),
    'flame' : Rect((0,48*5),(48*4,48*2)),
    'jet'   : Rect((48*4,48*5),(48*5,48*2)),
    'fire'  : Rect((48*9,48*5),(48*2,48*3)),
    'fir'   : Rect((48*11,48*5),(48*2,48*3)),
    'oak'   : Rect((48*13,48*5),(48*2,48*3)),
    'flower': Rect((48*15,48*6),(48,48*2)),
    'shrub' : Rect((48*16,48*6),(48*2,48*2)),
    'block' : Rect((48*18,48*6),(48*2,48*2)),
    'tallgrass1': Rect((0,48*9),(48,48*2)),
    'tallgrass2': Rect((48,48*9),(48*2,48*2)),
    'castle': Rect((48*3,48*8),(48*8,48*4)),
    'rock'  :Rect((48*12,48*9),(48*3,48*2)),
    'boulder':Rect((48*15,48*8),(48*3,48*3)),
    'outcrop':Rect((48*18,48*8),(48*2,48*3)),
    'widegrass'  :Rect((48*13,48*11),(48*5,48*1)),
    'grass'  :Rect((48*18,48*11),(48*2,48*1)),
}


class World(object):
    def __init__(self,background,screen_rect):
        # Foreground drawing
        self.things = []
        # Background drawing
        self.dirty_rects = [screen_rect] # We must draw the whole background on startup
        self.background = background
    def draw(self,screen):
        for rect in self.dirty_rects:
            screen.blit(self.background,(0,0),rect)
        for thing in self.things:
            thing.draw(screen)
#This is my class :D
            
            
            
class Player(object):
    #So pos,vel, and acc ALL have 0 and 1 , e.g: pos[0] is X coordinates, so on.
    def __init__(self,sprite,screen,pos,velocity,acc):
        self.sprite = pygame.transform.rotate(sprite,-90)
        self.pos = pos
        self.velocity= velocity
        self.acc = acc
        self.screen = screen
    
    def draw(self):
        screen.blit(self.sprite,self.pos)
        
    def move(self):
         pressed = pygame.key.get_pressed()
         if pressed[pygame.K_s]:
            self.velocity[0] += 5
         elif pressed[pygame.K_w]:
            self.velocity[0] -= 5
         self.pos[0] += self.velocity
        

def erase(rect): # Draw the background over an area to "erase" what's there.
    screen.blit(background,rect.topleft,rect)
    erase(screen.get_rect())

if __name__ == "__main__":
    
    clock = pygame.time.Clock() # A clock to keep track of time
    world = World(background,screen.get_rect())
    
    

    player = Player(spritesheet.subsurface(source_rects["jet"]),screen,[(screenWidth/2)-25,screenHeight/2],[(0),(0)],[0,0])
    
    while True:
        clock.tick(60) # If we go faster than 60fps, stop and wait.
        for event in pygame.event.get(): # Get everything that's happening
            if event.type == QUIT: # If someone presses the X button
                pygame.quit() # Shuts down the window
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()
        world.draw(screen)

        player.draw()
        player.move()
        
        
        
       
            
        pygame.display.flip()

