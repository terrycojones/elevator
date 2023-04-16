from elevator.constants import (
    UP,
    DOWN,
    ARRIVE,
    CLOSE,
)


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
