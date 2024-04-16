import pygame
from pygame.locals import *

class Manager:
    """Manager for all objects. Should be used to create and remove new objects, as it manages the ID system."""

    # key: ID, value: object
    points = {}
    links = {}
    images = {}

    @staticmethod
    def new_obj(args, _class, _dict, id):
        """Adds a new object to the corresponding dictionary, assign an ID if needed"""
        if id is None:
            id = 0 # get the first available ID, starting at 0
            while id in _dict: id += 1
        else: id = int(id)

        _dict[id] = _class(*args, id)

    @staticmethod
    def new_point(x, y, id=None):
        Manager.new_obj((x, y), Point, Manager.points, id)

    @staticmethod
    def new_link(x, y, id=None):
        Manager.new_obj((x, y), Link, Manager.links, id)

    @staticmethod
    def new_image(name, id=None):
        Manager.new_obj((name,), Image, Manager.images, id)

class Point:
    """Point in the graph, can be attached to various links and have text and an image"""
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id

        self.text = None # rendered pygame font, None for no text
        self.image = -1 # image id, -1 for no image

class Link:
    """Link between two points in the graph"""
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.strength = 5

        # linked points
        self.a = None
        self.b = None

class Image:
    """Pygame surface loaded from image file"""
    def __init__(self, name, id):
        self.name = name
        self.surf = pygame.image.load('images/%s.png' %name)

class Graph:
    """Graph manager, for displaying the graph, handling scroll, and updating elements"""
    W = 900
    H = 500

    def __init__(self):
        if not pygame.get_init(): raise Exception('Pygame not initialized')

        self.screen = pygame.display.set_mode((self.W, self.H))
        self.clock = pygame.time.Clock()
        self.ticks = pygame.time.get_ticks

    def update(self):
        """Handles pygame event loop, updates elements, displays the graph"""
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                quit()
                return # just in case

        # update visible elements

        # render graph

def syntax_error(y, expression):
    raise SyntaxError('Could not parse save file at line %d: "%s"' %(y+1, expression))

def open_save(path):
    global objects

    with open(path) as f: lines = f.read().split('\n')
    for y, raw in enumerate(lines):
        # format line: remove leading and trailing spaces, double spaces, comments
        line = ''
        prev = ' '
        for c in raw:
            if c == prev == ' ': continue
            if c == '#': break
            line += c
            prev = c
        line = line.rstrip()
        if not line: continue

        # get command from line
        line = line.split(' ')
        cmd = line[0]
        args = line[1:]

        match cmd:
            case 'I':
                if len(args) != 2: syntax_error(y, raw)
                Manager.new_image(*args)
            case 'P':
                if len(args) != 3: syntax_error(y, raw)
                Manager.new_point(*args)
            case _: syntax_error(y, raw)

pygame.init()

open_save('test_save.txt')
