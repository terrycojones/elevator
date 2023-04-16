import sys

from elevator.constants import describe

from elevator.handle.arrive import handle_ARRIVE  # noqa
from elevator.handle.call_pressed import handle_CALL_PRESSED  # noqa
from elevator.handle.clear_call import handle_CLEAR_CALL  # noqa
from elevator.handle.clear_direction import handle_CLEAR_DIRECTION  # noqa
from elevator.handle.clear_stop import handle_CLEAR_STOP  # noqa
from elevator.handle.end import handle_END  # noqa
from elevator.handle.handle_close import handle_CLOSE  # noqa
from elevator.handle.open import handle_OPEN  # noqa
from elevator.handle.reset import handle_RESET  # noqa
from elevator.handle.set_direction import handle_SET_DIRECTION  # noqa
from elevator.handle.stop_pressed import handle_STOP_PRESSED  # noqa
from elevator.handle.write_test import handle_WRITE_TEST  # noqa

_GLOBALS = globals()


class Logic:
    def __init__(self, elevator):
        self.elevator = elevator

    def handleEvent(self, event):
        try:
            handler = _GLOBALS[f"handle_{describe(event.what)}"]
        except KeyError:
            print(
                f"No handler found for {describe(event.what)} event {event}",
                file=sys.stderr,
            )
        else:
            return handler(event, self.elevator)
