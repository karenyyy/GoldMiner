import random

import numpy

import event
from knowledgeBase import KnowledgeBase
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
    def __init__(self, event_controller):
        self.event_controller = event_controller
        self.event_controller.register_listener(self)
        self.gameOver = True
        self.gold_grabbed = False

    def _generate_world(self):
        self.gameOver = False
        self.gold_grabbed = False
        self.pos = (-1, 0)
        self.facing = facing_list['right']
        self.move = [action_list['forward']]

        self.visited = set()
        self.danger = set()
        self.safe = set()
        self.possible_danger = set()

        self.world = numpy.zeros((4, 4, 5))
        self.kb = KnowledgeBase()

        # Place gold randomly
        done = False
        while not done:
            i = random.choice(range(4))
            j = random.choice(range(4))
            if self.world[i][j][1] != 1 and self.world[i][j][4] != 1 and self.world[i][j][2] != 1 and (
                            i != 0 and j != 0):
                self.world[i][j][1] = 1
                done = True

        # Place the wumpus randomly
        done = False
        while not done:
            i = random.choice(range(4))
            j = random.choice(range(4))
            if self.world[i][j][1] != 1 and self.world[i][j][4] != 1 and self.world[i][j][2] != 1 and (
                            i != 0 and j != 0):
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
                if self.world[i][j][1] != 1 and self.world[i][j][4] != 1 and self.world[i][j][2] != 1 and (
                                i != 0 and j != 0):
                    self.world[i][j][2] = 1
                    done = True
                    # generating Breeze
                    for pos in neighbors(i, j):
                        self.world[pos[0]][pos[1]][0] = 1

        ev = event.WorldBuilt(self.world)
        self.event_controller.post(ev)

    def findSafe(self, i, j):
        possible_next = neighbors(i, j) - self.visited
        possible_next -= self.safe
        possible_next -= self.danger

        update_safe = set()
        update_danger = set()

        if (self.world[i][j][0] == 0) and (self.world[i][j][3] == 0):
            self.possible_danger -= set((i, j))
            update_safe |= possible_next
        else:
            self.possible_danger |= possible_next

        print "possible_danger list: ", self.possible_danger, "visited list:", self.visited

        possible_danger = self.possible_danger.copy()
        if len(self.visited) > 1:
            for x in possible_danger:
                if self.kb.ask(expr('(P%s%s | W%s%s)' % (x * 2))):
                    # dpll not satisfied
                    print '(P%s%s | W%s%s)' % (x * 2), "is dangerous"
                    update_danger.add(x)
                    self.possible_danger.remove(x)
                    ev = event.FoundDanger(x)
                    self.event_controller.post(ev)
                elif self.kb.ask(expr('(~P%s%s & ~W%s%s)' % (x * 2))):
                    # dpll satisfied
                    print '(~P%s%s & ~W%s%s)' % (x * 2), "is safe"
                    update_safe.add(x)
                    self.possible_danger.remove(x)
        if len(update_safe) > 0:
            self.safe |= update_safe
        if len(update_danger) > 0:
            self.danger |= update_danger

        print "safe list: ", self.safe

    def collectNeightbors(self, coor1, coor2, path_lst):
        res = []
        for (x, y) in neighbors(coor1, coor2):
            if ((x, y) in self.visited) and ((x, y) not in path_lst):
                res.append((x, y))
        return res

    def shortestPathHelper(self, cost, path):
        path_covered = []
        curr_pos = self.pos
        c = cost[curr_pos]
        while c > 1:
            for i in self.collectNeightbors(curr_pos[0], curr_pos[1], path):
                if cost[i] < c:
                    c = c - 1
                    path_covered.append(i)
                    curr_pos = i
                    break
        return path_covered

    def shortestPath(self, goal):
        visited = self.visited
        cost = {}
        for i in visited:
            cost[i] = float("inf")
        cost[goal] = 0

        path_tracing_lst = [goal]

        while len(path_tracing_lst) > 0:
            tmp = path_tracing_lst.pop()
            for (x, y) in self.collectNeightbors(tmp[0], tmp[1], path_tracing_lst):
                if cost[(x, y)] > cost[tmp] + 1:
                    cost[(x, y)] = cost[tmp] + 1
                    path_tracing_lst.append((x, y))

        path = self.shortestPathHelper(cost, path_tracing_lst)
        path.append(goal)
        return path

    def getMoveFromPath(self, path):
        move = []
        # preserve the previous state
        prev_pos = self.pos
        prev_facing = self.facing
        for pos in path:
            dx = pos[0] - prev_pos[0]
            dy = pos[1] - prev_pos[1]
            dy_dict = {
                -1: 'down',
                1: 'up',
                0: 'up'  # does not move vertically
            }
            dx_dict = {
                -1: 'left',
                1: 'right',
                0: dy_dict[dy]
            }
            facing = facing_list[dx_dict[dx]]
            diff_facing = facing - prev_facing

            if diff_facing != 0:  # direction altered
                pos_diff = abs(diff_facing)
                if pos_diff > 2:    # if face_up-->face_left
                    diff_facing = -diff_facing
                    pos_diff = pos_diff % 2
                if diff_facing < 0:
                    direction = action_list['left']
                elif diff_facing > 0:
                    direction = action_list['right']

                move.extend([direction] * pos_diff) # turn one way pos_diff times
                prev_facing = facing    # update facing
            move.append(action_list['forward'])
            prev_pos = pos
        move.reverse()
        return move

    def shootingRange(self, facing, move_coordinate):
        shooting_range = []
        dx, dy = move_coordinate[facing]
        x, y = (self.pos[0] + dx, self.pos[1] + dy)
        while (x in range(4)) and (y in range(4)):
            shooting_range.append((x, y))
            x, y = (x + dx, y + dy)
        return shooting_range

    def doAction(self, action):
        move_coordinate = {
            facing_list['up']: (0, 1),
            facing_list['right']: (1, 0),
            facing_list['down']: (0, -1),
            facing_list['left']: (-1, 0),
        }
        if action is action_list['forward']:
            dx, dy = move_coordinate[self.facing]
            (next_x, next_y) = (self.pos[0] + dx, self.pos[1] + dy)
            if (next_x, next_y) in neighbors(*self.pos):    # must be valid on board
                ev = event.PlayerForward((next_x, next_y))
                self.event_controller.post(ev)
                if (next_x, next_y) not in self.visited:
                    self.visited.add((next_x, next_y))
                    if (next_x, next_y) in self.safe:
                        self.safe.remove((next_x, next_y))
                    
                    curr_state = self.world[next_x][next_y]

                    if curr_state[1] == 1:  # if has gold then grab it
                        self.doAction(action_list['grab'])
                    elif (curr_state[2] == 1) or (curr_state[4] == 1):  # is has monster or pit then die
                        self.gameOver = True
                        ev = event.PlayerDie()
                        self.event_controller.post(ev)
                    else:
                        # if B or S (possible danger)
                        index = 0
                        knowledge = []
                        for x in curr_state:
                            if x == 1:
                                knowledge.append("%s%s%s" % (map_list[index], next_x, next_y))
                            elif x == 0:
                                knowledge.append("~%s%s%s" % (map_list[index], next_x, next_y))
                            index += 1
                        if len(knowledge) > 0:
                            print "add rules to knowledge base: ", ' & '.join(knowledge)
                            self.kb.addRules(expr(' & '.join(knowledge)))
                        # find next safe move
                        print "before:", "visited:", self.visited, "safe:", self.safe, "danger:", self.danger
                        self.findSafe(next_x, next_y)
                    print "after:", "visited:", self.visited, "safe:", self.safe, "danger:", self.danger
                # update curr pos
                self.pos = (next_x, next_y)

        elif action is action_list['left']:
            self.facing = (self.facing - 1) % 4
            ev = event.PlayerTurn(
                event.PlayerTurn.direction_list['left'], self.facing)
            self.event_controller.post(ev)

        elif action is action_list['right']:
            self.facing = (self.facing + 1) % 4
            ev = event.PlayerTurn(
                event.PlayerTurn.direction_list['right'], self.facing)
            self.event_controller.post(ev)

        elif action is action_list['shoot']:
            for i, j in self.shootingRange(self.facing, move_coordinate):
                if self.world[i][j][4] == 1:
                    self.world[i][j][4] = 0
                    for pos in neighbors(i, j):
                        self.world[pos[0]][pos[1]][3] = 0  # eliminate stench
                    ev = event.PlayerShoot()
                    self.event_controller.post(ev)
                    ev = event.MonsterDie((i, j))
                    self.event_controller.post(ev)

        elif action is action_list['grab']:
            i, j = (self.pos[0], self.pos[1])
            self.world[i][j][1] = 0
            self.gold_grabbed = True
            ev = event.PlayerGrabGold(self.pos)
            self.event_controller.post(ev)

    def next(self):
        if not self.gameOver and (not self.gold_grabbed):
            try:
                action = self.move.pop()
            except IndexError:
                action = self.nextAction()

            self.doAction(action)
        else:
            ev = event.Reset()
            self.event_controller.post(ev)

    def nextAction(self):
        # always prefer the safer strategy each move
        if len(self.safe) > 0:
            next_move_list = self.safe
        elif len(self.possible_danger) > 0:
            next_move_list = self.possible_danger
        else:
            next_move_list = self.danger
        goal = next_move_list.pop()
        optimal_path = self.shortestPath(goal)
        self.move = self.getMoveFromPath(optimal_path)
        action = self.move.pop()
        return action

    def notify(self, e):
        if isinstance(e, event.GenerateRequest):

            self._generate_world()
        elif isinstance(e, event.NextStep):
            self.next()
