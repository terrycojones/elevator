def handle_CLEAR_CALL(event, elevator):
    elevator.state.clearCall(event.floor, event.direction, event)
    return []
