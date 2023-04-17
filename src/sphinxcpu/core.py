#!/usr/bin/env python3

import glob
import struct

from .decoder import decode_instruction
from .utils import register_names, abi_register_name_dict

from elftools.elf.elffile import ELFFile

# Instructions are always 4-byte aligned for RV32I
INST_ALIGN = 4
DEFAULT_RAM_SIZE = 0x1000

class SphinxRAM:
    def __init__(self, ram_size=DEFAULT_RAM_SIZE):
        self.ram_size = ram_size
        self.ram = b"\x00" * ram_size

    def __str__(self):
        ram_str = ""
        for i, data in enumerate(self.ram):
            if i % 8 == 0:
                ram_str += "\n"
            ram_str += f"0x{i:03X}: {data:02X}  "
        return ram_str

    def write(self, data, addr=0):
        self.ram = self.ram[:addr] + data + self.ram[addr+len(data):]

    def read(self, start_idx, end_idx=1):
        return self.ram[start_idx:start_idx+end_idx]

    def dump(self):
        print(self.__str__())


class SphinxCPU:
    def __init__(self, start_pc=0):
        self.registers = self.reset_regs()
        self.registers["pc"] = start_pc
        self.time_period = 0

    def __str__(self):
        dump_str = f"Time period: {time_period}\n"
        dump_str += "Register states:\n"
        for i, r in enumerate(self.registers.keys()):
            dump_str += "0x{0:5d}: {0:32X} ".format(r, self.registers[r])
            if i > 0 and i % 10 == 0:
                dump_str += "\n"
        return dump_str

    def dump(self):
        print(self.__str__())

    def reset_regs(self) -> dict:
        return { reg: 0 for reg in register_names() }

    def next_cycle(self, ram):
        # 1. Fetch instruction from RAM
        print("@@@@@ Instruction fetch @@@@@")
        raw_inst = ram.read(self.registers["pc"], INST_ALIGN)
        print(f"Hex: 0x{raw_inst.hex()}")
        raw_inst_bin = struct.unpack("<I", raw_inst)[0]
        print(f"Bin: {bin(raw_inst_bin)}")
        # Decode
        inst_type = decode_instruction(raw_inst_bin)
        print(inst_type)

        # Execute

        # Memory Access

        # Write back

        # Increment PC
        self.registers["pc"] += INST_ALIGN


if __name__ == "__main__":
    sphinx_cpu = SphinxCPU()
    sphinx_ram = SphinxRAM()
    
    #for f in glob.glob("tests/riscv-tests/isa/rv32ui-p-*"):
    f = "../../tests/riscv-tests/isa/rv32ui-p-xor"

    with open(f, "rb") as ff:
        e = ELFFile(ff)
        seg = e.get_segment(1)
        #print("****\n** SEGMENT **\n****")
        #hex_str = ""
        #for i, b in enumerate(seg.data()):
        #    if i > 0 and i % 16 == 0:
        #        print(hex_str)
        #        hex_str = ""
        #    hex_str += f"{b:02x} "
        sphinx_ram.write(seg.data())
    #sphinx_ram.dump()
    for i in range(5):
        print(f"***\n*** Step {i} ***\n***")
        sphinx_cpu.next_cycle(sphinx_ram)
    
