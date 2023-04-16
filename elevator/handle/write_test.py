import sys
from pathlib import Path

from elevator.handle.utils import writeTest


def handle_WRITE_TEST(event, elevator):
    if elevator.testDir is None:
        print(
            "Received WRITE_TEST event but the elevator testDir is None",
            file=sys.stderr,
        )
        return []

    testDir = Path(elevator.testDir)
    if not testDir.exists():
        testDir.mkdir()

    testFile = writeTest(elevator, testDir)
    print(f"Wrote test to {str(testFile)!r}.", file=sys.stderr)

    return []
