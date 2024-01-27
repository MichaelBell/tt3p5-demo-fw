import ttboard.util.time as time
from ttboard.mode import RPMode
from ttboard.demoboard import DemoBoard
from ttboard.pins.gpio_map import GPIOMap

# Pin import to provide access in REPL
# to things like tt.uio3.mode = Pin.OUT
from ttboard.pins.upython import Pin

tt = DemoBoard(iniFile='/hovalaag.ini')

# Configure high inputs to Hovalaag
tt.uio0.mode = Pin.OUT
tt.uio1.mode = Pin.OUT
tt.uio2.mode = Pin.OUT
tt.uio3.mode = Pin.OUT

gpio_inputs_to_hova = [
    tt.in0,
    tt.in1,
    tt.in2,
    tt.in3,
    tt.in4,
    tt.in5,
    tt.in6,
    tt.in7,
    tt.uio0,
    tt.uio1,
    tt.uio2,
    tt.uio3,
    ]

gpio_outputs_from_hova = [
    tt.out0,
    tt.out1,
    tt.out2,
    tt.out3,
    tt.out4,
    tt.out5,
    tt.out6,
    tt.out7,
    tt.uio4,
    tt.uio5,
    tt.uio6,
    tt.uio7,    
    ]

def clock():
    #time.sleep_us(1)
    tt.project_clk.off()
    #time.sleep_us(1)
    tt.project_clk.on()
    #time.sleep_us(1)
    
def set_input(val):
    for gpio in gpio_inputs_to_hova:
        gpio(val & 1)
        val >>= 1
    time.sleep_us(1)

def read_output():
    val = 0
    for gpio in reversed(gpio_outputs_from_hova):
        val <<= 1
        val |= gpio()
    return val
    
def reset():
    set_input(4)
    tt.project_nrst.off()
    for _ in range(10):
        clock()
    #tt.project_clk.off()
    time.sleep_us(1)
    tt.project_nrst.on()

def run_instr(instr, in1, in2):
    outs = []
    set_input(instr & 0xFFF)
    clock()
    outs.append(read_output())
    set_input((instr >> 12) & 0xFFF)
    clock()
    outs.append(read_output())
    set_input((instr >> 24) & 0xFFF)
    clock()
    outs.append(read_output())
    set_input(in1)
    clock()
    outs.append(read_output())
    set_input(in2)
    pc = read_output()
    clock()
    outs.append(read_output())
    out = read_output()
    #print(outs)
    return (pc, out)

