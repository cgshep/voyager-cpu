from dataclasses import dataclass
from enum import IntEnum, Enum, unique

from utils import register_names

REG_DICT = { i: reg for i, reg in enumerate(register_names()) }

@unique
class Instruction(str, Enum):
    LUI = "LUI"
    AUIPC = "AUIPC"
    JAL = "JAL"
    JALR = "JALR"
    BEQ = "BEQ"
    BNE = "BNE"
    BLT = "BLT"
    BGE = "BGE"
    BLTU = "BLTU"
    BGEU = "BGEU"
    LB = "LB"
    LH = "LH"
    LW = "LW"
    LBU = "LBU"
    LHU = "LHU"
    SB = "SB"
    SH = "SH"
    SW = "SW"
    ADDI = "ADDI"
    SLTI = "SLTI"
    SLTIU = "SLTIU"
    XORI = "XORI"
    ORI = "ORI"
    ANDI = "ANDI"
    SLLI = "SLLI"
    SRLI = "SRLI"
    SRAI = "SRAI"
    ADD = "ADD"
    SUB = "SUB"
    SLL = "SLL"
    SLT = "SLT"
    SLTU = "SLTU"
    XOR = "XOR"
    SRL = "SRL"
    SRA = "SRA"
    OR = "OR"
    AND = "AND"
    FENCE = "FENCE"
    FENCE_I = "FENCE_I"
    ECALL = "ECALL"
    EBREAK = "EBREAK"
    CSRRW = "CSRRW"
    CSRRS = "CSRRS"
    CSRRC = "CSRRC"
    CSRRWI = "CSRRWI"
    CSRRSI = "CSRRSI"
    CSRRCI = "CSRRCI"


class DecodeError(Exception):
    pass


@dataclass
class RVInst:
    mnemonic: str
    opcode: int

    def __str__(self):
        # Ignore the opcode for now.
        return self.mnemonic


@dataclass
class RType(RVInst):
    rd: int
    funct3: int
    rs1: int
    rs2: int
    funct7: int

    def __str__(self):
        return super(RType,self).__str__() + f",rd:{hex(self.rd)},"\
            f"rs1:{hex(self.rs1)},rs2:{hex(self.rs2)}"


@dataclass
class IType(RVInst):
    imm: int
    rd: int
    funct3: int
    rs1: int

    def __str__(self):
        return super(IType, self).__str__() + \
            f",rd:{REG_DICT[self.rd]},rs1:{REG_DICT[self.rs1]}," \
            f"imm:{hex(self.imm)}"

@dataclass
class SType(RVInst):
    imm: int
    funct3: int
    rs1: int
    rs2: int

    def __str__(self):
        return super(SType, self).__str__() + \
            f",imm:{hex(self.imm)},funct3:{hex(self.funct3)}," \
            f"rs1:{REG_DICT[self.rs1]},rs2:{REG_DICT[self.rs2]}"

@dataclass
class BType(RVInst):
    imm: int
    funct3: int
    rs1: int
    rs2: int

    def __str__(self):
        return super(BType, self).__str__() + \
            f",rs1:{REG_DICT[self.rs1]},rs2:{REG_DICT[self.rs2]}," \
            f"imm:{hex(self.imm)}"
    
@dataclass
class UType(RVInst):
    imm: int
    rd: int

    def __str__(self):
        return super(UType, self).__str__() + \
            f",rd:{REG_DICT[self.rd]},imm:{hex(self.imm)}"

@dataclass
class JType(RVInst):
    imm: int
    rd: int

    def __str__(self):
        return super(JType, self).__str__() + \
            f",rd:{REG_DICT[self.rd]},imm:{hex(self.imm)}"

