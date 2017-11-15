
import pygame
from pygame.locals import *

import event

fps = 10

wait_ticks = 5


class CPUSpinnerController:

    def __init__(self, event_controller):
        self.event_controller = event_controller
        self.event_controller.register_listener(self)
        self.clock = pygame.time.Clock()
        self.keep_going = True
        self.auto_mode = False

    def run(self):
        count = 0
        i=1
        while self.keep_going:
            self.clock.tick(fps)
            ev = event.Tick()
            self.event_controller.post(ev)
            '''
            if i==1:
                ev = event.Help()
                self.event_controller.post(ev)
                i-=1
            '''
            if count == 0:
                if self.auto_mode:
                    ev = event.NextStep()
                    self.event_controller.post(ev)
                count = wait_ticks
            count -= 1

    def notify(self, ev):

        if isinstance(ev, event.Quit):
            self.keep_going = False

        elif isinstance(ev, event.AutoMode):
            if self.auto_mode:
                self.auto_mode = False
            else:
                self.auto_mode = True


class KeyboardController:
    def __init__(self, event_controller):
        self.event_controller = event_controller
        self.event_controller.register_listener(self)

    def notify(self, e):
        if isinstance(e, event.Tick):
            for e in pygame.event.get():
                ev = None
                if e.type == QUIT:
                    ev = event.Quit()
                elif e.type == KEYDOWN:
                    if e.key == K_q:
                        ev = event.Quit()
                    elif e.key == K_r:
                        ev = event.Reset()
                    elif e.key == K_SPACE:
                        ev = event.NextStep()
                    elif e.key == K_i:
                        ev = event.AutoMode()
                    elif e.key == K_v:
                        ev = event.View()
                    elif e.key == K_h:
                        ev = event.Help()

                if ev:
                    self.event_controller.post(ev)
