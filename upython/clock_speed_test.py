# Clock speed test
# This test clocks the tt_um_test design at a high frequency
# and checks the counter has incremented by the correct amount

import machine
import rp2
import time

from ttboard.mode import RPMode
from ttboard.demoboard import DemoBoard

# Frequency for the RP2040, the design is clocked at half this frequency
freq = 133_000_000

machine.freq(freq)

# PIO program to drive the clock.  Put a value n and it clocks n+1 times
# Reads 0 when done.
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, autopull=True, pull_thresh=32, autopush=True, push_thresh=32)
def clock_prog():
    out(x, 32)              .side(0)
    label("clock_loop")
    nop()                   .side(1)
    jmp(x_dec, "clock_loop").side(0)
    in_(null, 32)           .side(0)

# Select design, don't apply config so the PWM doesn't start.
tt = DemoBoard(applyUserConfig=False)
tt.shuttle.tt_um_test.enable()

# Setup the PIO clock driver
sm = rp2.StateMachine(0, clock_prog, freq=freq, sideset_base=machine.Pin(0))
sm.active(1)

# Run 1 clock
print("Clock test... ", end ="")
sm.put(1)
sm.get()
print(f" done. Value: {tt.output_byte}")

while True:
    last = tt.output_byte
    
    # Run clock for approx 1 second, sending a multiple of 256 clocks plus 1.
    t = time.ticks_us()
    sm.put((freq // 512) * 256)
    sm.get()
    t = time.ticks_us() - t
    print(f"Clocked for {t}us: ", end = "")
        
    # Check the counter has incremented by 1.
    if tt.output_byte != last + 1:
        print("Error: ", end="")
    print(tt.output_byte)
    
    # Sleep so the 7-seg display can be read
    time.sleep(0.5)