@unique
class Opcode(IntEnum):
    # These instructions are identified using only
    # the opcode field
    LUI      = 0b0110111
    AUIPC    = 0b0010111
    JAL      = 0b1101111
    JALR     = 0b1100111
    #
    # Branch instructions:
    # BEQ, BNE, BLT, BGE, BLTU, BGEU
    #
    BRANCH =  0b1100011
    #
    # Load instructions:
    # LB, LH, LW, LBU, LHU
    #
    LOAD = 0b0000011
    #
    # Store instructions:
    # SB, SH, SW
    STORE = 0b0100011
    #
    # Immediate instructions:
    # ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI
    #
    IMMEDIATE = 0b0010011
    #
    # Arithmetic/logical instructions:
    # ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND
    #
    ARITHMETIC = 0b0110011
    #
    # Fence instructions:
    # FENCE, FENCE.I
    #
    FENCES = 0b0001111
    #
    # System instructions:
    # ECALL, EBREAK, CSRRW, CSRRS, CSRRC, CSRRWI, CSRRSI, CSRRCI
    #
    SYSTEM = 0b1110011


class Funct3(IntEnum):
    JALR = BEQ = LB = SB = ADDI = ADD = SUB = FENCE = ECALL = EBREAK = 0b000
    BNE = LH = SH = SLLI = SLL = FENCE_I = CSRRW = 0b001
    BLT = LBU = XORI = XOR = 0b100
    BGE = LHU = SRLI = SRAI = SRL = SRA = CSRRWI = 0b101
    BLTU = ORI = OR = CSRRSI = 0b110
    BGEU = ANDI = AND = CSRRCI = 0b111
    LW = SW = SLTI = SLT = CSRRS = 0b010
    SLTIU = SLTU = CSRRC = 0b011


class Funct7(IntEnum):
    SLLI = SRLI = ADD = SLL = SLT = SLTU = XOR = SRL = OR = AND = 0b0000000
    SRAI = SUB = SRA = 0b0100000

def nop_inst() -> RVInst:
    """
    Returns a NOP instruction.

    Returns:
        RVInst: IType instruction of `addi x0, x0, 0`.
    """
    return IType(mnemonic=Instruction.ADDI, opcode=0b0010011,
                 imm=0, rd=0, funct3=0, rs1=0)

def jtype_imm(inst: int) -> int:
    """
    Decodes J-type immediates.

    Args:
        inst(int): Word-length instruction in bytes.
    Returns:
        int: J-type immediate value.
    """
    return sign_extend((((inst >> 31) & 0b1) << 20) |
                       (((inst >> 12) & 0b11111111) << 12) |
                       (((inst >> 20) & 0b1) << 11) |
                       (((inst >> 21) & 0x3FF) << 1), 20)

def btype_imm(inst: int, signed=True) -> int:
    """
    Decodes B-type immediates.

    Args:
        inst(int): Word-length instruction in bytes.
    Returns:
        int: B-type immediate value.
    """
    b_imm1 = (inst >> 7) & 0b11111
    b_imm2 = (inst >> 25) & 0b1111111
    x = ((b_imm2 >> 5) << 12) | \
        ((b_imm1 & 0b1) << 11) | \
        ((b_imm2 & 0b111111) << 5) | \
        ((b_imm1 >> 1) << 1)

    return sign_extend(x, 12) if signed else x
    
def itype_imm(inst: int, signed=True) -> int:
    """
    Decodes an I-type immediate value.

    Args:
       inst(int): Word-length instruction in bytes.

    Returns:
       int: I-type immediate value.
    """
    x = (inst >> 20) & 0xFFF
    return sign_extend(x, 12) if signed else x

def stype_imm(inst: int) -> int:
    """
    Decodes an S-type immediate value.

    Args:
       inst(int): Word-length instruction in bytes.

    Returns:
       int: S-type immediate value.
    """
    return sign_extend((((inst >> 25) & 0b1111111) << 5) |
                       ((inst >> 7) & 0b11111), 12)

def utype_imm(inst: int) -> int:
    """
    Decodes an U-type immediate value.

    Args:
       inst(int): Word-length instruction in bytes.

    Returns:
       int: U-type immediate value.
    """
    return sign_extend(((inst >> 12) & 0xFFFFFF) << 12)

def sign_extend(val: int, bit_len: int=32) -> int:
    """
    Sign-extends a value to a given extension
    bit length (default = 32 bits).

    Args:
        val(int): Value to extend.
        bit_len(int): Extension length.
    
    Returns:
        int: Sign-extended value.
    """
    sign_bit = 1 << (bit_len - 1)
    return (val & (sign_bit - 1)) - (val & sign_bit)
    
