import pygame
from zipfile import ZipFile
from math import sqrt, floor, log
from os.path import exists, splitext, basename
from pygame.locals import *

# lower fps if window inactive, but needs win32 utils to do that
from sys import platform
if 'win' in platform:
    import win32gui
else:
    class win32gui:
        def GetForegroundWindow(*args): return True

from tkinter.filedialog import askopenfilename, asksaveasfilename

def get_popup_bg(message):
    """Creates the base for a popup. Returns the created background from a message string."""

    # make a darkened background from the current screen state
    dark = pygame.Surface((Graph.W, Graph.H), SRCALPHA)
    dark.fill((0, 0, 0, 127))
    background = pygame.Surface((Graph.W, Graph.H))
    background.blit(screen, (0, 0))
    background.blit(dark, (0, 0))

    # make a box for the UI
    pygame.draw.rect(background, Palette.background, Rect((Graph.W*0.15, Graph.H*0.15, Graph.W*0.7, Graph.H*0.7)))

    # draw the text, can have multiple lines
    y = Graph.H*0.3
    for line in message.split('\n'):
        text = font.render(line, True, Palette.text)
        background.blit(text, (Graph.W/2 - text.get_width()/2, y))
        y += 16

    old = pygame.Surface((Graph.W, Graph.H))
    old.blit(screen, (0, 0))
    return old, background

def ask_input_box(message, cast, check=lambda s: len(s), max_width=400):
    """Input box, freezes other actions to ask for user value.
    Param message: message to display. Can contain newlines, but may overflow onto the input
    Param cast: function used to check for input format
    Param check: lambda used to check if the entry value is valid"""

    # get base popup
    old_screen, background = get_popup_bg(message)

    # init error text
    error_text = [font.render("Error: can't decode value", True, Palette.red),
                  font.render('  Error: text too long', True, Palette.red),
                  font.render('  Error: invalid value', True, Palette.red)]
    error_pos = (Graph.W/2 - error_text[0].get_width()/2, Graph.H*0.3 + 20)

    button1 = Button('Add', Graph.W/2 - 120, Graph.H*2/3)
    button2 = Button('Cancel', Graph.W/2 + 120, Graph.H*2/3)

    # loop until the user presses Enter
    string = ''
    run = True
    while run:
        enter = False # for when to try to get out of the loop
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.event.post(pygame.event.Event(QUIT))
                return
            elif event.type == KEYDOWN:
                if event.key == K_BACKSPACE: string = string[:-1]
                elif event.key == K_ESCAPE: return
                elif event.key == K_RETURN or event.key == K_KP_ENTER:
                    enter = True
                else:
                    string += event.unicode
            elif event.type == VIDEORESIZE:
                graph.resize()

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
        if not check(string): error = 3
        if enter and not error: run = False

        screen.blit(background, (0, 0))
        if error: screen.blit(error_text[error-1], error_pos)

        # draw actual textbox
        w = max(text.get_width() + (0 if blink else char_w), 200) # minimum input size
        x = Graph.W/2 - w/2
        y = Graph.H/2 - 8
        pygame.draw.rect(screen, Palette.neutral, Rect((x-4, y-4), (w+8, 24)))
        screen.blit(text, (x, y))

        # update buttons
        if button1.update(events) and not error: run = False
        if button2.update(events): return

        pygame.display.flip()
        clock.tick(FPS)

    # restore old screen state in case there are multiple popups back-to-back, darkening the screen
    screen.blit(old_screen, (0, 0))

    return cast(string)

def ask_button(message, buttons):
    """Input with message. The returned value is either None if quitted the window or pressed Escape,
    or the value associated with each of the buttons.
    Param message: message to be displayed, can use newlines, but not too many as it would fill the screen
    Param buttons: list (can be empty) of pairs (returned value, 'button text')"""

    old_screen, background = get_popup_bg(message)

    # set up buttons objects, next to one another
    offset = Graph.W/2 - 60*(len(buttons)-1)
    i = 0
    for res, text in buttons:
        buttons[i] = (res, Button(text, offset + 120*i, Graph.H/2, 100))
        i += 1

    run = True
    res = None # returned result
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                run = False
                res = None
                pygame.event.post(pygame.event.Event(QUIT))
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                run = False
                res = None
            elif event.type == VIDEORESIZE:
                graph.resize()

        screen.blit(background, (0, 0))

        for value, button in buttons:
            if button.update(events):
                run = False
                res = value

        pygame.display.flip()
        clock.tick(FPS)

    screen.blit(old_screen, (0, 0))
    return res

def import_image():
    files = askopenfilename(title='Import image(s)', filetypes=(('Image files', ('png', 'jpg', 'bmp', 'gif')),), multiple=True)

    if type(files) == tuple and len(files): # double protection in case API changes
        for file in files:
            try:
                # None to tell the constructor that the image comes from the disk
                Manager.new_image(file, None)
            except:
                print('Error loading image')

def ask_filename(new=False):
    """Triggers a filedialog to select a save file, and returns the file.
    If new is set to True, the function will be used for choosing a new file name."""

    filetype = (('Progression Graph File', '.graph'),)

    if new:
        file = asksaveasfilename(title='Save to file', filetypes=filetype)

        # make sure the file has the right extension
        if file and not file.endswith('.graph'): file += '.graph'

    else: file = askopenfilename(title='Open save file', filetypes=filetype)

    pygame.event.get() # don't trigger this infinitely
    return file

