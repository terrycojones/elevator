from elevator.constants import (
    UP,
    ARRIVE,
    OPEN,
    CLOSE,
    CLEAR_CALL,
    SET_DIRECTION,
    CLEAR_DIRECTION,
)
from elevator.event import Event
from elevator.handle.utils import (
    pickDirectionBasedOnStopButtons,
    pickDirectionBasedOnCallButtons,
)


def handle_CLOSE(closeEvent, elevator):
    state = elevator.state
    state.floor = closeEvent.floor
    state.closed = True
    responseEvents = []
    delay = 0

    if state.destination is not None and state.destination != closeEvent.floor:
        assert state.direction is not None
        # We already figured out what floor to go to next (this will
        # happens on arrivals when we have to immediately figure out
        # where we will go next so we can set the indicator so people
        # know whether to get on).
        pass
        # assert state.destination != state.floor
    else:
        # We are not headed anywhere, so we have to figure out where to
        # go, if anywhere.

        # We can't be closing on a floor where a stop button is still
        # outstanding.
        assert not state.stopButtons[closeEvent.floor]

        buttonFloor, direction = pickDirectionBasedOnStopButtons(closeEvent, state)

        if direction is None:
            buttonFloor, direction = pickDirectionBasedOnCallButtons(closeEvent, state)
        if direction is None:
            # Nothing pressed. Stay here.
            if state.direction is not None:
                responseEvents.append(
                    Event(
                        CLEAR_DIRECTION,
                        None,
                        direction=direction,
                        delay=0,
                        causedBy=closeEvent,
                    )
                )
            state.direction = state.destination = None
        else:
            if buttonFloor == state.floor:
                # We were called from the floor we just closed the door on.
                #
                # Note: this cannot be from a stop button (see assert above), it
                # must be from a call.
                assert state.callButtons[state.floor][direction]

                # TODO: This shouldn't be done so late, because we have
                # just above decided to re-open. The call button should
                # be cleared first. Need a test for this.
                #
                # I think this is now fixed.
                if state.callButtons[state.floor][direction]:
                    responseEvents.append(
                        Event(
                            CLEAR_CALL,
                            state.floor,
                            direction=direction,
                            delay=delay,
                            causedBy=closeEvent,
                        )
                    )
                responseEvents.append(
                    Event(OPEN, state.floor, delay=delay, causedBy=closeEvent)
                )
                delay += elevator.openDoorDelay
                responseEvents.append(
                    Event(CLOSE, state.floor, delay=delay, causedBy=closeEvent)
                )
            else:
                if state.callButtons[state.floor][direction]:
                    responseEvents.append(
                        Event(
                            CLEAR_CALL,
                            state.floor,
                            direction=direction,
                            delay=0,
                            causedBy=closeEvent,
                        )
                    )

                if state.direction != direction:
                    responseEvents.append(
                        Event(
                            SET_DIRECTION,
                            None,
                            direction=direction,
                            delay=0,
                            causedBy=closeEvent,
                        )
                    )
                state.direction = direction
                state.destination = buttonFloor
                # Schedule the arrival at our next floor.
                delay += elevator.interFloorDelay
                nextFloor = state.floor + (1 if direction == UP else -1)
                assert 0 <= nextFloor < elevator.floors
                assert state.destination != state.floor
                responseEvents.append(
                    Event(ARRIVE, nextFloor, delay=delay, causedBy=closeEvent)
                )

    return responseEvents
