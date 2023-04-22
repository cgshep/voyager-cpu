import pytest

from voyagercpu.decoder import *

def test_decode_instruction_type():
    # jal x0, 72
    inst = decode_instruction(0x0480006f)
    assert type(inst) == JType
    assert inst.mnemonic == Instruction.JAL
    assert inst.imm == 72
    assert REG_DICT[inst.rd] == "x0"

    # jal x0, -8
    inst = decode_instruction(0xff9ff06f)
    assert type(inst) == JType
    assert inst.mnemonic == Instruction.JAL
    assert inst.imm == -8
    assert REG_DICT[inst.rd] == "x0"

    # addi x8, x0, 0
    inst = decode_instruction(0x00000413)
    assert type(inst) == IType
    assert inst.mnemonic == Instruction.ADDI
    assert inst.imm == 0
    assert REG_DICT[inst.rd] == "x8"
    assert REG_DICT[inst.rs1] == "x0"

    # addi x12, x0, 0
    inst = decode_instruction(0x00000613)
    assert type(inst) == IType
    assert inst.mnemonic == Instruction.ADDI
    assert inst.imm == 0
    assert REG_DICT[inst.rd] == "x12"
    assert REG_DICT[inst.rs1] == "x0"

    # addi x15, x0, 0
    inst = decode_instruction(0x00000793)
    assert type(inst) == IType
    assert inst.mnemonic == Instruction.ADDI
    assert inst.imm == 0
    assert REG_DICT[inst.rd] == "x15"
    assert REG_DICT[inst.rs1] == "x0"    

    # auipc x30, 4096
    inst = decode_instruction(0x00001f17)
    assert type(inst) == UType
    assert inst.mnemonic == Instruction.AUIPC
    assert inst.imm == 4096
    assert REG_DICT[inst.rd] == "x30"

    # auipc x10, -8192
    inst = decode_instruction(0xffffe517)
    assert type(inst) == UType
    assert inst.mnemonic == Instruction.AUIPC
    assert inst.imm == -8192
    assert REG_DICT[inst.rd] == "x10"

    # lui x7, 267390976
    inst = decode_instruction(0x0ff013b7)
    assert type(inst) == UType
    assert inst.mnemonic == Instruction.LUI
    assert inst.imm == 267390976
    assert REG_DICT[inst.rd] == "x7"

    # sw x3,-60(x30)
    inst = decode_instruction(0xfc3f2223)
    assert type(inst) == SType
    assert inst.mnemonic == Instruction.SW
    assert inst.imm == -60
    assert REG_DICT[inst.rs1] == "x30"
    assert REG_DICT[inst.rs2] == "x3"

    # sw x1,128(x21)
    inst = decode_instruction(0x081aa023)
    assert type(inst) == SType
    assert inst.mnemonic == Instruction.SW
    assert inst.imm == 128
    assert REG_DICT[inst.rs1] == "x21"
    assert REG_DICT[inst.rs2] == "x1"

    # csrrs x30,mcause,x0
    inst = decode_instruction(0x34202f73)
    assert type(inst) == IType
    assert inst.mnemonic == Instruction.CSRRS
    assert REG_DICT[inst.rd] == "x30"
    assert REG_DICT[inst.rs1] == "x0"

    # ori x3, x3, 1337
    inst = decode_instruction(0x5391e193)
    assert type(inst) == IType
    assert inst.mnemonic == Instruction.ORI
    assert inst.imm == 1337
    assert REG_DICT[inst.rd] == "x3"
    assert REG_DICT[inst.rs1] == "x3"

    # xori x5, x7, -247
    inst = decode_instruction(0xf093c293)
    assert type(inst) == IType
    assert inst.mnemonic == Instruction.XORI
    assert inst.imm == -247
    assert REG_DICT[inst.rd] == "x5"
    assert REG_DICT[inst.rs1] == "x7"

    # bne x10,x0, 0
    inst = decode_instruction(0x00051063)
    assert type(inst) == BType
    assert inst.mnemonic == Instruction.BNE
    assert inst.imm == 0
    assert REG_DICT[inst.rs1] == "x10"
    assert REG_DICT[inst.rs2] == "x0"

    # beq x0, x3, -32
    inst = decode_instruction(0xfe3000e3)
    assert type(inst) == BType
    assert inst.mnemonic == Instruction.BEQ
    assert inst.imm == -32
    assert REG_DICT[inst.rs1] == "x0"
    assert REG_DICT[inst.rs2] == "x3"

    # ecall
    inst = decode_instruction(0x00000073)
    assert type(inst) == IType
    assert inst.mnemonic == Instruction.ECALL

    # sub x2, x4, x5
    inst = decode_instruction(0x40520133)
    assert type(inst) == RType
    assert inst.mnemonic == Instruction.SUB
    assert REG_DICT[inst.rd] == "x2"
    assert REG_DICT[inst.rs1] == "x4"
    assert REG_DICT[inst.rs2] == "x5"
