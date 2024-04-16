import pygame
from pygame.locals import *

def syntax_error(y, expression):
    """Used to help handling file parsing errors"""
    raise SyntaxError('Could not parse save file at line %d: "%s"' %(y+1, expression))

class Palette:
    """Static class, used to store colors data"""
    text = (255, 255, 255)
    background = (50, 50, 50)

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
        Manager.new_obj((float(x), float(y)), Point, Manager.points, id)

    @staticmethod
    def new_link(x, y, id=None):
        Manager.new_obj((float(x), float(y)), Link, Manager.links, id)

    @staticmethod
    def new_image(name, id=None):
        Manager.new_obj((name,), Image, Manager.images, id)

    @staticmethod
    def attach_image(point_id, image_id):
        """Sets the image reference of a point"""
        points[int(point_id)].set_image(image_id)

    @staticmethod
    def attach_text(point_id, text):
        """Sets the text of a point"""
        points[int(point_id)].set_text(text)

class Point:
    """Point in the graph, can be attached to various links and have text and an image"""
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id

        self.text = ''
        self.text_surf = None # rendered pygame font, None for no text
        self.image = -1 # image id, -1 for no image

    def set_text(self, text):
        """Sets the point's text and updates its text Surface"""
        self.text = text
        self.text_surf = None if not text else font.render(text, True, Palette.text)

    def set_image(self, image):
        self.image = int(image)

    def remove_image(self):
        self.image = -1

class Link:
    """Link between two points in the graph"""
    def __init__(self, p1, p2, id):
        self.x = x
        self.y = y
        self.id = id
        self.strength = 5

        # linked points IDs
        self.p1 = p1
        self.p2 = p2

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
        self.save_file = None
        self.objects = []

    def open(self, save_file):
        """Sets self.save_file and load save file"""
        self.save_file = save_file

        # TODO: handle deletion of old objects

        with open(save_file) as f: lines = f.read().split('\n')
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

            # execute action depending on command
            match cmd:
                case 'P': # add new point
                    if len(args) != 3: syntax_error(y, raw)
                    Manager.new_point(*args)
                case 'L': # add new link
                    if len(args) != 3: syntax_error(y, raw)
                    Manager.new_link(*args)
                case 'I': # add new image
                    if len(args) != 2: syntax_error(y, raw)
                    Manager.new_image(*args)
                case 'Ai': # attach an image to a point
                    if len(args) != 2: syntax_error(y, raw)
                    Manager.attach_image(*args)
                case 'At': # attach text to a point
                    if len(args) != 2: syntax_error(y, raw)
                    Manager.attach_text(*args)
                case _: syntax_error(y, raw)

    def save(self):
        """Save graph contents into self.save_file"""
        content = []

        if self.save_file is None: raise ValueError('No save loaded')

        # points
        content.append('# POINTS')
        for id, point in Manager.points.items():
            content.append('P %d %d %d' %(point.x, point.y, id))

        # links
        content += ('', '# LINKS')
        for id, link in Manager.links.items():
            content.append('L %d %d %d' %(Manager.points[link.p1].id, Manager.points[link.p2].id, id))

        # images
        content += ('', '# IMAGES')
        for id, image in Manager.images.items():
            content.append('I %s %d' %(image.name, image.id))

        # images attached to points
        content += ('', '# LINK IMAGES')
        for id, point in Manager.points.items():
            if point.image != -1:
                content.append('Ai %d %d' %(id, Manager.images[point.image].id))

        # text attached to points
        content += ('', '# TEXT')
        for id, point in Manager.points.items():
            if point.text != '':
                content.append('At %d %d' %(id, point.text.id))

        # save into file
        with open(self.save_file, 'w') as f: f.write('\n'.join(content))

    def update(self, events):
        """Updates objects and menu, displays the graph"""
        # update and render menu and UI
        screen.fill(Palette.background)

        # update and render graph objects

FPS = 60
pygame.init()

screen = pygame.display.set_mode((Graph.W, Graph.H))
font = pygame.font.SysFont('consolas', 16)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks

graph = Graph()
graph.open('test_save.txt')
graph.save()

while True:
    # handle pygame event loop
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            quit()

    graph.update(events)
    pygame.display.flip()
    clock.tick(FPS)
