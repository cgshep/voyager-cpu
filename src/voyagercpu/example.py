#!/usr/bin/env python3
import struct

from ram import VoyagerRAM
from cpu import VoyagerCPU
from utils import logger

from elftools.elf.elffile import ELFFile

REPL_PROMPT = "> Next step (n), view registers (r), memory (m), quit (q), or enter N steps: "
PROGRAM_PROMPT = "> Select test program - (1, default) rv32ui-p-xor, " \
    "(2) rv32ui-p-add, " \
    "(3) rv32ui-p-srai: "
SEG_N = 1
TEST_PROGRAM_PATH =  "./tests/riscv-tests-prebuilt-binaries/isa/rv32ui/"

if __name__ == "__main__":
    voyager_cpu = VoyagerCPU()
    voyager_ram = VoyagerRAM()

    usr_in = input(PROGRAM_PROMPT)
    f = TEST_PROGRAM_PATH
    
    if "2" in usr_in:
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
        voyager_ram.write(seg.data())

    while True:
        usr_in = input(REPL_PROMPT)
        if "r" in usr_in:
            print(sphinx_cpu)
        elif "m" in usr_in:
            print(sphinx_ram)
        elif "q" in usr_in:
            break
        elif "n" in usr_in:
            voyager_cpu.next_cycle(sphinx_ram)
            logger.debug(f"Step: {i}")
        elif usr_in.isdigit():
            for i in range(int(usr_in)):
                if i % 5 == 0:
                    print(f"Step: {i}")
                voyager_cpu.next_cycle(sphinx_ram)
        else:
            print("Try again")
    print("Bye!")
