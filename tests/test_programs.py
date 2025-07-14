from voyagercpu.cpu import CPU
from voyagercpu.memory import Memory


def run_program(program, max_cycles=1000):
    """
    Utility to load a program, run it, and return final CPU state.
    """
    mem = Memory()
    mem.load_program(program)

    cpu = CPU()
    cpu.run(mem, max_cycles=max_cycles)

    return cpu.dump_state()


def assert_reg(state, reg, expected):
    actual = state['regs'][reg]
    assert actual == expected, \
        f"Expected x{reg}={expected}, got {actual}"


def test_add_program():
    state = run_program([
        0x00200093,  # li x1,2
        0x00100113,  # li x2,1
        0x002081b3,  # add x3,x1,x2
        0x0000006f,
    ])
    assert_reg(state, 3, 3)


def test_sub_program():
    state = run_program([
        0x00500093,  # li x1,5
        0x00200113,  # li x2,2
        0x402081b3,  # sub x3,x1,x2
        0x0000006f,
    ])
    assert_reg(state, 3, 3)


def test_or_program():
    state = run_program([
        0x00100093,  # li x1,1
        0x00200113,  # li x2,2
        0x0020e1b3,  # or x3,x1,x2
        0x0000006f,
    ])
    assert_reg(state, 3, 3)


def test_beq_program():
    state = run_program([
        0x00100093,  # li x1,1
        0x00100113,  # li x2,1
        0x00208463,  # beq x1,x2,+4
        0x00000013,  # nop (skipped)
        0x00300193,  # li x3,3
        0x0000006f,
    ])
    assert_reg(state, 3, 3)


def test_addi_program():
    state = run_program([
        0x00100093,  # li x1,1
        0x00208113,  # addi x2,x1,2
        0x0000006f,
    ])
    assert_reg(state, 2, 3)


def test_loop_sum():
    program = [
        0x00000093,       # li x1,0
        0x00100113,       # li x2,1
        0x00b00213,       # li x4,11
        0x002080b3,       # add x1,x1,x2
        0x00110113,       # addi x2,x2,1
        0xfe414ce3,       # blt x2,x4,-8
        0x000081b3,       # add x3,x1,x0
        0x0000006f,
    ]
    state = run_program(program, max_cycles=100)
    assert_reg(state, 3, 55)  # sum in x3
    assert_reg(state, 2, 11)  # x2 final
    assert_reg(state, 1, 55)  # x1 final


def test_slti_program():
    state = run_program([
        0x00100093,  # li x1,1
        0x0020a113,  # slti x2,x1,2
        0x0000006f,
    ])
    assert_reg(state, 2, 1)
