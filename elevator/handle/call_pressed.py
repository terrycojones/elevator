from elevator.constants import (
    UP,
    DOWN,
    ARRIVE,
    OPEN,
    CLOSE,
    SET_DIRECTION,
)

from elevator.event import Event


def handle_CALL_PRESSED(callEvent, elevator):
    state = elevator.state
    delay = 0

    if state.callButtons[callEvent.floor][callEvent.direction]:
        # This call button is already pressed and has been reacted to.
        return []

    state.pressCall(callEvent.floor, callEvent.direction, callEvent.handledAt)

    responseEvents = []

    # We only need to figure out what's next if we were not heading somewhere.
    if state.destination is None and state.closed:
        assert state.direction is None
        # We were not in motion. So we can go to the floor of the call.
        if callEvent.floor == state.floor:
            # We are already where we need to be.
            if state.closed:
                # Someone wants to get on, and we're already sitting
                # idle on their floor.  Open the doors to let them on.
                responseEvents.append(Event(OPEN, callEvent.floor, causedBy=callEvent))
                delay += elevator.openDoorDelay
                responseEvents.append(
                    Event(CLOSE, callEvent.floor, delay=delay, causedBy=callEvent)
                )
                # We can't schedule an arrive because they haven't
                # gotten on yet. That will be figured out when the
                # CLOSE happens (they may not even get on). They may
                # also change their mind and press a stop button that
                # is not in the direction they indicated they wanted to
                # go in.
            else:
                # Someone re-pressed the call button even though
                # the doors are open.  We could make sure the next
                # scheduled event is a CLOSE and adjust the close time
                # (but then we would have to also see if there was an
                # ARRIVE also scheduled and adjust that). Then we'd
                # want to limit how many times we do that because
                # otherwise someone could hold the doors open
                # indefinitely. So for now just ignore it.
                pass
        else:
            # The call comes from another floor.
            direction = UP if callEvent.floor > state.floor else DOWN
            if state.direction != direction:
                responseEvents.append(
                    Event(
                        SET_DIRECTION,
                        None,
                        direction=direction,
                        delay=0,
                        causedBy=callEvent,
                    )
                )

            state.direction = direction
            state.destination = callEvent.floor
            nextFloor = state.floor + (1 if state.direction == UP else -1)
            assert 0 <= nextFloor < elevator.floors
            delay += elevator.interFloorDelay
            assert state.destination != state.floor
            responseEvents.append(
                Event(ARRIVE, nextFloor, delay=delay, causedBy=callEvent)
            )

    return responseEvents
