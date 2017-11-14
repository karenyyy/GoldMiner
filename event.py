class Event:
    def __init__(self):
        self.name = "Generic event"


class Tick(Event):
    def __init__(self):
        self.name = "CPU tick"


class Quit(Event):
    def __init__(self):
        self.name = "Program quits"


class AppStart(Event):
    def __init__(self, app):
        self.name = "Program starts"
        self.app = app


class GenerateRequest(Event):
    def __init__(self):
        self.name = "Generate a new world"


class Reset(Event):
    def __init__(self):
        self.name = "Reset the world"


class WorldBuilt(Event):
    def __init__(self, world):
        self.name = "a new world built, let's go ~~"
        self.world = world


class FoundDanger(Event):
    def __init__(self, pos):
        self.name = "found new danger"
        self.pos = pos


class NextStep(Event):
    def __init__(self):
        self.name = "Next step"


class AutoMode(Event):
    def __init__(self):
        self.name = "Auto/manual step mode"


class View(Event):
    def __init__(self):
        self.name = "View mode"


class Help(Event):
    def __init__(self):
        self.name = "Display help info"


class MonsterDie(Event):
    def __init__(self, pos):
        self.name = "Monster dies"
        self.pos = pos


class PlayerForward(Event):
    def __init__(self, pos):
        self.name = "Player moves forward"
        self.pos = pos


class PlayerTurn(Event):
    direction_list = {'left': 0, 'right': 1}

    def __init__(self, direction, facing):
        if direction is PlayerTurn.direction_list['left']:
            direc = "left"
        elif direction is PlayerTurn.direction_list['right']:
            direc = "right"
        self.name = "Player turns %s" % direc
        self.direction = direction
        self.facing = facing


class PlayerGrabGold(Event):
    def __init__(self, pos):
        self.name = "Player grabs the GOLD !! :P"
        self.pos = pos


class PlayerShoot(Event):
    def __init__(self):
        self.name = "Player shoots !!!!"


class PlayerDie(Event):
    def __init__(self):
        self.name = "Player dies @T_T@"


class EventController:
    def __init__(self):
        self.listeners = {}

    def register_listener(self, listener):
        self.listeners[listener] = True

    def UnregisterListener(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, ev):
        if not (isinstance(ev, Tick) or isinstance(ev, NextStep) or isinstance(ev, Help) or isinstance(ev, View) or isinstance(ev, AutoMode)):
            print " >>>>>> ", ev.name

        for listener in self.listeners.keys():
            if listener is None:
                del self.listeners[listener]
                continue

            listener.notify(ev)
