from machine import Pin, Timer
import json
import time
import sys

# control
ctrl_mgmt   = Pin(1, Pin.OUT)    

# Set these once mgmt mux switched
ctrl_en     = None  
ctrl_rst_n  = None
ctrl_inc    = Pin(6, Pin.OUT)

user_clk    = Pin(0, Pin.OUT)
user_rst_n  = Pin(5, Pin.OUT)

user_in = [Pin(9, Pin.OUT),
    Pin(10, Pin.OUT),
    Pin(11, Pin.OUT),
    Pin(12, Pin.OUT),
    Pin(17, Pin.OUT),
    Pin(18, Pin.OUT),
    Pin(19, Pin.OUT),
    Pin(20, Pin.OUT)]

# Set these once mgmt mux switched
user_out  = []

# Clear these to inputs before switching design
# individual tests may change directions/redefine
user_io   = []

def reset_mux():
    global user_io, ctrl_en, ctrl_inc, ctrl_rst_n

    # Set user ios to inputs
    user_io = [
        Pin(21, Pin.IN),
        Pin(22, Pin.IN),
        Pin(23, Pin.IN),
        Pin(24, Pin.IN),
        Pin(25, Pin.IN),
        Pin(26, Pin.IN),
        Pin(27, Pin.IN),
        Pin(28, Pin.IN),
    ]

    # Enable management control
    ctrl_mgmt.value(0)
    time.sleep_ms(1)
    ctrl_en = Pin(8, Pin.OUT)
    ctrl_rst_n = Pin(7, Pin.OUT)

    # reset the controller
    ctrl_inc.value(0)
    ctrl_rst_n(1)
    ctrl_en.value(0)
    time.sleep_ms(10)
    ctrl_rst_n(0)
    time.sleep_ms(10)

    # When the mgmt mux is flipped, pin 7 is driven by the TT ASIC, so should
    # be an input.  Therefore, pull up input now to release the reset.
    ctrl_rst_n = Pin(7, Pin.IN, Pin.PULL_UP)
    time.sleep_ms(10)

def enable_design(name):
    global user_out, ctrl_en, ctrl_inc, ctrl_rst_n

    with open("shuttle_index.json") as fh:
        index = json.load(fh)
        for project in index["mux"]:
            if index["mux"][project]["macro"] == name:
                count = int(project)
                repo = index["mux"][project]["repo"]
                commit = index["mux"][project]["commit"]

    try:
        print(f"enabling design {name} by sending {count} [0b{count:08b}] pulses")
        print(f"design repo {repo} @ {commit}")
    except NameError:
        print(f"no such design {name}")
        sys.exit(1)

    reset_mux()

    # send the number of pulses required
    for c in range(count):
        ctrl_inc.value(1)
        time.sleep_ms(1)
        ctrl_inc.value(0)
        time.sleep_ms(1)


    # When the mgmt mux is flipped, pin 8 is driven by the TT ASIC, so should
    # be an input.  Therefore, set as a pull up input now to enable the design.
    ctrl_en = Pin(8, Pin.IN, Pin.PULL_UP)
    time.sleep_ms(1)

    ctrl_mgmt.value(1)
    time.sleep_ms(1)

    # Clear ctrl pins and set up the output pin mapping
    ctrl_en = None
    ctrl_rst_n = None

    # Pull down to ensure 7-seg doesn't light if undriven
    user_out = [
        Pin(3, Pin.IN, Pin.PULL_DOWN),
        Pin(4, Pin.IN, Pin.PULL_DOWN),
        Pin(7, Pin.IN, Pin.PULL_DOWN),
        Pin(8, Pin.IN, Pin.PULL_DOWN),
        Pin(13, Pin.IN, Pin.PULL_DOWN),
        Pin(14, Pin.IN, Pin.PULL_DOWN),
        Pin(15, Pin.IN, Pin.PULL_DOWN),
        Pin(16, Pin.IN, Pin.PULL_DOWN),
    ]

def test_design_tnt_counter():
    # select design
    enable_design("tt_um_test")

    # reset
    user_rst_n.value(0)

    # enable the internal counter of test design
    user_in[0].value(1)
    time.sleep_ms(100)

    # take out of reset
    user_rst_n.value(1)

    # clock it forever
    while True:
        user_clk.value(0)
        time.sleep_ms(100)
        user_clk.value(1)
        time.sleep_ms(100)
        print(user_out[0].value(), user_out[1].value(), user_out[2].value(), user_out[3].value())

def test_design_loopback():
    # select design
    enable_design("tt_um_loopback")

    # toggle user in 0 forever
    while True:
        user_in[0].value(0)
        time.sleep_ms(500)
        print(user_out[0].value(), user_out[1].value(), user_out[2].value(), user_out[3].value())
        user_in[1].value(1)
        time.sleep_ms(500)
        print(user_out[0].value(), user_out[1].value(), user_out[2].value(), user_out[3].value())

def test_design_vga():
    # select design
    enable_design("tt_um_vga_clock")
    # reset
    user_rst_n.value(0)
    time.sleep_ms(1)
    user_rst_n.value(1)

    # toggle clock
    while True:
        user_clk.value(0)
        user_clk.value(1)
        print(user_out[0].value(), user_out[1].value(), user_out[2].value(), user_out[3].value())

def test_design_powergate_add():
    # select design
    enable_design("tt_um_power_test")

    # toggle user in 0 forever
    while True:
        user_in[0].value(0)
        time.sleep_ms(100)
        print(user_out[0].value(), user_out[1].value(), user_out[2].value(), user_out[3].value())
        user_in[0].value(1)
        time.sleep_ms(100)
        print(user_out[0].value(), user_out[1].value(), user_out[2].value(), user_out[3].value())

def test_design_powergate_ringosc():
    # select design
    enable_design("tt_um_ringosc_cnt_pfet")

    # toggle user in 0 forever
    while True:
        time.sleep_ms(100)
        print(user_out[0].value(), user_out[1].value(), user_out[2].value(), user_out[3].value())

def test_design_hovalaag():
    # select design
    enable_design("tt_um_MichaelBell_hovalaag")

    import hovalaag
    hovalaag.hello()
    # hovalaag.test_alu()
    # hovalaag.test_rng()

if __name__ == '__main__':
    test_design_tnt_counter()
#    test_design_loopback()
#    test_design_vga()
#    test_design_powergate_add()
#    test_design_powergate_ringosc()
#    test_design_hovalaag()