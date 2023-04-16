# flake8: noqa F401
from elevator.constants import UP, DOWN, CALL_PRESSED, STOP_PRESSED, OFF
from elevator.event import Event
from elevator.elevator import runElevator


def testElevator():
    events = [
        Event(CALL_PRESSED, 2, direction=UP, queuedAt=1681606483.657214, serial=0),
        Event(STOP_PRESSED, 4, queuedAt=1681606489.195549, serial=8),
        Event(CALL_PRESSED, 4, direction=DOWN, queuedAt=1681606495.160845, serial=16),
        Event(STOP_PRESSED, 0, queuedAt=1681606498.437873, serial=22),
    ]
    e = runElevator(events, floors=5, openDoorDelay=0.5, interFloorDelay=0.5)
    state = e.state
    stats = e.stats

    assert state.floor == 0
    assert state.closed is True
    assert state.direction is None
    assert state.destination is None

    # Test stop buttons.
    stopButtons = state.stopButtons
    assert stopButtons[0].state is False
    assert stopButtons[1].state is False
    assert stopButtons[2].state is False
    assert stopButtons[3].state is False
    assert stopButtons[4].state is False

    # Test call buttons.
    callButtons = state.callButtons
    assert callButtons[0][UP].state is False
    assert callButtons[0][DOWN].state is False
    assert callButtons[1][UP].state is False
    assert callButtons[1][DOWN].state is False
    assert callButtons[2][UP].state is False
    assert callButtons[2][DOWN].state is False
    assert callButtons[3][UP].state is False
    assert callButtons[3][DOWN].state is False
    assert callButtons[4][UP].state is False
    assert callButtons[4][DOWN].state is False

    # Test stop button counts.
    stopButtonCounts = stats.stopButtonCounts
    assert stopButtonCounts[0] == 1
    assert stopButtonCounts[1] == 0
    assert stopButtonCounts[2] == 0
    assert stopButtonCounts[3] == 0
    assert stopButtonCounts[4] == 1

    # Test stop button clear counts.
    stopButtonClearCounts = stats.stopButtonClearCounts
    assert stopButtonClearCounts[0] == 1
    assert stopButtonClearCounts[1] == 0
    assert stopButtonClearCounts[2] == 0
    assert stopButtonClearCounts[3] == 0
    assert stopButtonClearCounts[4] == 1

    # Test arrive counts.
    arriveCounts = stats.arriveCounts
    assert arriveCounts[0] == 1
    assert arriveCounts[1] == 2
    assert arriveCounts[2] == 2
    assert arriveCounts[3] == 2
    assert arriveCounts[4] == 1

    # Test open counts.
    openCounts = stats.openCounts
    assert openCounts[0] == 1
    assert openCounts[1] == 0
    assert openCounts[2] == 1
    assert openCounts[3] == 0
    assert openCounts[4] == 2

    # Test close counts.
    closeCounts = stats.closeCounts
    assert closeCounts[0] == 1
    assert closeCounts[1] == 0
    assert closeCounts[2] == 1
    assert closeCounts[3] == 0
    assert closeCounts[4] == 2

    # Test call button counts.
    callButtonCounts = stats.callButtonCounts
    assert callButtonCounts[0][UP] == 0
    assert callButtonCounts[0][DOWN] == 0
    assert callButtonCounts[1][UP] == 0
    assert callButtonCounts[1][DOWN] == 0
    assert callButtonCounts[2][UP] == 1
    assert callButtonCounts[2][DOWN] == 0
    assert callButtonCounts[3][UP] == 0
    assert callButtonCounts[3][DOWN] == 0
    assert callButtonCounts[4][UP] == 0
    assert callButtonCounts[4][DOWN] == 1

    # Test call button clear counts.
    callButtonClearCounts = stats.callButtonClearCounts
    assert callButtonClearCounts[0][UP] == 0
    assert callButtonClearCounts[0][DOWN] == 0
    assert callButtonClearCounts[1][UP] == 0
    assert callButtonClearCounts[1][DOWN] == 0
    assert callButtonClearCounts[2][UP] == 1
    assert callButtonClearCounts[2][DOWN] == 0
    assert callButtonClearCounts[3][UP] == 0
    assert callButtonClearCounts[3][DOWN] == 0
    assert callButtonClearCounts[4][UP] == 0
    assert callButtonClearCounts[4][DOWN] == 1
