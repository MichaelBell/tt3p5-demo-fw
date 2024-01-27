from machine import Pin
from rp2 import PIO, StateMachine, asm_pio

@asm_pio(sideset_init=PIO.OUT_HIGH, autopull=True, pull_thresh=32, out_shiftdir=PIO.SHIFT_RIGHT, in_shiftdir=PIO.SHIFT_LEFT, 
         out_init=(PIO.OUT_LOW,)*4 + (PIO.IN_LOW,)*4 + (PIO.OUT_LOW,)*8)
def hova_output_prog():
    # Send instruction
    set(x, 4)
    label("instr_loop")
    out(isr, 12)         
    in_(isr, 4)          .side(1)
    mov(pins, isr)
    jmp(x_dec, "instr_loop").side(0)
    out(null, 32)        .side(1)

@asm_pio(autopush=True, push_thresh=12, out_shiftdir=PIO.SHIFT_RIGHT, in_shiftdir=PIO.SHIFT_LEFT)
def hova_input_prog():
    set(x, 2)
    label("discard_loop")
    wait(1, gpio, 0)
    wait(0, gpio, 0)
    jmp(x_dec, "discard_loop")
    
    nop().delay(2)
    in_(pins, 12)
    wait(1, gpio, 0)
    wait(0, gpio, 0)

    # The assumption is that the next instruction will not be immediately queued
    # hence we can take our time decoding the next PC before decoding OUT
    set(x, 1).delay(3)
    label("decode_loop")
    mov(y, pins)
    mov(osr, y)
    out(null, 22)
    in_(osr, 4)
    mov(osr, y)
    out(null, 10)
    in_(osr, 4)
    mov(osr, y)
    out(null, 4)
    in_(osr, 2)
    in_(y, 2)
    jmp(x_dec, "decode_loop")

class HovalaagPIO:
    def __init__(self, tt):
        self.tx_sm = StateMachine(0, hova_output_prog, out_base=Pin(9), sideset_base=Pin(0), freq=133_000_000)
        self.rx_sm = StateMachine(1, hova_input_prog, in_base=Pin(3), freq=133_000_000)
        self.rx_sm.active(1)
        #self.rx_sm.exec("set(x, 4)")
        self.tx_sm.active(1)
        self.tt = tt

    @micropython.native
    def run_instr(self, instr, in1, in2):
        self.tx_sm.put(instr)
        
        stat = self.rx_sm.get()
        #print(f"{stat & 0x33:02x}", end=" ")

        if (stat & 0x1) != 0: in1.pop(0)
        if (stat & 0x2) != 0: in2.pop(0)
        
        in1_val = 0 if len(in1) == 0 else in1[0]
        in2_val = 0 if len(in2) == 0 else in2[0]
        
        self.tx_sm.put(in1_val | (in2_val << 12))
        pc = self.rx_sm.get()
        #print(pc, end=" ")
        out = self.rx_sm.get()
        if out > 2047: out -= 4096
        #print(out)
        
        return stat, pc, out
