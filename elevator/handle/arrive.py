from elevator.constants import (
    UP,
    DOWN,
    ARRIVE,
    OPEN,
    CLOSE,
    CLEAR_CALL,
    CLEAR_STOP,
    SET_DIRECTION,
    CLEAR_DIRECTION,
)
from elevator.event import Event
from elevator.handle.utils import (
    pickDirectionBasedOnStopButtons,
    pickDirectionBasedOnCallButtons,
)


def handle_ARRIVE(arrivalEvent, elevator):
    state = elevator.state
    state.floor = arrivalEvent.floor
    responseEvents = []
    delay = 0

    assert state.closed
    assert state.floor == arrivalEvent.floor
    assert state.direction is not None

    if state.stopButtons[state.floor]:
        # The stop button for this floor was pressed. Clear the button,
        # open the doors, and schedule a door close.
        responseEvents.append(
            Event(CLEAR_STOP, arrivalEvent.floor, delay=delay, causedBy=arrivalEvent)
        )
        responseEvents.append(
            Event(OPEN, arrivalEvent.floor, delay=delay, causedBy=arrivalEvent)
        )
        delay += elevator.openDoorDelay
        responseEvents.append(
            Event(CLOSE, arrivalEvent.floor, delay=delay, causedBy=arrivalEvent)
        )

        nextStopFloor = state.outstandingStop(state.direction)

        if nextStopFloor is not None:
            # A stop button is pressed, so someone on the elevator is
            # expecting to continue on in this direction.
            assert state.direction is not None

            # Clear the call button for this direction on this floor,
            # if pressed.
            if state.callButtons[arrivalEvent.floor][state.direction]:
                responseEvents.append(
                    Event(
                        CLEAR_CALL,
                        arrivalEvent.floor,
                        direction=state.direction,
                        delay=0,
                        causedBy=arrivalEvent,
                    )
                )

            # Schedule the arrival at our next floor.
            nextFloor = state.floor + (1 if nextStopFloor > arrivalEvent.floor else -1)
            assert 0 <= nextFloor < elevator.floors
            if state.destination is None:
                state.destination = nextFloor
            delay += elevator.interFloorDelay
            assert state.destination != state.floor
            responseEvents.append(
                Event(ARRIVE, nextFloor, delay=delay, causedBy=arrivalEvent)
            )
        else:
            # We are not obliged to carry on in the current direction.

            # We must figure out on arrival which way to go next so
            #     the up/down indicator can show people whether to get on or not.
            #     Note that if no buttons are pressed, we will just stop here.
            #
            # Do not look at other stop buttons (pressed for the other
            #     direction by people who changed their minds. Let them wait?)
            #     I.e., the decision about where to go next is based only on
            #     call buttons (their floors and directions). We need a function
            #     that can pick a next direction based on our current floor and
            #     the call button state.
            buttonFloor, direction = pickDirectionBasedOnCallButtons(
                arrivalEvent, state
            )
            if direction is None:
                buttonFloor, direction = pickDirectionBasedOnStopButtons(
                    arrivalEvent, state
                )
            if direction is None:
                # Nothing pressed. Stay here.

                if state.direction is not None:
                    responseEvents.append(
                        Event(
                            CLEAR_DIRECTION,
                            None,
                            delay=0,
                            causedBy=arrivalEvent,
                        )
                    )
                state.direction = None
            else:
                # Clear the call button (if it has been pressed) for
                # this direction on this floor.
                if state.callButtons[arrivalEvent.floor][direction]:
                    responseEvents.append(
                        Event(
                            CLEAR_CALL,
                            arrivalEvent.floor,
                            direction=direction,
                            delay=delay,
                            causedBy=arrivalEvent,
                        )
                    )

                if buttonFloor != state.floor:
                    # Change the elevator current direction to be up/down.
                    if state.direction != direction:
                        responseEvents.append(
                            Event(
                                SET_DIRECTION,
                                None,
                                direction=direction,
                                delay=0,
                                causedBy=arrivalEvent,
                            )
                        )
                    state.direction = direction
                    # Schedule the arrival at our next floor.
                    nextFloor = state.floor + (1 if state.direction == UP else -1)
                    assert 0 <= nextFloor < elevator.floors
                    state.destination = nextFloor
                    delay += elevator.interFloorDelay
                    assert state.destination != state.floor
                    responseEvents.append(
                        Event(ARRIVE, nextFloor, delay=delay, causedBy=arrivalEvent)
                    )
    else:
        # No one wanted to stop at this floor.  We can pick people up
        # here if the call button for our current direction is pressed.
        #
        # Note that there may or may not be a stop or call button
        # further on in the current direction, we may simply have been
        # called to this floor.

        # If we have arrived at the bottom or top of the building we
        # have to change direction.
        if state.floor == 0:
            assert state.direction == DOWN
            state.direction = None
            assert state.destination == 0
            # state.destination = None
        elif state.floor == elevator.floors - 1:
            assert state.direction == UP
            state.direction = None
            assert state.destination == elevator.floors - 1
            # state.destination = None

        if state.direction is not None:
            if state.callButtons[arrivalEvent.floor][state.direction]:
                # We can't always schedule a next ARRIVE event because no
                # buttons may have been pressed. Just let the scheduled
                # CLOSE event happen. Buttons will presumably have been
                # pressed in the meantime (we just opened to let people
                # on. They may still be there, may get on, and may press a
                # button, etc).
                responseEvents.append(
                    Event(OPEN, arrivalEvent.floor, delay=delay, causedBy=arrivalEvent)
                )
                delay += elevator.openDoorDelay
                responseEvents.append(
                    Event(
                        CLOSE,
                        arrivalEvent.floor,
                        delay=delay,
                        causedBy=arrivalEvent,
                    )
                )

            if state.destination is not None and state.destination != state.floor:
                # Don't stop here. Schedule the arrival at the next floor.
                nextFloor = state.floor + (1 if state.direction == UP else -1)
                assert 0 <= nextFloor < elevator.floors
                delay += elevator.interFloorDelay
                responseEvents.append(
                    Event(ARRIVE, nextFloor, delay=delay, causedBy=arrivalEvent)
                )

    return responseEvents
