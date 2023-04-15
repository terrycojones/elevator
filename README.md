## Assumptions

When someone gets on at a floor and presses a button, they always get off
at the floor they originally intended.

People don't make mistakes in button pressing.

Can't tell how many people get on/off.

Can't tell if the elevator is empty.

Door "open" time includes time taken for doors to open and close, as well
as for remaining open.

People push their destination floor on entering, and do so before the doors
are closed.

If no buttons are pressed in this time, no one got on (i.e., probably this
was a drop-off, or the person clicked and ran).

The elevator makes a plan at the moment the door is closed.

Elevator will not stop between floors and change direction.

Doors start off closed on floor zero.

Number of people who get on = number of different buttons that are pressed
before the doors closed. Repeat identical presses ignored.

When an elevator leaves a floor, it always moves in the direction the
people on board are expecting?

Everyone on board is expecting the elevator to move in a constant direction
until it reaches their floor. So reversals would not be allowed in this
case.

A "plan" could therefore be seen as a series of up and down sweeps.

Cannot know before arriving on a floor and picking the person up where they
might want to go (but could infer expected trip distance :-))

Could aim to minimize expected overall disappointment (Bayesian).

When people arrive at a floor to get on, they don't press the button to
call the elevator for their desired direction if the button has already
been pressed.

No one stands at the elevator without pushing the button to indicate their
direction (if the button is unpressed). Such a person could just get on
when the lift arrives and push an inner button to go in an unanticipated
direction. I.e., elevator stops at the floor to let someone off and has no
future plan. But someone gets on and presses a button. That has to count as
a non-empty elevator.

No one gets on and then doesn't ever leave = death by starvation.

No children get on who cannot reach any buttons = death.

When the elevator is in motion, all the people on board want to go in the
direction that it is traveling in. So it has to keep going until it gets to
the extreme in that direction. Along the way it may pick up more people
(all of whom necessarily want to go in that same direction) who may press
more extreme buttons in the same direction.

On the top floor there is no up call button. On the bottom floor there is
no down call button.

## Thinking

Any valid path is a series of sweeps, up, then down, etc. Always going to
the extreme. But we just have to figure out the direction of the first
sweep, then move that way. At the next stop, we figure things out again (in
part based on the current direction, if any).

Only when we have no more extreme floor request in the current direction,
if any, do we need to figure out the next path.

One full sweep down and then up will clear all outstanding requests. So you
only have to consider those two possible paths (given the invariant that
you don't change direction on someone who is already traveling in the
direction they want to go in).

When the elevator is on a floor with the doors open, the call buttons on
that floor are inactive. No, you should still be able to call it for the
other direction.

May be going to a floor because you are called there (in which case you
know the next required direction) or because someone wants to get off
there. Or both.

When you are called to a floor, you know the wanted direction of travel, so
can estimate the probability of the next intended floor (but not floors!?)
according to how many floors are above or below in the pre-indicated travel
direction.

Of course you may get to a floor and have some people wanting to go up and
some wanting to go down.

If the elevator is empty and called to a floor where both call buttons have
been pressed, which way should it go? Depends on how many floors above and
below, and whether any people on those floors have pushed a button
compatible with the movement. If in the middle floor and there are no other
button presses, go with the first button direction. Will this fall out of a
general search optimization? Should do.

Would be safer if the elevator periodically went to the ground floor and
opened its doors, no matter what (when idle). Someone who had a heart
attack could be discovered.

## Approach

Write a top-level function that can either

    - take a list of events (with times) and it runs through them,
      inserting its own events when arriving at floors, doors closing,
      etc. This is good for testing. The list would be converted to a
      priority queue (based on event time). So this is a special case of
      the one below: the a priori list of events gets converted into a
      priority queue.

    - take a queue that it can poll for events, in which case it also inserts
      its own events into the queue and reacts in normal time. This is good
      for building a UI or an actual elevator.

The logic is the same in either case. We have a State class and an Event
class. The Event class can be serializable so we could have a separate
process that receives events on stdin, driven by a UI, and sends decisions
(the movement direction) and events back.

## Logic (new: 2023-04-11)

