#!/usr/bin/env python

from time import time

from elevator.constants import (
    DEFAULT_FLOORS,
    END,
    DEFAULT_OPEN_DOOR_DELAY,
    DEFAULT_INTER_FLOOR_DELAY,
)

from elevator.dpq import DelayPriorityQueue
from elevator.event import Event
from elevator.logic import Logic
from elevator.state import State
from elevator.stats import Stats


class Elevator:
    def __init__(
        self,
        queue,
        floors=DEFAULT_FLOORS,
        openDoorDelay=DEFAULT_OPEN_DOOR_DELAY,
        interFloorDelay=DEFAULT_INTER_FLOOR_DELAY,
        testDir=None,
    ):
        self.queue = queue
        self.floors = floors
        self.openDoorDelay = openDoorDelay
        self.interFloorDelay = interFloorDelay
        self.testDir = testDir
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
    """Make an elevator and pass it some pre-determined events."""

    # Put all events into a queue.

    firstEventQueuedAt = None
    now = time()

    queue = DelayPriorityQueue()
    for event in events:
        if firstEventQueuedAt is None:
            firstEventQueuedAt = event.queuedAt

        # If the event has a queued at time, we are replaying events from
        # some earlier source (likely the GUI). Adjust the old times to be
        # relative to the current time to make sure they come out of the
        # queue exactly as they should.
        if event.queuedAt is not None:
            event.queuedAt = now + event.queuedAt - firstEventQueuedAt

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
        type=float,
        default=2.0,
        help="The number of seconds between floors.",
    )

    parser.add_argument(
        "--openDoorDelay",
        type=float,
        default=5.0,
        help="The number of seconds the doors stay open.",
    )

    parser.add_argument(
        "--testDir",
        help="The directory to write automated tests to.",
    )
