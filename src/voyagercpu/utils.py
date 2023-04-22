import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def abi_register_names() -> list:
    """
    Returns a list of RISC-V ABI register names.

    Returns:
        list: List of ABI register names as strings.
    """
    return ["zero", "ra", "sp", "gp", "tp"] + \
        [f"t{i}" for i in range(3)] + \
        ["s0", "s1"] + \
        [f"a{i}" for i in range(8)] + \
        [f"s{i}" for i in range(2, 12)] + \
        [f"t{i}" for i in range(3, 7)] + ["pc"]

def register_names() -> list:
    """
    Returns a list of basic RISC-V register names.

    These have the form x0-31. Their ABI names 
    may be derived using `abi_register_names()`.

    Returns:
       list: List of register names as strings.
    """
    return [f"x{i}" for i in range(32)] + ["pc"]

def abi_register_name_dict() -> dict:
    """
    Creates a dict of standard registers and their ABI names, 
    e.g. ("x0" -> "zero"), ("x2" -> "sp") etc.
    """
    return { reg: abi for reg, abi in
             zip(register_names(), abi_register_names()) }

def int_to_hex_str(val: int,
                   endian: str="little",
                   prefix: str="0x") -> str:
    # Get the hex string of val and pad it with a leading
    # zero if its length isn't even
    val_hex_str = hex(val)[2:]
    if val_hex_str % 2 != 0:
        val_hex_str = "0" + val_hex_str

    if endian == "big":
        return prefix + val_hex_str
    elif endian == "little":
        return prefix + "".join(
            reversed([a[i:i+2] for i in range(0, len(a), 2)]))
    else:
        raise ValueError("Endian must be \"little\" or \"big\"!")