```

if event == ARRIVE:
    # We have arrived at a floor.

    # Invariants:
    #    The doors are shut.
    #    There must be a current direction.

    set the current floor

    if there is a stop button pressed for this floor:
        clear the stop button
        schedule(OPEN, 0)
        schedule(CLOSE, door_open_time)

        if there is a stop button pressed for a floor further on in this direction:
            # Someone on the elevator is expecting to continue on in this direction.
            clear the call button (which may not have been pressed) for this direction on this floor
            schedule(ARRIVE, floor +/- 1, door_open_time + inter_floor_time)
        else:
            # We are not obliged to carry on in the current direction.
            #
            # We must figure out on arrival which way to go next so
            #     the up/down indicator can show people whether to get on or not.
            #     Note that if no buttons are pressed, we will just stop here.
            # Decision: do not look at other stop buttons (pressed for the other
            #     direction by people who changed their minds. Let them wait?)
            #     I.e., the decision about where to go next is based only on
            #     call buttons (their floors and directions). We need a function
            #     that can pick a next direction based on our current floor and
            #     the call button state.
            direction = pick_direction_based_on_call_buttons()
            if direction is None:
                direction = pick_direction_based_on_stop_buttons()
            if direction is still None:
                # stay here!
                set current direction to be NONE
            else:
                turn on the up/down direction light so people know whether to get on
                clear the call button (which may not have been pressed) for this direction on this floor
                change the elevator current direction to be up/down
                schedule(ARRIVE, floor +/- 1, door_open_time + inter_floor_time)

    else:
        # No one wanted to stop at this floor. We must be on our way elsewhere.
        # But we can pick people up here if the right call button is pressed.
        #
        # There may or may not be a stop or call button further on in this direction,
        # we may simply have been called to this floor.

        if the call button in the current direction on this floor is pressed:
            schedule(OPEN, 0)
            schedule(CLOSE, door_open_time)
            # We can't always schedule an arrive because no buttons may have been
            # pressed. We can just wait until the CLOSE event happens. Buttons will
            # presumably have been pressed in the meantime (we just opened to let
            # people on, and they may still be there and may get on, and may press
            # a button, etc).
        else:
            # Don't stop here. Schedule the arrival at the next floor.
            schedule(ARRIVE, floor +/- 1, door_open_time + inter_floor_time)

    return

if event == OPEN:
    set door state to be open

if event == CLOSE:
    set door state to be closed.
    turn off direction indicator
    if there is anything in the queue:
        assert that the queue length is one
        assert that the scheduled event is an ARRIVE
        assert that the floor for the event is one above or below us, according to
            the saved direction.

    else:
        # Nothing in the queue, so we have to figure out where to go, if anywhere.

        direction = pick_direction_based_on_call_buttons()
        if direction is None:
            # stay here!
            set current direction to be NONE
        else:
            change the elevator current direction to be up/down
            schedule(ARRIVE, floor +/- 1, inter_floor_time)

if event == CALL:
    if this call button is already pressed:
        return

    if current direction is NONE:
        # We were not in motion. So we can go to the floor.

        direction = get direction relative to us for call button
        if direction is NONE:
            # We are already where we need to be.
            if doors are already open:
                # Someone is re-pressing the call button even though the doors are open.
                # We could make sure the next scheduled event is a CLOSE and adjust the
                # close time (but then we would have to also see if there was an ARRIVE
                # also scheduled and adjust that). Then we'd want to limit how many times
                # we do that because otherwise someone could hold the doors open
                # indefinitely. So for now just ignore it.
                pass
            else:
                # Someone wants to get on, and we're already sitting idle on their floor.
                schedule(OPEN, 0)
                schedule(CLOSE, door_open_time)
                # We can't schedule an arrive because they haven't gotten on yet. That
                # will be figured out when the CLOSE happens (they may not even get on).
        else:
            set the up/down call button indicator on the calling floor
            change the elevator current direction to be up/down
            schedule(ARRIVE, floor +/- 1, inter_floor_time)

    else:
        # We are already in motion.
        set the up/down call button indicator on the calling floor
```

## Original partial logic (written for the course)

When the doors close:

```
if (there is a current direction):
    if (there is an outstanding stop in that direction):
        clear the outside call button for the current direction
        go one step in the current direction
        continue
    else:
        clear the outstanding direction and fall-through to the below.

# Else, an upward or downward sweep has just finished. Everyone who was on
# must have just gotten off. But new people may have just gotten on.
#
# So we can now go up or down or just sit there.

if (stop buttons in both directions have been pressed by people getting on):

    The problem here is that we have to figure what direction we are going
    to move in _before_ we open the doors, so only the right people get on.
    The direction indicator has to be set when the door opens.

    We have to decide whether to go up or down based on call buttons that
    were pressed on other floors (if any) because we have no information
    from the call buttons on this floor (both were pressed and we do not yet
    know where those people will want to go).

    Go towards the calling floor first pressed?  Or count how many calls
    there are in that direction and wanting to continue in that direction,
    since we can do them all in one sweep. If we can't decide, we should
    head to the nearest extreme (up or down) and if there is no way to
    decide (we are on the middle floor and the other calls came at exactly
    the same time, pick a random direction.

    If there are calls in both directions, there are 4 combinations of
    where they might be wanting to go. E.g., the person below might want to
    go down, and the person above might want to too. Or they might want to
    move towards or away from each other, etc.  If they both want to go in
    the same direction, we could go first to the nearest one. If they are
    conflicting, go to the one that is closest to an extreme.

elif (any floor stop button below the current level was pressed):
    set current direction to down
    go down one floor
elif (any floor stop button above the current level was pressed):
    set current direction to up
    go up one floor
elif (there are call buttons pressed both above and below):
    Decide whether to go up or down based call buttons pressed (maybe towards earliest call button press)
elif (there are call buttons pressed below):
    Go down one floor
elif (there are call buttons pressed above):
    Go up one floor
else:
    # raise RuntimeError('Inconceivable!')
```
