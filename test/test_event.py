import pytest


from elevated.constants import CALL, UP
from elevated.event import Event


def testFromJSONString():
    event = Event.fromJSONString(f'{{"what": {CALL}, "floor": 0, "direction": {UP}}}')
    assert event.what == CALL
    assert event.floor == 0
    assert event.direction == UP
