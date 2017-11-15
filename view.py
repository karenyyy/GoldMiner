#!/usr/bin/env python

import os

import pygame as pg
from pygame.locals import *

import agent, event

color = {
    'gray': (100, 100, 100),
    'white': (255, 255, 255),
    'light_green': (20, 60, 20),
    'danger': (150, 50, 50)
}


help = """
    CMPSC360 Project GoldMiner Demo
    *** I: Intelligent agent mode
    *** V: View what state it is in each cell
    *** R: Reset the board
    *** Q: Quit the game
    *** Enter: Next step
    *** ->: turn left
    *** <-: turn right
   Press H to hide the help information 
   
   Have fun \(^o^)/\(^o^)/\(^o^)/
"""


status_font = (os.path.join('helpInfoFont', 'Pacifico.ttf'), 22)


def load_image(name):
    fullname = os.path.join('images', name)
    image = pg.image.load(fullname)
    image = image.convert()
    image.set_colorkey(image.get_at((0, 0)), RLEACCEL)
    return image, image.get_rect()


class MainFrame:

    def __init__(self, event_controller):
        self.event_controller = event_controller
        self.event_controller.register_listener(self)

        pg.init()
        self.screen = pg.display.set_mode((769, 920), pg.RESIZABLE)
        pg.display.set_caption('GoldMiner (360 project game)')
        self.background = pg.Surface(self.screen.get_size())
        self.background.convert()
        self.background.fill(color["white"])

        self.screen.blit(self.background, (0, 0))
        pg.display.update()

        self.back_sprites = pg.sprite.RenderUpdates()
        self.front_sprites = pg.sprite.RenderUpdates()

        self.sectors = {}
        self.player_sector = None
        self.view_all = False

        self.help_display = HelpDisplay()
        self.help_display.rect.center = self.background.get_rect().center

    def app_start(self):
        dx, dy = (192, 192)
        x, y = (3, 4)
        rect = pg.Rect(2 + 192 * 3, -192 + 2, 188, 188)
        for count in xrange(16):
            if count % 4 == 0:
                x -= 3
                y -= 1
                rect = rect.move(-3 * dx, dy)
            else:
                x += 1
                rect = rect.move(dx, 0)
            new_sector = Sector(self.back_sprites)
            new_sector.index = (x, y)
            new_sector.rect = rect
            self.sectors[(x, y)] = new_sector


        self.player = Player()

        ev = event.GenerateRequest()
        self.event_controller.post(ev)

    def player_moveto(self, pos):
        self.player_sector = self.sectors[pos]
        self.player.moveto = self.player_sector.rect.center

    def help(self):
        if not self.front_sprites.has(self.help_display):
            self.help_display.add(self.front_sprites)
        else:
            self.help_display.remove(self.front_sprites)


    def player_forward(self, ev):
        if not self.front_sprites.has(self.player):
            self.player.add(self.front_sprites)
            self.player.update_facing(agent.facing_list['right'])
        self.player_moveto(ev.pos)
        self.sectors[ev.pos].visit()
        self.front_sprites.update()
        self.redraw()

    def player_turn(self, ev):
        self.player.update_facing(ev.facing)



    def found_danger(self, ev):
        self.sectors[ev.pos].set_danger()

    def view(self, ev):
        if self.view_all:
            self.view_all = False
        else:
            self.view_all = True

        for s in self.sectors.values():
            if not s.visited:
                s.view(self.view_all)

    def world_built(self, ev):
        for key, sector in self.sectors.items():
            item = ev.world[key]
            for x in range(5):
                if item[x] == 1:
                    thing = agent.map_list[x].lower()
                    sector.things.append(thing)

    def reset_world(self, ev):
        for sector in self.sectors.values():
            sector.visited = False
            sector.danger = False
            sector.image.fill(color['gray'])
            sector.things = []
        self.player.remove(self.front_sprites)

        ev = event.GenerateRequest()
        self.event_controller.post(ev)

    def redraw(self):
        # Draw everything
        self.back_sprites.clear(self.screen, self.background)
        self.front_sprites.clear(self.screen, self.background)

        self.back_sprites.update()
        self.front_sprites.update()

        dirty_rects1 = self.back_sprites.draw(self.screen)
        dirty_rects2 = self.front_sprites.draw(self.screen)

        dirty_rects = dirty_rects1 + dirty_rects2
        pg.display.update(dirty_rects)

    def notify(self, ev):
        if isinstance(ev, event.Tick):
            self.redraw()
        elif isinstance(ev, event.AppStart):
            self.app_start()
        elif isinstance(ev, event.Reset):
            self.reset_world(ev)
        elif isinstance(ev, event.WorldBuilt):
            self.world_built(ev)
        elif isinstance(ev, event.PlayerForward):
            self.player_forward(ev)
        elif isinstance(ev, event.PlayerTurn):
            self.player_turn(ev)

        elif isinstance(ev, event.View):
            self.view(ev)
        elif isinstance(ev, event.Help):
            self.help(ev)
        elif isinstance(ev, event.FoundDanger):
            self.found_danger(ev)


