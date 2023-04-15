DEFAULT_FLOORS = 5
DEFAULT_OPEN_DOOR_DELAY = 10
DEFAULT_INTER_FLOOR_DELAY = 2

(
    UP,
    DOWN,
    CALL,
    STOP,
    ARRIVE,
    OPEN,
    CLOSE,
    END,
    OFF,
    CLEAR_STOP,
    CLEAR_CALL,
    LIGHT_INDICATOR,
    CLEAR_INDICATOR,
    RESET,
    WRITE_TEST,
) = range(15)

# UP and DOWN need to be 0 and 1
assert UP == 0 and DOWN == 1

_names = {
    UP: "up",
    DOWN: "down",
    CALL: "call",
    STOP: "stop",
    ARRIVE: "arrive",
    OPEN: "open",
    CLOSE: "close",
    END: "end",
    OFF: "off",
    CLEAR_STOP: "clear_stop",
    CLEAR_CALL: "clear_call",
    LIGHT_INDICATOR: "light_indicator",
    CLEAR_INDICATOR: "clear_indicator",
    RESET: "reset",
    WRITE_TEST: "write_test",
}


def describe(what):
    return _names.get(what, f"<<<UNKNOWN {what=}>>>")
