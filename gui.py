#!/usr/bin/env python

import sys
from functools import partial
import argparse

from PySide6.QtCore import Qt, Slot, QProcess
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QCheckBox,
    QLabel,
    QGroupBox,
    QStyle,
)

from elevated.constants import (
    ARRIVE,
    CALL,
    CLEAR_CALL,
    CLEAR_INDICATOR,
    CLEAR_STOP,
    CLOSE,
    DOWN,
    END,
    OPEN,
    RESET,
    STOP,
    UP,
    describe,
)
from elevated.elevator import addStandardOptions
from elevated.event import Event


class ElevatorControlUI(QWidget):
    def __init__(self, args):
        super().__init__()

        self.floors = args.floors
        self.floor = 1
        self.initProcess(args)
        self.init_ui()

    def handleEvent(self, event):
        if event.what == OPEN:
            self.handleOpen(event)
        elif event.what == CLOSE:
            self.handleClose(event)
        elif event.what == STOP:
            self.handleStop(event)
        elif event.what == CLEAR_STOP:
            self.handleStop(event)
        elif event.what == ARRIVE:
            self.handleArrive(event)
        elif event.what == CLEAR_CALL:
            self.handleClearCall(event)
        elif event.what == CLEAR_INDICATOR:
            self.handleClearIndicator(event)
        else:
            print(f"Don't know how to handle {event}.", file=sys.stderr)

    def handleProcessOutput(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8").rstrip()
        for line in data.split("\n"):
            event = Event.fromJSONString(line)
            if event:
                self.handleEvent(event)
            else:
                print(
                    f"GUI could not parse process output line {line!r}", file=sys.stderr
                )
                # sys.exit(1)

    def handleProcessStderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8")
        print("---> GUI: received process stderr:", file=sys.stderr)
        print(data, end="", file=sys.stderr)
        print("---> GUI: end of process stderr", file=sys.stderr)

    def initProcess(self, args):
        self.process = QProcess()
        self.process.setProgram("gui-process.py")
        self.process.setArguments(
            [
                "--floors",
                str(self.floors),
                "--interFloorDelay",
                str(args.interFloorDelay),
                "--openDoorDelay",
                str(args.openDoorDelay),
            ]
        )
        self.process.readyReadStandardOutput.connect(self.handleProcessOutput)
        self.process.readyReadStandardError.connect(self.handleProcessStderr)
        self.process.start()

        # Test
        # event = Event(CALL, 3, direction=UP)
        # utf8 = event.toJSON().encode("utf-8") + b"\n"
        # self.process.write(utf8)

    def init_ui(self):
        self.setWindowTitle("Elevator Control UI")

        mainLayout = QVBoxLayout()

        # Create panel for call buttons
        callPanel = QGroupBox("Call Buttons")
        callLayout = QVBoxLayout()

        self.callButtons = []

        # Call buttons on each floor.
        for floor in reversed(range(self.floors)):
            floorLabel = QLabel(f"Floor {floor}")
            floorLabel.setAlignment(Qt.AlignCenter)
            upButton = QCheckBox()
            downButton = QCheckBox()
            self.callButtons.append((upButton, downButton))

            if floor < self.floors - 1:
                upButton.clicked.connect(partial(self.callPressed, floor, UP))
            else:
                upButton.setCheckable(False)

            if floor > 0:
                downButton.clicked.connect(partial(self.callPressed, floor, DOWN))
            else:
                downButton.setCheckable(False)

            icon = self.style().standardIcon(QStyle.SP_ArrowUp)
            upButton.setIcon(icon)

            icon = self.style().standardIcon(QStyle.SP_ArrowDown)
            downButton.setIcon(icon)

            floor_layout = QHBoxLayout()
            floor_layout.addWidget(floorLabel)
            floor_layout.addWidget(upButton)
            floor_layout.addWidget(downButton)

            callLayout.addLayout(floor_layout)

        callPanel.setLayout(callLayout)
        mainLayout.addWidget(callPanel)

        # Create panel for stop buttons
        stopPanel = QGroupBox("Stop Buttons")
        stopLayout = QVBoxLayout()

        self.stopButtons = []

        for i in reversed(range(self.floors)):
            stopButton = QCheckBox(f"{i}")
            self.stopButtons.append(stopButton)
            # Connect signal to slot
            stopButton.clicked.connect(partial(self.stopPressed, i))
            stopLayout.addWidget(stopButton)

        stopPanel.setLayout(stopLayout)
        mainLayout.addWidget(stopPanel)

        # Create floor indicator label
        self.floor_indicator_label = QLabel("Current Floor: 1")
        self.floor_indicator_label.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.floor_indicator_label)

        # Doors label
        self.doorsLabel = QLabel("Doors: CLOSED")
        self.doorsLabel.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.doorsLabel)

        # Direction label
        # self.direction_label = QLabel("Direction: UP")
        # self.direction_label.setAlignment(Qt.AlignCenter)
        # mainLayout.addWidget(self.direction_label)

        # Reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        mainLayout.addWidget(self.reset_button)

        # Quit button
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.quit)
        self.quit_button.clicked.connect(QApplication.instance().quit)
        mainLayout.addWidget(self.quit_button)

        self.setLayout(mainLayout)

    @Slot()
    def callPressed(self, floor, direction):
        print(f"{describe(direction)} call for elevator on floor {floor}")
        # self.callButtons[floor][direction].setChecked(True)
        event = Event(CALL, floor, direction=direction)
        utf8 = event.toJSON().encode("utf-8") + b"\n"
        self.process.write(utf8)

    @Slot()
    def stopPressed(self, floor):
        print(f"Stop button pressed for floor: {floor}")
        event = Event(STOP, floor)
        utf8 = event.toJSON().encode("utf-8") + b"\n"
        self.process.write(utf8)

    @Slot()
    def reset(self):
        event = Event(RESET, None)
        utf8 = event.toJSON().encode("utf-8") + b"\n"
        self.process.write(utf8)
        self.updateFloor(0)
        self.doorsLabel.setText("Doors: CLOSED")
        for floor in range(self.floors):
            self.stopButtons[floor].setChecked(False)
            self.callButtons[floor][UP].setChecked(False)
            self.callButtons[floor][DOWN].setChecked(False)

    @Slot()
    def quit(self):
        event = Event(END, None)
        utf8 = event.toJSON().encode("utf-8") + b"\n"
        self.process.write(utf8)
        self.process.waitForFinished()

    def handleClearCall(self, event):
        print(
            f"Clear call for floor {event.floor} direction {describe(event.direction)}"
        )
        self.callButtons[event.floor][event.direction].setChecked(False)

    def handleClearIndicator(self, event):
        print(f"Clear indicator for floor {event.floor}. Not implemented.")
        pass

    def handleOpen(self, event):
        print(f"Open on floor: {event.floor}")
        self.updateFloor(event.floor)
        self.doorsLabel.setText("Doors: OPEN")

    def handleClose(self, event):
        print(f"Close on floor: {event.floor}")
        self.updateFloor(event.floor)
        self.doorsLabel.setText("Doors: CLOSED")

    def handleStop(self, event):
        print(f"Stop pressed for floor: {event.floor}")
        self.stopButtons[event.floor].setChecked(True)

    def handleClearStop(self, event):
        print(f"Clear stop button for floor: {event.floor}")
        self.stopButtons[event.floor].setChecked(False)

    def handleArrive(self, event):
        self.updateFloor(event.floor)

    def updateFloor(self, floor):
        self.floor = floor
        self.floor_indicator_label.setText(f"Current Floor: {floor}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=("Run an elevator."))
    addStandardOptions(parser)
    app = QApplication([])
    window = ElevatorControlUI(parser.parse_args())
    window.show()
    app.exec()
