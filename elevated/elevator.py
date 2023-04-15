#!/usr/bin/env python

from elevated.constants import (
    DEFAULT_FLOORS,
    END,
    DEFAULT_OPEN_DOOR_DELAY,
    DEFAULT_INTER_FLOOR_DELAY,
)

from elevated.dpq import DelayPriorityQueue
from elevated.event import Event
from elevated.logic import Logic
from elevated.state import State
from elevated.stats import Stats


class Elevator:
    def __init__(
        self,
        queue,
        floors=DEFAULT_FLOORS,
        openDoorDelay=DEFAULT_OPEN_DOOR_DELAY,
        interFloorDelay=DEFAULT_INTER_FLOOR_DELAY,
    ):
        self.queue = queue
        self.floors = floors
        self.openDoorDelay = openDoorDelay
        self.interFloorDelay = interFloorDelay
        self.logic = Logic(self)
        self.reset()

    def reset(self):
        self.state = State(self.floors)
        self.stats = Stats(self.floors)
        self.history = []

    def handleEvent(self, respectTime=True):
        event = self.queue.get(respectTime)
        if event:
            self.history.append(event)
            self.stats.handleEvent(event)
            for responseEvent in self.logic.handleEvent(event):
                self.queue.put(responseEvent)
            return event


def runElevator(
    events,
    floors=DEFAULT_FLOORS,
    openDoorDelay=DEFAULT_OPEN_DOOR_DELAY,
    interFloorDelay=DEFAULT_INTER_FLOOR_DELAY,
):
    """Make an elevator and pass it some events."""
    queue = DelayPriorityQueue()
    for event in events:
        queue.put(event)
    queue.put(Event(END, None))
    elevator = Elevator(
        queue=queue,
        floors=floors,
        openDoorDelay=openDoorDelay,
        interFloorDelay=interFloorDelay,
    )

    while True:
        event = elevator.handleEvent(respectTime=False)
        if event:
            if event.what == END:
                assert len(queue) == 0
                break

    return elevator


def addStandardOptions(parser):
    parser.add_argument(
        "--floors",
        type=int,
        default=5,
        help="The number of floors in the building.",
    )

    parser.add_argument(
        "--interFloorDelay",
        type=int,
        default=2,
        help="The number of seconds between floors.",
    )

    parser.add_argument(
        "--openDoorDelay",
        type=int,
        default=5,
        help="The number of seconds the doors stay open.",
    )
