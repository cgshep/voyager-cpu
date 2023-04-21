#!/usr/bin/env python3

import glob
import logging
import struct

from decoder import *
from utils import register_names, abi_register_name_dict

from elftools.elf.elffile import ELFFile

# Instructions are always 4-byte aligned for RV32I
INST_ALIGN = 4
DEFAULT_RAM_SIZE = 0x1000
PC_REG_INDEX = 32

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
        self.regfile = self.reset_regs()
        self.regfile[PC_REG_INDEX] = start_pc
        self.time_period = 0

    def __str__(self) -> str:
        dump_str = f"Time period: {self.time_period}\n"
        dump_str += "Register states:\n"
        for i, r in enumerate(self.regfile.keys()):
            dump_str += f"{REG_DICT[i]}: {self.regfile[r]} \t"
            if i % 5 == 0 and i > 0:
                dump_str += "\n"
        return dump_str

    def reset_regs(self) -> dict:
        return { i: 0 for i, _ in enumerate(register_names()) }

    def __fetch(self, ram):
        logger.debug("@@@@@ Instruction fetch @@@@@")
        raw_inst = ram.read(self.regfile[PC_REG_INDEX],
                            INST_ALIGN)
        logger.debug(f"Hex: 0x{raw_inst.hex()}")
        # Convert to little endian
        raw_inst_bin = struct.unpack("<I", raw_inst)[0]
        logger.debug(f"Bin: {bin(raw_inst_bin)}")
        return raw_inst_bin

    def __decode(self, raw_inst: int) -> RVInst:
        return decode_instruction(raw_inst)

    def __execute(self, inst: RVInst):
        mne = inst.mnemonic
        if mne == Instruction.LUI:
            self.regfile[inst.rd] = inst.imm
        elif mne == Instruction.AUIPC:
            self.regfile[inst.rd] = self.regfile[PC_REG_INDEX] + inst.imm
        elif mne == Instruction.JAL:
            self.regfile[inst.rd] = self.regfile[PC_REG_INDEX] + INST_ALIGN
            self.regfile[PC_REG_INDEX] += inst.imm
        elif mne == Instruction.JALR:
            self.regfile[inst.rd] = self.regfile[PC_REG_INDEX] + INST_ALIGN
            self.regfile[PC_REG_INDEX] = self.regfile[inst.rs1] + inst.imm
        elif type(inst) == BType:
            if mne == Instruction.BEQ and inst.rs1 == inst.rs2:
                self.regfile[PC_REG_INDEX] += inst.imm
            elif mne == Instruction.BNE and inst.rs1 != inst.rs2:
                self.regfile[PC_REG_INDEX] += inst.imm
            elif (mne == Instruction.BLT or mne == Instruction.BLTU) and inst.rs1 < inst.rs2:
                self.regfile[PC_REG_INDEX] += inst.imm
            elif (mne == Instruction.BGE or mne == Instruction.BGEU) and inst.rs1 >= inst.rs2:
                self.regfile[PC_REG_INDEX] += inst.imm
        elif mne == Instruction.LB or mne == Instruction.LBU:
            self.regfile[inst.rd] = ram[inst.rs1 + inst.imm]
        elif mne == Instruction.LH or mne == Instruction.LHU:
            addr = inst.rs1 + inst.imm
            self.regfile[inst.rd] = ram[addr:addr+2]
        elif mne == Instruction.LW:
            addr = inst.rs1 + inst.imm
            self.regfile[inst.rd] = ram[addr:addr+4]
        elif mne == Instruction.SB:
            ram[inst.rs1 + inst.imm] = struct.unpack("B", self.regfile[inst.rs2] & 0xFF)
        elif mne == Instruction.SH:
            ram[inst.rs1 + inst.imm] = struct.unpack("H", self.regfile[inst.rs2] & 0xFFFF)
        elif mne == Instruction.SW:
            ram[inst.rs1 + inst.imm] = struct.unpack("I", self.regfile[inst.rs2] & 0xFFFFFFFF)
        elif mne == Instruction.ADDI:
            self.regfile[inst.rd] = self.regfile[inst.rs1] + inst.imm
        elif mne == Instruction.SLTI or mne == Instruction.SLTIU:
            self.regfile[inst.rd] = 1 if self.regfile[inst.rs1] < inst.imm else 0
        elif mne == Instruction.XORI:
            self.regfile[inst.rd] = self.regfile[inst.rs1] ^ inst.imm
        elif mne == Instruction.ORI:
            self.regfile[inst.rd] = self.regfile[inst.rs1] | inst.imm
        elif mne == Instruction.ANDI:
            self.regfile[inst.rd] = self.regfile[inst.rs1] & inst.imm
        elif mne == Instruction.SLLI:
            self.regfile[inst.rd] = self.regfile[inst.rs1] << inst.imm
        elif mne == Instruction.SRLI:
            sign_bit = self.regfile[inst.rs1] >> 31
            res = self.regfile[inst.rs1] >> (inst.imm & 0x1F)
            res |= (0xFFFFFFFF * sign_bit) << (32 - (inst.imm & 0x1F))
            self.regfile[inst.rd] = res
        elif mne == Instruction.SRAI:
            self.regfile[inst.rd] = self.regfile[inst.rs1] >> inst.imm
        elif mne == Instruction.ADD:
            self.regfile[inst.rd] = self.regfile[inst.rs1] + self.regfile[inst.rs2]
        elif mne == Instruction.SUB:
            self.regfile[inst.rd] = self.regfile[inst.rs1] - self.regfile[inst.rs2]
        elif mne == Instruction.SLL:
            self.regfile[inst.rd] = self.regfile[inst.rs1] << self.regfile[inst.rs2]
        elif mne == Instruction.SLT:
            self.regfile[inst.rd] = 1 if self.regfile[inst.rs1] < self.regfile[inst.rs2] else 0
        elif mne == Instruction.SLTU:
            rs1_u = self.regfile[inst.rs1] & 0xFFFFFFFF
            rs2_u = self.regfile[inst.rs2] & 0xFFFFFFFF
            self.regfile[inst.rd] = 1 if rs1_u < rs2_u else 0
        elif mne == Instruction.XOR:
            self.regfile[inst.rd] = self.regfile[inst.rs1] ^ self.regfile[inst.rs2]
        elif mne == Instruction.SRL:
            sign_bit = self.regfile[inst.rs1] >> 31
            res = self.regfile[inst.rs1] >> (self.regfile[inst.rs2] & 0x1F)
            res |= (0xFFFFFFFF * sign_bit) << (32 - (self.regfile[inst.rs2] & 0x1F))
            self.regfile[inst.rd] = res
        elif mne == Instruction.SRA:
            self.regfile[inst.rd] = self.regfile[inst.rs1] >> self.regfile[inst.rs2]
        elif mne == Instruction.OR:
            self.regfile[inst.rd] = self.regfile[inst.rs1] | self.regfile[inst.rs2]
        elif mne == Instruction.AND:
            self.regfile[inst.rd] = self.regfile[inst.rs1] & self.regfile[inst.rs2]
        else:
            logger.debug("System instructions not implemented")

    def next_cycle(self, ram):
        raw_inst = self.__fetch(ram)
        decoded_inst = self.__decode(raw_inst)
        logger.debug(decoded_inst)
        self.__execute(decoded_inst)
        
        # Increment PC
        self.regfile[PC_REG_INDEX] += INST_ALIGN
        logger.debug(self.__str__())
        self.time_period += 1


if __name__ == "__main__":
    sphinx_cpu = SphinxCPU()
    sphinx_ram = SphinxRAM()
    
    #for f in glob.glob("tests/riscv-tests/isa/rv32ui-p-*"):
    f = "../../tests/riscv-tests/isa/rv32ui-p-xor"
    MAX_STEPS = 64
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

    for i in range(MAX_STEPS):
        logger.debug(f"***\n*** Step {i} ***\n***")
        sphinx_cpu.next_cycle(sphinx_ram)
    
