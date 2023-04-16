class Button:
    def __init__(self, state=False, pressedAt=None):
        self.state = state
        self.pressedAt = pressedAt

    def __str__(self):
        if self.state:
            return f"Pressed (at {self.pressedAt})"
        else:
            return "Unpressed"

    def __lt__(self, other):
        if self.pressedAt is None:
            return False
        if other.pressedAt is None:
            return True
        return self.pressedAt < other.pressedAt

    def __bool__(self):
        return self.state

    def press(self, when):
        self.state = True
        self.pressedAt = when

    def clear(self):
        self.state = False
        self.pressedAt = None
