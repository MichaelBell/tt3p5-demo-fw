import time
import random

import hovalaag

h = hovalaag.Hovalaag()

def hello():
    char_time = 0.5
    
    in1 = [0b01110110, 0b11111001, 0b00111000, 0b10111000, 0b00111111]
    
    # Display HELLO
    #        ALU- A- B- C- D W- F- PC O I X K----- L-----
    h.run_instr(0b0000_00_00_00_0_00_00_00_0_0_0_000000_000000, in1) # IN1=H
    h.run_instr(0b0000_11_00_00_0_00_00_00_0_0_0_000000_000000, in1) # A=IN1, IN1=E.
    h.run_instr(0b0000_11_00_00_0_10_00_00_0_0_0_000000_000000, in1) # W=A, A=IN1, IN1=L
    h.run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, in1) # OUT1=W, W=A, A=IN1, IN1=L.
    time.sleep(char_time) # H
    h.run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, in1) # OUT1=W, W=A, A=IN1, IN1=O
    time.sleep(char_time) # E.
    h.run_instr(0b0000_11_00_00_0_10_00_00_1_0_0_000000_000000, in1) # OUT1=W, W=A, A=IN1
    time.sleep(char_time) # L
    h.run_instr(0b0000_01_00_00_0_10_00_00_1_0_0_000000_000000) # OUT1=W, W=A, A=0
    time.sleep(char_time) # L.
    h.run_instr(0b0000_00_00_00_0_10_00_00_1_0_0_000000_000000) # OUT1=W, W=A
    time.sleep(char_time) # O
    h.run_instr(0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000) # OUT1=W
    time.sleep(char_time)


def test_example_loop1():
    #     ALU- A- B- C- D W- F- PC O I X K----- L-----
    prog = hovalaag.Program([
        0b0000_11_00_00_0_00_00_00_0_0_0_000000_000000,  # A=IN1
        0b0000_00_10_00_0_00_00_00_0_0_0_000000_000000,  # B=A
        0b0101_01_01_00_0_00_00_00_0_0_0_000000_000000,  # A=B=A+B
        0b0101_01_01_00_0_00_00_00_0_0_0_000000_000000,  # A=B=A+B
        0b0101_00_00_00_0_01_00_00_0_0_0_000000_000000,  # W=A+B
        0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000,  # OUT1=W
        0b0000_00_00_00_0_00_00_01_0_0_0_000000_000000,  # JMP 0
    ])

    NUM_VALUES = 10
    in1 = [random.randint(-2048 // 8,2047 // 8) for x in range(NUM_VALUES)]
    
    prog.reset(in1)
    out = prog.run_until_out1_len(h, NUM_VALUES)
    print(in1)
    print(out)

    for i in range(NUM_VALUES):
        assert out[i] == in1[i] * 8

def test_aoc2020_1_1():
    prog = hovalaag.Program([
        0x0f0017e4,
        0x6d001000,
        0x60127000,
        0x0c001000,
        0x10031011,
        0x60137007,
        0x0c009004,
        0x0c003000,
        0x0c003000,
        0x030017e4,
        0x6d183000,
        0x60127000,
        0x0c013011,
        0x10021000,
        0x6c137009,
        0x10031011,
        0x0000900e,
        0x270057e4,
        0x60081000,
        0x00005000,
    ])

    in1 = [
        2000, 
50, 
1984, 
1600, 
1736, 
1572, 
2010, 
1559, 
1999, 
1764, 
1808, 
1745, 
1343, 
1495, 
1860, 
1977, 
1981, 
1640, 
1966, 
1961, 
1978, 
1719, 
1930, 
535, 
1804, 
1535, 
1507, 
1284, 
1618, 
1991, 
1589, 
1593, 
1960, 
1953, 
1963, 
1697, 
1741, 
1823, 
1932, 
1789, 
1822, 
1972, 
1570, 
1651, 
1800, 
1514, 
726, 
1567, 
72, 
1987, 
1791, 
1842, 
1020, 
1541, 
1383, 
1505, 
2009, 
1925, 
13, 
1973, 
1599, 
1632, 
1905, 
1626, 
1554, 
1913, 
1890, 
1583, 
1513, 
1828, 
187, 
1616, 
1508, 
1524, 
1613, 
1648, 
32, 
1612, 
1992, 
1671, 
1955, 
1943, 
1936, 
1870, 
1629, 
1493, 
1770, 
1699, 
1990, 
1658, 
1592, 
1596, 
1888, 
1540, 
239, 
1677, 
1602, 
1877, 
1481, 
2004, 
1985, 
1829, 
1980, 
2008, 
1964, 
897, 
1843, 
1750, 
1969, 
1790, 
1989, 
1606, 
1484, 
1983, 
1986, 
1501, 
1511, 
1543, 
1869, 
1051, 
1810, 
1716, 
1633, 
1850, 
1500, 
1120, 
1849, 
1941, 
1403, 
1515, 
1915, 
1862, 
2002, 
1952, 
1893, 
1494, 
1610, 
1797, 
1908, 
1534, 
1979, 
2006, 
1971, 
1993, 
1432, 
1547, 
1488, 
1642, 
1982, 
1666, 
1856, 
1889, 
1691, 
1976, 
1962, 
2005, 
1611, 
1665, 
1816, 
1880, 
1896, 
1552, 
1809, 
1844, 
1553, 
1841, 
1785, 
1968, 
1491, 
1498, 
1995, 
1748, 
1533, 
1988, 
2001, 
1917, 
1788, 
1537, 
1659, 
1574, 
1724, 
1997, 
923, 
1476, 
1763, 
1817, 
1998, 
1848, 
1974, 
1830, 
1672, 
1861, 
1652, 
1551, 
1363, 
1645, 
1996, 
1965, 
1967, 
1778, 
0
    ]

    h.executed = 0
    prog.reset(in1)
    t = time.ticks_ms()
    out = prog.run_until_out1_len(h, 2)
    t = time.ticks_ms() - t
    print(f"Executed {h.executed} instructions in {t}ms")
    print(out)
    assert out[0] + out[1] == 2020
