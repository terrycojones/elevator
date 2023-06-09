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

from elevator.constants import (
    ARRIVE,
    CALL_PRESSED,
    CLEAR_CALL,
    CLEAR_DIRECTION,
    CLEAR_STOP,
    CLOSE,
    DOWN,
    END,
    SET_DIRECTION,
    OPEN,
    RESET,
    STOP_PRESSED,
    UP,
    WRITE_TEST,
    describe,
)
from elevator.elevator import addStandardOptions
from elevator.event import Event


class ElevatorGUI(QWidget):
    def __init__(self, args):
        super().__init__()

        self.floors = args.floors
        self.floor = 1
        self.initProcess(args)
        self.initUI(args)

    def initProcess(self, args):
        arguments = [
            "--floors",
            str(self.floors),
            "--interFloorDelay",
            str(args.interFloorDelay),
            "--openDoorDelay",
            str(args.openDoorDelay),
        ]
        if args.testDir:
            arguments.extend(("--testDir", args.testDir))

        self.process = QProcess()
        self.process.setProgram("gui-process.py")
        self.process.setArguments(arguments)
        self.process.readyReadStandardOutput.connect(self.handleProcessOutput)
        self.process.readyReadStandardError.connect(self.handleProcessStderr)
        self.process.start()

    def initUI(self, args):
        self.setWindowTitle("Elevator Control UI")

        mainLayout = QHBoxLayout()

        # Floor labels
        floorPanel = QGroupBox("Floor")
        floorLayout = QVBoxLayout()

        for floor in reversed(range(self.floors)):
            label = QLabel(str(floor))
            floorLayout.addWidget(label)

        floorPanel.setLayout(floorLayout)
        mainLayout.addWidget(floorPanel)

        # Create panel for stop buttons
        stopPanel = QGroupBox("Stop buttons")
        stopLayout = QVBoxLayout()

        self.stopButtons = []

        for floor in range(self.floors):
            stopButton = QCheckBox()
            self.stopButtons.append(stopButton)
            stopButton.clicked.connect(partial(self.stopPressed, floor))

        for stopButton in reversed(self.stopButtons):
            stopLayout.addWidget(stopButton)

        stopPanel.setLayout(stopLayout)
        mainLayout.addWidget(stopPanel)

        # Create panel for call buttons
        callPanel = QGroupBox("Call buttons")
        callLayout = QVBoxLayout()

        self.callButtons = []

        # Call buttons on each floor.
        for floor in range(self.floors):
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

        for floor in reversed(range(self.floors)):
            floorLayout = QHBoxLayout()
            floorLayout.addWidget(self.callButtons[floor][UP])
            floorLayout.addWidget(self.callButtons[floor][DOWN])
            callLayout.addLayout(floorLayout)

        callPanel.setLayout(callLayout)
        mainLayout.addWidget(callPanel)

        # Create panel for controls, status, etc.
        controlPanel = QGroupBox("Status / control")
        controlLayout = QVBoxLayout()

        # Create floor indicator label
        self.floorIndicatorLabel = QLabel("Current Floor: 1")
        self.floorIndicatorLabel.setAlignment(Qt.AlignCenter)
        controlLayout.addWidget(self.floorIndicatorLabel)

        # Direction indicator label
        self.directionLabel = QLabel("Direction: None")
        self.directionLabel.setAlignment(Qt.AlignCenter)
        controlLayout.addWidget(self.directionLabel)

        # Doors label
        self.doorsLabel = QLabel("Doors: CLOSED")
        self.doorsLabel.setAlignment(Qt.AlignCenter)
        controlLayout.addWidget(self.doorsLabel)

        # Reset button
        self.resetButton = QPushButton("Reset")
        self.resetButton.clicked.connect(self.reset)
        controlLayout.addWidget(self.resetButton)

        if args.testDir:
            # Test button
            self.testButton = QPushButton("Write test")
            self.testButton.clicked.connect(self.writeTest)
            controlLayout.addWidget(self.testButton)

        # Quit button
        self.quitButton = QPushButton("Quit")
        self.quitButton.clicked.connect(self.quit)
        self.quitButton.clicked.connect(QApplication.instance().quit)
        controlLayout.addWidget(self.quitButton)

        controlPanel.setLayout(controlLayout)
        mainLayout.addWidget(controlPanel)

        self.setLayout(mainLayout)

    @Slot()
    def callPressed(self, floor, direction):
        self.send(Event(CALL_PRESSED, floor, direction=direction))

    @Slot()
    def stopPressed(self, floor):
        self.send(Event(STOP_PRESSED, floor))

    @Slot()
    def reset(self):
        self.send(Event(RESET, None))
        self.updateFloor(0)
        self.doorsLabel.setText("Doors: CLOSED")
        self.directionLabel.setText("Direction: None")
        for floor in range(self.floors):
            self.stopButtons[floor].setChecked(False)
            self.callButtons[floor][UP].setChecked(False)
            self.callButtons[floor][DOWN].setChecked(False)

    @Slot()
    def quit(self):
        self.send(Event(END, None))
        self.process.waitForFinished()

    @Slot()
    def writeTest(self):
        self.send(Event(WRITE_TEST, None))

    def send(self, event):
        utf8 = event.toJSON().encode("utf-8") + b"\n"
        self.process.write(utf8)

    def handleEvent(self, event):
        if event.what == OPEN:
            self.handleOpen(event)
        elif event.what == CLOSE:
            self.handleClose(event)
        elif event.what == CLEAR_STOP:
            self.handleClearStop(event)
        elif event.what == ARRIVE:
            self.handleArrive(event)
        elif event.what == CLEAR_CALL:
            self.handleClearCall(event)
        elif event.what == CLEAR_DIRECTION:
            self.handleClearDirection(event)
        elif event.what == SET_DIRECTION:
            self.handleSetDirection(event)
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
        # print("---> GUI: received process stderr:", file=sys.stderr)
        print(data, end="", file=sys.stderr)
        # print("---> GUI: end of process stderr", file=sys.stderr)

    def handleClearCall(self, event):
        self.callButtons[event.floor][event.direction].setChecked(False)

    def handleClearDirection(self, event):
        self.directionLabel.setText("Direction: None")

    def handleSetDirection(self, event):
        self.directionLabel.setText(f"Direction: {describe(event.direction)}")

    def handleOpen(self, event):
        self.updateFloor(event.floor)
        self.doorsLabel.setText("Doors: OPEN")

    def handleClose(self, event):
        self.updateFloor(event.floor)
        self.doorsLabel.setText("Doors: CLOSED")

    def handleStop(self, event):
        self.updateFloor(event.floor)
        self.stopButtons[event.floor].setChecked(True)

    def handleClearStop(self, event):
        self.stopButtons[event.floor].setChecked(False)

    def handleArrive(self, event):
        self.updateFloor(event.floor)

    def updateFloor(self, floor):
        self.floor = floor
        self.floorIndicatorLabel.setText(f"Current Floor: {floor}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=("Run an elevator."))
    addStandardOptions(parser)
    app = QApplication([])
    window = ElevatorGUI(parser.parse_args())
    window.show()
    app.exec()
