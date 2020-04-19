#!/usr/bin/env python3
import random,math
import pygame
from pygame import Rect
from pygame.locals import *
import button
import bar
import numpy as np

class bar_chart(object):
    def __init__(self,bar_back,full_bar,empty_bar,pos,text=None):
        self.pos = pos
        self.back = bar_back
        self.back_offset = self.back.get_rect()
        self.back_pos = [self.pos[0] - self.back_offset[2]//2, self.pos[1] - self.back_offset[3]//2]
        self.full_bar = full_bar
        self.full = empty_bar
        self.empty = empty_bar
        self.text = text
        self.bar_offset = self.empty.get_rect()
        self.font = pygame.font.Font('font/retro_shine/Retro Shine.ttf', 12)
        self.text_1 = self.font.render(self.text, True, white)
        #self.textpos1 = [self.pos[0] - self.bar_offset[2]//2 , self.pos[1] + self.bar_offset[3]//2 + 10]
        self.empty_pos = self.pos
        self.full_pos = self.pos
        self.textpos1 = [self.pos[0],self.pos[1]+self.bar_offset[3]+10]
        #self.empty_pos = [self.pos[0] - (self.bar_offset[2]//2), self.pos[1] - (self.bar_offset[3]//2) ]
        #self.full_pos = [self.pos[0] - (self.bar_offset[2]//2), self.pos[1] - (self.bar_offset[3]//2)]

    def draw(self,screen):
        #screen.blit(self.back,self.back_pos)
        screen.blit(self.empty,self.empty_pos)
        screen.blit(self.full,self.full_pos)
        screen.blit(self.text_1,self.textpos1)

    def update_full(self,percent): #percent is a number between 0 and 1
        #self.full_pos = [self.pos[0]  - (self.bar_offset[2]//2)  , (self.pos[1] + (self.bar_offset[3]//2) ) ]
        self.full = self.full_bar.subsurface( pygame.Rect( (0,0) , (self.bar_offset[2],self.bar_offset[3]*percent) ) )
        self.full_rect = self.full.get_rect()
        self.full_pos = [self.pos[0] , (self.pos[1] + (self.bar_offset[3]) ) - self.full_rect[3]]


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
        self.words = 'on'
        self.font = pygame.font.Font('font/retro_shine/Retro Shine.ttf', 10)
        self.text_on = self.font.render('On', True, white)
        self.text_off = self.font.render('off', True, white)
        self.text = self.font.render(self.words,True,blue)
        self.imagedim = self.image.get_rect()
        self.text_x = pos[0] + 10
        self.text_y = pos[1] + (self.imagedim[3] // 2) - 15
        self.textpos = [self.text_x,self.text_y]
        
    def draw(self,screen):
        screen.blit(self.image,self.pos)
        screen.blit(self.text,self.textpos)
        #print(self.pos)
        #print(self.imagedim)
        #print(self.textpos)
    def button_clicked(self,click_pos):
        self.pos_x = click_pos[0] - self.pos[0]
        self.pos_y = click_pos[1] - self.pos[1]
        if self.image.get_rect().collidepoint(self.pos_x,self.pos_y):
            self.interaction = True
        else:
            self.interaction = False

    def update_status_off(self,screen,click_pos): #click_position is the position of where the mouse is from pygame.mouse.get_pos()
        """updates the current status of the button based on a click, can pass the status to the ship class to control
           what the ship will do depending on the status.
        """
        self.pos_x = click_pos[0] - self.pos[0]
        self.pos_y = click_pos[1] - self.pos[1]
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
    def update_text(self,num):
        if isinstance(num,int) or isinstance(num,float):
            self.words = str(round(num,3))
        elif isinstance(num,str):
            self.words = num
        self.text = self.font.render(self.words,True,blue)

class Text(object):
    def __init__(self,text,pos):
        self.words = text
        self.pos = pos
        self.font = pygame.font.Font('font/retro_shine/Retro Shine.ttf', 12)
        self.text_disp = self.font.render(self.words,True,white) 
    def draw(self,screen):
        screen.blit(self.text_disp,self.pos)




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

A = [0 , r*x1, o*x2, o*x3]
B = [r*x4 , 0, o*x5, 0]
C = [0, o*x6, 0, o*x7]
D = [0, o*x8, r*x9, 0]
 
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

-step(1): display screen
-step(2): draw bars to the 
-step(3): draw number display
-step(4): add buttons
-step(5): add button functions
-step(6): add governing eq



"""
if __name__ == "__main__":
    r = 2
    o = 3

    x1 = .2
    x2 = .1
    x3 = .4
    x4 = .07
    x5 = .15
    x6 = .12 
    x7 = .21
    x8 = .09
    x9 = .11

    po=10
    co=5
    so=8
    To=15

    P_max = 100
    C_max = 100
    S_max = 100
    T_max = 100

    # U = [P,C,S,T]
    A = np.array([[0 , r*x1, o*x2, o*x3],[r*x4 , 0, o*x5, 0],[0, o*x6, 0, o*x7],[0, o*x8, r*x9, 0]])
    w,V = np.linalg.eig(A)
     #take the real part of U
  

    #R and O decay
    gam_r = .002
    gam_o = .002

    #Initialize pygames and images
    pygame.init()
    screen = pygame.display.set_mode((1024,768))
    bar_back = pygame.image.load("bar_back.png").convert_alpha()
    full_bar = pygame.image.load("full_growth.png").convert_alpha()
    empty_bar = pygame.image.load("empty_growth.png").convert_alpha()
    display_button = pygame.image.load("display_button.png").convert_alpha() # 100x45
    plus_button = pygame.image.load("plus_button.png").convert_alpha()  #45x45
    min_button = pygame.image.load("min_button.png").convert_alpha()
    white = (255, 255, 255)
    blue = (0, 0, 128)
    mid_x = (1024 // 2)
    mid_y = (768 //2)
    #initialize bars
    pop_pos = [124.8,75]
    pop_bar = bar_chart(bar_back,full_bar,empty_bar,pop_pos,'pop')
    tech_pos = [124.8*2 + 100, 75] # 100 is the width of the bar
    tech_bar = bar_chart(bar_back,full_bar,empty_bar,tech_pos,'tech')
    sea_pos = [124.8*3 + 100*2, 75]
    sea_bar = bar_chart(bar_back,full_bar,empty_bar,sea_pos,'sea')
    temp_pos = [124.8*4 + 100*3, 75]
    temp_bar = bar_chart(bar_back,full_bar,empty_bar,temp_pos,'temp')
    #initialize displays
    pop_disp_pos = [124.8, mid_y + 20]
    pop_disp = Active_Button(display_button,display_button,pop_disp_pos)
    tech_disp_pos = [124.8*2 + 100, mid_y + 20]
    tech_disp = Active_Button(display_button,display_button,tech_disp_pos)
    sea_disp_pos = [124.8*3 + 100*2, mid_y + 20]
    sea_disp = Active_Button(display_button,display_button,sea_disp_pos)
    temp_disp_pos = [124.8*4 + 100*3, mid_y + 20]
    temp_disp = Active_Button(display_button,display_button,temp_disp_pos)
    #initialize resource buttons
    p_pos_r = [124.8 + 124.8//2 + 100, mid_y +125]
    m_pos_r = [124.8 + 124.8//2 + 300, mid_y +125]
    r_pos = [124.8 + 124.8//2 + 400, mid_y +125]
    p_button_r = Active_Button(plus_button,plus_button,p_pos_r)
    m_button_r = Active_Button(min_button,min_button,m_pos_r)
    r_disp = Active_Button(display_button,display_button,r_pos)
    p_button_r.update_text('+')
    m_button_r.update_text('-')
    re_pos = [124.8 + 124.8//2 + 200 ,mid_y +125 + 10]
    resources = Text('R',re_pos)
    #initialize output buttons
    p_pos_o = [124.8 + 124.8//2 + 100, mid_y +190]
    m_pos_o = [124.8 + 124.8//2 + 300, mid_y +190]
    o_pos = [124.8 + 124.8//2 + 400, mid_y +190]
    p_button_o = Active_Button(plus_button,plus_button,p_pos_o)
    m_button_o = Active_Button(min_button,min_button,m_pos_o)
    o_disp = Active_Button(display_button,display_button,o_pos)
    p_button_o.update_text('+')
    m_button_o.update_text('-')
    out_pos = [124.8 + 124.8//2 + 200 ,mid_y +190 +10]
    outputs = Text('O',out_pos)

    completion = 0
    t = 0
    game = True
    while game == True : 
        screen.fill(blue) 
        pop_bar.draw(screen)
        pop_disp.draw(screen)
        tech_bar.draw(screen)
        tech_disp.draw(screen)
        sea_bar.draw(screen)
        sea_disp.draw(screen)
        temp_bar.draw(screen)
        temp_disp.draw(screen)
        m_button_r.draw(screen)
        p_button_r.draw(screen)
        m_button_o.draw(screen)
        p_button_o.draw(screen)
        o_disp.draw(screen)
        r_disp.draw(screen)
        resources.draw(screen)
        outputs.draw(screen)


        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit() 
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()

        pressed = pygame.mouse.get_pressed()
        if pressed[0]:
            p_button_r.button_clicked(pygame.mouse.get_pos())
            m_button_r.button_clicked(pygame.mouse.get_pos())
            if p_button_r.interaction == True and r < 100:
                r += 1
            if m_button_r.interaction == True and r > 0:
                r -= 1
            p_button_o.button_clicked(pygame.mouse.get_pos())
            m_button_o.button_clicked(pygame.mouse.get_pos())
            if p_button_o.interaction == True and o < 100:
                o += 1
            if m_button_o.interaction == True and o > 0:
                o -= 1
        #governing equations

        U = po*V[:,0]*np.exp(w[0]*t) + co*V[:,1]*np.exp(w[1]*t)  + so*V[:,2]*np.exp(w[2]*t) + To*V[:,3]*np.exp(w[3]*t) 

        P = np.real(U[0])
        C = np.real(U[1])
        S = np.real(U[2])
        T = np.real(U[3])

        if P < 100 and P > 0:
            pop_disp.update_text(P)
        elif P >= 100:
            pop_disp.update_text(100)
        elif P <= 0:
            pop_disp.update_text(0)
        if C < 100 and C > 0:
            tech_disp.update_text(C)
        elif C >= 100:
            tech_disp.update_text(100)
        elif C <= 0:
            tech_disp.update_text(0)
        if S < 100 and S > 0:
            sea_disp.update_text(S)
        elif S >= 100:
            sea_disp.update_text(100)
        elif S <= 0:
            sea_disp.update_text(0)
        if T < 100 and T > 0:
            temp_disp.update_text(T)
        elif T >= 100:
            temp_disp.update_text(100)
        elif T <= 0:
            temp_disp.update_text(0)

        pop_per = P/P_max
        tech_per = C/C_max
        sea_per = S/S_max
        temp_per = T/T_max

        if pop_per >= 0 and pop_per <= 1:
            pop_bar.update_full(pop_per)
        if tech_per >= 0 and tech_per <= 1:
            tech_bar.update_full(tech_per)
        if sea_per >= 0 and sea_per <= 1:
            sea_bar.update_full(sea_per)
        if temp_per >= 0 and temp_per <= 1:
            temp_bar.update_full(temp_per)
        
        #decay and governing equations
        R = r - gam_r
        r = R
        if r > 0 and r < 100:
            r_disp.update_text(str(round(r,0)))
        elif r < 0:
            r = 0
        elif r > 100:
            r = 100
        gam_or = r*.0001
        O = o - gam_o + gam_or
        o = O
        if o > 0 and o < 100:
            o_disp.update_text(str(round(o,0)))
        elif o < 0:
            o = 0
        elif o > 100:
            o = 100

        pygame.display.flip()
        t +=.001


