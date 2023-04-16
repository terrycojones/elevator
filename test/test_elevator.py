from elevator.constants import UP, DOWN, CALL_PRESSED, STOP_PRESSED, DEFAULT_FLOORS
from elevator.event import Event
from elevator.elevator import runElevator


def testNoEvents():
    "We must not move if no events are given."
    events = []
    e = runElevator(events)
    assert e.state.floor == 0


class TestUp:
    """Test simple upwards movements"""

    def testUpOneFloor(self):
        "We must be able to go up one floor."
        events = [Event(CALL_PRESSED, 1, direction=UP)]
        e = runElevator(events)
        assert e.state.floor == 1
        assert e.state.closed

    def testUpTwoFloors(self):
        "We must be able to go up two floors."
        events = [Event(CALL_PRESSED, 2, direction=UP)]
        e = runElevator(events)
        assert e.state.floor == 2
        assert e.state.closed

    def testCallToGoUp(self):
        "We must be able to call to go up from the various floors"
        for floor in range(0, DEFAULT_FLOORS - 1):
            events = [Event(CALL_PRESSED, floor, direction=UP)]
            e = runElevator(events)
            assert e.state.floor == floor

    def testCallToGoDownFromFour(self):
        "We must be able to call to go down from the fourth floor"
        events = [Event(CALL_PRESSED, 4, direction=DOWN)]
        e = runElevator(events)
        assert e.state.floor == 4

    def testCallToGoDown(self):
        "We must be able to call to go down from the various floors"
        for floor in range(1, DEFAULT_FLOORS):
            events = [Event(CALL_PRESSED, floor, direction=DOWN)]
            e = runElevator(events)
            assert e.state.floor == floor

    def testUpTwoFloorsOneByOne(self):
        "We must be able to go up two floors, stopping at each."
        events = [
            Event(CALL_PRESSED, 1, direction=UP),
            Event(CALL_PRESSED, 2, direction=UP),
        ]
        e = runElevator(events)
        assert e.state.floor == 2
        assert e.state.closed

    def testUpThreeFloors(self):
        "We must be able to go up three floors."
        events = [Event(CALL_PRESSED, 3, direction=UP)]
        e = runElevator(events)
        assert e.state.floor == 3
        assert e.state.closed

    def testUpThreeFloorsOpenOnce(self):
        """
        We must be able to go up three floors. The door on floor three should
        only open once.
        """
        events = [Event(CALL_PRESSED, 3, direction=UP)]
        e = runElevator(events)
        assert e.state.floor == 3
        assert e.stats.openCounts[3] == 1
        assert e.stats.closeCounts[3] == 1


class TestAlongRoute:
    """Test picking someone up along our way."""

    def testPickUpAlongTheWay(self):
        events = [
            Event(CALL_PRESSED, 2, direction=UP),
            Event(STOP_PRESSED, 3),
            Event(CALL_PRESSED, 1, direction=UP),
        ]
        e = runElevator(events)
        assert e.state.floor == 3


class TestUpDown:
    """Test simple upwards then downwards movements."""

    def testReturnToGround120(self):
        events = [
            Event(CALL_PRESSED, 1, direction=UP),
            Event(STOP_PRESSED, 2),
            # The delay in the following is needed, else the
            # elevator will stop on the way up, and clear this
            # call instead of returning to it after it has gone
            # up.
            Event(CALL_PRESSED, 0, direction=UP, delay=200),
        ]
        e = runElevator(events, floors=10)
        assert e.state.floor == 0
        assert e.state.closed

    def testReturnToGround(self):
        "We must be able to call to go up, then go up, then go down."
        floors = 10
        for callFrom in range(1, floors - 1):
            for stopOn in range(callFrom + 1, floors):
                for returnTo in range(0, stopOn):
                    events = [
                        Event(CALL_PRESSED, callFrom, direction=UP),
                        Event(STOP_PRESSED, stopOn),
                        # The delay in the following is needed, else the
                        # elevator will stop on the way up, and clear this
                        # call instead of returning to it after it has gone
                        # up.
                        Event(CALL_PRESSED, returnTo, direction=UP, delay=200),
                    ]
                    e = runElevator(events, floors=floors)
                    assert (
                        e.state.floor == returnTo
                    ), f"{callFrom=} {stopOn=} {returnTo=} != {e.state.floor}"
                    assert e.state.closed
