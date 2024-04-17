import pygame
from pygame.locals import *

def syntax_error(y, expression):
    """Used to help handling file parsing errors"""
    raise SyntaxError('Could not parse save file at line %d: "%s"' %(y+1, expression))

class Palette:
    """Static class, used to store colors data"""
    text = (255, 255, 255)
    background = (40, 40, 43)
    neutral = (80, 80, 85)
    red = (255, 0, 0)

def ask_input_box(message, cast, max_width=400, forbidden='', allow_empty=False):
    """Input box, freezes other actions to ask for user value.
Param cast: function used to check for input format
Param forbidden: don't allow these characters"""

    # make a darkened background from the current screen state
    dark = pygame.Surface((Graph.W, Graph.H), SRCALPHA)
    dark.fill((0, 0, 0, 127))
    background = pygame.Surface((Graph.W, Graph.H))
    background.blit(screen, (0, 0))
    background.blit(dark, (0, 0))
    
    # make box for the UI
    pygame.draw.rect(background, Palette.background, Rect((Graph.W*0.2, Graph.H*0.2, Graph.W*0.6, Graph.H*0.6)))
    text = font.render(message, True, Palette.text)
    background.blit(text, (Graph.W/2 - text.get_width()/2, Graph.H*0.3))

    # init error text
    error_text = [font.render('Error: incorrect value', True, Palette.red),
                  font.render(' Error: text too long', True, Palette.red),
                  font.render("Error: can't be empty", True, Palette.red)]
    error_pos = (Graph.W/2 - error_text[0].get_width()/2, Graph.H*0.3 + 20)

    # get the "_" character width, useful later on
    blink_w = font.render('_', True, Palette.text).get_width()

    # loop until the user presses Enter
    string = ''
    run = True
    while run:
        enter = False # for when to try to get out of the loop
        for event in pygame.event.get():
            if event.type == QUIT:
                return # returning None should trigger a quit externally
            elif event.type == KEYDOWN:
                if event.key == K_BACKSPACE: string = string[:-1]
                elif event.key == K_RETURN or event.key == K_KP_ENTER:
                    enter = True
                elif event.unicode not in forbidden:
                    string += event.unicode

        # add blinking cursor for displayed text
        blink = ticks()%1000 < 600
        text = font.render(string + ('_' if blink else ''), True, Palette.text)

        # handle incorrect value
        error = 0
        try: cast(string)
        except: error = 1
        if text.get_width() > max_width:
            error = 2
            # trim the displayed text
            temp = text
            text = pygame.Surface((max_width, 16), SRCALPHA)
            text.blit(temp, (0, 0))
        if enter and not error:
            if not string and not allow_empty: error = 3
            else: run = False

        screen.blit(background, (0, 0))
        if error: screen.blit(error_text[error-1], error_pos)

        # draw actual textbox
        w = max(text.get_width() + (0 if blink else blink_w), 200) # minimum input size
        x = Graph.W/2 - w/2
        y = Graph.H/2 - 8
        pygame.draw.rect(screen, Palette.neutral, Rect((x-4, y-4), (w+8, 24)))
        screen.blit(text, (x, y))

        pygame.display.flip()
        clock.tick(FPS)

    return cast(string)

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

class GraphObject:
    def update(self, events):
        raise NotImplementedError

    def collide(self, pos):
        raise NotImplementedError

class Point(GraphObject):
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

    def collide(self, pos):
        x, y = graph.get_pos(self.x, self.y)
        return x-10 < pos[0] < x+10 and y-10 < pos[1] < y+10

    def update(self, events):
        x, y = graph.get_pos(self.x, self.y)
        pygame.draw.rect(screen, Palette.text, Rect((x-3, y-3), (6, 6)))

class Link(GraphObject):
    """Link between two points in the graph"""
    def __init__(self, p1, p2, id):
        self.x = x
        self.y = y
        self.id = id
        self.strength = 5

        # linked points IDs
        self.p1 = p1
        self.p2 = p2

    def update(self, events):
        pass

class Image:
    """Pygame surface loaded from image file"""
    def __init__(self, name, id):
        self.name = name
        self.surf = pygame.image.load('images/%s.png' %name)

