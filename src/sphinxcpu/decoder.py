import enum

from dataclasses import dataclass
from .utils import register_names

REG_DICT = { i: reg for i, reg in enumerate(register_names()) }

class DecodeError(Exception):
    pass

@dataclass
class RVInst:
    name: str
    opcode: int

    def __str__(self):
        # Ignore the opcode for now.
        return self.name

@dataclass
class RType(RVInst):
    rd: int
    funct3: int
    rs1: int
    rs2: int
    funct7: int

    def __str__(self):
        return super(RType,self).__str__() + f",rd:{bin(self.rd)},"\
            f"funct3:{bin(self.funct3)},rs1:{bin(self.rs1)},"\
            f"rs2:{bin(self.rs2)},funct7:{bin(self.funct7)}"

@dataclass
class IType(RVInst):
    imm: int
    rd: int
    funct3: int
    rs1: int

    def __str__(self):
        return super(IType, self).__str__() + \
            f",imm:{bin(self.imm)},rd:{REG_DICT[self.rd]}," \
            f"funct3:{bin(self.funct3)},rs1:{REG_DICT[self.rs1]}"

@dataclass
class SType(RVInst):
    imm: int
    funct3: int
    rs1: int
    rs2: int

    def __str__(self):
        return super(SType, self).__str__() + \
            f",imm:{bin(self.imm)},funct3:{bin(self.funct3)}," \
            f"rs1:{REG_DICT[self.rs1]},rs2:{REG_DICT[self.rs2]}"

@dataclass
class BType(RVInst):
    imm: int
    funct3: int
    rs1: int
    rs2: int

    def __str__(self):
        return super(BType, self).__str__() + \
            f",imm:{bin(self.imm)},funct3:{bin(self.funct3)}," \
            f"rs1:{REG_DICT[self.rs1]},rs2:{REG_DICT[self.rs2]}"

@dataclass
class UType(RVInst):
    imm: int
    rd: int

    def __str__(self):
        return super(UType, self).__str__() + \
            f",rd:{REG_DICT[self.rd]},imm:{bin(self.imm)}"

@dataclass
class JType(RVInst):
    imm: int
    rd: int

    def __str__(self):
        return super(JType, self).__str__() + \
            f",rd:{REG_DICT[self.rd]},imm:{hex(self.imm)}"

class Opcode(enum.IntEnum):
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

class Funct3(enum.IntEnum):
    JALR = BEQ = LB = SB = ADDI = ADD = SUB = FENCE = ECALL = EBREAK = 0b000
    BNE = LH = SH = SLLI = SLL = FENCE_I = CSRRW = 0b001
    BLT = LBU = XORI = XOR = 0b100
    BGE = LHU = SRLI = SRAI = SRL = SRA = CSRRWI = 0b101
    BLTU = ORI = OR = CSRRSI = 0b110
    BGEU = ANDI = AND = CSRRCI = 0b111
    LW = SW = SLTI = SLT = CSRRS = 0b010
    SLTIU = SLTU = CSRRC = 0b011

class Funct7(enum.IntEnum):
    SLLI = SRLI = ADD = SLL = SLT = SLTU = XOR = SRL = OR = AND = 0b0000000
    SRAI = SUB = SRA = 0b0100000

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
                       (((inst >> 21) & 0x3FF) << 1))

def btype_imm(inst: int) -> int:
    """
    Decodes B-type immediates.

    Args:
        inst(int): Word-length instruction in bytes.
    Returns:
        int: B-type immediate value.
    """
    b_imm1 = (inst >> 12) & 0xFFFFFF
    b_imm2 = (inst >> 25) & 0b1111111
    return sign_extend(((b_imm2 >> 5) << 12) |
                       ((b_imm1 & 0b1) << 11) |
                       ((b_imm2 & 0b111111) << 5) |
                       ((b_imm1 >> 1) << 1))

def itype_imm(inst: int) -> int:
    """
    Decodes an I-type immediate value.

    Args:
       inst(int): Word-length instruction in bytes.

    Returns:
       int: I-type immediate value.
    """
    return sign_extend((inst >> 20) & 0xFFF)