def image_selector():
    """Graphical image selector, displays all loaded images into a grid for the user to select"""

    # get and resize all loaded images
    images = list(Manager.images.values())
    ids = list(Manager.images.keys())
    for i, image in enumerate(images):
        surf = image.surf
        w, h = surf.get_size()
        if w > h: w, h = 50, 50*h/w
        else: w, h = 50*w/h, 50
        images[i] = pygame.transform.scale(surf, (w, h))

    w = (Graph.W-50) // 90 # images in one row
    iheight = len(images)//w*90 + 50 # total images table height
    vheight = Graph.H-46 # visible height
    scroll = 0
    do_scroll = iheight > vheight

    cancel = Button('Cancel', Graph.W/2, Graph.H-36)
    border_col = Palette.mult(Palette.background, 1.2)

    run = True
    selection = None
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                run = False
                selection = None
                pygame.event.post(pygame.event.Event(QUIT))
            elif event.type == MOUSEWHEEL and do_scroll:
                scroll = min(max(scroll - 20*event.y, 0), iheight-vheight)
            elif event.type == MOUSEBUTTONDOWN and selection is not None:
                run = False # clicked on an image
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                run = False
                res = None
            elif event.type == VIDEORESIZE:
                graph.resize()

        screen.fill(Palette.background)

        # draw scrollbar if needed
        if do_scroll:
            y = scroll * vheight / (iheight-20)
            h = vheight*vheight/iheight - 20
            pygame.draw.rect(screen, Palette.text, Rect(Graph.W-15, 10+y, 5, h))

        # get mouse data and display images
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        selection = None
        for i, image in enumerate(images):
            x, y = 50 + 90*(i%w), 50 + 90*(i//w) - scroll
            if -50 < y < vheight:
                if x-10 <= mx < x+60 and y-10 <= my < y+60:
                    # image hovered
                    pygame.draw.rect(screen, Palette.neutral, Rect(x-10, y-10, 70, 70))
                    if click:
                        selection = i # image clicked
                        run = False
                screen.blit(image, (x, y))

        # display bottom border and Cancel button
        pygame.draw.rect(screen, border_col, Rect(0, vheight, Graph.W, 46))
        if cancel.update(events):
            run = False
            selection = None

        pygame.display.flip()
        clock.tick(FPS)

    if selection is None: return
    return Manager.images[ids[selection]]

class Button:
    """Simple button widget to use in popups"""

    def __init__(self, text, x, y, min_w=200):
        """Creates a button at pos (x, y) on the screen (top center),
        with width of at least min_w pixels"""

        self.x = x
        self.y = y

        # create the base text surface and pad it,
        # also add space on the sides if needed to get to min_w width
        text = font.render(text, True, Palette.text)
        wt, ht = text.get_size()
        w = min_w if wt < min_w else wt
        self.w, self.h = w+10, ht+10

        tsurf = pygame.Surface((self.w, self.h), SRCALPHA)
        tsurf.blit(text, (self.w/2 - wt/2 + 5, 5))

        # make textures depending on the button state: normal, hovered, selected
        self.surfs = [None]*3
        for i, mult in enumerate((1, 1.2, 1.5)):
            surf = pygame.Surface((self.w, self.h), SRCALPHA)
            surf.fill(Palette.mult(Palette.neutral, mult))
            surf.blit(tsurf, (0, 0))
            self.surfs[i] = surf

    def update(self, events):
        """Returns True if the button is clicked, False otherwise.
        The button is also updated and drawn on the screen"""

        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        hovered = self.x - self.w/2 <= mx <= self.x + self.w/2 and \
                  self.y <= my <= self.y + self.h

        res = False
        for event in events:
            if event.type == MOUSEBUTTONUP:
                if hovered:
                    res = True
                    break

        # display the button
        screen.blit(self.surfs[(click+1) * hovered], (self.x - self.w/2, self.y))

        return res

class Error:
    """Static class, used to make handling exceptions easier"""

    @staticmethod
    def syntax(y, expression):
        """Used to help handling file parsing errors"""
        ask_button('Could not parse save file at line %d:\n"%s"\nAborting file loading' %(y+1, expression), [(0, 'OK')])

    @staticmethod
    def corrupted_file(comment, success):
        """Used when a non-critical file parsing error has been found. This doesn't interrupt file loading."""
        load_text = 'The file will still be loaded, check for side-effects.' if success else ''
        ask_button('Detected save file corruption:\n"%s"\n%s' %(comment, load_text), [(0, 'OK')])

    @staticmethod
    def zipfile(error):
        """Used when an error occurs while loading the save zip file"""
        ask_button('Error while parsing for files in the save file:\n"%s"\nAborting file loading' %error, [(0, 'OK')])

class Palette:
    """Static class, used to store colors data"""
    text = (255, 255, 255)
    background = (40, 40, 43)
    neutral = (80, 80, 85)
    red = (255, 0, 0)
    zoom_bar = ((200, 200, 200), (170, 170, 170))

    # States base colors. Nodes and links colors are derived from them
    states = ((255, 0, 0), (127, 127, 0), (0, 255, 0))

    link = [None]*3 # contains a nested list: [[todo normal, todo hovered, todo selected], [doing], [completed]]
    # same for box colors
    box_outer = [None]*3
    box_sep = [None]*3
    box_inner = [None]*3

    init = False # to make sure Palette is init

    @staticmethod
    def __init__():
        Palette.init = True

        for i, col in enumerate(Palette.states):
            # init link colors
            Palette.link[i] = (col, Palette.mult(col, 0.6, 127), Palette.mult(col, 0.3, 192))

            # init node colors
            Palette.box_outer[i] = (Palette.mult(col, 0.4, 50), Palette.mult(col, 0.4, 60), Palette.mult(col, 0.4, 80))
            Palette.box_sep[i] = (Palette.mult(col, 0.2, 0), Palette.mult(col, 0.2, 20), Palette.mult(col, 0.2, 40))
            Palette.box_inner[i] = (Palette.mult(col, 0.3, 100), Palette.mult(col, 0.3, 120), Palette.mult(col, 0.3, 150))

    @staticmethod
    def mult(col, x, add=0):
        """Changes the exposition of a color: x=1 does nothing, x=0 is black, and colors are clamped.
        You can also specify add, an offset applied to all the color's components.

        Warning: only supports RGB colors"""

        if x == 1 and not add: return col

        r, g, b = col[0]*x + add, col[1]*x + add, col[2]*x + add
        return (255 if r > 255 else r, 255 if g > 255 else g, 255 if b > 255 else b)

Palette.__init__()

class Manager:
    """Manager for all objects. Should be used to create and remove new objects, as it manages the ID system."""

    # key: ID, value: object
    nodes = {}
    links = {}
    images = {}

    @staticmethod
    def new_obj(args, _class, _dict, id):
        """Adds a new object to the corresponding dictionary, assigns an ID if needed"""
        if id is None:
            id = 0 # get the first available ID, starting at 0
            while id in _dict: id += 1
        else: id = int(id)

        _dict[id] = _class(*args, id)
        return _dict[id]

    @staticmethod
    def new_node(x, y, rank, state, id=None):
        result = Manager.new_obj((float(x), float(y), int(rank), int(state)), Node, Manager.nodes, id)

        # sort nodes to display the more important ones on top
        keys = sorted(Manager.nodes.keys(), key=lambda key: Manager.nodes[key].rank)
        copy = dict(Manager.nodes)
        Manager.nodes = {}
        for key in keys:
            Manager.nodes[key] = copy[key]

        return result

    @staticmethod
    def new_link(n1, n2, id=None):
        n1 = Manager.nodes[int(n1)]
        n2 = None if n2 is None else Manager.nodes[int(n2)]
        return Manager.new_obj((n1, n2), Link, Manager.links, id)

    @staticmethod
    def new_image(name, content, id=None):
        return Manager.new_obj((name, content), Image, Manager.images, id)

    @staticmethod
    def attach_image(node_id, image_id):
        """Sets the image reference of a node"""
        Manager.nodes[int(node_id)].set_image(Manager.images[int(image_id)])

    @staticmethod
    def attach_text(node_id, text):
        """Sets the text of a node"""
        Manager.nodes[int(node_id)].set_text(None if text == '' else text)

    @staticmethod
    def reset():
        Manager.nodes = {}
        Manager.links = {}
        Manager.images = {}

class GraphObject:
    def update(self, events):
        raise NotImplementedError

    def collide(self, pos):
        raise NotImplementedError

class Node(GraphObject):
    """Node in the graph, can be attached to various links and have text and an image"""
    N_RANKS = 5
    rank_sizes = [40, 50, 60, 80, 100]
    assert len(rank_sizes) == N_RANKS

    def __init__(self, x, y, rank, state, id):
        self.x = x
        self.y = y
        self.state = state
        self.id = id

        self.text = None # text, None for no text
        self.image = None # image, None for no image

        self.surf = None # should always contain the surface with the right size
        # rendered pygame fonts, None for no text
        # if text, will contain [shortened text, full text (on hover/selection)]
        self.text_surfs = None
        self.size = None # should contain the size according to self.rank

        self.set_rank(rank) # init self.rank, self.size and self.surfs

    @staticmethod
    def get_rank_size(rank):
        """Returns the size from a particular node rank, handles incorrect values"""
        rank = min(max(rank, 0), Node.N_RANKS-1)
        return Node.rank_sizes[rank]

    def set_rank(self, rank):
        self.rank = rank
        self.size = Node.get_rank_size(rank)
        self.set_image(self.image)

        # update attached links
        for link in Manager.links.values():
            if self == link.n1 or self == link.n2:
                link.refresh()

    def cycle_rank(self):
        self.set_rank((self.rank+1) % Node.N_RANKS)

    def cycle_state(self):
        # order: todo, completed, doing
        self.state = (self.state-1) % 3
        self.set_image(self.image) # update self._surf

        for link in Manager.links.values():
            if self == link.n1 or self == link.n2:
                link.refresh()

    @staticmethod
    def black_back(surf):
        """Adds a semi-transparent Palette.background background to a surface"""
        new = pygame.Surface(surf.get_size(), SRCALPHA)

        black = pygame.Surface(surf.get_size(), SRCALPHA)
        black.fill(Palette.background)
        black.set_alpha(127)
        new.blit(black, (0, 0))
        new.blit(surf, (0, 0))

        return new

    def set_text(self, text):
        """Sets the node's text and updates its text Surface"""
        self.text = text
        if text is None:
            self.text_surfs = None
        else:
            max_width = 100
            if len(text)*char_w2 > max_width:
                # make unselected surface: cut text
                surf = font2.render(text[:int(max_width/char_w2)-3]+'...', True, Palette.text)
                self.text_surfs = [Node.black_back(surf), None]

                # make selected surface: word wrap if necessary
                # get words and split them if bigger than max_width
                words = []
                for word in text.split(' '):
                    while len(word)*char_w2 > max_width:
                        i = int(max_width/char_w2)-1
                        add, word = word[:i]+'-', word[i:]
                        words.append(add)
                    words.append(word)

                lines = ['']
                i = 0
                for word in words:
                    space = ' ' if lines[i] else ''
                    if len(lines[i]+space+word) * char_w2 > max_width:
                        if lines[i] == '':
                            lines[i] += word
                            lines.append('')
                        else: lines.append(word)
                        i += 1
                    else:
                        lines[i] += space+word

                # assemble lines into one surface
                width = len(max(lines, key=lambda l: len(l)))*char_w2
                surf = pygame.Surface((width, 12*len(lines)), SRCALPHA)
                for y, line in enumerate(lines):
                    line = font2.render(line, True, Palette.text)
                    surf.blit(line, (width/2 - line.get_width()/2, y*12))

                self.text_surfs[1] = Node.black_back(surf)
            else:
                # same text for both unselected and selected
                surf = Node.black_back(font2.render(text, True, Palette.text))
                self.text_surfs = [surf, surf]

    def set_image(self, image):
        """Sets and resizes self.surfs depending on self.size"""
        s = self.size
        self.image = image
        self.surfs = [None]*3

        # draw empty box
        m = int(s/10) # outline margin
        if m > 5: m = 5

        for i in range(3): # set normal, hovered, and selected surfaces
            self.surfs[i] = pygame.Surface((s, s))
            self.surfs[i].fill(Palette.box_outer[self.state][i])
            pygame.draw.rect(self.surfs[i], Palette.box_sep[self.state][i], Rect(m-1, m-1, s - m*2 + 2, s - m*2 + 2))
            pygame.draw.rect(self.surfs[i], Palette.box_inner[self.state][i], Rect(m, m, s - m*2, s - m*2))

        # if image, resize it and add it to the surface
        if image is not None:
            w, h = image.surf.get_size()
            s -= m*2 + 2
            if w > h: w, h = s, s*h/w
            else: w, h = s*w/h, s

            image = pygame.transform.scale(image.surf, (w, h))
            for i in range(3):
                self.surfs[i].blit(image, (m+1, m+1))

    def collide(self, pos):
        """Checks if the given position in screen coordinates intersects with the node"""
        x, y = graph.project(self.x, self.y)
        s = self.size/2
        return x-s < pos[0] < x+s and y-s < pos[1] < y+s

    def visible(self):
        """Returns True if visible, taking scroll and zoom into account, otherwise returns False"""
        x, y = graph.project(self.x, self.y)
        s = self.size/2
        return -s <= x < Graph.W+s and -s <= y < Graph.H+s

    def update(self, events, surf, project, force_text=False):
        """Called by grah update() each frame. Blits a surface onto surf at the position given by the projector.
        The text is cut when not hovered/selected, but this can be overriden by setting force_text to True"""
        x, y = project(self.x, self.y)

        # use a different texture when hovered
        i = 2 if self == graph.selection else 1 if self == graph.hovered else 0
        surf.blit(self.surfs[i], (x - self.size/2, y - self.size/2))

        # draw text
        if self.text_surfs is not None:
            t = self.text_surfs[force_text or bool(i)]
            surf.blit(t, (x - t.get_width()/2, y + self.size/2 + 5))

class Link(GraphObject):
    """Link between two nodes in the graph"""

    rank_sizes = [2, 3, 5, 8, 15]
    assert len(rank_sizes) == Node.N_RANKS

    def __init__(self, n1, n2, id):
        self.id = id

        # linked nodes
        self.n1 = n1
        self.n2 = n2 # can be None if just created

        self.refresh() # set self.rank, self.size and self.state

    @staticmethod
    def get_rank_size(rank):
        """Returns the size from a particular link rank, handles incorrect values"""
        rank = min(max(rank, 0), Node.N_RANKS-1)
        return Link.rank_sizes[rank]

    def refresh(self):
        """Triggered for all links when a node changes rank or state, to update the link's properties"""
        if self.n2 is None: self.rank = self.n1.rank
        else: self.rank = max(self.n1.rank, self.n2.rank)

        self.size = Link.get_rank_size(self.rank)

        if self.n2 is None: self.state = self.n1.state
        else: self.state = max(self.n1.state, self.n2.state)

    def collide(self, mpos):
        """Checks if the link collides with the mouse, with self.size tolerance.
        How it works:
        Let p1 and p2 be the two link end points once projected into screen space, and M the mouse pos.
        Let (D) be the line between p1 and p2, and M' the approximation of M projected onto (D).
        M' is hence the point in (D) that is at the same distance from p1 as M.

        The goal of this method is to compute the distance (squared) between M' and M,
        and compare it to self.size (squared). If the former is smaller, a collision is registered.

        During the calculation, we compute t, directional vector of (D). If t is not in [0, 1],
        the projected point is outside the segment of (D) that sits between p1 and p2,
        hence there is no collision in this case.

        In case p1 == p2, the line formed by the link is treated as a circle of radius self.size
        for collision checks. This shouldn't usually matter as the ends of the links are nodes
        and their collision detection runs first in Graph.update.
        """
        x1, y1 = graph.project(self.n1.x, self.n1.y)
        x2, y2 = graph.project(self.n2.x, self.n2.y)
        xm, ym = mpos
        s2 = self.size*self.size
        if x1 == x2 and y1 == y2:
            dx, dy = xm-x1, ym-y1
            return dx*dx + dy*dy <= s2

        # calculate t
        dx, dy = xm-x1, ym-y1
        p1_m = dx*dx + dy*dy
        dx, dy = x2-x1, y2-y1
        p1_p2 = dx*dx + dy*dy
        t = sqrt(p1_m/p1_p2)
        if t < 0 or t > 1: return False

        # calculate M' position
        xm2, ym2 = x1 + dx*t, y1 + dy*t

        dx, dy = xm-xm2, ym-ym2
        return dx*dx + dy*dy <= s2

    def update(self, events, surf, project):
        """Called by grah update() each frame. Draws a line onto surf at the position given by the projector."""

        # get end nodes screen coordinates
        pos1 = project(self.n1.x, self.n1.y)
        if self.n2 is None:
            # the link is currently being drawn
            pos2 = pygame.mouse.get_pos()
        else: pos2 = project(self.n2.x, self.n2.y)

        # get color depending on if the link is hovered/selected
        i = 2 if self == graph.selection else 1 if self == graph.hovered else 0
        col = Palette.link[self.state][i]
        pygame.draw.line(surf, col, pos1, pos2, self.size)

class Image:
    """Pygame surface loaded from image file.
    The stored path is cut to the base name, to then be cached in the save zip file."""

    def __init__(self, path, content, id):
        """Loads an image from the save zip file (content is a bytes array)
        or from the disk (content is None, and path is used to load the image)"""

        self.path = basename(path)
        self.name = splitext(self.path)[0]
        if content is None:
            # load image from disk
            self.surf = pygame.image.load(path).convert_alpha()
        else:
            # get the width, height, and image data from content
            i = content.index(b'.')
            w = int(content[:i].decode())
            content = content[i+1:]
            i = content.index(b'.')
            h = int(content[:i].decode())
            content = content[i+1:]
            self.surf = pygame.image.frombytes(content, (w, h), 'RGBA')
        self.id = id

class UI:
    """UI elements on top of the screen: help, info about selection"""

    def __init__(self):
        self.surf = None # blitted, cached surface
        self.zoom_surf = None

        self.raw_texts = [('Left click: select elements, drag with mouse: move object/camera, mouse scroll: zoom in/out, S: save file, W: save as file, N: new file, O: open file, P: new node, I: import image to the images bank, E: export graph to image (no background), F: export with background'),
                          'Del: delete link']
        # edit texts to discriminate between deleting a node, its image or its text
        text = 'L: start link, I: attach image from the bank, T: add text, R: cycle rank, S: cycle state, Del: delete %s'
        self.raw_texts.append(text %'node')
        self.raw_texts.append(text %"the node's text")
        self.raw_texts.append(text %"the node's image")
        for i in range(len(self.raw_texts)):
            self.raw_texts[i] += ', Z: reset zoom, A: reset camera pos+zoom, Q: quit'

        self.process_raw_texts()

        # zoom indicator
        self.last_zoom = 0

    def process_raw_texts(self):
        """Makes text surfaces out of self.raw_texts"""

        self.text = [None]*len(self.raw_texts)
        for i, text in enumerate(self.raw_texts):
            # word wrap
            lines = ['']
            j = 0
            for word in text.split(' '):
                space = ' ' if lines[j] else ''
                if len(lines[j]+space+word) * char_w > Graph.W - 24:
                    if lines[j] == '':
                        lines[j] += word
                        lines.append('')
                    else: lines.append(word)
                    j += 1
                else:
                    lines[j] += space+word

            # add all lines of a text into one surface
            h = len(lines)*16
            y = 0
            surf = pygame.Surface((Graph.W, h), SRCALPHA)

            for line in lines:
                surf.blit(font.render(line, True, Palette.text), (0, y))
                y += 16
            self.text[i] = surf

        self.update_surf(True)

    def update_surf(self, init=False):
        """Updates cached Surface: redraws background, adds elements depending on selection.
        If init is True (should be set to True only on init), graph is assumed to not exist (same as when graph.selection is None)."""

        if init or graph.selection is None:
            text = self.text[0]
        elif type(graph.selection) == Link:
            text = self.text[1]
        elif type(graph.selection) == Node:
            text = self.text[4 if graph.selection.image is not None else 3 if graph.selection.text is not None else 2]

        h = 24 + text.get_height()
        self.surf = pygame.Surface((Graph.W, h), SRCALPHA)

        pygame.draw.rect(self.surf, Palette.neutral, Rect((0, 0), (Graph.W, h)))
        self.surf.blit(text, (12, 12))

    def refresh_zoom(self):
        """Refreshes the cached self.zoom_surf according to the current graph zoom"""
        step = 10**floor(log(1/graph.zoom, 10))
        w = int(step*graph.zoom*Graph.unit_size)

        # prepre text for the surface
        text = font2.render(str(step), True, Palette.text)
        _w = text.get_width()

        self.zoom_surf = pygame.Surface((_w + 5 + w*4, 12), SRCALPHA)
        for i in range(4):
            col = Palette.zoom_bar[i&1]
            pygame.draw.rect(self.zoom_surf, col, Rect(_w + 5 + i*w, 2, w, 8))
        self.zoom_surf.blit(text, (0, 0))

    def update(self, zoom):
        """Displays the cached surface to the screen, updates zoom indicator.
        Param zoom: boolean, True if changed zoom this frame"""

        height = self.surf.get_height()
        self.surf.set_alpha(100 if pygame.mouse.get_pos()[1] < height and pygame.mouse.get_focused() else 255)
        screen.blit(self.surf, (0, 0))

        if zoom: self.last_zoom = ticks()
        dt = ticks()-self.last_zoom

        if dt < 3000:
            # recalculate the cached surface
            if zoom or self.zoom_surf is None:
                self.refresh_zoom()

            w = self.zoom_surf.get_width()
            self.zoom_surf.set_alpha(255 if dt < 2000 else (3000-dt)*0.255)
            screen.blit(self.zoom_surf, (Graph.W-w-10, height+12))

class Graph:
    """Graph manager, for displaying the graph, handling scroll, and updating elements"""
    W = 900
    H = 500

    unit_size = 100 # graph unit to pixel ratio

    def __init__(self):
        assert Palette.init

        self.scroll_x = 0
        self.scroll_y = 0
        self.zoom = 1

        self.save_file = None

        # movement utilities
        self.drag_start = None # moved/scroll element pos when drag started
        self.drag_mouse_start = None # mouse pos when drag started

        self.selection = None # selected Graph object, or None if no selection
        self.hovered = None # hovered Graph object
        self.link = None # if link in construction, store it here, else None

        self.ui = UI()

        # debug information
        self.debug_surf = None

        self.changes = False # set to True when changed something (will trigger a popup on close)

    def resize(self):
        """Triggered when a pygame.VIDEORESIZE event is detected. Updates Graph.W, Graph.H and ui"""

        global screen

        Graph.W, Graph.H = screen.get_size()
        change = False
        if Graph.W < 640:
            Graph.W = 640
            change = True
        if Graph.H < 480:
            Graph.H = 480
            change = True

        if change: # minimum window size
            surf = pygame.Surface(screen.get_size())
            surf.blit(screen, (0, 0))
            screen = pygame.display.set_mode((Graph.W, Graph.H), RESIZABLE)
            screen.blit(surf, (0, 0))

        if 'ui' in dir(self):
            self.ui.process_raw_texts()

    def debug(self, *args):
        """Adds debug information to be displayed in self.update, deprecated unless in development.
        *args: many arguments that will be added to the debug string with space separators.
        There should not be newlines in there, artifacts can appear."""
        text = ' '.join(str(a) for a in args)
        width = len(text)*char_w

        if self.debug_surf is None:
            # create new Surface
            self.debug_surf = pygame.Surface((width, 16))
            y = 0
        else:
            # append text in a new line
            w, h = self.debug_surf.get_size()
            width = w if w > width else width
            surf = pygame.Surface((width, h+16))
            surf.blit(self.debug_surf, (0, 0))
            self.debug_surf = surf
            y = h

        self.debug_surf.blit(font.render(text, True, Palette.text), (0, y))

    def open(self, save_file):
        """Sets self.save_file and loads save file"""

        # make a backup in case something goes wrong and the file fails to open
        backup = [dict(Manager.nodes), dict(Manager.links), dict(Manager.images),
                  self.scroll_x, self.scroll_y, self.zoom]
        Manager.reset()

        success = True
        try:
            lines = [] # in case there's an error and it doesn't get defined

            other_files = {} # file name: content
            with ZipFile(save_file) as z:
                lines = z.read('save.txt').decode().split('\n')
                for file in z.filelist:
                    file = file.filename
                    if file != 'save.txt':
                        other_files[file] = z.read(file)

        except Exception as e:
            Error.zipfile(e)
            success = False

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
                case 'P': # add new node
                    if len(args) != 5:
                        Error.syntax(y, raw)
                        success = False
                    try:
                        Manager.new_node(*args)
                    except:
                        Error.corrupted_file('wrong node values: '+raw, success)
                case 'L': # add new link
                    if len(args) != 3:
                        Error.syntax(y, raw)
                        success = False
                    try:
                        Manager.new_link(*args)
                    except:
                        Error.corrupted_file('wrong link values: '+raw, success)
                case 'I': # add new image
                    if len(args) != 2:
                        Error.syntax(y, raw)
                        success = False
                    try:
                        name, id = args
                        content = other_files[name]
                        Manager.new_image(name, content, id)
                    except:
                        Error.corrupted_file('wrong image values: '+raw, success)
                        success = False
                case 'Ai': # attach an image to a node
                    if len(args) != 2:
                        Error.syntax(y, raw)
                        success = False
                    try:
                        Manager.attach_image(*args)
                    except:
                        Error.corrupted_file('error while attaching image: '+raw, success)
                        success = False
                case 'At': # attach text to a node
                    if len(args) != 2:
                        Error.syntax(y, raw)
                        success = False
                    try:
                        Manager.attach_text(args[0], args[1].replace('\0', ' '))
                    except:
                        Error.corrupted_file('error while attaching text: '+raw, success)
                        success = False

                case '_S':
                    if len(args) != 2:
                        Error.syntax(y, raw)
                        success = False
                    try:
                        self.scroll_x, self.scroll_y = float(args[0]), float(args[1])
                    except:
                        Error.corrupted_file('invalid scroll position', success)
                case '_Z':
                    if len(args) != 1:
                        Error.syntax(y, raw)
                        success = False
                    try:
                        self.zoom = float(args[0])
                    except:
                        Error.corrupted_file('invalid zoom value', success)
                    if not self.zoom: # forbidden value: reset zoom
                        self.zoom = 1
                case _:
                    Error.syntax(y, raw)
                    success = False

            if not success: break

        if success:
            self.open_successful(save_file)
            for d in backup: del d
        else:
            # unload the objects and restore the previous ones
            # manually deleting makes for less memory usage
            del Manager.links
            del Manager.images
            del Manager.nodes # nodes last because then they no longer have any references
            Manager.nodes, Manager.links, Manager.images, self.scroll_x, self.scroll_y, self.zoom = backup

    def open_successful(self, save_file):
        """If opening a file was successful, prepare graph (reset variables)"""
        self.save_file = save_file

        # reset variables
        self.drag_start = None
        self.drag_mouse_start = None
        self.selection = None
        self.hovered = None
        self.hovered_l = None
        self.link = None
        self.changes = False
        set_title(save_file, False)
        self.ui.update_surf()

    def save(self):
        """Saves graph contents into self.save_file"""

        if self.save_file is None: raise ValueError('No save loaded')

        # general information
        content = ['# GENERAL INFO',
                   '_S %f %f' %(self.scroll_x, self.scroll_y),
                   '_Z %f' %(self.zoom)]

        # nodess
        content += ('', '# NODES')
        for id, node in Manager.nodes.items():
            content.append('P %f %f %d %d %d' %(node.x, node.y, node.rank, node.state, id))

        # links
        content += ('', '# LINKS')
        for id, link in Manager.links.items():
            content.append('L %d %d %d' %(link.n1.id, link.n2.id, id))

        # images
        content += ('', '# IMAGES')
        for id, image in Manager.images.items():
            # check if this image is used in the graph, otherwise don't save it
            used = False
            for node in Manager.nodes.values():
                if node.image == image:
                    used = True
                    break

            if used:
                content.append('I %s %d' %(image.path, image.id))

        # images attached to nodes
        content += ('', '# LINK IMAGES')
        used_image_ids = []
        for id, node in Manager.nodes.items():
            if node.image is not None:
                content.append('Ai %d %d' %(id, node.image.id))
                used_image_ids.append(node.image.id)

        # text attached to nodes
        content += ('', '# TEXT')
        for id, node in Manager.nodes.items():
            if node.text is not None:
                content.append('At %d %s' %(id, node.text.replace(' ', '\0')))

        # save into zip file
        with ZipFile(self.save_file, 'w') as z:
            # add the main save file into the zip file
            z.writestr('save.txt', '\n'.join(content)+'\n')

            # encode the width, height and image data into image files
            for id in set(used_image_ids):
                image = Manager.images[id]
                w, h = image.surf.get_size()
                content = b'%d.%d.%s' %(w, h, pygame.image.tostring(image.surf, 'RGBA'))
                z.writestr(image.path, content)

        self.changes = False
        set_title(self.save_file)

    def newfile(self):
        Manager.reset()
        self.open_successful(None)

    def saveas(self):
        file = ask_filename(True)
        if file != '':
            self.save_file = file
            self.save()

    def export(self, transparent):
        """Exports the graph into a png image, either with Palette.background background or no background.
        The render is done at zoom 1, and a margin of 20px is added around the graph.
        There needs to be at least one element in the graph for it to be rendered.
        Very large graphs might MemoryError, might have to export to another zoom. TODO?
        For now, it just raises an error."""

        if not len(Manager.nodes):
            ask_button('Cannot render an empty graph.', [(0, 'OK')])
            return

        if self.save_file is None: file = None
        else: file = splitext(basename(self.save_file))[0]+'.png'
        file = asksaveasfilename(title='Export to file', filetypes=(('PNG files', '.png'),), initialfile=file)
        pygame.event.get()
        if not file: return
        if not file.endswith('.png'): file += '.png'
        self.select(None)

        # display a loading screen
        old_screen, background = get_popup_bg('Loading... Please wait.')
        screen.blit(background, (0, 0))
        pygame.display.flip()

        # get the bounding boxes
        x0 = y0 = x1 = y1 = None
        for node in Manager.nodes.values():
            w, h = node.text_surfs[1].get_size()
            offsettop = node.size/2/Graph.unit_size
            offsetx = max(offsettop, w/2/Graph.unit_size)
            offsetbtm = offsettop + (5+h)/Graph.unit_size
            if x0 is None or node.x-offsetx < x0: x0 = node.x-offsetx
            if y0 is None or node.y-offsettop < y0: y0 = node.y-offsettop
            if x1 is None or node.x+offsetx > x1: x1 = node.x+offsetx
            if y1 is None or node.y+offsetbtm > y1: y1 = node.y+offsetbtm
        w, h = (x1-x0)*Graph.unit_size, (y1-y0)*Graph.unit_size

        try:
            surf = pygame.Surface((w+80, h+80), SRCALPHA)
        except MemoryError:
            ask_button('A MemoryError occured.\nMaybe try to lower the size of your graph.', [(0, 'OK')])
            return

        if not transparent:
            surf.fill(Palette.background)

        # add all objects: make a custom projector for this surface
        project = lambda x, y: ((x-x0)*Graph.unit_size + 40, (y-y0)*Graph.unit_size + 40)

        for link in Manager.links.values():
            link.update([], surf, project)
        for node in Manager.nodes.values():
            node.update([], surf, project, True)

        pygame.image.save(surf, file)

        # reset the screen to as it was before for safety
        screen.blit(old_screen, (0, 0))
        pygame.display.flip()

    def project(self, x, y):
        """Returns the position, in screen coordinates, corresponding to a position in graph coordinates"""
        z = self.zoom * Graph.unit_size
        return (x - self.scroll_x) * z + self.W/2, (y - self.scroll_y) * z + self.H/2

    def screen2coord(self, x, y):
        """Returns the position, in graph coordinates, corresponding to a position in screen coordinates"""
        z = self.zoom * Graph.unit_size
        return (x - self.W/2) / z + self.scroll_x, (y - self.H/2) / z + self.scroll_y

    def select(self, obj):
        """Sets self.selection to obj and updates self.ui"""
        self.selection = obj
        self.ui.update_surf()

    def update(self, events):
        """Updates objects and menu, displays the graph"""
        # move and zoom
        pressed = pygame.mouse.get_pressed()[0]
        mpos = pygame.mouse.get_pos()

        # get visible graph objects now, useful for collision checks
        visible_n = [] # node objects that are visible
        for node in Manager.nodes.values():
            if node.visible():
                visible_n.append(node)
        visible_l = [] # same for links
        for link in Manager.links.values():
            if link.n1 in visible_n or link.n2 in visible_n or link.n2 is None or True:
                visible_l.append(link)

        self.hovered = None
        for node in visible_n:
            if node.collide(mpos):
                self.hovered = node
                break
        for link in visible_l:
            # don't select a link if something else has been selected,
            # or if currently creating a link
            if self.hovered is not None or self.link is not None: break
            if link.collide(mpos): self.hovered = link

        change = False # did the user do a change this frame?
        change_zoom = False # did the zoom change this frame?

        # events check
        for event in events:
            # start dragging
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.select(self.hovered)

                if self.selection is None:
                    self.drag_start = (self.scroll_x, self.scroll_y)
                elif type(self.selection) == Node:
                    self.drag_start = (self.selection.x, self.selection.y)
                if type(self.selection) != Link:
                    self.drag_mouse_start = event.pos

                # finish adding a link
                if type(self.selection) == Node and self.link is not None and self.link.n1 != self.selection:
                    # check if no link exists between these two nodes
                    ok = True
                    for link in Manager.links.values():
                        if (link.n1 == self.link.n1 and link.n2 == self.selection) or \
                            (link.n2 == self.link.n1 and link.n1 == self.selection):
                            ok = False
                            break

                    if ok:
                        self.link.n2 = self.selection
                        self.link.refresh()
                        self.link = None
                        self.select(None)
                        self.drag_start = None # prevent unwanted drag
                        change = True

            # stop dragging
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                self.drag_start = None
                self.drag_mouse_start = None

            # zoom
            elif event.type == MOUSEWHEEL and not pressed:
                mx, my = self.screen2coord(*mpos)

                if event.y > 0: self.zoom *= 1.2 # zoom in
                else: self.zoom /= 1.2 # zoom out
                if self.zoom == 0: self.zoom = 1 # reset zoom in this rare case

                # keep zoom around mouse
                dx, dy = self.scroll_x+mx, self.scroll_y+my
                mx, my = self.screen2coord(*mpos)
                self.scroll_x, self.scroll_y = dx-mx, dy-my

                change_zoom = True

            # keys
            elif event.type == KEYDOWN:
                if event.key == K_z:
                    self.zoom = 1
                    self.ui.refresh_zoom()
                elif event.key == K_a:
                    self.zoom = 1
                    self.ui.refresh_zoom()
                    self.scroll_x = self.scroll_y = 0
                elif event.key == K_q:
                    if quit_app():
                        return

                elif event.key == K_ESCAPE:
                    if self.link is None:
                        # unselect by hitting Escape
                        self.select(None)
                    else:
                        # or undo the creation of a new link
                        del Manager.links[self.link.id]
                        self.link = None

                elif event.key == K_RETURN and self.link is None:
                    self.select(None)

                elif self.selection is None:
                    if event.key == K_p:
                        self.select(Manager.new_node(*self.screen2coord(*mpos), 0, 0))
                        change = True
                    elif event.key == K_s:
                        if self.save_file is None: self.saveas()
                        else: self.save()
                    elif event.key == K_w:
                        self.saveas()
                    elif event.key == K_n:
                        if not self.changes or want_to_save() is not None:
                            self.newfile()
                    elif event.key == K_o:
                        if not self.changes or want_to_save() is not None:
                            path = ask_filename()
                            if path != '': self.open(path)
                    elif event.key == K_i:
                        import_image()
                    elif event.key == K_e:
                        self.export(True)
                    elif event.key == K_f:
                        self.export(False)

                elif type(self.selection) == Node:
                    if event.key == K_l and self.link is None:
                        self.link = Manager.new_link(self.selection.id, None)
                        self.select(None)
                    elif event.key == K_i:
                        image = image_selector()
                        if image is not None:
                            self.selection.set_image(image)
                            change = True
                    elif event.key == K_t:
                        check = lambda s: len(s) and '\n' not in s and '\r' not in s and '\t' not in s
                        text = ask_input_box('Enter node text:', str, check, self.W-20)
                        if text is not None:
                            self.selection.set_text(text)
                            change = True
                    elif event.key == K_r:
                        self.selection.cycle_rank()
                        change = True
                    elif event.key == K_s:
                        self.selection.cycle_state()
                        change = True
                    elif event.key == K_DELETE:
                        if self.selection.image is not None:
                            self.selection.set_image(None)
                        elif self.selection.text is not None:
                            self.selection.set_text(None)
                        else:
                            to_delete = [] # links that connect to the deleted node
                            for id, link in Manager.links.items():
                                if link.n1 == self.selection or link.n2 == self.selection:
                                    to_delete.append(id)
                            del Manager.nodes[self.selection.id]
                            for link in to_delete:
                                del Manager.links[link]
                            self.selection = None
                        self.select(self.selection) # update self.ui
                        change = True

                elif type(self.selection) == Link:
                    if event.key == K_DELETE:
                        del Manager.links[self.selection.id]
                        self.select(None)
                        change = True

        if self.drag_start is not None:
            x, y = self.drag_start
            x0, y0 = self.drag_mouse_start
            x1, y1 = mpos
            m = 1/self.zoom/self.unit_size
            dx = (x0-x1) * m
            dy = (y0-y1) * m
            if self.selection is None:
                self.scroll_x = x + dx
                self.scroll_y = y + dy
            else:
                self.selection.x = x - dx
                self.selection.y = y - dy
                change = bool(dx or dy)

        if change:
            self.changes = True
            set_title(self.save_file, True)

        screen.fill(Palette.background)

        # update and render graph objects
        for link in visible_l: link.update(events, screen, self.project)
        for node in visible_n: node.update(events, screen, self.project)

        # update and render menu and UI
        self.ui.update(change_zoom)

        # display debug screen if needed
        if self.debug_surf is not None:
            screen.blit(self.debug_surf, (0, 0))
            self.debug_surf = None

def set_title(name, unsaved=False):
    """Sets the title of the pygame application"""

    if name is None:
        name = '[no file]'
        unsaved = True
    if unsaved: name = '*%s*' %name
    pygame.display.set_caption('Progression Graph - '+name)

def want_to_save():
    """Triggers a "save before doing some action?" popup.
    Returns: 0: save, 1: don't save, None: cancel
    Put into a function because used multiple times in the code."""

    return ask_button('You have unsaved changes. Do you want to save?', [(0, 'Yes'), (1, 'No'), (None, 'Cancel')])

def quit_app():
    """Displays a save and quit? popup if made changes.
    Returns True if the window should be closed, otherwise False."""
    global run

    res = 1 if not graph.changes else want_to_save()

    if res is None: return
    if res == 0: graph.save()
    run = False
    return True

_FPS = 60 # actually used FPS will be based on this value
pygame.init()
pygame.key.set_repeat(400, 30)

screen = pygame.display.set_mode((Graph.W, Graph.H), RESIZABLE)
hwnd = pygame.display.get_wm_info()['window']
set_title(None)
font = pygame.font.SysFont('consolas', 16)
font2 = pygame.font.SysFont('consolas', 12)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks

# get the characters length (fonts should be monospace)
char_w = font.render('_', True, Palette.text).get_width()
char_w2 = font2.render('_', True, Palette.text).get_width()

graph = Graph()

dt = 0 # time passed in last frame, in seconds
run = True
while run:
    active = hwnd == win32gui.GetForegroundWindow() and pygame.mouse.get_focused()
    FPS = _FPS if active else _FPS/10

    # handle pygame event loop
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            quit_app()
        elif event.type == VIDEORESIZE:
            graph.resize()

    graph.update(events)
    pygame.display.flip()
    dt = clock.tick(FPS)/1000

pygame.quit()
