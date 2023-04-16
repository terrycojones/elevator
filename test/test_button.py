from elevator.button import Button


def testDefaultUnpressed():
    b = Button()
    assert not b


def testPress():
    b = Button()
    b.press(0)
    assert b
    assert b.pressedAt == 0


def testClear():
    b = Button()
    assert not b
    b.clear()
    assert not b
    b.press(0)
    b.clear()
    assert not b
    assert b.pressedAt is None
