import pygame
from pygame.locals import *

def open_save(name):
    with open('files/%s.txt' %name) as f: content = f.read().split('\n')