def hello():
    reset()
    time.sleep(1)
    
    char_time = 0.5
    # Display HELLO
    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0000_00_00_00_0_00_00_00_0_0_0_000000_000000, 0b01110110, 0) # IN1=H
    run_instr(0b0000_11_00_00_0_00_00_00_0_0_0_000000_000000, 0b11111001, 0) # A=IN1, IN1=E.
    run_instr(0b0000_11_00_00_0_10_00_00_0_0_0_000000_000000, 0b00111000, 0) # W=A, A=IN1, IN1=L
    run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, 0b10111000, 0) # OUT1=W, W=A, A=IN1, IN1=L.
    time.sleep(char_time) # H
    run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, 0b00111111, 0) # OUT1=W, W=A, A=IN1, IN1=O
    time.sleep(char_time) # E.
    run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W, W=A, A=IN1
    time.sleep(char_time) # L
    run_instr(0b0000_01_00_00_0_10_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W, W=A, A=0
    time.sleep(char_time) # L.
    run_instr(0b0000_00_00_00_0_10_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W, W=A
    time.sleep(char_time) # O
    run_instr(0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W
    time.sleep(char_time) # Off

def test_alu_op(alu_op, a, b, sym, expected_result):
    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0000_00_00_00_0_00_00_00_0_0_0_000000_000000, a, 0)     # IN1=a
    run_instr(0b0000_11_11_00_0_00_00_00_0_0_1_000000_000000 + b, 0, 0) # A=IN1, B=b
    run_instr(0b0000_00_00_00_0_01_10_00_0_0_0_000000_000000 + (alu_op << 28), 0, 0)  # W=ALU
    pc, out = run_instr(0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000, 0, 0)  # OUT1=W

    if out > 2047: out -= 4096

    print("FAIL: " if expected_result != out else "PASS: ", end="")

    print(f"{b} {sym} {a} = {out} (expected: {expected_result})")

def load_val_to_c(val):
    run_instr(0b0000_00_11_00_0_00_00_00_0_0_1_000000_000000 + val, 0, 0) # B=val
    run_instr(0b0010_00_00_01_0_00_00_00_0_0_0_000000_000000, 0, 0) # C=B

def test_alu():
    reset()
    #time.sleep(1)
    
    test_alu_op(0b0000, 7, 35, "[0]", 0)   # Zero
    test_alu_op(0b0001, 7, 35, "[-A]", -7)  # -A
    test_alu_op(0b0010, 7, 35, "[B]", 35)  # B

    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0000_00_00_10_0_00_00_00_0_0_0_000000_000000, 0, 0)  # DEC
    test_alu_op(0b0011, 7, 35, "[C]", -1)  # C

    load_val_to_c(23)
    test_alu_op(0b0011, 7, 35, "[C]", 23)  # C

    test_alu_op(0b0100, 7, 35, "[A>>1]", 3)   # A>>1
    test_alu_op(0b0101, 7, 35, "+", 42)  # A+B
    test_alu_op(0b0110, 7, 35, "-", 28)  # B-A
    test_alu_op(0b0111, 7, 35, "+", 42)  # A+B+F
    test_alu_op(0b1000, 7, 35, "-", 28)  # B-A-F

    test_alu_op(0b0110, 35, 7, "-", -28)  # B-A
    test_alu_op(0b0111, 7, 35, "+F", 43)  # A+B+F
    test_alu_op(0b0110, 35, 7, "-", -28)  # B-A
    test_alu_op(0b1000, 7, 35, "-F", 27)  # B-A-F

    test_alu_op(0b1001, 7, 35, "|", 7|35)  # A|B
    test_alu_op(0b1010, 7, 35, "&", 7&35)  # A&B
    test_alu_op(0b1011, 7, 35, "^", 7^35)  # A^B
    test_alu_op(0b1100, 7, 35, "~", ~7)  # ~A
    test_alu_op(0b1101, 7, 35, "[A]", 7)  # A
    test_alu_op(0b1110, 8, 35, "[RND]", 0)  # Random number - disabled
    test_alu_op(0b1111, 9, 42, "[1]", 1)  # 1

def test_rng():
    reset()
    
    set_input(0x18)
    tt.project_nrst.off()
    clock()
    tt.project_nrst.on()    

    for _ in range(10):
        run_instr(0b1110_00_00_00_0_01_00_00_0_0_0_000000_000000, 0, 0)  # W=RND
        pc, out1 = run_instr(0b1110_00_00_00_0_01_00_00_1_0_0_000000_000000, 0, 0)  # OUT1=W, W=RND
        pc, out2 = run_instr(0b1110_00_00_00_0_00_00_00_1_1_0_000000_000000, 0, 0)  # OUT2=W
        print("Random numbers: ", out1, out2)

def test_large():
    reset()
    
    val = 3978
    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0000_01_11_00_0_00_00_00_0_0_1_000000_000000 + val, 0, 0) # A=0,B=val
    run_instr(0b0101_01_00_00_0_00_00_00_0_0_0_000000_000000, 0, 0)  # A=A+B
    run_instr(0b0000_00_00_00_0_10_00_00_0_0_0_000000_000000, 0, 0)  # W=A
    pc, out1 = run_instr(0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000, 0, 0)  # OUT1=W
    print(out1)

def count():
    reset()

    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0000_01_01_00_0_00_01_00_0_0_0_000000_000000, 0, 0)  # A=0,B=0,F=ZERO(0)
    run_instr(0b0111_01_00_00_0_10_00_00_0_0_0_000000_000000, 0, 0)  # A=A+B+F,W=A
    
    while True:
        pc, out1 = run_instr(0b0111_01_00_00_0_10_00_00_1_0_0_000000_000000, 0, 0)  # A=A+B+F,W=A,OUT1=W
        time.sleep_ms(100)

if __name__ == "__main__":
    hello()
    test_alu()
    test_rng()
    #count()
    #test_large()
    
    tt.project_clk.off()