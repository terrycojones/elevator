from elevated.constants import UP, DOWN, CALL, OFF, STOP
from elevated.event import Event
from elevated.elevator import runElevator

def testElevator():
    events = [
        Event(CALL, 3, UP),
        Event(STOP, 0),
    ]
    e = runElevator(events, floors=5)
    state = e.state

    assert state.floor == 0
    assert state.closed == True

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

    # Test direction indicator lights.
    indicatorLights = state.indicatorLights
    assert indicatorLights[0] == OFF
    assert indicatorLights[1] == OFF
    assert indicatorLights[2] == OFF
    assert indicatorLights[3] == OFF
    assert indicatorLights[4] == OFF
