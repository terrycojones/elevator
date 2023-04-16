# flake8: noqa F401
from elevator.constants import UP, DOWN, CALL_PRESSED, STOP_PRESSED, OFF
from elevator.event import Event
from elevator.elevator import runElevator


def testElevator():
    events = [
        Event(STOP_PRESSED, 1, queuedAt=1681606360.6776419, serial=0),
        Event(STOP_PRESSED, 0, queuedAt=1681606364.058727, serial=7),
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
    assert stopButtonCounts[1] == 1
    assert stopButtonCounts[2] == 0
    assert stopButtonCounts[3] == 0
    assert stopButtonCounts[4] == 0

    # Test stop button clear counts.
    stopButtonClearCounts = stats.stopButtonClearCounts
    assert stopButtonClearCounts[0] == 1
    assert stopButtonClearCounts[1] == 1
    assert stopButtonClearCounts[2] == 0
    assert stopButtonClearCounts[3] == 0
    assert stopButtonClearCounts[4] == 0

    # Test arrive counts.
    arriveCounts = stats.arriveCounts
    assert arriveCounts[0] == 1
    assert arriveCounts[1] == 1
    assert arriveCounts[2] == 0
    assert arriveCounts[3] == 0
    assert arriveCounts[4] == 0

    # Test open counts.
    openCounts = stats.openCounts
    assert openCounts[0] == 1
    assert openCounts[1] == 1
    assert openCounts[2] == 0
    assert openCounts[3] == 0
    assert openCounts[4] == 0

    # Test close counts.
    closeCounts = stats.closeCounts
    assert closeCounts[0] == 1
    assert closeCounts[1] == 1
    assert closeCounts[2] == 0
    assert closeCounts[3] == 0
    assert closeCounts[4] == 0

    # Test call button counts.
    callButtonCounts = stats.callButtonCounts
    assert callButtonCounts[0][UP] == 0
    assert callButtonCounts[0][DOWN] == 0
    assert callButtonCounts[1][UP] == 0
    assert callButtonCounts[1][DOWN] == 0
    assert callButtonCounts[2][UP] == 0
    assert callButtonCounts[2][DOWN] == 0
    assert callButtonCounts[3][UP] == 0
    assert callButtonCounts[3][DOWN] == 0
    assert callButtonCounts[4][UP] == 0
    assert callButtonCounts[4][DOWN] == 0

    # Test call button clear counts.
    callButtonClearCounts = stats.callButtonClearCounts
    assert callButtonClearCounts[0][UP] == 0
    assert callButtonClearCounts[0][DOWN] == 0
    assert callButtonClearCounts[1][UP] == 0
    assert callButtonClearCounts[1][DOWN] == 0
    assert callButtonClearCounts[2][UP] == 0
    assert callButtonClearCounts[2][DOWN] == 0
    assert callButtonClearCounts[3][UP] == 0
    assert callButtonClearCounts[3][DOWN] == 0
    assert callButtonClearCounts[4][UP] == 0
    assert callButtonClearCounts[4][DOWN] == 0
