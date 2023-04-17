#!/usr/bin/env python3
import pytest

from sphinxcpu.decoder import *

def test_decode_instruction_type():
    jal_i = 0x0480006f
    assert type(decode_instruction(jal_i)) == JType

#from elftools.elf.elffile import ELFFile
#def test_init():
#    sphinx_ram = SphinxRAM()
#    sphinx_ram.dump()
#
#def test_fetch():
#    sphinx_ram = SphinxRAM()
#    with open("tests/riscv-tests/isa/rv32ui-p-xor", "rb") as f:
#       seg = ELFFile(f).get_segment(1)
#        sphinx_ram.write(seg.data())
        
        

