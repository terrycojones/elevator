import sys
from datetime import datetime

from elevator.constants import (
    ARRIVE,
    CALL_PRESSED,
    CLOSE,
    DOWN,
    STOP_PRESSED,
    UP,
    describe,
)
from elevator.event import Event


def pickDirectionBasedOnStopButtons(event, state):
    presses = []
    for floor in range(state.floors):
        if floor != event.floor:
            button = state.stopButtons[floor]
            if button:
                presses.append((button, floor))

    # If there were some stop buttons pressed, head towards the floor where
    # the earliest button press happened.
    if presses:
        presses.sort()
        floor = presses[0][1]
        return floor, UP if floor > state.floor else DOWN

    # There were no stop presses.
    return None, None


def pickDirectionBasedOnCallButtons(event, state):
    assert event.what in {ARRIVE, CLOSE}

    # If one or more call buttons on the floor we are on is pressed, pick a
    # direction based on these.

    if state.callButtons[event.floor][UP] and state.callButtons[event.floor][DOWN]:
        # Both up and down call buttons are pressed on the floor we just arrived on.
        # Go in the direction of the earliest press.
        if state.callButtons[event.floor][UP] < state.callButtons[event.floor][DOWN]:
            return event.floor, UP
        else:
            return event.floor, DOWN
    elif state.callButtons[event.floor][UP]:
        return event.floor, UP
    elif state.callButtons[event.floor][DOWN]:
        return event.floor, DOWN

    # Look for call buttons on other floors.
    presses = []
    for floor in range(state.floors):
        if floor != event.floor:
            for direction in UP, DOWN:
                button = state.callButtons[floor][direction]
                if button:
                    presses.append((button, floor))

    # If there were some presses, head towards the floor where the earliest
    # call happened.
    if presses:
        presses.sort()
        floor = presses[0][1]
        return floor, UP if floor > state.floor else DOWN

    # There were no call presses.
    return None, None


def _rhs(value):
    # Produce either an "is" comparison or an "==" one for testing a value.
    return ("is" if value in {None, True, False} else "==") + f" {value!r}"


def writeTest(elevator, testDir):
    date = datetime.now().strftime("%Y%m%d")
    count = 1 + max(
        map(
            int,
            [
                str(filename).rsplit("-", maxsplit=1)[1].split(".")[0]
                for filename in testDir.glob(f"test_{date}-*.py")
            ],
        ),
        default=0,
    )

    testFile = testDir / f"test_{date}-{count:03d}.py"
    assert not testFile.exists()

    with open(testFile, "w") as fp:
        sys.stdout = fp
        print(
            """\
# flake8: noqa F401
from elevator.constants import UP, DOWN, CALL_PRESSED, STOP_PRESSED, OFF
from elevator.event import Event
from elevator.elevator import runElevator

def testElevator():
    events = ["""
        )

        wantedEvents = {UP, DOWN, CALL_PRESSED, STOP_PRESSED}
        for event in elevator.history:
            if event.what in wantedEvents:
                direction = (
                    ""
                    if event.direction is None
                    else f", direction={describe(event.direction)}"
                )
                delay = "" if event.delay == 0 else f", delay={event.delay}"
                print(
                    f"        Event({describe(event.what)}, "
                    f"{event.floor}{direction}{delay}, "
                    f"queuedAt={event.queuedAt}, "
                    f"serial={event.serial}),"
                )

        print(
            f"    ]\n    e = runElevator(events, "
            f"floors={elevator.floors}, "
            f"openDoorDelay={elevator.openDoorDelay}, "
            f"interFloorDelay={elevator.interFloorDelay})"
        )
        print("    state = e.state")
        print("    stats = e.stats\n")

        print(f"    assert state.floor == {elevator.state.floor}")
        print(f"    assert state.closed {_rhs(elevator.state.closed)}")
        print(f"    assert state.direction {_rhs(elevator.state.direction)}")
        print(f"    assert state.destination {_rhs(elevator.state.destination)}")

        print("\n    # Test stop buttons.")
        print("    stopButtons = state.stopButtons")
        for floor in range(elevator.floors):
            print(
                f"    assert stopButtons[{floor}].state is "
                f"{elevator.state.stopButtons[floor].state}"
            )

        print("\n    # Test call buttons.")
        print("    callButtons = state.callButtons")
        for floor in range(elevator.floors):
            for direction in UP, DOWN:
                print(
                    f"    assert callButtons[{floor}]["
                    f"{describe(direction)}].state is "
                    f"{elevator.state.callButtons[floor][direction].state}"
                )

        print("\n    # Test stop button counts.")
        print("    stopButtonCounts = stats.stopButtonCounts")
        for floor in range(elevator.floors):
            print(
                f"    assert stopButtonCounts[{floor}] "
                f"== {elevator.stats.stopButtonCounts[floor]}"
            )

        print("\n    # Test stop button clear counts.")
        print("    stopButtonClearCounts = stats.stopButtonClearCounts")
        for floor in range(elevator.floors):
            print(
                f"    assert stopButtonClearCounts[{floor}] "
                f"== {elevator.stats.stopButtonClearCounts[floor]}"
            )

        print("\n    # Test arrive counts.")
        print("    arriveCounts = stats.arriveCounts")
        for floor in range(elevator.floors):
            print(
                f"    assert arriveCounts[{floor}] "
                f"== {elevator.stats.arriveCounts[floor]}"
            )

        print("\n    # Test open counts.")
        print("    openCounts = stats.openCounts")
        for floor in range(elevator.floors):
            print(
                f"    assert openCounts[{floor}] "
                f"== {elevator.stats.openCounts[floor]}"
            )

        print("\n    # Test close counts.")
        print("    closeCounts = stats.closeCounts")
        for floor in range(elevator.floors):
            print(
                f"    assert closeCounts[{floor}] "
                f"== {elevator.stats.closeCounts[floor]}"
            )

        print("\n    # Test call button counts.")
        print("    callButtonCounts = stats.callButtonCounts")
        for floor in range(elevator.floors):
            for direction in UP, DOWN:
                print(
                    f"    assert callButtonCounts[{floor}]["
                    f"{describe(direction)}] == "
                    f"{elevator.stats.callButtonCounts[floor][direction]}"
                )

        print("\n    # Test call button clear counts.")
        print("    callButtonClearCounts = stats.callButtonClearCounts")
        for floor in range(elevator.floors):
            for direction in UP, DOWN:
                print(
                    f"    assert callButtonClearCounts[{floor}]["
                    f"{describe(direction)}] == "
                    f"{elevator.stats.callButtonClearCounts[floor][direction]}"
                )

    sys.stdout = sys.__stdout__

    return testFile
