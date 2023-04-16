from elevator.constants import (
    UP,
    DOWN,
    ARRIVE,
    OPEN,
    CLOSE,
    SET_DIRECTION,
)

from elevator.event import Event


def handle_STOP_PRESSED(stopEvent, elevator):
    state = elevator.state
    delay = 0

    state.pressStop(stopEvent.floor, stopEvent.handledAt)

    responseEvents = []
    # We only need to figure out what's next if we were not moving in a
    # particular direction.
    if state.direction is None and state.closed:
        # We were not in motion. So we can go to the floor of the stop.
        if stopEvent.floor == state.floor:
            # We are already where we need to be.
            if state.closed:
                # Someone wants to get off, and we're already sitting
                # idle on their floor.  Open the doors to let them out.
                responseEvents.append(Event(OPEN, stopEvent.floor, causedBy=stopEvent))
                delay += elevator.openDoorDelay
                responseEvents.append(
                    Event(CLOSE, stopEvent.floor, delay=delay, causedBy=stopEvent)
                )
            else:
                # Someone re-pressed the stop button even though
                # the doors are open.  We could make sure the next
                # scheduled event is a CLOSE and adjust the close time
                # (but then we would have to also see if there was an
                # ARRIVE also scheduled and adjust that). Then we'd
                # want to limit how many times we do that because
                # otherwise someone could hold the doors open
                # indefinitely. So for now just ignore it.
                pass
        else:
            # The stop is for another floor.
            direction = UP if stopEvent.floor > state.floor else DOWN
            if state.direction != direction:
                responseEvents.append(
                    Event(
                        SET_DIRECTION,
                        None,
                        direction=direction,
                        delay=0,
                        causedBy=stopEvent,
                    )
                )
            state.direction = direction
            state.destination = stopEvent.floor
            assert state.destination != state.floor
            nextFloor = state.floor + (1 if state.direction == UP else -1)
            assert 0 <= nextFloor < elevator.floors
            delay += elevator.interFloorDelay
            responseEvents.append(
                Event(ARRIVE, nextFloor, delay=delay, causedBy=stopEvent)
            )

    return responseEvents
