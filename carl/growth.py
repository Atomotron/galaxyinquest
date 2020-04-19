#!/usr/bin/env python3
import random,math
import pygame
from pygame import Rect
from pygame.locals import *
import button
import bar
"""
[P_dot,C_dot,S_dot,T_dot]  = C * [P,C,S,T]
C = (  0  a1  a2  a3)
       b1  0  b2   0
        0 c1   0  c2
        0 d1  d2   0)

P_dot = a1*C + a2*S + a3*T
C_dot = b1*P + b2*S
S_dot = c1*C + c2*T
T_dot = d1*C + d2*S

population = P = po +
tech = C = co +
sea_level = S = co +
Temp = T = to +

[a1,a2,a3] = [r*x1,o*x2,o*x3]
[b1,b2] = [r*x4,o*x5]
[c1,c2] = [o*x6,o*x7]
[d1,d2] = [o*x8,r*x9]
 
x1-x9 = arbitrary weighting factors


r = resources
o = outputs  
r and o are controlled by buttons
ri = intial r
oi = intial o
r = ri - gamma_r
o = oi - gamma_o +gamma_or*r
gamma_r = resource decay
gamma_o = output decay
gamma_or = output growth due to resources  

bars charts will show percentage of P,C,S,T relative to the the max P,C,S,T
buttons will increase or decrease r and o
show on the side the numerical value or perctange


"""
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