class HelpDisplay(pg.sprite.Sprite):
    """Help information"""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((500, 580))
        self.image.set_alpha(255 * 0.6)
        self.image.fill(color['white'])
        self.rect = self.image.get_rect()
        self.text = help

        self.draw_text()

    def draw_text(self):
        fo = pg.font.Font(*status_font)

        prevpos = None
        for line in self.text.split('\n'):
            textr = fo.render(line, 1, color['danger'])
            textrpos = textr.get_rect()
            textrpos.left = self.image.get_rect().left
            if prevpos:
                textrpos.top = prevpos.bottom
            else:
                textrpos.top = self.image.get_rect().top
            prevpos = textrpos
            self.image.blit(textr, textrpos)


class Sector(pg.sprite.Sprite):

    def __init__(self, group=None):
        pg.sprite.Sprite.__init__(self, group)
        self.image = pg.Surface((180, 180))
        self.image.fill(color['gray'])

        self.index = None
        self.visited = False
        self.danger = False
        self.view = False
        self.things = []

    def draw_things(self):
        if self.danger:
            self.image.fill(color['danger'])
        for t in self.things:
            self.draw_img(t)

    def clear_things(self):
        if self.danger:
            self.image.fill(color['danger'])
        else:
            self.image.fill(color['gray'])

    def view(self, view_flag):
        self.view = view_flag
        if view_flag:
            self.draw_things()
        else:
            self.clear_things()

    def set_danger(self):
        if not self.danger:
            self.danger = True
            self.image.fill(color['danger'])
            if self.view:
                self.draw_things()

    def draw_img(self, s):
        image, rect = load_image('%s.png' % s)
        rect.center = self.image.get_rect().center

        self.image.blit(image, rect)

    def visit(self):
        if not self.visited:
            self.visited = True
            self.image.fill((180, 180, 180))
            self.draw_things()

    def update(self):
        pass



class Player(pg.sprite.Sprite):

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((30, 30))
        self.image.fill((180, 180, 180))
        self.rect = self.image.get_rect()

        self.moveto = None
        self.facing = None

    def update_facing(self, facing=None):

        def draw_facing(image, rect):
            if self.facing == 0:
                rect.midtop = self.image.get_rect().midtop
            elif self.facing == 1:
                rect.midright = self.image.get_rect().midright
            elif self.facing == 2:
                rect.midbottom = self.image.get_rect().midbottom
            elif self.facing == 3:
                rect.midleft = self.image.get_rect().midleft
            self.image.blit(image, rect)

        # clear the old facing line
        if self.facing is not None:
            image = pg.Surface((30, 30))
            image.fill((180, 180, 180))
            rect = image.get_rect()
            draw_facing(image, rect)
        self.facing = facing
        image, rect = load_image('facing_%s.png' % self.facing)
        draw_facing(image, rect)

    def update(self):
        if self.moveto:
            self.rect.center = self.moveto
            self.moveto = None
