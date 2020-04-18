#!/usr/bin/env python3
import random,math
import pygame
from pygame import Rect
from pygame.locals import *


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


    def draw(self,screen):
        screen.blit(self.image,self.pos)

    def update_status(self,screen,click_pos): #click_position is the position of where the mouse is from pygame.mouse.get_pos()
        """updates the current status of the button based on a click, can pass the status to the ship class to control
           what the ship will do depending on the status.
        """
        self.pos_x = click_pos[0]
        self.pos_y = click_pos[1]
        if self.image.collidepoint(self.pos_x,self.pos_y):  #check if button position interacts with the button rect
            self.interaction = True
        else:
            self.interaction = False

        if self.interaction == True:
            if self.image == self.on:
                self.image = self.off # currently a seperate off button but could just change the color
                self.current_status = False
                self.draw(screen)
            elif self.image == self.off:
                self.image == self.image
                self.current_status = True
                self.draw(screen)
   

#create text object
#~font from font file
#font = pygame.font.Font('freesansbold.ttf', 32)  
#~text object (text,antialias, color, background=NONE)
#text = font.render('GeeksForGeeks', True, green, blue)

#get text rect
#textRect = text.get_rect()

#write to screen
#display_surface.blit(text, textRect)


