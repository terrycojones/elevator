import sys
from pathlib import Path
from datetime import datetime

from elevated.constants import (
    UP,
    DOWN,
    ARRIVE,
    OPEN,
    CLOSE,
    CALL,
    OFF,
    END,
    STOP,
    CLEAR_CALL,
    CLEAR_STOP,
    LIGHT_INDICATOR,
    CLEAR_INDICATOR,
    WRITE_TEST,
    describe,
)

from elevated.event import Event


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
        assert floor != event.floor
        return floor, UP if floor > state.floor else DOWN

    # There were no call presses.
    return None, None


class Logic:
    def __init__(self, elevator):
        self.elevator = elevator

    def handleEvent(self, event):
        handler = getattr(self, f"handle_{describe(event.what).upper()}")
        if handler:
            return handler(event)
        else:
            print(
                f"No handler found for {describe(event.what)} event {event}",
                file=sys.stderr,
            )

    def handle_RESET(self, event):
        self.elevator.reset()
        return []

    def handle_STOP(self, stopEvent):
        elevator = self.elevator
        state = elevator.state
        delay = 0

        state.pressStop(stopEvent.floor, stopEvent.handledAt)

        responseEvents = []
        # We only need to figure out what's next if we were not moving in a
        # particular direction.
        if state.lastDirection is None:
            # We were not in motion. So we can go to the floor of the stop.
            if stopEvent.floor == state.floor:
                # We are already where we need to be.
                if state.closed:
                    # Someone wants to get off, and we're already sitting
                    # idle on their floor.  Open the doors to let them out.
                    responseEvents.append(
                        Event(OPEN, stopEvent.floor, causedBy=stopEvent)
                    )
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
                state.lastDirection = direction
                # Schedule the arrival at our next floor.
                nextFloor = state.floor + (1 if direction == UP else -1)
                assert 0 <= nextFloor < elevator.floors
                delay += elevator.interFloorDelay
                responseEvents.append(
                    Event(ARRIVE, nextFloor, delay=delay, causedBy=stopEvent)
                )

        return responseEvents

    def handle_END(self, event):
        return []

    def handle_WRITE_TEST(self, event):
        elevator = self.elevator
        if elevator.testDir is None:
            print(
                "Received WRITE_TEST event but the elevator testDir is None",
                file=sys.stderr,
            )
            return []

        testDir = Path(elevator.testDir)
        if not testDir.exists():
            testDir.mkdir()

        date = datetime.now().strftime("%Y%m%d")
        count = len(tuple(testDir.glob(f"test_{date}-*.py")))

        while True:
            count += 1
            testFile = testDir / f"test_{date}-{count:03d}.py"
            if not testFile.exists():
                break

        with open(testFile, "w") as fp:
            sys.stdout = fp
            print(
                """\
from elevated.constants import UP, DOWN, CALL, OFF, STOP
from elevated.event import Event
from elevated.elevator import runElevator

def testElevator():
    events = ["""
            )

            wantedEvents = {UP, DOWN, CALL, STOP}
            lastHandledAt = None
            for event in elevator.history:
                if event.what in wantedEvents:
                    assert event.delay == 0
                    if lastHandledAt is None:
                        lastHandledAt = event.handledAt
                    event.delay = event.handledAt - lastHandledAt
                    lastHandledAt = event.handledAt
                    direction = (
                        ""
                        if event.direction is None
                        else f", {describe(event.direction).upper()}"
                    )
                    delay = (
                        ""
                        if event.delay == 0
                        else f", delay={event.delay}"
                    )
                    print(
                        f"        Event({describe(event.what).upper()}, "
                        f"{event.floor}{direction}{delay}),"
                        # f"queuedAt={event.queuedAt}),"
                    )

            print(f"    ]\n    e = runElevator(events, floors={elevator.floors})")
            print("    state = e.state\n")

            print(f"    assert state.floor == {elevator.state.floor}")
            print(f"    assert state.closed == {elevator.state.closed}")
            print("\n    # Test stop buttons.")
            print("    stopButtons = state.stopButtons")

            for floor in range(elevator.floors):
                print(f"    assert stopButtons[{floor}].state is "
                      f"{elevator.state.stopButtons[floor].state}")

            print("\n    # Test call buttons.")
            print("    callButtons = state.callButtons")

            for floor in range(elevator.floors):
                for direction in UP, DOWN:
                    print(f"    assert callButtons[{floor}]["
                          f"{describe(direction).upper()}].state is "
                          f"{elevator.state.callButtons[floor][direction].state}")

            print("\n    # Test direction indicator lights.")
            print("    indicatorLights = state.indicatorLights")

            for floor in range(elevator.floors):
                print(f"    assert indicatorLights[{floor}] == "
                      f"{describe(elevator.state.indicatorLights[floor]).upper()}")

        sys.stdout = sys.__stdout__

        print(f"Wrote test to {str(testFile)!r}.", file=sys.stderr)
        return []

    def handle_LIGHT_INDICATOR(self, event):
        elevator = self.elevator
        state = elevator.state
        state.indicate(event.floor, event.direction)
        return []

    def handle_CLEAR_INDICATOR(self, event):
        elevator = self.elevator
        state = elevator.state
        state.indicate(event.floor, OFF)
        return []

    def handle_CLEAR_CALL(self, event):
        elevator = self.elevator
        state = elevator.state
        state.clearCall(state.floor, event.direction)
        return []

    def handle_CLEAR_STOP(self, event):
        elevator = self.elevator
        state = elevator.state
        state.clearStop(state.floor)
        return []

    def handle_CALL(self, callEvent):
        elevator = self.elevator
        state = elevator.state
        delay = 0

        if state.callButtons[callEvent.floor][callEvent.direction]:
            # This call button is already pressed and has been reacted to.
            # print('Call already pressed.', file=sys.stderr)
            return []

        state.pressCall(callEvent.floor, callEvent.direction, callEvent.handledAt)

        responseEvents = []
        # We only need to figure out what's next if we were not moving in a
        # particular direction.
        if state.lastDirection is None:
            # We were not in motion. So we can go to the floor of the call.
            if callEvent.floor == state.floor:
                # We are already where we need to be.
                if state.closed:
                    # Someone wants to get on, and we're already sitting
                    # idle on their floor.  Open the doors to let them on.
                    responseEvents.append(
                        Event(OPEN, callEvent.floor, causedBy=callEvent)
                    )
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
                state.lastDirection = direction
                # Schedule the arrival at our next floor.
                nextFloor = state.floor + (1 if direction == UP else -1)
                assert 0 <= nextFloor < elevator.floors
                delay += elevator.interFloorDelay
                responseEvents.append(
                    Event(ARRIVE, nextFloor, delay=delay, causedBy=callEvent)
                )

        return responseEvents

    def handle_CLOSE(self, closeEvent):
        elevator = self.elevator
        state = elevator.state
        state.floor = closeEvent.floor
        state.closed = True
        responseEvents = []
        delay = 0

        if arrive := self.elevator.queue.hasArriveEvent():
            # We already figured out what floor to go to next (this will
            # happen on arrival when we have to immediately figure out
            # where we are going next so we can light the indicator so
            # people know whether to get on).
            assert arrive.floor != state.floor
            assert state.lastDirection is not None
        else:
            # There is no arrival event in the queue, so we have to figure
            # out where to go, if anywhere.

            # We can't be closing on a floor where a stop button is still
            # outstanding.
            assert not state.stopButtons[closeEvent.floor]

            buttonFloor, direction = pickDirectionBasedOnStopButtons(closeEvent, state)

            if direction is None:
                buttonFloor, direction = pickDirectionBasedOnCallButtons(
                    closeEvent, state
                )
            if direction is None:
                # Nothing pressed. Stay here.
                state.lastDirection = None
            else:
                state.lastDirection = direction
                if buttonFloor == state.floor:
                    # We were called from the floor we just closed the door on.
                    #
                    # Note: this cannot be from a stop button (see assert above), it
                    # must be from a call.
                    assert state.callButtons[state.floor][direction]

                    # TODO: This shouldn't be done so late, because we have
                    # just above decided to re-open. The call button should
                    # be cleared first. Need a test for this.
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

                    # Schedule the arrival at our next floor.
                    delay += elevator.interFloorDelay
                    nextFloor = state.floor + (1 if direction == UP else -1)
                    assert 0 <= nextFloor < elevator.floors
                    responseEvents.append(
                        Event(ARRIVE, nextFloor, delay=delay, causedBy=closeEvent)
                    )

        if state.lastDirection is not None:
            responseEvents.append(
                Event(
                    CLEAR_INDICATOR,
                    state.floor,
                    delay=0,
                    causedBy=closeEvent,
                )
            )

        return responseEvents

    def handle_OPEN(self, openEvent):
        elevator = self.elevator
        state = elevator.state
        state.closed = False
        responseEvents = []
        delay = 0

        assert state.floor == openEvent.floor

        # Clear the call button (if it has been pressed) for this direction
        # on this floor.
        if state.lastDirection is not None:
            if state.callButtons[openEvent.floor][state.lastDirection]:
                responseEvents.append(
                    Event(
                        CLEAR_CALL,
                        openEvent.floor,
                        direction=state.lastDirection,
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

    def handle_ARRIVE(self, arrivalEvent):
        elevator = self.elevator
        state = elevator.state
        state.floor = arrivalEvent.floor
        responseEvents = []
        delay = 0

        # Invariants:
        #    The doors are shut.
        #    There must be a current direction.
        assert state.closed
        assert state.floor == arrivalEvent.floor or state.lastDirection is not None

        # print(state, file=sys.stderr)

        if state.stopButtons[state.floor]:
            # The stop button for this floor was pressed. Clear the button,
            # open the doors, and schedule a door close.
            responseEvents.append(
                Event(
                    CLEAR_STOP, arrivalEvent.floor, delay=delay, causedBy=arrivalEvent
                )
            )
            responseEvents.append(
                Event(OPEN, arrivalEvent.floor, delay=delay, causedBy=arrivalEvent)
            )
            delay += elevator.openDoorDelay
            responseEvents.append(
                Event(CLOSE, arrivalEvent.floor, delay=delay, causedBy=arrivalEvent)
            )

            nextStopFloor = state.outstandingStop(state.lastDirection)

            if nextStopFloor is not None:
                # A stop button is pressed, so someone on the elevator is
                # expecting to continue on in this direction.
                responseEvents.append(
                    Event(
                        LIGHT_INDICATOR,
                        arrivalEvent.floor,
                        direction=state.lastDirection,
                        delay=0,
                        causedBy=arrivalEvent,
                    )
                )

                # Clear the call button for this direction on this floor,
                # if pressed.
                if state.callButtons[arrivalEvent.floor][state.lastDirection]:
                    responseEvents.append(
                        Event(
                            CLEAR_CALL,
                            arrivalEvent.floor,
                            direction=state.lastDirection,
                            delay=0,
                            causedBy=arrivalEvent,
                        )
                    )

                # Schedule the arrival at our next floor.
                nextFloor = state.floor + (
                    1 if nextStopFloor > arrivalEvent.floor else -1
                )
                assert 0 <= nextFloor < elevator.floors
                delay += elevator.interFloorDelay
                responseEvents.append(
                    Event(ARRIVE, nextFloor, delay=delay, causedBy=arrivalEvent)
                )
            else:
                # We are not obliged to carry on in the current direction.
                #
                # We must figure out on arrival which way to go next so
                #     the up/down indicator can show people whether to get on or not.
                #     Note that if no buttons are pressed, we will just stop here.
                # Decision: do not look at other stop buttons (pressed for the other
                #     direction by people who changed their minds. Let them wait?)
                #     I.e., the decision about where to go next is based only on
                #     call buttons (their floors and directions). We need a function
                #     that can pick a next direction based on our current floor and
                #     the call button state.
                _, direction = pickDirectionBasedOnCallButtons(arrivalEvent, state)
                if direction is None:
                    _, direction = pickDirectionBasedOnStopButtons(arrivalEvent, state)
                if direction is None:
                    # Nothing pressed. Stay here.
                    state.lastDirection = None
                else:
                    # Turn on the up/down direction light so people know
                    # whether to get on.
                    responseEvents.append(
                        Event(
                            LIGHT_INDICATOR,
                            arrivalEvent.floor,
                            direction=direction,
                            delay=delay,
                            causedBy=arrivalEvent,
                        )
                    )
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

                    responseEvents.append(
                        Event(
                            CLEAR_INDICATOR,
                            arrivalEvent.floor,
                            delay=delay,
                            causedBy=arrivalEvent,
                        )
                    )

                    # Change the elevator current direction to be up/down.
                    state.lastDirection = direction

                    # Schedule the arrival at our next floor.
                    nextFloor = state.floor + (1 if direction == UP else -1)
                    assert 0 <= nextFloor < elevator.floors
                    delay += elevator.interFloorDelay
                    responseEvents.append(
                        Event(ARRIVE, nextFloor, delay=delay, causedBy=arrivalEvent)
                    )
        else:
            # No one wanted to stop at this floor. We must be on our way
            # elsewhere.  But we can pick people up here if the call button
            # for our current direction is pressed.
            #
            # Note that there may or may not be a stop or call button
            # further on in the current direction, we may simply have been
            # called to this floor.

            # If we have arrived at the bottom or top of the building we
            # have to change direction.
            if state.floor == 0:
                assert state.lastDirection == DOWN
                state.lastDirection = UP
            elif state.floor == elevator.floors - 1:
                assert state.lastDirection == UP
                state.lastDirection = DOWN

            if state.callButtons[arrivalEvent.floor][state.lastDirection]:
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
                    Event(CLOSE, arrivalEvent.floor, delay=delay, causedBy=arrivalEvent)
                )
            else:
                # Don't stop here. Schedule the arrival at the next floor.
                nextFloor = state.floor + (1 if state.lastDirection == UP else -1)
                assert 0 <= nextFloor < elevator.floors
                delay += elevator.interFloorDelay
                responseEvents.append(
                    Event(ARRIVE, nextFloor, delay=delay, causedBy=arrivalEvent)
                )

        return responseEvents
