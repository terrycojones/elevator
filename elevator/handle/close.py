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
            # We cannot consider re-opening on our current floor. This is
            # because we may be closing after opening for the exact same
            # call. I.e., opening twice on the floor. It is not possible to
            # clear the call button on arrival because we do not _always_
            # know in which direction we will go next.
            buttonFloor, direction = pickDirectionBasedOnCallButtons(
                closeEvent, state, considerCurrentFloor=False
            )

        if direction is None:
            # Nothing pressed. Stay here.
            if state.direction is not None:
                responseEvents.append(
                    Event(
                        CLEAR_DIRECTION,
                        None,
                        delay=0,
                        causedBy=closeEvent,
                    )
                )
            state.direction = state.destination = None
        else:
            # We must be going to a different floor.
            assert buttonFloor != state.floor

            # Turn off (if it is on) the direction light on this floor for
            # the direction we're going in.
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
            delay += elevator.interFloorDelay
            nextFloor = state.floor + (1 if direction == UP else -1)
            assert 0 <= nextFloor < elevator.floors
            assert state.destination != state.floor
            responseEvents.append(
                Event(ARRIVE, nextFloor, delay=delay, causedBy=closeEvent)
            )

    return responseEvents
