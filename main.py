
from agent import Agent
from app import App
from controller import *
from event import EventController
from human import Human
from view import MainFrame


def main():
    event_controller = EventController()

    main_frame = MainFrame(event_controller)
    spinner = CPUSpinnerController(event_controller)
    mode = raw_input("Human mode (H/h) / AI mode (A/a) : ")
    keyboard = KeyboardController(event_controller)


    if mode == "H" or mode == "h":
        human = Human(event_controller)
    elif mode == "A" or mode == "a":
        ai = Agent(event_controller)

    else:
        print "Plz put in the right mode (# o #)"

    app = App(event_controller)

    spinner.run()


if __name__ == "__main__":
    main()

