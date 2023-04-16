def handle_CLEAR_STOP(event, elevator):
    state = elevator.state
    state.clearStop(state.floor)
    return []
