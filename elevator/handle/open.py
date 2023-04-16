from elevator.constants import CLEAR_CALL, CLEAR_STOP
from elevator.event import Event


def handle_OPEN(openEvent, elevator):
    state = elevator.state
    state.closed = False
    responseEvents = []
    delay = 0

    assert state.floor == openEvent.floor

    # Clear the call button (if it has been pressed) for this direction
    # on this floor.
    if state.direction is not None:
        if state.callButtons[openEvent.floor][state.direction]:
            responseEvents.append(
                Event(
                    CLEAR_CALL,
                    openEvent.floor,
                    direction=state.direction,
                    delay=delay,
                    causedBy=openEvent,
                )
            )

    # Clear the stop button (if it has been pressed) for this floor.
    if state.stopButtons[openEvent.floor]:
        responseEvents.append(
            Event(
                CLEAR_STOP,
                openEvent.floor,
                delay=delay,
                causedBy=openEvent,
            )
        )

    return responseEvents
