#!/usr/bin/env python3
import struct

from ram import SphinxRAM
from cpu import SphinxCPU
from utils import logger

from elftools.elf.elffile import ELFFile

# Instructions are always 4-byte aligned for RV32I
INST_ALIGN = 4
PC_REG_INDEX = 32
REPL_PROMPT = "> Next step (n), view registers (r), memory (m), quit (q), or enter N steps: "
PROGRAM_PROMPT = "> Select the test program - (1) rv32ui-p-xor, " \
    "(2) rv32ui-p-add, " \
    "(3) rv32ui-p-srai: "
SEG_N = 1
TEST_PROGRAM_PATH =  "./tests/official-test-binaries/"

if __name__ == "__main__":
    sphinx_cpu = SphinxCPU()
    sphinx_ram = SphinxRAM()

    usr_in = input(PROGRAM_PROMPT)
    f = TEST_PROGRAM_PATH
    
    if "1" in usr_in:
        f += "rv32ui-p-xor"
    elif "2" in usr_in:
        f += "rv32ui-p-add"
    elif "3" in usr_in:
        f += "rv32ui-p-srai"
    else:
        f += "rv32ui-p-xor"

    print(f"Loading {f}...")

    with open(f, "rb") as ff:
        e = ELFFile(ff)
        for i, s in enumerate(e.iter_segments()):
            print(f"Segment {i} type: {s['p_type']}")

        print(f"Loading segment {SEG_N}...")
        seg = e.get_segment(SEG_N)
        sphinx_ram.write(seg.data())

    while True:
        usr_in = input(REPL_PROMPT)
        if "r" in usr_in:
            print(sphinx_cpu)
        elif "m" in usr_in:
            print(sphinx_ram)
        elif "q" in usr_in:
            break
        elif "n" in usr_in:
            sphinx_cpu.next_cycle(sphinx_ram)
            logger.debug(f"Step: {i}")
        elif usr_in.isdigit():
            for i in range(int(usr_in)):
                if i % 5 == 0:
                    print(f"Step: {i}")
                sphinx_cpu.next_cycle(sphinx_ram)
        else:
            print("Try again")
    print("Bye!")
