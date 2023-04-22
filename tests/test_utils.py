import pytest

from voyagercpu.utils import *

def test_abi_register_name_dict():
    #See: https://riscv.org/wp-content/uploads/2017/05/riscv-spec-v2.2.pdf
    d = abi_register_name_dict()
    assert d["x0"] == "zero"
    assert d["x1"] == "ra"
    assert d["x4"] == "tp"
    assert d["x7"] == "t2"
    assert d["x10"] == "a0"
    assert d["x13"] == "a3"
    assert d["x17"] == "a7"
    assert d["x18"] == "s2"
    assert d["x27"] == "s11"
    assert d["x28"] == "t3"
    assert d["x31"] == "t6"
    assert d["pc"] == "pc"