def stype_imm(inst: int) -> int:
    """
    Decodes an S-type immediate value.

    Args:
       inst(int): Word-length instruction in bytes.

    Returns:
       int: S-type immediate value.
    """
    return sign_extend((((inst >> 25) & 0b1111111) << 5) |
                       ((inst >> 7) & 0b11111))

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
    inst_type = name = None

    if opcode == Opcode.LUI:
        inst_type = UType
        name = "LUI"
    elif opcode == Opcode.AUIPC:
        inst_type = UType
        name = "AUIPC"
    elif opcode == Opcode.JAL:
        inst_type = JType
        name = "JAL"
    elif opcode == Opcode.JALR:
        inst_type = IType
        name = "JALR"
    elif opcode == Opcode.BRANCH:
        inst_type = BType
        if funct3 == Funct3.BEQ:
            name = "BEQ"
        elif funct3 == Funct3.BNE:
            name = "BNE"
        elif funct3 == Funct3.BLT:
            name = "BLT"
        elif funct3 == Funct3.BGE:
            name = "BGE"
        elif funct3 == Funct3.BLTU:
            name = "BLTU"
        elif funct3 == Funct3.BGEU:
            name = "BGEU"
        else:
            raise DecodeError("Invalid branch instruction!")
    elif opcode == Opcode.LOAD:
        inst_type = IType
        if funct3 == Funct3.LB:
            name = "LB"
        elif funct3 == Funct3.LH:
            name = "LH"
        elif funct3 == Funct3.LW:
            name = "LW"
        elif funct3 == Funct3.LBU:
            name = "LBU"
        elif funct3 == Funct3.LHU:
            name = "LHU"
        else:
            raise DecodeError("Invalid load instruction!")
    elif opcode == Opcode.STORE:
        inst_type = SType
        if funct3 == Funct3.SB:
            name = "SB"
        elif funct3 == Funct3.SH:
            name = "SH"
        elif funct3 == Funct3.SW:
            name = "SW"
        else:
            raise DecodeError("Invalid store instruction!")
    elif opcode == Opcode.IMMEDIATE:
        inst_type = IType
        if funct3 == Funct3.ADDI:
            name = "ADDI"
        elif funct3 == Funct3.SLTI:
            name = "SLTI"
        elif funct3 == Funct3.SLTIU:
            name = "SLTIU"
        elif funct3 == Funct3.XORI:
            name = "XORI"
        elif funct3 == Funct3.ORI:
            name = "ORI"
        elif funct3 == Funct3.ANDI:
            name = "ANDI"
        elif funct3 == Funct3.SLLI:
            name = "SLLI"
        elif funct3 == Funct3.SRLI:
            if funct7 == Funct7.SRLI:
                name = "SRLI"
            elif funct7 == Funct7.SRAI:
                name = "SRAI"
            else:
                raise DecodeError("Invalid funct7!")
        else:
            raise DecodeError("Invalid funct3!")
    elif opcode == Opcode.ARITHMETIC:
        inst_type = RType
        name = "ARITH"
        if funct3 == Funct3.ADD:
            if funct7 == Funct7.ADD:
                name = "ADD"
            elif funct7 == Funct7.SUB:
                name = "SUB"
        elif funct3 == Funct3.SLL:
            name = "SLL"
        elif funct3 == Funct3.SLT:
            name = "SLT"
        elif funct3 == Funct3.SLTU:
            name = "SLTU"
        elif funct3 == Funct3.XOR:
            name = "XOR"
        elif funct3 == Funct3.SRL:
            if funct7 == Funct7.SRL:
                name = "SRL"
            elif funct7 == Funct7.SRA:
                name = "SRA"
        elif funct3 == Funct3.OR:
            name = "OR"
        elif funct3 == Funct3.AND:
            name = "AND"
        else:
            raise DecodeError("Invalid arithmetic instruction!")
    elif opcode == Opcode.FENCES:
        inst_type = IType
        if funct3 == Funct3.FENCE:
            name = "FENCE"
        elif funct3 == Funct3.FENCE_I:
            name = "FENCE.I"
        else:
            raise DecodeError("Invalid fence instruction!")
    elif opcode == Opcode.SYSTEM:
        # System instructions also differ from the
        # pre-defined types.
        inst_type = IType
        if funct3 == Funct3.ECALL:
            # ECALL and EBREAK have the same funct3.
            # Use funct7 to select.
            if funct7 == Funct7.ECALL:
                name = "ECALL"
            elif funct7 == Funct7.EBREAK:
                name = "EBREAK"
            else:
                raise DecodeError("Invalid environment instruction!")
        elif funct3 == Funct3.CSRRW:
            name = "CSRRW"
        elif funct3 == Funct3.CSRRS:
            name = "CSRRS"
        elif funct3 == Funct3.CSRRC:
            name = "CSRRC"
        elif funct3 == Funct3.CSRRWI:
            name = "CSRRWI"
        elif funct3 == Funct3.CSRRSI:
            name = "CSRRSI"
        elif funct3 == Funct3.CSRRCI:
            name = "CSRRCI"
        else:
            raise DecodeError("Invalid system instruction!")        
    else:
        raise DecodeError("Invalid opcode!")

    if inst_type == RType:
        return RType(name=name, opcode=opcode, rd=rd, funct3=funct3,
                     rs1=rs1, rs2=rs2, funct7=funct7)
    elif inst_type == IType:
        return IType(name=name, opcode=opcode, imm=itype_imm(inst),
                     rd=rd, funct3=funct3, rs1=rs1)
    elif inst_type == SType:
        return SType(name=name, opcode=opcode, imm=stype_imm(inst),
                     funct3=funct3, rs1=rs1, rs2=rs2)
    elif inst_type == BType:
        return BType(name=name, opcode=opcode, imm=btype_imm(inst),
                     funct3=funct3, rs1=rs1, rs2=rs2)
    elif inst_type == UType:
        return UType(name=name, opcode=opcode, imm=utype_imm(inst), rd=rd)
    elif inst_type == JType:
        return JType(name=name, opcode=opcode, imm=jtype_imm(inst), rd=rd)
    else:
        raise DecodeError("A serious error occurred.")
