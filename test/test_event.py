from elevator.constants import CALL_PRESSED, UP
from elevator.event import Event


def testFromJSONString():
    event = Event.fromJSONString(
        f'{{"what": {CALL_PRESSED}, "floor": 0, "direction": {UP}}}'
    )
    assert event.what == CALL_PRESSED
    assert event.floor == 0
    assert event.direction == UP
