from machine import Pin
from time import sleep_us, sleep

gpio_inputs_to_hova = [
    Pin(9, Pin.OUT),
    Pin(10, Pin.OUT),
    Pin(11, Pin.OUT),
    Pin(12, Pin.OUT),
    Pin(17, Pin.OUT),
    Pin(18, Pin.OUT),
    Pin(19, Pin.OUT),
    Pin(20, Pin.OUT),
    Pin(21, Pin.OUT),
    Pin(22, Pin.OUT),
    Pin(23, Pin.OUT),
    Pin(24, Pin.OUT)
    ]

gpio_outputs_from_hova = [
    Pin(3, Pin.IN, Pin.PULL_DOWN),
    Pin(4, Pin.IN, Pin.PULL_DOWN),
    Pin(7, Pin.IN, Pin.PULL_DOWN),
    Pin(8, Pin.IN, Pin.PULL_DOWN),
    Pin(13, Pin.IN, Pin.PULL_DOWN),
    Pin(14, Pin.IN, Pin.PULL_DOWN),
    Pin(15, Pin.IN, Pin.PULL_DOWN),
    Pin(16, Pin.IN, Pin.PULL_DOWN)
    ]

gpio_clk = Pin(0, Pin.OUT)
gpio_rst = Pin(5, Pin.OUT)

def clock():
    sleep_us(1)
    gpio_clk.off()
    sleep_us(2)
    gpio_clk.on()
    sleep_us(1)
    
def set_input(val):
    for gpio in gpio_inputs_to_hova:
        gpio.value(val & 1)
        val >>= 1

def read_output():
    val = 0
    for gpio in reversed(gpio_outputs_from_hova):
        val <<= 1
        val |= gpio.value()
    return val
    
def reset():
    set_input(4)
    gpio_rst.off()
    for _ in range(10):
        clock()
    gpio_clk.off()
    sleep_us(1)
    gpio_rst.on()

def run_instr(instr, in1, in2):
    outs = []
    set_input(instr & 0x3FF)
    clock()
    outs.append(read_output())
    set_input((instr >> 12) & 0x3FF)
    clock()
    outs.append(read_output())
    set_input((instr >> 24) & 0x3FF)
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
    sleep(1)
    
    char_time = 0.5
    # Display HELLO
    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0000_00_00_00_0_00_00_00_0_0_0_000000_000000, 0b01110110, 0) # IN1=H
    run_instr(0b0000_11_00_00_0_00_00_00_0_0_0_000000_000000, 0b11111001, 0) # A=IN1, IN1=E.
    run_instr(0b0000_11_00_00_0_10_00_00_0_0_0_000000_000000, 0b00111000, 0) # W=A, A=IN1, IN1=L
    run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, 0b10111000, 0) # OUT1=W, W=A, A=IN1, IN1=L.
    sleep(char_time) # H
    run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, 0b00111111, 0) # OUT1=W, W=A, A=IN1, IN1=O
    sleep(char_time) # E.
    run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W, W=A, A=IN1
    sleep(char_time) # L
    run_instr(0b0000_01_00_00_0_10_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W, W=A, A=0
    sleep(char_time) # L.
    run_instr(0b0000_00_00_00_0_10_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W, W=A
    sleep(char_time) # O
    run_instr(0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000, 0, 0) # OUT1=W
    sleep(char_time) # Off

def test_alu_op(alu_op, a, b, sym, expected_result):
    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0000_00_00_00_0_00_00_00_0_0_0_000000_000000, a, 0)     # IN1=a
    run_instr(0b0000_11_11_00_0_00_00_00_0_0_1_000000_000000 + b, 0, 0) # A=IN1, B=b
    run_instr(0b0000_00_00_00_0_01_10_00_0_0_0_000000_000000 + (alu_op << 28), 0, 0)  # W=ALU
    pc, out = run_instr(0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000, 0, 0)  # OUT1=W

    if out > 127: out -= 256

    print("FAIL: " if expected_result != out else "PASS: ", end="")

    print(f"{b} {sym} {a} = {out} (expected: {expected_result})")

def load_val_to_c(val):
    run_instr(0b0000_00_11_00_0_00_00_00_0_0_1_000000_000000 + val, 0, 0) # B=val
    run_instr(0b0010_00_00_01_0_00_00_00_0_0_0_000000_000000, 0, 0) # C=B

def test_alu():
    reset()
    sleep(1)
    
    test_alu_op(0b0000, 7, 35, "[0]", 0)   # Zero
    test_alu_op(0b0001, 7, 35, "[-A]", -7)  # -A
    test_alu_op(0b0010, 7, 35, "[B]", 35)  # B

    #           ALU- A- B- C- D W- F- PC O I X K----- L-----
    run_instr(0b0010_00_00_10_0_00_00_00_0_0_0_000000_000000, 0, 0)  # DEC
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
    gpio_rst.off()
    clock()
    gpio_rst.on()    

    for _ in range(10):
        run_instr(0b1110_00_00_00_0_01_00_00_0_0_0_000000_000000, 0, 0)  # W=RND
        pc, out1 = run_instr(0b1110_00_00_00_0_01_00_00_1_0_0_000000_000000, 0, 0)  # OUT1=W, W=RND
        pc, out2 = run_instr(0b1110_00_00_00_0_00_00_00_1_1_0_000000_000000, 0, 0)  # OUT2=W
        print("Random numbers: ", out1, out2)

if __name__ == "__main__":
    gpio_mgmt = Pin(1, Pin.OUT)
    gpio_mgmt.on()
    Pin(6, Pin.OUT).off()
    
    hello()
    test_alu()
    test_rng()

