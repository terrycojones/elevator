import sys
import heapq
from time import time

from elevated.constants import ARRIVE, END


class Element:
    def __init__(self, time, inc, event):
        self.time = time
        self.inc = inc
        self.event = event

    def __lt__(self, other):
        if other.event.what is END:
            return True
        elif self.event.what is END:
            return False
        else:
            return (self.time, self.inc) < (other.time, other.inc)


class DelayPriorityQueue:
    def __init__(self):
        self.queue = []
        self.inc = 0

    def __len__(self):
        return len(self.queue)

    def peek(self):
        return self.queue[0].event if self.queue else None

    def put(self, event):
        # The event may already have an queue entry time as a result of
        # being created by a GUI.
        if event.queuedAt is None:
            now = time()
            event.enqueued(now, self.inc)
        else:
            now = event.queuedAt
        heapq.heappush(self.queue, Element(now + event.delay, self.inc, event))
        # print("QUEUE PUT", event, file=sys.stderr)
        self.inc += 1

    def get(self, respectTime=True):
        # Get the next event. If respectTime is True, get the most-recently
        # passed event, if any. Return None if the queue is empty or if the
        # next event is still in the future.
        if self.queue:
            now = time()
            if respectTime and self.queue[0].time > now:
                return
            element = heapq.heappop(self.queue)
            event = element.event
            event.handled(now)
            print("QUEUE GOT", event, file=sys.stderr)
            return event

    def hasArriveEvent(self):
        for element in self.queue:
            if element.event.what == ARRIVE:
                return element.event
