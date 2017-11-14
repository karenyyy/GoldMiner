
from agent import Agent
from app import App
from controller import *
from event import EventManager
from human import Human
from view import MainFrame


def main():
    ev_manager = EventManager()

    main_frame = MainFrame(ev_manager)
    spinner = CPUSpinnerController(ev_manager)
    mode = raw_input("Human mode (H/h) / AI mode (A/a) : ")
    keybd = KeyboardController(ev_manager)

    if mode == "H" or mode == "h":
        human = Human(ev_manager)
    elif mode == "A" or mode == "a":
        ai = Agent(ev_manager)
    else:
        print "Plz put in the right mode"

    app = App(ev_manager)

    spinner.run()

if __name__ == "__main__":
    main()

