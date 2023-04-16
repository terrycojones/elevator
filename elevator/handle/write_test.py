import sys
from pathlib import Path
from datetime import datetime

from elevator.constants import (
    UP,
    DOWN,
    CALL_PRESSED,
    STOP_PRESSED,
    describe,
)
from elevator.event import Event


def handle_WRITE_TEST(event, elevator):
    if elevator.testDir is None:
        print(
            "Received WRITE_TEST event but the elevator testDir is None",
            file=sys.stderr,
        )
        return []

    testDir = Path(elevator.testDir)
    if not testDir.exists():
        testDir.mkdir()

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

    def rhs(value):
        # Produce either an "is" comparison or an "==" one for testing a value.
        return ("is" if value in {None, True, False} else "==") + f" {value}"

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
        print(f"    assert state.closed {rhs(elevator.state.closed)}")
        print(f"    assert state.direction {rhs(elevator.state.direction)}")
        print(f"    assert state.destination {rhs(elevator.state.destination)}")

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

    print(f"Wrote test to {str(testFile)!r}.", file=sys.stderr)
    return []
