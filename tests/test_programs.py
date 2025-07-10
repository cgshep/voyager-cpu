from voyagercpu.cpu import CPU
from voyagercpu.memory import Memory

def test_add_program():
    mem = Memory()
    # A simple binary program: adds 1+2 and stores in x3
    # Example: actual bytes you’d get from assembling RISC-V source
    program = [
        0x00200093,  # li x1,2
        0x00100113,  # li x2,1
        0x002081b3,  # add x3,x1,x2
        0x0000006f   # jump to self (halt)
    ]
    mem.load_program(program)
    cpu = CPU()
    cpu.run(mem)  # or step until halt
    state = cpu.dump_state()
    assert state['regs'][3] == 3


def test_sub_program():
    mem = Memory()
    program = [
        0x00500093,  # li x1,5
        0x00200113,  # li x2,2
        0x402081b3,  # sub x3,x1,x2
        0x0000006f   # halt
    ]
    mem.load_program(program)
    cpu = CPU()
    cpu.run(mem)
    state = cpu.dump_state()
    assert state['regs'][3] == 3


def test_or_program():
    mem = Memory()
    program = [
        0x00100093,  # li x1,1
        0x00200113,  # li x2,2
        0x0020e1b3,  # or x3,x1,x2
        0x0000006f   # halt
    ]
    mem.load_program(program)
    cpu = CPU()
    cpu.run(mem)
    state = cpu.dump_state()
    assert state['regs'][3] == 3


def test_beq_program():
    mem = Memory()
    program = [
        0x00100093,        # li x1,1
        0x00100113,        # li x2,1
        0x00208463,        # beq x1,x2,+4
        0x00000013,        # nop (skipped)
        0x00300193,        # li x3,3
        0x0000006f         # halt
    ]
    mem.load_program(program)
    cpu = CPU()
    cpu.run(mem)
    state = cpu.dump_state()
    assert state['regs'][3] == 3


def test_addi_program():
    mem = Memory()
    program = [
        0x00100093,  # li x1,1
        0x00208113,  # addi x2,x1,2
        0x0000006f   # halt
    ]
    mem.load_program(program)
    cpu = CPU()
    cpu.run(mem)
    state = cpu.dump_state()
    assert state['regs'][2] == 3


def test_loop_sum():
    mem = Memory()
    program = [
        0x00000093,       # li x1,0
        0x00100113,       # li x2,1
        0x00b00213,       # li x4,11
        0x002080b3,       # add x1,x1,x2
        0x00110113,       # addi x2,x2,1
        0xfe414ce3,       # BLT x2,x4,-8
        0x000081b3,       # add x3,x1,x0
        0x0000006f        # halt
    ]

    mem.load_program(program)
    cpu = CPU()
    cpu.run(mem, max_cycles=100)
    state = cpu.dump_state()
    assert state['regs'][3] == 55, \
        f"loop_sum_fixed: expected x3=55, got {state['regs'][3]}"


def test_slti_program():
    mem = Memory()
    program = [
        0x00100093,  # li x1,1
        0x0020a113,  # slti x2,x1,2
        0x0000006f   # halt
    ]
    mem.load_program(program)
    cpu = CPU()
    cpu.run(mem)
    state = cpu.dump_state()
    assert state['regs'][2] == 1
