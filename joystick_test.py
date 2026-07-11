"""
Arcade joystick limit-switch monitor (MicroPython)

Wiring assumption: PULL-DOWN configuration.
  - Each GPIO reads LOW at rest (pulled to ground).
  - The switch common is tied to V_logic (3.3 V), so closing a
    switch pulls its GPIO HIGH.
  => pressed  <=>  pin.value() == 1   (ACTIVE_HIGH = True)

Polls every POLL_MS milliseconds (level-triggered) and prints a
status readout. By default it prints only when something changes,
so you get a clean press/release log instead of 50 lines/second.

Save as main.py on the board (or run in Thonny). Ctrl-C to stop.
"""

from machine import Pin
import time

# ---- Configuration -------------------------------------------------------

# GPIO number -> cardinal direction. Edit if your wiring differs.
PIN_MAP = {
    2: "right",
    3: "left",
    4: "up",
    5: "down",
}

POLL_MS = 20               # polling interval (level-triggered)
ACTIVE_HIGH = False         # pull-down wiring: a pressed switch reads HIGH
PRINT_EVERY_CYCLE = False  # True = print every poll; False = print on change

# ---- Setup ---------------------------------------------------------------

def make_inputs(pin_map, active_high):
    """Create Pin objects in input mode with the matching pull resistor.

    Enabling the internal resistor is harmless if you also wired an
    external one (they just sit in parallel), and required if you didn't.
    """
    pull = Pin.PULL_DOWN if active_high else Pin.PULL_UP
    return {gpio: Pin(gpio, Pin.IN, pull) for gpio in pin_map}


def read_states(pins, active_high):
    """Return {gpio: is_pressed(bool)} for every pin."""
    states = {}
    for gpio, pin in pins.items():
        level = pin.value()
        states[gpio] = (level == 1) if active_high else (level == 0)
    return states

# ---- Display -------------------------------------------------------------

def _cell(name, active):
    """Fixed-width (7 char) cell: [ NAME ] when active, plain when not."""
    if active:
        return "[" + "{:^5}".format(name.upper()) + "]"
    return " " + "{:^5}".format(name) + " "


def render_joystick(active_dirs):
    """ASCII-art cross with active directions highlighted."""
    up    = _cell("up",    "up"    in active_dirs)
    down  = _cell("down",  "down"  in active_dirs)
    left  = _cell("left",  "left"  in active_dirs)
    right = _cell("right", "right" in active_dirs)
    center = "(  +  )" if active_dirs else "(  o  )"
    return "\n".join([
        " " * 11 + up,
        "   " + left + " " + center + " " + right,
        " " * 11 + down,
    ])


def format_status(states, pin_map):
    active_dirs = {pin_map[g] for g, pressed in states.items() if pressed}

    # Summary line in the pin (direction) form you asked for.
    pressed = [(g, pin_map[g]) for g in sorted(pin_map) if states[g]]
    if pressed:
        summary = "pressed: " + ", ".join(
            'GPIO{} ("{}")'.format(g, d) for g, d in pressed)
    else:
        summary = "pressed: none"

    # Per-pin detail lines.
    lines = []
    for gpio in sorted(pin_map):
        mark = "CLOSED" if states[gpio] else "open  "
        lines.append('  GPIO {:>2} [{}]  ->  interpreted as "{}"'.format(
            gpio, mark, pin_map[gpio]))

    return "\n".join([render_joystick(active_dirs), "", summary] + lines)

# ---- Main loop -----------------------------------------------------------

def main():
    pins = make_inputs(PIN_MAP, ACTIVE_HIGH)
    print("Joystick switch monitor. Ctrl-C to stop.")
    print("Wiring: {}  (a pressed switch reads {}).".format(
        "pull-down" if ACTIVE_HIGH else "pull-up",
        "HIGH" if ACTIVE_HIGH else "LOW"))

    last = None
    while True:
        states = read_states(pins, ACTIVE_HIGH)
        if PRINT_EVERY_CYCLE or states != last:
            print("-" * 34)
            print(format_status(states, PIN_MAP))
            last = states
        time.sleep_ms(POLL_MS)


main()
