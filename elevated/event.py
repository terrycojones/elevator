import sys
import json

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
    describe,
)


class Event:
    def __init__(
        self,
        what,
        floor,
        direction=None,
        delay=0,
        queuedAt=None,
        handledAt=None,
        serial=None,
        causedBy=None,
    ):
        if what in {CALL, CLEAR_CALL, LIGHT_INDICATOR}:
            assert direction is not None, f"None direction in {describe(what)} event."
            assert direction in {UP, DOWN}
        else:
            assert direction is None
        self.what = what
        self.floor = floor
        self.direction = direction
        self.delay = delay
        self.queuedAt = queuedAt  # Time when the event is enqueued.
        self.handledAt = handledAt  # Time when the event is taken from the queue.
        self.serial = serial  # Event serial number. Added when enqueued.
        self.causedBy = causedBy  # The event causing this event.

    def __str__(self):
        direction = (
            f" direction={describe(self.direction)}"
            if self.direction is not None
            else "            "
        )
        delay = f" delay={self.delay:.1f}" if self.delay is not None else "         "
        serial = (
            f" serial={self.serial:2d}" if self.serial is not None else "          "
        )
        cause = (
            f" cause={self.causedBy.serial:2d}"
            if (self.causedBy is not None and self.causedBy.serial is not None)
            else "         "
        )
        queued = f" queued={self.queuedAt:.2f}" if self.queuedAt is not None else ""
        handled = f" handled={self.handledAt:.2f}" if self.handledAt is not None else ""
        return (
            f"<Event {describe(self.what).upper()} floor={self.floor}"
            f"{direction}{delay}{serial}{cause}{queued}{handled}>"
        )

    def enqueued(self, when, serial):
        self.queuedAt = when
        self.serial = serial

    def handled(self, when):
        self.handledAt = when

    @classmethod
    def fromJSONString(klass, jsonStr):
        try:
            j = json.loads(jsonStr)
        except json.decoder.JSONDecodeError as e:
            print(f"Could not convert string {jsonStr!r} to JSON: {e}", file=sys.stderr)
            raise
        else:
            return klass(
                j["what"],
                j["floor"],
                direction=j.get("direction"),
                delay=j.get("delay", 0),
                queuedAt=j.get("queuedAt"),
                handledAt=j.get("handledAt"),
                serial=j.get("serial"),
            )

    def toJSON(self):
        return json.dumps(
            {
                "what": self.what,
                "floor": self.floor,
                "direction": self.direction,
                "delay": self.delay,
                "queuedAt": self.queuedAt,
                "handledAt": self.handledAt,
                "serial": self.serial,
            }
        )
