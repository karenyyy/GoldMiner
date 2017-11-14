
import random

import numpy

import event
from kb import WumpusKnowledgeBase
from logicalExpr import expr

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

map_list = ['B', 'G', 'P', 'S', 'W']


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


class Agent:

    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.gameOver = True
        self.gold_grabbed = False
        self.shooting_range = set()
        for i in range(4):
            for j in range(4):
                self.shooting_range.add((i, j))

    def _generate_world(self):
        self.gameOver = False
        self.gold_grabbed = False
        self.pos = (-1, 0)
        self.facing = facing_list['right']
        self.visited = set()
        self.danger = set()
        self.safe = set()
        self.fringe = set()
        self.move = [action_list['forward']]

        self.world = numpy.zeros((4, 4, 5))
        self.kb = WumpusKnowledgeBase()

        # Place gold randomly
        done = False
        while not done:
            i = random.choice(range(4))
            j = random.choice(range(4))
            if self.world[i][j][1] != 1 and self.world[i][j][4] != 1 and self.world[i][j][2] != 1 and (i != 0 and j != 0):
                self.world[i][j][1] = 1
                done = True

        # Place the wumpus randomly
        done = False
        while not done:
            i = random.choice(range(4))
            j = random.choice(range(4))
            if self.world[i][j][1] != 1 and self.world[i][j][4] != 1 and self.world[i][j][2] != 1 and (i != 0 and j != 0):
                self.world[i][j][4] = 1
                # generating Strench
                for pos in neighbors(i, j):
                    self.world[pos[0]][pos[1]][3] = 1
                done = True

        # Place pits randomly
        for _ in range(4):
            done = False
            while not done:
                i = random.choice(range(4))
                j = random.choice(range(4))
                if self.world[i][j][1] != 1 and self.world[i][j][4] != 1 and self.world[i][j][2] != 1 and (i != 0 and j != 0):
                    self.world[i][j][2] = 1
                    done = True
                    # generating Breeze
                    for pos in neighbors(i, j):
                        self.world[pos[0]][pos[1]][0] = 1

        ev = event.WorldBuiltEvent(self.world)
        self.ev_manager.post(ev)

    def next(self):

        if not self.gameOver and (not self.gold_grabbed):
            if len(self.move) > 0:
                action = self.move.pop()
            else:
                action = self.nextAction()

            self.doAction(action)
        else:
            ev = event.ResetEvent()
            self.ev_manager.post(ev)


    def nextAction(self):
        if len(self.safe) > 0:
            source = self.safe
        elif len(self.fringe) > 0:
            source = self.fringe
        else:
            source = self.danger
        goal = source.pop()
        self.move = self.convert2Move(self.shortest_path(goal))
        action = self.move.pop()
        return action

    def findSafe(self, i, j):
        new = neighbors(i, j) - self.visited
        new -= self.safe
        new -= self.danger

        new_safe = set()
        new_danger = set()

        if (self.world[i][j][0] == 0) and (self.world[i][j][3] == 0):
            self.fringe -= set((i, j))
            new_safe |= new
        else:
            self.fringe |= new

        print "fringe list: ", self.fringe, "visited list:", self.visited

        fringe = self.fringe.copy()
        if len(self.visited) > 1:
            for x in fringe:
                if self.kb.ask(expr('(P%s%s | W%s%s)' % (x * 2))):
                    # dpll not satisfied
                    print '(P%s%s | W%s%s)' % (x * 2), "is dangerous"
                    new_danger.add(x)
                    self.fringe.remove(x)
                    ev = event.FoundDangerEvent(x)
                    self.ev_manager.post(ev)
                elif self.kb.ask(expr('(~P%s%s & ~W%s%s)' % (x * 2))):
                    # dpll satisfied
                    print '(~P%s%s & ~W%s%s)' % (x * 2), "is safe"
                    new_safe.add(x)
                    self.fringe.remove(x)
        if len(new_safe) > 0:
            self.safe |= new_safe
        if len(new_danger) > 0:
            self.danger |= new_danger

        print "safe list: ", self.safe

    def shortest_path(self, goal):
        g = self.visited
        print g, "visited"
        v = {}
        for x in g:
            v[x] = float("inf")
        v[goal] = 0

        def v_neighbors(i, j, s):
            li = []
            for t in neighbors(i, j):
                if (t in self.visited) and (t not in s):
                    li.append(t)
            return li

        def get_path(v):
            path = []
            a = self.pos
            t = v[a]
            while t > 1:
                for x in v_neighbors(a[0], a[1], s):
                    if v[x] < t:
                        t = t - 1
                        path.append(x)
                        a = x
                        break
            return path

        s = [goal]
        while (len(s) > 0):
            u = s.pop()
            for x in v_neighbors(u[0], u[1], s):
                if v[x] > v[u] + 1:
                    v[x] = v[u] + 1
                    s.append(x)

        pa = get_path(v)
        pa.append(goal)
        return pa

    def convert2Move(self, path):
        move = []
        prev = self.pos
        prev_facing = self.facing
        for pos in path:
            dx = pos[0] - prev[0]
            dy = pos[1] - prev[1]
            dy_dict = {
                -1: 'down',
                1: 'up',
                0: 'up'  # dummy item
            }
            dx_dict = {
                -1: 'left',
                1: 'right',
                0: dy_dict[dy]
            }
            facing = facing_list[dx_dict[dx]]
            d = facing - prev_facing

            if d != 0:
                c = abs(d)
                if c > 2:
                    d = -d
                    c = c % 2
                if d < 0:
                    direction = action_list['left']
                elif d > 0:
                    direction = action_list['right']

                move.extend([direction] * c)
                prev_facing = facing
            move.append(action_list['forward'])
            prev = pos
        move.reverse()
        return move

    def doAction(self, action):
        move_coordinate = {
            facing_list['up']: (0, 1),
            facing_list['right']: (1, 0),
            facing_list['down']: (0, -1),
            facing_list['left']: (-1, 0),
        }
        if action is action_list['forward']:
            dx, dy = move_coordinate[self.facing]
            new_pos = (self.pos[0] + dx, self.pos[1] + dy)
            if new_pos in neighbors(*self.pos):
                ev = event.PlayerForwardEvent(new_pos)
                self.ev_manager.post(ev)

                if new_pos not in self.visited:
                    i, j = new_pos
                    percept = self.world[i][j]
                    ev = event.PlayerPerceiveEvent(percept)
                    self.ev_manager.post(ev)

                    self.visited.add((i, j))
                    if (i, j) in self.safe:
                        self.safe.remove((i, j))

                    if percept[1] == 1:
                        self.gold_grabbed = True
                        self.doAction(action_list['grab'])
                    elif (percept[2] == 1) or (percept[4] == 1):
                        self.gameOver = True
                        ev = event.PlayerDieEvent()
                        self.ev_manager.post(ev)
                    else:
                        c = 0
                        know = []
                        for x in percept:
                            # if B, G, S
                            if x == 1:
                                know.append("%s%s%s" % (map_list[c], i, j))
                            elif x == 0:
                                know.append("~%s%s%s" % (map_list[c], i, j))
                            c += 1
                        if len(know) > 0:
                            print "add rules to knowledge base: ", ' & '.join(know)
                            self.kb.addRules(expr(' & '.join(know)))
                        # find next safe move
                        print "before:", "visited:", self.visited, "safe:", self.safe, "danger:", self.danger
                        self.findSafe(i, j)
                    print "after:", "visited:", self.visited, "safe:", self.safe, "danger:", self.danger
                # update curr pos
                self.pos = new_pos

        elif action is action_list['left']:
            self.facing = (self.facing - 1) % 4

            ev = event.PlayerTurnEvent(
                event.PlayerTurnEvent.direction_list['left'], self.facing)
            self.ev_manager.post(ev)

        elif action is action_list['right']:
            self.facing = (self.facing + 1) % 4

            ev = event.PlayerTurnEvent(
                event.PlayerTurnEvent.direction_list['right'], self.facing)
            self.ev_manager.post(ev)

        elif action is action_list['shoot']:
            def shootingRange(facing):
                shooting_range = []
                dx, dy = move_coordinate[facing]
                x, y = (self.pos[0] + dx, self.pos[1] + dy)
                while (x in range(4)) and (y in range(4)):
                    shooting_range.append((x, y))
                    x, y = (x + dx, y + dy)
                return shooting_range

            for i, j in shootingRange(self.facing):
                if self.world[i][j][4] == 1:
                    self.wumpus_die(i, j)

                    ev = event.PlayerShootEvent()
                    self.ev_manager.post(ev)

        elif action is action_list['grab']:
            i, j = (self.pos[0], self.pos[1])
            self.world[i][j][1] = 0
            self.gold_grabbed = True

            ev = event.PlayerPickEvent(self.pos)
            self.ev_manager.post(ev)

    def wumpus_die(self, i, j):

        self.world[i][j][4] = 0
        for pos in neighbors(i, j):
            self.world[pos[0]][pos[1]][3] = 0  # eliminate stench

        ev = event.WumpusDieEvent((i, j))
        self.ev_manager.post(ev)

    def notify(self, e):
        if isinstance(e, event.GenerateRequestEvent):

            self._generate_world()
        elif isinstance(e, event.StepEvent):
            self.next()
