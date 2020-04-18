#!/usr/bin/env python3
import random,math
import pygame
from pygame import Rect
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((1024,768))
on_img = pygame.image.load("on.png").convert_alpha()
off_img = pygame.image.load("off.png").convert_alpha()
white = (255, 255, 255)
blue = (0, 0, 128)
pos = [1024 // 2, 768 //2]
mid_x = (1024 // 2)
mid_y = (768 //2)

#if button cliked, check if position of click is within the rect of the stationary sprite.
#event = pygame.mouse.get_pressed()
#if event = click:
#   button.update_status(screen,pygame.mouse.get_pos())




class Active_Button(object):
    def __init__(self,on_image,off_image,pos):
        """on_image = on button object
           off_image = off button object
           pos = button position
        """
        self.current_status = True #button witll start "on"
        self.on = on_image
        self.off = off_image
        self.pos = pos # button position
        self.interaction = False #the interactions status of the button
        self.image = self.on #default button image rect
        self.font = pygame.font.Font('font/retro_shine/Retro Shine.ttf', 16)
        self.text_on = self.font.render('On', True, white)
        self.text_off = self.font.render('Off', True, white)
        self.text = self.text_on
        self.imagedim = self.image.get_rect()
        self.text_x = pos[0] + (self.imagedim[2] // 2) - 20
        self.text_y = pos[1] + (self.imagedim[3] // 2) - 15
        self.textpos = [self.text_x,self.text_y]
        


    def draw(self,screen):
        screen.blit(self.image,self.pos)
        screen.blit(self.text,self.textpos)
        #print(self.pos)
        #print(self.imagedim)
        #print(self.textpos)

    def update_status_off(self,screen,click_pos): #click_position is the position of where the mouse is from pygame.mouse.get_pos()
        """updates the current status of the button based on a click, can pass the status to the ship class to control
           what the ship will do depending on the status.
        """
        self.pos_x = click_pos[0] - mid_x
        self.pos_y = click_pos[1] - mid_y
        if self.image.get_rect().collidepoint(self.pos_x,self.pos_y):  #check if button position interacts with the button rect
            self.interaction = True
        else:
            self.interaction = False

        if self.interaction == True:
            self.image = self.off # currently a seperate off button but could just change the color
            self.current_status = False
            self.text = self.text_off
            #print('off')
            self.draw(screen)

    def update_status_on(self,screen,click_pos): #click_position is the position of where the mouse is from pygame.mouse.get_pos()
        """updates the current status of the button based on a click, can pass the status to the ship class to control
           what the ship will do depending on the status.
        """
        self.pos_x = click_pos[0] - mid_x
        self.pos_y = click_pos[1] - mid_y
        if self.image.get_rect().collidepoint(self.pos_x,self.pos_y):  #check if button position interacts with the button rect
            self.interaction = True
        else:
            self.interaction = False

        if self.interaction == True:
            self.image = self.on # currently a seperate off button but could just change the color
            self.current_status = True
            self.text = self.text_on
            #print('on')
            self.draw(screen)
    def toggle(self,screen,click_pos):
         if self.current_status:
               self.update_status_off(self,screen,click_pos)
         else:
               self.update_status_on(self,screen,click_pos)
            
            

if __name__ == "__main__":

    active_button = Active_Button(on_img,off_img,pos)
    first = True
    while True : 
        screen.fill(white) 
        active_button.draw(screen)

        for event in pygame.event.get(): # Get everything that's happening
            if event.type == QUIT: # If someone presses the X button
                pygame.quit() # Shuts down the window
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()

        pressed = pygame.mouse.get_pressed()
        if pressed[0]:
            active_button.toggle(screen,pygame.mouse.get_pos())
        if pressed[2]:
            active_button.toggle(screen,pygame.mouse.get_pos())

        pygame.display.flip()

#create text object
#~font from font file
#font = pygame.font.Font('freesansbold.ttf', 32)  
#~text object (text,antialias, color, background=NONE)
#text = font.render('GeeksForGeeks', True, green, blue)

#get text rect
#textRect = text.get_rect()

#write to screen
#display_surface.blit(text, textRect)


