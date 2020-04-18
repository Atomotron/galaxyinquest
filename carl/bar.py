#!/usr/bin/env python3
import random,math
import pygame
from pygame import Rect
from pygame.locals import *



class bar_chart(object):
    def __init__(self,bar_back,full_bar,empty_bar,pos):
        self.pos = pos
        self.back = bar_back
        self.back_offset = self.back.get_rect()
        self.back_pos = [self.pos[0] - self.back_offset[2]//2, self.pos[1] - self.back_offset[3]//2]
        self.full_bar = full_bar
        self.full = empty_bar
        self.empty = empty_bar
        self.bar_offset = self.empty.get_rect()
        self.font = pygame.font.Font('font/retro_shine/Retro Shine.ttf', 16)
        self.text_1 = self.font.render('left click to go up', True, white)
        self.text_2 = self.font.render('right click to go down', True, white)
        self.textpos1 = [self.pos[0] - self.bar_offset[2]//2 , self.pos[1] + self.bar_offset[3]//2 + 10]
        self.textpos2 = [self.pos[0] - self.bar_offset[2]//2 , self.pos[1] + self.bar_offset[3]//2 + 40]
        self.empty_pos = [self.pos[0] - (self.bar_offset[2]//2), self.pos[1] - (self.bar_offset[3]//2) ]
        self.full_pos = [self.pos[0] - (self.bar_offset[2]//2), self.pos[1] - (self.bar_offset[3]//2)]

    def draw(self,screen):
        screen.blit(self.back,self.back_pos)
        screen.blit(self.empty,self.empty_pos)
        screen.blit(self.full,self.full_pos)
        screen.blit(self.text_1,self.textpos1)
        screen.blit(self.text_2,self.textpos2)

    def update_full(self,percent): #percent is a number between 0 and 1
        self.full_pos = [self.pos[0]  - (self.bar_offset[2]//2)  , (self.pos[1] + (self.bar_offset[3]//2) ) ]
        self.full = self.full_bar.subsurface( pygame.Rect( (0,0) , (self.bar_offset[2],self.bar_offset[3]*percent) ) )
        self.full_rect = self.full.get_rect()
        self.full_pos = [self.pos[0]  - (self.bar_offset[2]//2)  , (self.pos[1] + (self.bar_offset[3]//2) ) - self.full_rect[3]]
       
            
            

if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((1024,768))
    bar_back = pygame.image.load("bar_back.png").convert_alpha()
    full_bar = pygame.image.load("full_bar.png").convert_alpha()
    empty_bar = pygame.image.load("empty_bar.png").convert_alpha()
    white = (255, 255, 255)
    blue = (0, 0, 128)
    mid_x = (1024 // 2)
    mid_y = (768 //2)
    pos = [mid_x,mid_y]
    bar = bar_chart(bar_back,full_bar,empty_bar,pos)
    completion = 0
    while True : 
        screen.fill(white) 
        bar.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit() 
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()

        pressed = pygame.mouse.get_pressed()
        if pressed[0]:
            bar.update_full(completion)
            if completion <= 1:
                completion += .01
        if pressed[2]:
            bar.update_full(completion)
            if completion >=0:
                completion -=.01

        pygame.display.flip()


