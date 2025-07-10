import struct

from .decoder import *
from .utils import register_names, abi_register_name_dict, logger

# Instructions are always 4-byte aligned for RV32I
INST_ALIGN = 4
PC_REG_INDEX = 32

class AlignmentError(Exception):
    pass

class CPU:
    def __init__(self, start_pc=0, verbose=0):
        self.regfile = self.reset_regs()
        self.regfile[PC_REG_INDEX] = start_pc
        self.cycle = 0
        self.verbose = verbose

    def __str__(self) -> str:
        dump_str = f"Cycle: {self.cycle}\n"
        dump_str += "Register states:\n"
        for i, r in enumerate(self.regfile.keys()):
            dump_str += "{:>3}: {:<12}".format(REG_DICT[i], hex(self.regfile[r]))
            if (i + 1) % 5 == 0:
                dump_str += "\n"
        return dump_str

    def reset_regs(self) -> dict:
        return { i: 0 for i, _ in enumerate(register_names()) }

    def __fetch(self, memory):
        raw_inst = memory.read(self.regfile[PC_REG_INDEX],
                               INST_ALIGN)
        logger.debug(f"Fetched instruction: 0x{raw_inst.hex()}")
        # Convert to little endian
        raw_inst_bin = struct.unpack("<I", raw_inst)[0]
        return raw_inst_bin

    def __decode(self, raw_inst: int) -> RVInst:
        # No instruction
        if raw_inst == 0:
            logger.warning("No instruction!")

        try:
            decoded_inst = decode_instruction(raw_inst)
            logger.debug(f"Decoded: {decoded_inst}")
            return decoded_inst
        except DecodeError as e:
            logger.error(e)
            logger.error("Using NOP instead")
            return nop_inst()

    def __execute(self, inst: RVInst):
        if self.verbose:
            print(inst)
        mne = inst.mnemonic
        r = self.regfile # For brevity

        if type(inst) == UType:
            if mne == Instruction.LUI:
                r[inst.rd] = inst.imm
            elif mne == Instruction.AUIPC:
                r[inst.rd] = r[PC_REG_INDEX] + inst.imm
        elif type(inst) == JType:
            if mne == Instruction.JAL:
                r[inst.rd] = r[PC_REG_INDEX] + INST_ALIGN
                r[PC_REG_INDEX] += inst.imm
        elif type(inst) == BType:
        # Branch: compare register *values*, not indices
            a = r[inst.rs1]
            b = r[inst.rs2]
            taken = False
            if mne == Instruction.BEQ:
                taken = (a == b)
            elif mne == Instruction.BNE:
                taken = (a != b)
            elif mne == Instruction.BLT:
                taken = (a < b)
            elif mne == Instruction.BLTU:
                taken = ((a & 0xFFFFFFFF) < (b & 0xFFFFFFFF))
            elif mne == Instruction.BGE:
                taken = (a >= b)
            elif mne == Instruction.BGEU:
                taken = ((a & 0xFFFFFFFF) >= (b & 0xFFFFFFFF))
            if taken:
                logger.debug(f"Branch {mne.name} taken: PC += {inst.imm}")
                r[PC_REG_INDEX] += inst.imm
        elif type(inst) == SType:
            if mne == Instruction.SB:
                memory[inst.rs1 + inst.imm] = struct.unpack("B", r[inst.rs2] & 0xFF)
            elif mne == Instruction.SH:
                memory[inst.rs1 + inst.imm] = struct.unpack("H", r[inst.rs2] & 0xFFFF)
            elif mne == Instruction.SW:
                memory[inst.rs1 + inst.imm] = struct.unpack("I", r[inst.rs2] & 0xFFFFFFFF)
        elif type(inst) == IType:
            # JALR
            if mne == Instruction.JALR:
                r[inst.rd] = r[PC_REG_INDEX] + INST_ALIGN
                r[PC_REG_INDEX] = r[inst.rs1] + inst.imm
            # Load instructions
            elif mne == Instruction.LB or mne == Instruction.LBU:
                r[inst.rd] = memory[inst.rs1 + inst.imm]
            elif mne == Instruction.LH or mne == Instruction.LHU:
                addr = inst.rs1 + inst.imm
                r[inst.rd] = memory[addr:addr+2]
            elif mne == Instruction.LW:
                addr = inst.rs1 + inst.imm
                r[inst.rd] = memory[addr:addr+4]
            # Arithmetic immediate instructions
            elif mne == Instruction.ADDI:
                r[inst.rd] = r[inst.rs1] + inst.imm
            elif mne == Instruction.SLTI or mne == Instruction.SLTIU:
                r[inst.rd] = 1 if r[inst.rs1] < inst.imm else 0
            elif mne == Instruction.XORI:
                r[inst.rd] = r[inst.rs1] ^ inst.imm
            elif mne == Instruction.ORI:
                r[inst.rd] = r[inst.rs1] | inst.imm
            elif mne == Instruction.ANDI:
                r[inst.rd] = r[inst.rs1] & inst.imm
            elif mne == Instruction.SLLI:
                r[inst.rd] = r[inst.rs1] << inst.imm
            elif mne == Instruction.SRLI:
                sign_bit = r[inst.rs1] >> 31
                res = r[inst.rs1] >> (inst.imm & 0x1F)
                res |= (0xFFFFFFFF * sign_bit) << (32 - (inst.imm & 0x1F))
                r[inst.rd] = res
            elif mne == Instruction.SRAI:
                r[inst.rd] = r[inst.rs1] >> inst.imm
        elif type(inst) == RType:
            if mne == Instruction.ADD:
                r[inst.rd] = r[inst.rs1] + r[inst.rs2]
            elif mne == Instruction.SUB:
                r[inst.rd] = r[inst.rs1] - r[inst.rs2]
            elif mne == Instruction.SLL:
                r[inst.rd] = r[inst.rs1] << r[inst.rs2]
            elif mne == Instruction.SLT:
                r[inst.rd] = 1 if r[inst.rs1] < r[inst.rs2] else 0
            elif mne == Instruction.SLTU:
                rs1_u = r[inst.rs1] & 0xFFFFFFFF
                rs2_u = r[inst.rs2] & 0xFFFFFFFF
                r[inst.rd] = 1 if rs1_u < rs2_u else 0
            elif mne == Instruction.XOR:
                r[inst.rd] = r[inst.rs1] ^ r[inst.rs2]
            elif mne == Instruction.SRL:
                sign_bit = r[inst.rs1] >> 31
                res = r[inst.rs1] >> (r[inst.rs2] & 0x1F)
                res |= (0xFFFFFFFF * sign_bit) << (32 - (r[inst.rs2] & 0x1F))
                r[inst.rd] = res
            elif mne == Instruction.SRA:
                r[inst.rd] = r[inst.rs1] >> r[inst.rs2]
            elif mne == Instruction.OR:
                r[inst.rd] = r[inst.rs1] | r[inst.rs2]
            elif mne == Instruction.AND:
                r[inst.rd] = r[inst.rs1] & r[inst.rs2]

    def next_cycle(self, memory):
        prev_pc = self.regfile[PC_REG_INDEX]
        raw_inst = self.__fetch(memory)
        decoded_inst = self.__decode(raw_inst)
        self.__execute(decoded_inst)

        # Confirm that the PC is aligned at a multiple of 4
        if self.regfile[PC_REG_INDEX] & 0b11:
            raise AlignmentError(f"Progra mcounter is misaligned! - " \
                                 f"PC: {self.regfile[PC_REG_INDEX]}")
        
        if self.regfile[PC_REG_INDEX] == prev_pc:
            self.regfile[PC_REG_INDEX] += INST_ALIGN
        self.cycle += 1

    def dump_state(self):
        """
        Return current state as a dict for testing.
        """
        return {
            "cycle": self.cycle,
            "pc": self.regfile[PC_REG_INDEX],
            "regs": dict(self.regfile),  # copy
        }

    def run(self, memory, max_cycles=1000):
        """
        Run until max_cycles or halt condition detected
        """
        for _ in range(max_cycles):
            prev_pc = self.regfile[PC_REG_INDEX]
            self.next_cycle(memory)
            if self.regfile[PC_REG_INDEX] == prev_pc:
                break
