#!/usr/bin/env python3

import enum
import glob
import struct

from elftools.elf.elffile import ELFFile

# Instructions are always 4-byte aligned for RV32I
INST_ALIGN = 4

class Opcode(enum.Enum):
    LUI      = 0b0110111
    AUIPC    = 0b0010111
    JAL      = 0b1101111
    JALR     = 0b1100111
    # B: Shorthand for branch instructions
    B = BEQ = BNE = BLT = BGE = BLTU = BGEU = 0b1100011
    # L: Loads
    L = LB = LH = LW = LBU = LHU = 0b0000011
    # S: Stores 
    S = SB = SH = SW = 0b0100011
    # I: Immediate instructions
    I = ADDI = SLTI = SLTIU = XORI = ORI = ANDI = SLLI = SRLI = SRAI = 0b0010011
    # A: Arithmetic
    A = ADD = SUB = SLL = SLT = SLTU = XOR = SRL = SRA = OR = AND = 0b0110011
    # F: Fences
    F = FENCE = FENCE_I = 0b0001111
    # Sys: System instructions
    SYS = ECALL = EBREAK = CSRRW = CSRRS = CSRRC = CSRRWI = CSRRSI = CSRRCI = 0b1110011


class Funct3(enum.Enum):
    JALR = BEQ = LB = SB = ADDI = ADD = SUB = FENCE = ECALL = EBREAK = 0b000
    BNE = LH = SH = SLLI = SLL = FENCE_I = CSRRW = 0b001
    BLT = LBU = XORI = XOR = 0b100
    BGE = LHU = SRLI = SRAI = SRL = SRA = CSRRWI = 0b101
    BLTU = ORI = OR = CSRRSI = 0b110
    BGEU = ANDI = AND = CSRRCI = 0b111
    LW = SW = SLTI = SLT = CSRRS = 0b010
    SLTIU = SLTU = CSRRC = 0b011


class Funct7(enum.Enum):
    SLLI = SRLI = ADD = SLL = SLT = SLTU = XOR = SRL = OR = AND = 0b0000000
    SRAI = SUB = SRA = 0b0100000


DEFAULT_RAM_SIZE = 0x1000

class SphinxRAM:
    def __init__(self, ram_size=DEFAULT_RAM_SIZE):
        self.ram_size = ram_size
        self.ram = b"\x00" * ram_size

    def __str__(self):
        ram_str = "\n"
        for i, data in enumerate(self.ram):
            ram_str += f"0x{i:03X}: {data:02X}  "
            if i > 0 and i % 8 == 0:
                ram_str += "\n"
        return ram_str

    def write(self, data, addr=0):
        self.ram = self.ram[:addr] + data + self.ram[addr+len(data):]

    def dump(self):
        print(self.__str__())


class SphinxCPU:
    REGISTER_NAMES = ["x0", "ra", "sp", "gp", "tp", "pc"] \
        + [f"t{i}" for i in range(7)] \
        + [f"a{i}" for i in range(8)] \
        + [f"s{i}" for i in range(2, 12)]

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

    def reset_regs(self):
        return { r: 0 for r in self.REGISTER_NAMES }

    def next_cycle(self, ram):
        # Fetch
        
        # Decode

        # Execute

        # Memory Access

        # Write back

        # Increment PC
        self.registers["pc"] += INST_ALIGN


if __name__ == "__main__":
    sphinx_cpu = SphinxCPU()
    sphinx_ram = SphinxRAM()

    #for f in glob.glob("tests/riscv-tests/isa/rv32ui-p-*"):
    f = "tests/riscv-tests/isa/rv32ui-p-xor"
    print(f"File: {f}")
    with open(f, "rb") as ff:
        e = ELFFile(ff)
        seg = e.get_segment(1)
        print("****\n** SEGMENT **\n****")
        hex_str = ""
        for i, b in enumerate(seg.data()):
            if i > 0 and i % 16 == 0:
                print(hex_str)
                hex_str = ""
            hex_str += f"{b:02x} "

    # Load program into RAM
    #sphinx_ram.load()
