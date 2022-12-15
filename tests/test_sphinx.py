#!/usr/bin/env python3
import pytest

from sphinx import SphinxRAM, SphinxCPU
from elftools.elf.elffile import ELFFile

def test_decode():
    sphinx_ram = SphinxRAM()
    sphinx_ram.dump()
    with open("tests/riscv-tests/isa/rv32ui-p-xor", "rb") as f:
        seg = ELFFile(f).get_segment(1)
        sphinx_ram.write(seg.data())
        sphinx_ram.dump()
        

