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
    
    def __init__(self,screen,pos,variable,color,barName):
        self.barName = barName
        self.screen = screen
        self.pos = pos
        self.sizeX = 100
        self.sizeY = 200
        self.variable = variable
        self.color = color
        self.height = 0
        self.increasing = False
        
   
        
    def update(self,dv):

        if((self.variable+dv) <= 1 and (self.variable+dv) >=0 ):
            self.variable += dv


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
    
    dTemp = 0.0
    dPop = 0.000
    dSea = 0.0
    dTech = 0.0001
    
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

        temp = tempBar.variable
        tech = techBar.variable
        pop = popBar.variable
        sea = seaBar.variable
        
        if tech > 0.8:
            TempTechModifier = 0  
        elif tech < 0.8:
            TempTechModifier = (0.8 - tech) / 100
            
        if temp < 0.6 and temp > 0.4:
            TechTempModifier = 0.001
            PopTempModifier = 0.001
            SeaTempModifier = 0
        elif temp < 0.4:
            TechTempModifier = -0.003
            PopTempModifier = -0.003
            SeaTempModifier = -0.001
        elif temp > 0.6:
            TechTempModifier = -0.003
            PopTempModifier = -0.003
            SeaTempModifier = +0.001
                
                
        dTemp = (pop * 0.02) + TempTechModifier
        dTech = 0.001 + TechTempModifier + (pop * 0.02)
        dPop = 0.001 + PopTempModifier + PopSeaModifier + (tech * 0.02)
        dSea = SeaTempModifier
        
   
        print(sea)
        

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
