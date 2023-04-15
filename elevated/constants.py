DEFAULT_FLOORS = 5
DEFAULT_OPEN_DOOR_DELAY = 10
DEFAULT_INTER_FLOOR_DELAY = 2

(
    UP,
    DOWN,
    ARRIVE,
    CALL_PRESSED,
    CLEAR_CALL,
    CLEAR_DIRECTION,
    CLEAR_STOP,
    CLOSE,
    END,
    OFF,
    OPEN,
    RESET,
    SET_DIRECTION,
    STOP_PRESSED,
    WRITE_TEST,
) = range(15)

# UP and DOWN need to be 0 and 1
assert UP == 0 and DOWN == 1

_names = {
    UP: "up",
    DOWN: "down",
    ARRIVE: "arrive",
    CALL_PRESSED: "call_pressed",
    CLEAR_CALL: "clear_call",
    CLEAR_DIRECTION: "clear_direction",
    CLEAR_STOP: "clear_stop",
    CLOSE: "close",
    END: "end",
    OFF: "off",
    OPEN: "open",
    RESET: "reset",
    SET_DIRECTION: "set_direction",
    STOP_PRESSED: "stop_pressed",
    WRITE_TEST: "write_test",
    None: "None",
}


def describe(what):
    return _names[what]
