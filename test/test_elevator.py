from elevated.constants import UP, DOWN, CALL, STOP, DEFAULT_FLOORS
from elevated.event import Event
from elevated.elevator import runElevator


def testNoEvents():
    "We must not move if no events are given."
    events = []
    e = runElevator(events)
    assert e.state.floor == 0


class TestUp:
    """Test simple upwards movements"""

    def testUpOneFloor(self):
        "We must be able to go up one floor."
        events = [Event(CALL, 1, direction=UP)]
        e = runElevator(events)
        assert e.state.floor == 1
        assert e.state.closed

    def testUpTwoFloors(self):
        "We must be able to go up two floors."
        events = [Event(CALL, 2, direction=UP)]
        e = runElevator(events)
        assert e.state.floor == 2
        assert e.state.closed

    def testCallToGoUp(self):
        "We must be able to call to go up from the various floors"
        for floor in range(0, DEFAULT_FLOORS - 1):
            events = [Event(CALL, floor, direction=UP)]
            e = runElevator(events)
            assert e.state.floor == floor

    def testCallToGoDown(self):
        "We must be able to call to go down from the various floors"
        for floor in range(1, DEFAULT_FLOORS):
            events = [Event(CALL, floor, direction=DOWN)]
            e = runElevator(events)
            assert e.state.floor == floor

    def testUpTwoFloorsOneByOne(self):
        "We must be able to go up two floors, stopping at each."
        events = [
            Event(CALL, 1, direction=UP),
            Event(CALL, 2, direction=UP),
        ]
        e = runElevator(events)
        assert e.state.floor == 2
        assert e.state.closed

    def testUpThreeFloors(self):
        "We must be able to go up three floors."
        events = [Event(CALL, 3, direction=UP)]
        e = runElevator(events)
        assert e.state.floor == 3
        assert e.state.closed

    def testUpThreeFloorsOpenOnce(self):
        """
        We must be able to go up three floors. The door on floor three should
        only open once.
        """
        events = [Event(CALL, 3, direction=UP)]
        e = runElevator(events)
        assert e.state.floor == 3
        assert e.stats.openCounts[3] == 1
        assert e.stats.closeCounts[3] == 1


class TestAlongRoute:
    """Test picking someone up along our way."""

    def testPickUpAlongTheWay(self):
        events = [
            Event(CALL, 2, direction=UP),
            Event(STOP, 3),
            Event(CALL, 1, direction=UP),
        ]
        e = runElevator(events)
        assert e.state.floor == 3


class TestUpDown:
    """Test simple upwards then downwards movements."""

    def testPickUpAlongTheWay(self):
        events = [
            Event(CALL, 2, direction=UP),
            Event(STOP, 3),
            Event(CALL, 1, direction=UP),
        ]
        e = runElevator(events)
        assert e.state.floor == 3

    def testReturnToGround(self):
        "We must be able to call to go up, then go up, then go down."
        floors = 10
        for callFrom in range(1, floors - 1):
            for stopOn in range(callFrom + 1, floors):
                for returnTo in range(0, stopOn):
                    events = [
                        Event(CALL, callFrom, direction=UP),
                        Event(STOP, stopOn),
                        # The delay in the following is needed, else the
                        # elevator will stop on the way up, and clear this
                        # call instead of returning to it after it has gone
                        # up.
                        Event(CALL, returnTo, direction=UP, delay=200),
                    ]
                    e = runElevator(events, floors=floors)
                    assert (
                        e.state.floor == returnTo
                    ), f"{callFrom=} {stopOn=} {returnTo=} != {e.state.floor}"
                    assert e.state.closed