class UI:
    """UI elements on top of the screen: help, info about selection"""
    def __init__(self):
        self.surf = pygame.Surface((Graph.W, 40), SRCALPHA) # blitted, cached surface
        self.help_text = font.render('P: new point, S: save file, O: open file, I: load image', True, Palette.text)
        self.update_surf()

    def update_surf(self):
        """Updates cached surface: redraw background, add elements depending on selection"""
        pygame.draw.rect(self.surf, Palette.neutral, Rect((0, 0), (Graph.W, 40)))

        if graph.selection is None:
            self.surf.blit(self.help_text, (11, 11))

    def update(self):
        
        self.surf.set_alpha(100 if pygame.mouse.get_pos()[1] < 40 else 255)
        screen.blit(self.surf, (0, 0))

class Graph:
    """Graph manager, for displaying the graph, handling scroll, and updating elements"""
    W = 900
    H = 500

    def __init__(self):
        self.scroll_x = 0
        self.scroll_y = 0
        self.zoom = 1
        self.unit_size = 100 # graph unit to pixel ratio

        self.save_file = None
        self.objects = []

        # movement utilities
        self.drag_start = None # moved/scroll element pos when drag started
        self.drag_mouse_start = None # mouse pos when drag started
        self.selection = None # selected GraphPoint, or None if no selection

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

    def get_pos(self, x, y):
        """Returns the position, in screen coordinates, corresponding to a position in graph coordinates"""
        z = self.zoom * self.unit_size
        return (x - self.scroll_x) * z + self.W/2, (y - self.scroll_y) * z + self.H/2

    def visible(self, x, y):
        """Returns true if point is visible (taking scroll and zoom into account), else false"""
        x, y = self.get_pos(x, y)
        return 0 <= x < self.W and 0 <= y < self.H

    def update(self, events):
        """Updates objects and menu, displays the graph"""
        # move and zoom
        pressed = pygame.mouse.get_pressed()[0]

        # get visible graph objects now, useful for collision checks
        visible_p = [] # points
        for id, point in Manager.points.items():
            if self.visible(point.x, point.y):
                visible_p.append(id)
        visible_l = [] # links
        for id, link in Manager.links.items():
            if link.p1 in visible_p or link.p2 in visible_p:
                visible_l.append(id)

        # events check
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.selection = None
                for point in visible_p:
                    if self.selection is not None: break
                    point = Manager.points[point]
                    if point.collide(event.pos): self.selection = point
                for link in visible_l:
                    if self.selection is not None: break
                    link = Manager.points[link]
                    if point.collide(event.pos): self.selection = link

                # start dragging
                if self.selection is None:
                    self.drag_start = (self.scroll_x, self.scroll_y)
                else:
                    self.drag_start = (self.selection.x, self.selection.y)
                self.drag_mouse_start = event.pos

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                # stop dragging
                self.drag_start = None
                self.drag_mouse_start = None

            # zoom
            elif event.type == MOUSEWHEEL and not pressed:
                if event.y > 0: self.zoom *= 1.2 # zoom in
                elif self.zoom > 0.1: self.zoom /= 1.2 # zoom out
                else: self.zoom = 0.1 # min zoom

        if self.drag_start is not None:
            x, y = self.drag_start
            x0, y0 = self.drag_mouse_start
            x1, y1 = pygame.mouse.get_pos()
            m = 1/self.zoom/self.unit_size
            dx = (x0-x1) * m
            dy = (y0-y1) * m
            if self.selection is None:
                self.scroll_x = x + dx
                self.scroll_y = y + dy
            else:
                self.selection.x = x - dx
                self.selection.y = y - dy

        # update and render menu and UI
        screen.fill(Palette.background)

        # update and render graph objects
        for link in visible_l:
            Manager.links[link].update(events)
        for point in visible_p:
            Manager.points[point].update(events)

FPS = 60
pygame.init()

screen = pygame.display.set_mode((Graph.W, Graph.H))
pygame.display.set_caption('Progression graph')
font = pygame.font.SysFont('consolas', 16)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks

graph = Graph()
graph.open('test_save.txt')
graph.save()

dt = 0 # time passed in last frame, in seconds
run = True
while run:
    # handle pygame event loop
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT: run = False
        elif event.type == KEYDOWN:
            if event.key == K_p:
                print(ask_input_box('Test message box', int))

    graph.update(events)
    pygame.display.flip()
    dt = clock.tick(FPS)/1000

pygame.quit()
quit()
