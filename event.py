
class Event:

    def __init__(self):
        self.name = "Generic event"


class TickEvent(Event):
    def __init__(self):
        self.name = "CPU tick"


class QuitEvent(Event):
    def __init__(self):
        self.name = "Program quits"


class AppStartEvent(Event):
    def __init__(self, app):
        self.name = "Program starts"
        self.app = app

class GenerateRequestEvent(Event):
    def __init__(self):
        self.name = "Generate a new world"


class ResetEvent(Event):
    def __init__(self):
        self.name = "Reset the world"


class WorldBuiltEvent(Event):
    def __init__(self, world):
        self.name = "a new world built, let's go ~~"
        self.world = world


class FoundDangerEvent(Event):
    def __init__(self, pos):
        self.name = "found new danger"
        self.pos = pos


class StepEvent(Event):
    def __init__(self):
        self.name = "Next step"


class ToggleAutoEvent(Event):
    def __init__(self):
        self.name = "Auto/manual step mode"


class ToggleViewEvent(Event):
    def __init__(self):
        self.name = "View mode"


class HelpEvent(Event):
    def __init__(self):
        self.name = "Display help info"


class WumpusDieEvent(Event):
    def __init__(self, pos):
        self.name = "Monster dies"
        self.pos = pos


class PlayerForwardEvent(Event):
    def __init__(self, pos):
        self.name = "Player moves forward"
        self.pos = pos



class PlayerTurnEvent(Event):
    direction_list = {'left': 0, 'right': 1}
    def __init__(self, direction, facing):
        if direction is PlayerTurnEvent.direction_list['left']:
            direc = "left"
        elif direction is PlayerTurnEvent.direction_list['right']:
            direc = "right"
        self.name = "Player turns %s" % direc
        self.direction = direction
        self.facing = facing


class PlayerPickEvent(Event):
    def __init__(self, pos):
        self.name = "Player picks the GOLD !! :P"
        self.pos = pos


class PlayerShootEvent(Event):
    def __init__(self):
        self.name = "Player shoots !!!!"


class PlayerPerceiveEvent(Event):
    def __init__(self, percept):
        self.name = "Player perceives %s" % percept
        self.percept = percept


class PlayerDieEvent(Event):
    def __init__(self):
        self.name = "Player dies @T_T@"


class EventManager:

    def __init__(self):
        self.listeners = {}

    def register_listener(self, listener):
        self.listeners[listener] = True

    def UnregisterListener(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, ev):
        if not (isinstance(ev, TickEvent) or \
                isinstance(ev, StepEvent) or \
                isinstance(ev, HelpEvent) or \
                isinstance(ev, ToggleViewEvent) or \
                isinstance(ev, ToggleAutoEvent)):
            print (" >>> " + ev.name)

        for listener in self.listeners.keys():
            # self.listeners is empty dict
            if listener is None:
                del self.listeners[listener]
                continue

            listener.notify(ev)
