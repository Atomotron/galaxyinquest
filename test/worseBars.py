#!/usr/bin/env python3
import pygame,math
from pygame.locals import *

pygame.init()

screenHeight = 768
screenWidth = 1024

screen = pygame.display.set_mode((screenWidth,screenHeight))
clock = pygame.time.Clock() 



class Bar():
    
    def __init__(self,screen,pos,variable,color,barName,maxPop=1.0):
        self.maxPop = maxPop
        self.barName = barName
        self.screen = screen
        self.pos = pos
        self.sizeX = 100
        self.sizeY = 200
        self.variable = variable
        self.color = color
        self.height = 0

        
   
        
    def update(self,dv):

        if((self.variable+dv) <= self.maxPop and (self.variable+dv) >=-1 ):
            self.variable += dv

        if(self.variable > self.maxPop):
            self.variable = self.maxPop

        newSize =  (self.sizeY * self.variable)
        pygame.draw.rect(self.screen,self.color,((self.pos[0],(self.pos[1]+(self.sizeY * (1-self.variable)))),(self.sizeX,newSize)))
        wow = "{:.0f}".format( self.variable * 100 )
        outputText = str(self.barName) + ": %" + str(wow) 
        
        font = pygame.font.Font('LiberationSans-Regular.ttf', 12)
        text = font.render(outputText, True, (255,255,255))
        screen.blit(text,(self.pos[0] + 10 , self.pos[1] + 250))
        
        



if __name__ == "__main__":
    
   
    while True:
  
        clock.tick(60) 
        for event in pygame.event.get(): 
            if event.type == QUIT: 
                pygame.quit() 
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
  
        
        pygame.display.flip()