def decode_instruction(inst: int) -> RVInst:
    """
    Decodes a RV32I instruction.

    RISC-V instructions contain their opcode in the lower 7 bits. 
    In the specs, one or more logical instructions are mapped to 
    the same opcode. The funct3 field acts as a selector for R-, 
    I-, S-, and B-type instructions. For R-type instructions, 
    the funct7 field selects instructions with the same opcode 
    and funct3, e.g. add and sub instructions.
        
    Args:
        inst(int): Instruction as an integer.

    Returns:
        RVInst: RISC-V instruction data type.
    """
    opcode = inst & 0b1111111
    funct3 = (inst >> 12) & 0b111
    funct7 = (inst >> 25) & 0b1111111
    rd = (inst >> 7) & 0b11111
    rs1 = (inst >> 15) & 0b11111
    rs2 = (inst >> 20) & 0b11111
    inst_type = mnemonic = None
    imm_signed = True

    if opcode == Opcode.LUI:
        inst_type = UType
        mnemonic = Instruction.LUI
    elif opcode == Opcode.AUIPC:
        inst_type = UType
        mnemonic = Instruction.AUIPC
    elif opcode == Opcode.JAL:
        inst_type = JType
        mnemonic = Instruction.JAL
    elif opcode == Opcode.JALR:
        inst_type = IType
        mnemonic = Instruction.JALR
    elif opcode == Opcode.BRANCH:
        inst_type = BType
        if funct3 == Funct3.BEQ:
            mnemonic = Instruction.BEQ
        elif funct3 == Funct3.BNE:
            mnemonic = Instruction.BNE
        elif funct3 == Funct3.BLT:
            mnemonic = Instruction.BLT
        elif funct3 == Funct3.BGE:
            mnemonic = Instruction.BGE
        elif funct3 == Funct3.BLTU:
            mnemonic = Instruction.BLTU
            imm_signed = False
        elif funct3 == Funct3.BGEU:
            mnemonic = Instruction.BGEU
            imm_signed = False
        else:
            raise DecodeError("Invalid branch instruction!")
    elif opcode == Opcode.LOAD:
        inst_type = IType
        if funct3 == Funct3.LB:
            mnemonic = Instruction.LB
        elif funct3 == Funct3.LH:
            mnemonic = Instruction.LH
        elif funct3 == Funct3.LW:
            mnemonic = Instruction.LW
        elif funct3 == Funct3.LBU:
            mnemonic = Instruction.LBU
            imm_signed = False
        elif funct3 == Funct3.LHU:
            mnemonic = Instruction.LHU
            imm_signed = False
        else:
            raise DecodeError("Invalid load instruction!")
    elif opcode == Opcode.STORE:
        inst_type = SType
        if funct3 == Funct3.SB:
            mnemonic = Instruction.SB
        elif funct3 == Funct3.SH:
            mnemonic = Instruction.SH
        elif funct3 == Funct3.SW:
            mnemonic = Instruction.SW
        else:
            raise DecodeError("Invalid store instruction!")
    elif opcode == Opcode.IMMEDIATE:
        inst_type = IType
        if funct3 == Funct3.ADDI:
            mnemonic = Instruction.ADDI
        elif funct3 == Funct3.SLTI:
            mnemonic = Instruction.SLTI
        elif funct3 == Funct3.SLTIU:
            mnemonic = Instruction.SLTIU
            imm_signed = False
        elif funct3 == Funct3.XORI:
            mnemonic = Instruction.XORI
        elif funct3 == Funct3.ORI:
            mnemonic = Instruction.ORI
        elif funct3 == Funct3.ANDI:
            mnemonic = Instruction.ANDI
        elif funct3 == Funct3.SLLI:
            mnemonic = Instruction.SLLI
        elif funct3 == Funct3.SRLI:
            if funct7 == Funct7.SRLI:
                mnemonic = Instruction.SRLI
            elif funct7 == Funct7.SRAI:
                mnemonic = Instruction.SRAI
            else:
                raise DecodeError("Invalid funct7!")
        else:
            raise DecodeError("Invalid funct3!")
    elif opcode == Opcode.ARITHMETIC:
        inst_type = RType
        if funct3 == Funct3.ADD:
            if funct7 == Funct7.ADD:
                mnemonic = Instruction.ADD
            elif funct7 == Funct7.SUB:
                mnemonic = Instruction.SUB
        elif funct3 == Funct3.SLL:
            mnemonic = Instruction.SLL
        elif funct3 == Funct3.SLT:
            mnemonic = Instruction.SLT
        elif funct3 == Funct3.SLTU:
            mnemonic = Instruction.SLTU
        elif funct3 == Funct3.XOR:
            mnemonic = Instruction.XOR
        elif funct3 == Funct3.SRL:
            if funct7 == Funct7.SRL:
                mnemonic = Instruction.SRL
            elif funct7 == Funct7.SRA:
                mnemonic = Instruction.SRA
        elif funct3 == Funct3.OR:
            mnemonic = Instruction.OR
        elif funct3 == Funct3.AND:
            mnemonic = Instruction.AND
        else:
            raise DecodeError("Invalid arithmetic instruction!")
    elif opcode == Opcode.FENCES:
        inst_type = IType
        if funct3 == Funct3.FENCE:
            mnemonic = Instruction.FENCE
        elif funct3 == Funct3.FENCE_I:
            mnemonic = Instruction.FENCE.I
        else:
            raise DecodeError("Invalid fence instruction!")
    elif opcode == Opcode.SYSTEM:
        # System instructions also differ from the
        # pre-defined types.
        inst_type = IType

        if funct3 == Funct3.ECALL:
            # ECALL and EBREAK have the same funct3.
            # Bits [20:31] are used to differentiate them,
            # as 0 == ECALL and 1 == EBREAK. We can get
            # this from rs2 calculated earlier
            if rs2 == 0:
                mnemonic = Instruction.ECALL
            elif rs2 == 1:
                mnemonic = Instruction.EBREAK
            else:
                raise DecodeError("Invalid environment instruction!")
        elif funct3 == Funct3.CSRRW:
            mnemonic = Instruction.CSRRW
        elif funct3 == Funct3.CSRRS:
            mnemonic = Instruction.CSRRS
        elif funct3 == Funct3.CSRRC:
            mnemonic = Instruction.CSRRC
        elif funct3 == Funct3.CSRRWI:
            mnemonic = Instruction.CSRRWI
        elif funct3 == Funct3.CSRRSI:
            mnemonic = Instruction.CSRRSI
        elif funct3 == Funct3.CSRRCI:
            mnemonic = Instruction.CSRRCI
        else:
            raise DecodeError("Invalid system instruction!")        
    else:
        raise DecodeError("Invalid opcode!")

    if inst_type == RType:
        return RType(mnemonic=mnemonic, opcode=opcode, rd=rd,
                     funct3=funct3, rs1=rs1, rs2=rs2, funct7=funct7)
    elif inst_type == IType:
        return IType(mnemonic=mnemonic, opcode=opcode,
                     imm=itype_imm(inst, signed=imm_signed),
                     rd=rd, funct3=funct3, rs1=rs1)
    elif inst_type == SType:
        return SType(mnemonic=mnemonic, opcode=opcode, imm=stype_imm(inst),
                     funct3=funct3, rs1=rs1, rs2=rs2)
    elif inst_type == BType:
        return BType(mnemonic=mnemonic, opcode=opcode,
                     imm=btype_imm(inst, signed=imm_signed),
                     funct3=funct3, rs1=rs1, rs2=rs2)
    elif inst_type == UType:
        return UType(mnemonic=mnemonic, opcode=opcode, imm=utype_imm(inst), rd=rd)
    elif inst_type == JType:
        return JType(mnemonic=mnemonic, opcode=opcode, imm=jtype_imm(inst), rd=rd)
    else:
        raise DecodeError("A serious error occurred.")
