import sys

from elevated.constants import (
    END,
    CLEAR_STOP,
    WRITE_TEST,
    RESET,
    DEFAULT_FLOORS,
    CLEAR_DIRECTION,
    SET_DIRECTION,
    describe,
)


class Stats:
    IGNORED = {END, CLEAR_STOP, WRITE_TEST, RESET, CLEAR_DIRECTION, SET_DIRECTION}

    def __init__(self, floors=DEFAULT_FLOORS):
        assert floors > 0
        self.floors = floors
        self.stopButtonCounts = [0] * floors
        self.stopButtonClearCounts = [0] * floors
        self.callButtonCounts = [[0, 0] for _ in range(floors)]
        self.callButtonClearCounts = [[0, 0] for _ in range(floors)]
        self.arriveCounts = [0] * floors
        self.openCounts = [0] * floors
        self.closeCounts = [0] * floors

    def handleEvent(self, event):
        try:
            handler = getattr(self, f"handle_{describe(event.what).upper()}")
        except AttributeError:
            if event.what not in self.IGNORED:
                print(
                    f"No stats handler found for {describe(event.what)} event {event}. "
                    f"Ignoring.",
                    file=sys.stderr,
                )
        else:
            return handler(event)

    def handle_STOP_PRESSED(self, event):
        self.stopButtonCounts[event.floor] += 1

    def handle_CLEAR_STOP(self, event):
        self.stopButtonClearCounts[event.floor] += 1

    def handle_CALL_PRESSED(self, event):
        self.callButtonCounts[event.floor][event.direction] += 1

    def handle_CLEAR_CALL(self, event):
        self.callButtonClearCounts[event.floor][event.direction] += 1

    def handle_ARRIVE(self, event):
        self.arriveCounts[event.floor] += 1

    def handle_CLOSE(self, event):
        self.closeCounts[event.floor] += 1

    def handle_OPEN(self, event):
        self.openCounts[event.floor] += 1
