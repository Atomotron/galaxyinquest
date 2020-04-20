#!/usr/bin/env python3
import random, math
import pygame
from pygame import Rect
from pygame.locals import *


class bar_chart(object):
    def __init__(self, bar_back, full_bar, empty_bar, pos):
        self.pos = pos
        self.back = bar_back
        self.back_offset = self.back.get_rect()
        self.back_pos = [self.pos[0] - self.back_offset[2] // 2, self.pos[1] - self.back_offset[3] // 2]
        self.full_bar = full_bar
        self.full = empty_bar
        self.empty = empty_bar
        self.bar_offset = self.empty.get_rect()
        self.font = pygame.font.Font('font/retro_shine/Retro Shine.ttf', 16)
        self.text_1 = self.font.render('left click to go up', True, white)
        self.text_2 = self.font.render('right click to go down', True, white)
        self.textpos1 = [self.pos[0] - self.bar_offset[2] // 2, self.pos[1] + self.bar_offset[3] // 2 + 10]
        self.textpos2 = [self.pos[0] - self.bar_offset[2] // 2, self.pos[1] + self.bar_offset[3] // 2 + 40]
        self.empty_pos = [self.pos[0] - (self.bar_offset[2] // 2), self.pos[1] - (self.bar_offset[3] // 2)]
        self.full_pos = [self.pos[0] - (self.bar_offset[2] // 2), self.pos[1] - (self.bar_offset[3] // 2)]

    def draw(self, screen):
        #screen.blit(self.back, self.back_pos)
        screen.blit(self.empty, self.empty_pos)
        screen.blit(self.full, self.full_pos)
        screen.blit(self.text_1, self.textpos1)
        screen.blit(self.text_2, self.textpos2)

    def update_full(self, percent):  # percent is a number between 0 and 1
        self.full_pos = [self.pos[0] - (self.bar_offset[2] // 2), (self.pos[1] + (self.bar_offset[3] // 2))]
        self.full = self.full_bar.subsurface(pygame.Rect((0, 0), (self.bar_offset[2], self.bar_offset[3] * percent)))
        self.full_rect = self.full.get_rect()
        self.full_pos = [self.pos[0] - (self.bar_offset[2] // 2),
                         (self.pos[1] + (self.bar_offset[3] // 2)) - self.full_rect[3]]


if __name__ == "__main__":

    pygame.init()
    dTemp = 0.0
    dPop = 0.000
    dSea = 0.0
    dTech = 0.0001
    Temp = 0.50
    Tech = 0.50
    Pop = 0.50
    Sea = 0.50
    PopTempModifier = 0
    PopSeaModifier = 0
    TempTechModifier = 0
    TempSeaModifier = 0
    SeaTempModifier = 0
    screen = pygame.display.set_mode((1024, 1000))
    bar_back = pygame.image.load("bar_back.png").convert_alpha()
    full_bar = pygame.image.load("full_bar.png").convert_alpha()
    empty_bar = pygame.image.load("empty_bar.png").convert_alpha()
    white = (255, 255, 255)
    blue = (0, 0, 128)
    mid_x = (1024 // 2)
    mid_y = (768 // 2)
    pos = [0, mid_y]
    pos2 = [300, 768/2]
    pos3 = [600, 768 / 2]
    pos4 = [1000, 768 / 2]
    bar = bar_chart(bar_back, full_bar, empty_bar, pos)
    bar2 = bar_chart(bar_back, full_bar, empty_bar, pos2)
    bar3 = bar_chart(bar_back, full_bar, empty_bar, pos3)
    bar4 = bar_chart(bar_back, full_bar, empty_bar, pos4)
    while True:
        if Tech > 0.8:
            TempTechModifier = 0  # (We've learned to make our technology net zero).
        elif Tech < 0.8:
            TempTechModifier = (0.8 - Tech) / 100
        if Temp < 0.6 and Temp > 0.4:
            TechTempModifier = 0.001
            PopTempModifier = 0.001
            SeaTempModifier = 0
        elif Temp < 0.4:
            TechTempModifier = -0.003
            PopTempModifier = -0.003
            SeaTempModifier = -0.001
        elif Temp > 0.6:
            TechTempModifier = -0.003
            PopTempModifier = -0.003
            SeaTempModifier = +0.001
        dTemp = Pop * 0.02 + TempTechModifier
        dTech = 0.001 + TechTempModifier + Pop * 0.02
        dPop = 0.001 + PopTempModifier + PopSeaModifier + Tech * 0.02
        dSea = SeaTempModifier

        Temp += dTemp
        Tech += dTech
        Pop += dPop
        Sea += dSea
        if Temp >= 1:
            Temp = 1
        if Pop >= 1:
            Pop = 1
        if Sea >= 1:
            Sea = 1
        if Tech >= 1:
            Tech = 1
        screen.fill(white)
        bar.draw(screen)
        bar2.draw(screen)
        bar3.draw(screen)
        bar4.draw(screen)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()

        pressed = pygame.mouse.get_pressed()
        bar.update_full(Temp)
        bar2.update_full(Pop)
        bar3.update_full(Tech)
        bar4.update_full(Sea)
        #if pressed[0]:
        #    bar.update_full(completion)
        #    if completion <= 1:
        #        completion += .01
        #if pressed[2]:
        #    bar.update_full(completion)
        #    if completion >= 0:
        #        completion -= .01

        pygame.display.flip()

