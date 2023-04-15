import json

from elevated.button import Button
from elevated.constants import (
    DEFAULT_FLOORS,
    DOWN,
    OFF,
    UP,
    describe,
)


class State:
    def __init__(self, floors=DEFAULT_FLOORS):
        assert floors > 0
        self.floors = floors
        self.stopButtons = [Button() for _ in range(floors)]
        self.callButtons = list((Button(), Button()) for _ in range(floors))
        self.indicatorLights = [OFF] * floors
        self.floor = 0
        self.lastDirection = None
        self.closed = True

    def __str__(self):
        stops = " ".join(
            f"{floor}:{button}" for floor, button in enumerate(self.stopButtons)
        )
        calls = " ".join(
            f"{floor}:UP:{up},DOWN:{down}"
            for floor, (up, down) in enumerate(self.callButtons)
        )
        indicators = " ".join(
            f"{floor}:{describe(indicator)}"
            for floor, indicator in enumerate(self.indicatorLights)
        )
        return (
            f"<State floor={self.floor} closed={self.closed} "
            f"direction={describe(self.lastDirection)}, "
            f"stops=[{stops}] calls=[{calls}] indicators=[{indicators}]"
        )

    @classmethod
    def fromJSON(klass, j):
        state = klass(j["floors"])
        state.stopButtons = j["stopButtons"]
        state.callButtons = j["callButtons"]
        state.indicatorLights = j["indicatorLights"]
        state.floor = j["floor"]
        state.lastDirection = j["lastDirection"]
        state.closed = j["closed"]
        return state

    def toJSON(self):
        return json.dumps(
            {
                "floors": self.floors,
                "stopButtons": self.stopButtons,
                "callButtons": self.callButtons,
                "indicatorLights": self.indicatorLights,
                "floor": self.floor,
                "lastDirection": self.lastDirection,
                "closed": self.closed,
            }
        )

    def nextFloorForCall(self, floor):
        """
        What should be the next floor to go to given a call from a floor?
        """
        if floor > self.floor:
            new = self.floor + 1
            assert new < self.floors
            return UP, new
        elif floor < self.floor:
            new = self.floor - 1
            assert new >= 0
            return DOWN, new

        return None, None

    def pressCall(self, floor, direction, when):
        """
        The call button on floor was pressed for a certain direction.
        """
        if floor == self.floors - 1 and direction == UP:
            raise ValueError("UP call button pressed on top floor!")

        if floor == 0 and direction == DOWN:
            raise ValueError("DOWN call button pressed on bottom floor!")

        self.callButtons[floor][direction].press(when)

    def clearCall(self, floor, direction):
        """
        Clear the call button for a given direction on a floor.
        """
        if floor == self.floors - 1 and direction == UP:
            raise ValueError("Cannot clear UP call button on top floor!")

        if floor == 0 and direction == DOWN:
            raise ValueError("Cannot clear DOWN call button on bottom floor!")

        self.callButtons[floor][direction].clear()

    def pressStop(self, floor, when):
        """
        The stop button for a floor was pressed.
        """
        self.stopButtons[floor].press(when)

    def clearStop(self, floor):
        """
        Clear the stop button for a floor.
        """
        self.stopButtons[floor].clear()

    def indicate(self, floor, direction):
        """
        Set the direction indicator for a floor.
        """
        self.indicatorLights[floor] = direction

    def getRemainingFloors(self, direction):
        """
        Get the remaining floors in the given direction, in the order in which
        they will be encountered if the elevator moves in that direction.
        """
        assert direction in {UP, DOWN}
        if direction == UP:
            return tuple(range(self.floor + 1, self.floors))
        else:
            if self.floor == 0:
                return ()
            else:
                return tuple(reversed(range(self.floor)))

    def outstandingCall(self, direction):
        """
        Is there an outstanding pressed call button in the given direction?
        """
        for floor in self.getRemainingFloors(direction):
            if self.callButtons[floor][direction]:
                return floor

    def outstandingStop(self, direction):
        """
        Is there an outstanding pressed stop button in the given direction?
        """
        for floor in self.getRemainingFloors(direction):
            if self.stopButtons[floor]:
                return floor
