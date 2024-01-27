import machine

import ttboard.util.time as time
from ttboard.demoboard import DemoBoard
from ttboard.pins.gpio_map import GPIOMap

import hovalaag.pio


class Hovalaag:
    def __init__(self):
        machine.freq(133_000_000)
        
        # Configure high inputs to Hovalaag
        self.tt = DemoBoard(iniFile='/hovalaag.ini')

        self.tt.uio0.mode = machine.Pin.OUT
        self.tt.uio1.mode = machine.Pin.OUT
        self.tt.uio2.mode = machine.Pin.OUT
        self.tt.uio3.mode = machine.Pin.OUT

        self._set_input(4)
        self.tt.project_nrst.off()
        self.tt.project_clk.on()        # Hovalaag clcok should idle high
        for _ in range(20):
            self.tt.project_clk.toggle()
        time.sleep_us(1)
        self.tt.project_nrst.on()
        
        self.hp = pio.HovalaagPIO(self.tt)
        
        self.executed = 0

    @micropython.native
    def run_instr(self, instr, in1=[], in2=[]):
        self.executed += 1
        return self.hp.run_instr(instr, in1, in2)
    
    

    def _set_input(self, val):
        gpio_inputs_to_hova = [
            self.tt.in0,
            self.tt.in1,
            self.tt.in2,
            self.tt.in3,
            self.tt.in4,
            self.tt.in5,
            self.tt.in6,
            self.tt.in7,
            self.tt.uio0,
            self.tt.uio1,
            self.tt.uio2,
            self.tt.uio3]
        
        for gpio in gpio_inputs_to_hova:
            gpio(val & 1)
            val >>= 1


class Program:
    def __init__(self, prog, in1=None, in2=None):
        self.prog = prog
        if in1 is not None:
            self.reset(in1, in2)
        
    def reset(self, in1, in2=None):
        self.pc = 0
        self.in1 = in1.copy()
        self.in2 = in2.copy() if in2 is not None else []
        self.out1 = []
        self.out2 = [] if in2 is not None else self.in2
        
    @micropython.native
    def execute_one(self, h):
        stat, pc, out = h.run_instr(self.prog[self.pc], self.in1, self.in2)
        self.pc = pc
        if (stat & 0x10) != 0: self.out1.append(out)
        if (stat & 0x20) != 0: self.out2.append(out)
       
    @micropython.native
    def run_until_out1_len(self, h, expected_len):
        # JMP 0 to prime the inputs
        h.run_instr(0b0000_00_00_00_0_00_00_01_0_0_0_000000_000000, self.in1, self.in2)
        self.pc = 0
        
        while len(self.out1) < expected_len:
            self.execute_one(h)
            
        return self.out1
