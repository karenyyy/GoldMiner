

from event import TickEvent, AppStartEvent


class App:

    """Application logic"""

    STATE_PREPARING = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2

    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)

        self.state = App.STATE_PREPARING  # self.state=0

    def start(self):
        self.state = App.STATE_RUNNING  # self.state=1
        ev = AppStartEvent(self)
        self.ev_manager.post(ev)

    def notify(self, event):
        if isinstance(event, TickEvent):
            if self.state == App.STATE_PREPARING:
                self.start()

