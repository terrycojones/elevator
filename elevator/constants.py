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
    UP: "UP",
    DOWN: "DOWN",
    ARRIVE: "ARRIVE",
    CALL_PRESSED: "CALL_PRESSED",
    CLEAR_CALL: "CLEAR_CALL",
    CLEAR_DIRECTION: "CLEAR_DIRECTION",
    CLEAR_STOP: "CLEAR_STOP",
    CLOSE: "CLOSE",
    END: "END",
    OFF: "OFF",
    OPEN: "OPEN",
    RESET: "RESET",
    SET_DIRECTION: "SET_DIRECTION",
    STOP_PRESSED: "STOP_PRESSED",
    WRITE_TEST: "WRITE_TEST",
    None: "None",
}


def describe(what):
    return _names[what]
