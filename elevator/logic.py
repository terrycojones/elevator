import sys

from elevator.constants import describe

from elevator.handle.arrive import handle_ARRIVE
from elevator.handle.call_pressed import handle_CALL_PRESSED
from elevator.handle.clear_call import handle_CLEAR_CALL
from elevator.handle.clear_direction import handle_CLEAR_DIRECTION
from elevator.handle.clear_stop import handle_CLEAR_STOP
from elevator.handle.end import handle_END
from elevator.handle.handle_close import handle_CLOSE
from elevator.handle.open import handle_OPEN
from elevator.handle.reset import handle_RESET
from elevator.handle.set_direction import handle_SET_DIRECTION
from elevator.handle.stop_pressed import handle_STOP_PRESSED
from elevator.handle.write_test import handle_WRITE_TEST

_GLOBALS = globals()


class Logic:
    def __init__(self, elevator):
        self.elevator = elevator

    def handleEvent(self, event):
        # handler = getattr(self, f"handle_{describe(event.what)}")
        try:
            handler = _GLOBALS[f"handle_{describe(event.what)}"]
        except KeyError:
            print(
                f"No handler found for {describe(event.what)} event {event}",
                file=sys.stderr,
            )
        else:
            return handler(event, self.elevator)
