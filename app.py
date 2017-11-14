

from event import Tick, AppStart


class App:

    """Application logic"""

    STATE_PREPARING = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2

    def __init__(self, event_controller):
        self.event_controller = event_controller
        self.event_controller.register_listener(self)

        self.state = App.STATE_PREPARING  # self.state=0

    def start(self):
        self.state = App.STATE_RUNNING  # self.state=1
        ev = AppStart(self)
        self.event_controller.post(ev)

    def notify(self, event):
        if isinstance(event, Tick):
            if self.state == App.STATE_PREPARING:
                self.start()

