#!/usr/bin/env python3
import pygame,math
from pygame.locals import *

pygame.init()

screenHeight = 768
screenWidth = 1024

screen = pygame.display.set_mode((screenWidth,screenHeight))
image = pygame.image.load("../img/spriteanim_v2.png").convert_alpha()
gameSprite = pygame.image.load("../img/spritecolor_v2.png").convert_alpha()
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

        if((self.variable+dv) <= self.maxPop and (self.variable+dv) >=0 ):
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
    
    temp=pop=sea=tech=0.5
    
    tempBar = Bar(screen,(150,300),temp,(255,0,0),"Temp")
    popBar = Bar(screen,(350,300),pop,(0,255,0),"Pop")
    seaBar = Bar(screen,(550,300),sea,(255,255,0),"Sea")
    techBar = Bar(screen,(750,300),tech,(0,0,255),"Tech")
    
    dTemp = 0
    dPop = 0
    dSea = 0
    dTech = 0
    
    temp = tempBar.variable
    tech = techBar.variable
    pop = popBar.variable
    sea = seaBar.variable
    
    PopTempModifier = 0
    PopSeaModifier = 0
    TempTechModifier = 0
    TempSeaModifier = 0
    SeaTempModifier = 0

    
    
    while True:

        dPop = (pop * (2.7**0.0001)) - pop 
        dTemp += (pop - 0.5) * 0.0000001
        dSea -= (temp - 0.5) * 0.0000001 
        
        temp = tempBar.variable
        tech = techBar.variable
        pop = popBar.variable
        sea = seaBar.variable

         
        
        if(temp > 0.65 or temp < 0.35):
            dPop = -dPop
      
        
        if(sea > 0.65):
            popBar.maxPop = 1-((sea - 0.65) * 2)
            dTemp -= (sea-0.5) * 0.0000001
        elif(sea < 0.35):
            
            popBar.maxPop = 1-((0.35 - sea) * 2)
            dTemp += (sea-0.5) * 0.0000001
        
        
        clock.tick(60) 
        for event in pygame.event.get(): 
            if event.type == QUIT: 
                pygame.quit() 
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
    
        
        screen.fill((0,0,0))
        
        tempBar.update(dTemp)
        popBar.update(dPop)
        seaBar.update(dSea)
        techBar.update(dTech)
        
        
        
        
        
        
        
        
        
        
        
        pygame.display.flip()
