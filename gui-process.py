#!/usr/bin/env python

import sys
import os
import argparse
from time import sleep

from elevator.constants import END
from elevator.elevator import Elevator, addStandardOptions
from elevator.event import Event
from elevator.dpq import DelayPriorityQueue


def makeEvent(line):
    try:
        event = Event.fromJSONString(line)
    except ValueError as e:
        print(f"Could not convert {line!r} to JSON: {e}", sys.stderr)
    else:
        # print("Received event from stdin", file=sys.stderr)
        # print(event, file=sys.stderr)
        return event


def main(args):
    queue = DelayPriorityQueue()
    elevator = Elevator(
        queue=queue,
        floors=args.floors,
        openDoorDelay=args.openDoorDelay,
        interFloorDelay=args.interFloorDelay,
        testDir=args.testDir,
    )

    os.set_blocking(sys.stdin.fileno(), False)

    while True:
        if line := sys.stdin.readline():
            event = makeEvent(line.rstrip())
            if event.what == END:
                print("Received END event.", file=sys.stderr)
                break
            queue.put(event)

        nextEvent = elevator.handleEvent()
        if nextEvent and nextEvent.causedBy is not None:
            # print(f"Sending {nextEvent}", file=sys.stderr)
            print(nextEvent.toJSON(), flush=True)

        sleep(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=("Run an elevator logic process."))
    addStandardOptions(parser)
    main(parser.parse_args())
