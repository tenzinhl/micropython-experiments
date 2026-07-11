import array
import time
from machine import Pin
import rp2

# ---- Config ----
NUM_LEDS   = 64
DATA_PIN   = 22       # GPIO number your DIN wire is connected to (GP0 here)
BRIGHTNESS = 0.3      # 0.0-1.0. Keep low-ish; 64 LEDs at full white draws a LOT.

# ---- PIO program for WS2812 (800kHz) ----
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT,
             autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)             .side(0)    [T3 - 1]
    jmp(not_x, "do_zero") .side(1)    [T1 - 1]
    jmp("bitloop")        .side(1)    [T2 - 1]
    label("do_zero")
    nop()                 .side(0)    [T2 - 1]
    wrap()

# ---- Set up state machine ----
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(DATA_PIN))
sm.active(1)

# GRB buffer (WS2812B expects Green, Red, Blue order)
buf = array.array("I", [0] * NUM_LEDS)

def set_pixel(i, r, g, b):
    r = int(r * BRIGHTNESS)
    g = int(g * BRIGHTNESS)
    b = int(b * BRIGHTNESS)
    buf[i] = (g << 16) | (r << 8) | b

def show():
    # shift left by 8 so the 24 color bits sit in the top of each 32-bit word
    sm.put(buf, 8)

def wheel(pos):
    """Map 0-255 to a rainbow color (r, g, b)."""
    pos &= 255
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

# ---- Main loop: flowing rainbow ----
while True:
    for j in range(256):
        for i in range(NUM_LEDS):
            r, g, b = wheel((i * 256 // NUM_LEDS + j) & 255)
            set_pixel(i, r, g, b)
        show()
        time.sleep_ms(20)
