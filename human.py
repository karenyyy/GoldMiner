import random

import numpy
import pygame as pg
from pygame.locals import *

import event

action_list = {
    'forward': 1,
    'left': 2,
    'right': 3,
    'grab': 4,
    'shoot': 5
}

facing_list = {
    'up': 0,
    'right': 1,
    'down': 2,
    'left': 3
}

move_coordinate = {
    facing_list['up']: (0, 1),
    facing_list['right']: (1, 0),
    facing_list['down']: (0, -1),
    facing_list['left']: (-1, 0),
}


def neighbors(i, j):
    li = set()
    if (i - 1) in range(4):
        li.add((i - 1, j))
    if (i + 1) in range(4):
        li.add((i + 1, j))
    if (j - 1) in range(4):
        li.add((i, j - 1))
    if (j + 1) in range(4):
        li.add((i, j + 1))
    return li


class Human:
    def __init__(self, event_controller):
        self.event_controller = event_controller
        self.event_controller.register_listener(self)

    def _generate_world2(self):

        self.curr_pos = (-1, 0)
        self.facing = facing_list['right']
        self.maze = numpy.zeros((4, 4, 5))  # [B, G, P, S, M]
        # Place gold randomly
        done = False
        while not done:
            i = random.choice(range(4))
            j = random.choice(range(4))
            if self.maze[i][j][1] != 1 and self.maze[i][j][4] != 1 and self.maze[i][j][2] != 1 and (i != 0 and j != 0):
                self.maze[i][j][1] = 1
                done = True

        # Place the monster randomly
        done = False
        while not done:
            i = random.choice(range(4))
            j = random.choice(range(4))
            if self.maze[i][j][1] != 1 and self.maze[i][j][4] != 1 and self.maze[i][j][2] != 1 and (i != 0 and j != 0):
                self.maze[i][j][4] = 1
                # generating Stench
                for pos in neighbors(i, j):
                    self.maze[pos[0]][pos[1]][3] = 1
                done = True

        # Place pits randomly
        for _ in range(3):
            done = False
            while not done:
                i = random.choice(range(4))
                j = random.choice(range(4))
                if self.maze[i][j][1] != 1 and self.maze[i][j][4] != 1 and self.maze[i][j][2] != 1 and (
                        i != 0 and j != 0):
                    self.maze[i][j][2] = 1
                    # then place breeze
                    for pos in neighbors(i, j):
                        self.maze[pos[0]][pos[1]][0] = 1
                    done = True

        ev = event.WorldBuilt(self.maze)
        self.event_controller.post(ev)

    def notify(self, e):
        if isinstance(e, event.GenerateRequest):
            self._generate_world2()

        elif isinstance(e, event.Tick):
            for e in pg.event.get():
                if e.type == QUIT:
                    ev = event.Quit()
                    self.event_controller.post(ev)
                elif e.type == KEYDOWN:
                    if e.key == K_LEFT:
                        self.facing = (self.facing - 1) % 4
                        ev = event.PlayerTurn(
                            event.PlayerTurn.direction_list['left'], self.facing)
                        self.event_controller.post(ev)
                    elif e.key == K_RIGHT:
                        self.facing = (self.facing + 1) % 4
                        ev = event.PlayerTurn(
                            event.PlayerTurn.direction_list['right'], self.facing)
                        self.event_controller.post(ev)
                    elif e.key == K_RETURN:
                        dx, dy = move_coordinate[self.facing]
                        new_pos = (self.curr_pos[0] + dx, self.curr_pos[1] + dy)
                        if new_pos in neighbors(*self.curr_pos):
                            self.curr_pos = new_pos
                            ev = event.PlayerForward(self.curr_pos)
                            self.event_controller.post(ev)
                        if (self.maze[self.curr_pos[0]][self.curr_pos[1]][2] == 1) or (
                            self.maze[self.curr_pos[0]][self.curr_pos[1]][4] == 1):
                            ev = event.PlayerDie()
                            self.event_controller.post(ev)

                            self._generate_world2()
                            ev = event.Reset()
                            self.event_controller.post(ev)

                    elif e.key == K_s:
                        shooting_range = []
                        dx, dy = move_coordinate[self.facing]
                        x, y = (self.curr_pos[0] + dx, self.curr_pos[1] + dy)
                        while (x in range(4)) and (y in range(4)):
                            shooting_range.append((x, y))
                            x, y = (x + dx, y + dy)

                        for i, j in shooting_range:
                            if self.maze[i][j][4] == 1:
                                self.maze[i][j][4] = 0
                                for pos in neighbors(i, j):
                                    self.maze[pos[0]][pos[1]][3] = 0
                                ev = event.PlayerShoot()
                                self.event_controller.post(ev)
                                ev = event.MonsterDie(self.curr_pos)
                                self.event_controller.post(ev)
                                break

                    elif e.key == K_g:
                        i, j = (self.curr_pos[0], self.curr_pos[1])
                        self.maze[i][j][1] = 0

                        ev = event.PlayerGrabGold(self.curr_pos)
                        self.event_controller.post(ev)

                        self._generate_world2()
                        ev = event.Reset()
                        self.event_controller.post(ev)


                    else:
                        continue
