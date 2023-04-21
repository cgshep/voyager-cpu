#!/usr/bin/env python3

import glob
import struct

from ram import SphinxRAM
from cpu import SphinxCPU
from utils import logger

from elftools.elf.elffile import ELFFile

# Instructions are always 4-byte aligned for RV32I
INST_ALIGN = 4
PC_REG_INDEX = 32
REPL_PROMPT = "> Next step (n), View registers (r), View memory (m), Quit (q): "
SEG_N = 1

if __name__ == "__main__":
    sphinx_cpu = SphinxCPU()
    sphinx_ram = SphinxRAM()
    
    f = "../../tests/riscv-tests/isa/rv32ui-p-xor"
    print(f"Loaded {f}")
    MAX_STEPS = 64
    with open(f, "rb") as ff:
        e = ELFFile(ff)
        for i, s in enumerate(e.iter_segments()):
            print(f"Segment {i} type: {s['p_type']}")

        print(f"Loading segment {SEG_N}...")
        seg = e.get_segment(SEG_N)
        sphinx_ram.write(seg.data())

    for i in range(MAX_STEPS):
        usr_in = input(REPL_PROMPT)
        if "r" in usr_in:
            print(sphinx_cpu)
        elif "m" in usr_in:
            print(sphinx_ram)
        elif "q" in usr_in:
            exit("Bye!")
        else:
            pass
        logger.debug(f"Step: {i}")
        sphinx_cpu.next_cycle(sphinx_ram)
    
