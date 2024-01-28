# Clock speed test
# This test clocks the tt_um_test design at a high frequency
# and checks the counter has incremented by the correct amount

import machine
import rp2
import time

from ttboard.mode import RPMode
from ttboard.demoboard import DemoBoard

# PIO program to drive the clock.  Put a value n and it clocks n+1 times
# Reads 0 when done.
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, autopull=True, pull_thresh=32, autopush=True, push_thresh=32)
def clock_prog():
    out(x, 32)              .side(0)
    label("clock_loop")
    irq(4)                  .side(1)
    jmp(x_dec, "clock_loop").side(0)
    irq(clear, 4)           .side(0)
    in_(null, 32)           .side(0)

@rp2.asm_pio(autopush=True, push_thresh=32, in_shiftdir=rp2.PIO.SHIFT_RIGHT, fifo_join=rp2.PIO.JOIN_RX)
def read_prog():
    in_(pins, 2)

# Select design, don't apply config so the PWM doesn't start.
tt = DemoBoard(applyUserConfig=False)
tt.shuttle.tt_um_test.enable()

# Setup the PIO clock driver
sm = rp2.StateMachine(0, clock_prog, sideset_base=machine.Pin(0))
sm.exec("irq(clear, 4)")
sm.active(1)

# Setup the PIO counter read
sm_rx = rp2.StateMachine(1, read_prog, in_base=machine.Pin(3))

# Setup read DMA
dst_data = bytearray(8192)
d = rp2.DMA()

c = d.pack_ctrl(inc_read=False, treq_sel=5)

d.config(
    read=0x5020_0024,
    write=dst_data,
    count=len(dst_data)//4,
    ctrl=c,
    trigger=False
)

def start_rx():
    sm_rx.active(0)
    while sm_rx.rx_fifo() > 0: sm_rx.get()
    sm_rx.restart()
    if machine.Pin(3).value():
        sm_rx.exec("wait(0, pin, 0)")
    else:
        sm_rx.exec("wait(1, pin, 0)")
    sm_rx.active(1)


# Frequency for the RP2040, the design is clocked at half this frequency
def run_test(freq):
    # Multiply requested project clock frequency by 2 to get RP2040 clock
    freq *= 2
    
    if freq > 350_000_000:
        raise ValueError("Too high a frequency requested")
    
    if freq > 266_000_000:
        rp2.Flash().set_divisor(4)

    machine.freq(freq)

    try:
        # Run 1 clock
        print("Clock test... ", end ="")
        start_rx()
        sm.put(63)
        sm.get()
        print(f" done. Value now: {tt.output_byte}")

        for j in range(4):
            readings = sm_rx.get()
            for i in range(16):
                val = (readings >> (i*2)) & 0x3
                print(val, end = " ")
        print()
        sm_rx.active(0)
        
        total_errors = 0

        for _ in range(10):
            last = tt.output_byte
            
            start_rx()
            d.config(write=dst_data, trigger=True)
            
            # Run clock for approx 1 second, sending a multiple of 256 clocks plus 1.
            t = time.ticks_us()
            #sm.put((freq // 512) * 256)
            sm.put(1024*17)
            sm.get()
            t = time.ticks_us() - t
            print(f"Clocked for {t}us: ", end = "")
            
            for j in range(0,4):
                readings = dst_data[j]
                for i in range(4):
                    val = (readings >> (i*2)) & 0x3
                    print(val, end = " ")
                    
            # Check the counter has incremented by 1.
            if tt.output_byte != (last + 1) & 0xFF:
                print("Error: ", end="")
            print(tt.output_byte)
            
            # Check the counter continuously increases
            def verify(count, expected_val, retry):
                errors = 0
                
                for j in range(2,len(dst_data)):
                    readings = dst_data[j]
                    for i in range(4):
                        val = (readings >> (i*2)) & 0x3
                        if count == 1 and val != expected_val:
                            if retry:
                                return -1
                            else:
                                print(f"Error at {j}:{i} {val} should be {expected_val}")
                                errors += 1
                        count += 1
                        if count == 2:
                            expected_val = (expected_val + 1) & 0x3
                            count = 0
                    if errors > 10: break
                return errors
                    
            expected_val = dst_data[2] & 0x3
            errors = verify(1, expected_val, True)
            if errors == -1:
                expected_val = (dst_data[2] >> 2) & 0x3
                errors = verify(0, expected_val, False)
            
            total_errors += errors
            if errors > 10:
                return total_errors
            
            # Sleep so the 7-seg display can be read
            #time.sleep(0.5)
    finally:    
        if freq > 133_000_000:
            machine.freq(133_000_000)
            rp2.Flash().set_divisor(2)
            
    return total_errors

if __name__ == "__main__":
    freq = 50_000_000
    while True:
        print(f"\nRun at {freq/1000000}MHz project clock\n")
        errors = run_test(freq)
        if errors > 10: break
        freq += 1_000_000
