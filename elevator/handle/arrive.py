from elevator.constants import (
    UP,
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


def handle_ARRIVE(arriveEvent, elevator):
    state = elevator.state
    state.floor = arriveEvent.floor
    responseEvents = []
    delay = 0

    # print("ARRIVE:", arriveEvent, state, file=sys.stderr)

    assert state.closed
    assert state.floor == arriveEvent.floor
    assert state.direction is not None

    if state.stopButtons[state.floor]:
        # The stop button for this floor was pressed. Clear the button,
        # open the doors, and schedule a door close.
        responseEvents.append(
            Event(CLEAR_STOP, arriveEvent.floor, delay=delay, causedBy=arriveEvent)
        )
        responseEvents.append(
            Event(OPEN, arriveEvent.floor, delay=delay, causedBy=arriveEvent)
        )
        delay += elevator.openDoorDelay
        responseEvents.append(
            Event(CLOSE, arriveEvent.floor, delay=delay, causedBy=arriveEvent)
        )

        nextStopFloor = state.outstandingStop(state.direction)

        if nextStopFloor is not None:
            # A stop button is pressed, so someone on the elevator is
            # expecting to continue on in this direction.
            assert state.direction is not None

            # Clear the call button for this direction on this floor,
            # if pressed.
            if state.callButtons[arriveEvent.floor][state.direction]:
                responseEvents.append(
                    Event(
                        CLEAR_CALL,
                        arriveEvent.floor,
                        direction=state.direction,
                        delay=0,
                        causedBy=arriveEvent,
                    )
                )

            # Schedule the arrival at our next floor.
            nextFloor = state.floor + (1 if nextStopFloor > arriveEvent.floor else -1)
            assert 0 <= nextFloor < elevator.floors
            if state.destination is None:
                state.destination = nextFloor
            delay += elevator.interFloorDelay
            assert state.destination != state.floor
            responseEvents.append(
                Event(ARRIVE, nextFloor, delay=delay, causedBy=arriveEvent)
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
            buttonFloor, direction = pickDirectionBasedOnCallButtons(arriveEvent, state)
            if direction is None:
                buttonFloor, direction = pickDirectionBasedOnStopButtons(
                    arriveEvent, state
                )
            if direction is None:
                # Nothing pressed. Stay here.

                if state.direction is not None:
                    responseEvents.append(
                        Event(
                            CLEAR_DIRECTION,
                            None,
                            delay=0,
                            causedBy=arriveEvent,
                        )
                    )
                state.direction = None
            else:
                # Clear the call button (if it has been pressed) for
                # this direction on this floor.
                if state.callButtons[arriveEvent.floor][direction]:
                    responseEvents.append(
                        Event(
                            CLEAR_CALL,
                            arriveEvent.floor,
                            direction=direction,
                            delay=delay,
                            causedBy=arriveEvent,
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
                                causedBy=arriveEvent,
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
                        Event(ARRIVE, nextFloor, delay=delay, causedBy=arriveEvent)
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
        #
        # if state.floor == 0:
        #     assert state.direction == DOWN
        #     state.direction = None
        #     assert state.destination == 0
        # elif state.floor == elevator.floors - 1:
        #     assert state.direction == UP
        #     state.direction = None
        #     assert state.destination == elevator.floors - 1

        if state.destination is not None:
            assert state.direction is not None

            if state.destination == state.floor:
                # We were heading to this floor. Open the doors.
                responseEvents.append(
                    Event(OPEN, arriveEvent.floor, delay=delay, causedBy=arriveEvent)
                )
                delay += elevator.openDoorDelay
                responseEvents.append(
                    Event(
                        CLOSE,
                        arriveEvent.floor,
                        delay=delay,
                        causedBy=arriveEvent,
                    )
                )
            else:
                # We are heading somewhere else. Open the doors if the call
                # button has been pressed in the direction we're heading.

                if state.callButtons[arriveEvent.floor][state.direction]:
                    responseEvents.append(
                        Event(
                            CLEAR_CALL,
                            arriveEvent.floor,
                            direction=state.direction,
                            delay=0,
                            causedBy=arriveEvent,
                        )
                    )
                    responseEvents.append(
                        Event(
                            OPEN, arriveEvent.floor, delay=delay, causedBy=arriveEvent
                        )
                    )
                    delay += elevator.openDoorDelay
                    responseEvents.append(
                        Event(
                            CLOSE,
                            arriveEvent.floor,
                            delay=delay,
                            causedBy=arriveEvent,
                        )
                    )

                # Schedule the arrival at the next floor.
                nextFloor = state.floor + (1 if state.direction == UP else -1)
                assert 0 <= nextFloor < elevator.floors
                delay += elevator.interFloorDelay
                responseEvents.append(
                    Event(ARRIVE, nextFloor, delay=delay, causedBy=arriveEvent)
                )

    return responseEvents
