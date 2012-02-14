# -*- coding: utf-8 -*-
#
SW,SH = 640,480
BGCOLOR = (0, 0, 0)

from math import radians 

from OpenGL.GL import *
from OpenGL.GLU import *

import pygame
from pygame.locals import *

import random
import math
import numpy
import pickle
import os

LMB = 1
MMB = 2
RMB = 3
WUP = 4
WDN = 5

def main():
    pygame.init()
    screen = pygame.display.set_mode((160, 600))
    pygame.display.set_caption('DigDig2')
    #screen.blit(background, (0, 0))
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                done = True
                """
            elif event.type == MOUSEBUTTONDOWN:
                if fist.punch(chimp):
                    punch_sound.play() #punch
                    chimp.punched()
                else:
                    whiff_sound.play() #miss
            elif event.type == MOUSEBUTTONUP:
                fist.unpunch()
                """

        screen.fill((0,0,0))
        pygame.display.flip()

if __name__ == "__main__":
    main()
