from elevator.state import State
from elevator.constants import UP, DOWN


class TestRemainingUpFloors:
    def testFromGround(self):
        s = State()
        assert (1, 2, 3, 4) == s.getRemainingFloors(UP)

    def testFromTop(self):
        s = State(5)
        s.floor = 4
        assert () == s.getRemainingFloors(UP)


class TestRemainingDownFloors:
    def testFromGround(self):
        s = State()
        assert () == s.getRemainingFloors(DOWN)

    def testFromTop(self):
        s = State(5)
        s.floor = 4
        assert (3, 2, 1, 0) == s.getRemainingFloors(DOWN)


class TestOutstandingCall:
    def testUpFromBottom(self):
        FLOORS = 6
        for floor in range(1, FLOORS - 1):
            s = State(FLOORS)
            s.pressCall(floor, UP, 0)
            assert s.outstandingCall(UP) == floor

    def testDownFromTop(self):
        FLOORS = 6
        for floor in range(1, FLOORS - 1):
            s = State(FLOORS)
            s.floor = FLOORS - 1
            s.currentDirection = DOWN
            s.pressCall(floor, DOWN, 0)
            assert s.outstandingCall(DOWN) == floor
