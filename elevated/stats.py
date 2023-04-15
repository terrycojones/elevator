import sys

from elevated.constants import END, DEFAULT_FLOORS, describe


class Stats:
    IGNORED = {END}

    def __init__(self, floors=DEFAULT_FLOORS):
        assert floors > 0
        self.floors = floors
        self.stopButtonCounts = [0] * floors
        self.callButtonCounts = [[0, 0] for _ in range(floors)]
        self.callButtonClearCounts = [[0, 0] for _ in range(floors)]
        self.indicatorLightCounts = [[0, 0] for _ in range(floors)]
        self.indicatorLightClearCounts = [0] * floors
        self.arriveCounts = [0] * floors
        self.openCounts = [0] * floors
        self.closeCounts = [0] * floors

    def handleEvent(self, event):
        try:
            handler = getattr(self, f"handle_{describe(event.what).upper()}")
        except AttributeError:
            if event.what not in self.IGNORED:
                print(
                    f"No handler found for {describe(event.what)} event {event}. "
                    f"Ignoring.",
                    file=sys.stderr,
                )
        else:
            return handler(event)

    def handle_STOP(self, event):
        self.stopButtonCounts[event.floor] += 1

    def handle_CALL(self, event):
        self.callButtonCounts[event.floor][event.direction] += 1

    def handle_CLEAR_CALL(self, event):
        self.callButtonClearCounts[event.floor][event.direction] += 1

    def handle_ARRIVE(self, event):
        self.arriveCounts[event.floor] += 1

    def handle_CLOSE(self, event):
        self.closeCounts[event.floor] += 1

    def handle_OPEN(self, event):
        print("STAT OPEN", event, file=sys.stderr)
        self.openCounts[event.floor] += 1

    def handle_LIGHT_INDICATOR(self, event):
        self.indicatorLightCounts[event.floor][event.direction] += 1

    def handle_CLEAR_INDICATOR(self, event):
        self.indicatorLightClearCounts[event.floor] += 1
