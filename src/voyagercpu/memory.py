class Memory:
    DEFAULT_RAM_SIZE = 0x1000

    def __init__(self, ram_size=DEFAULT_RAM_SIZE):
        self.ram_size = ram_size
        self.ram = bytearray(ram_size)

    def __str__(self):
        ram_str = ""
        for i, data in enumerate(self.ram):
            if i % 8 == 0:
                ram_str += "\n"
            ram_str += f"0x{i:03X}: {data:02X}  "
        return ram_str

    def write(self, data: bytes, addr=0):
        self.ram[addr:addr+len(data)] = data

    def load_program(self, data, addr=0):
        """
        Loads a list of 32-bit ints into memory starting at `addr`
        """
        b = bytearray()
        for word in data:
            b += word.to_bytes(4, 'little')  # RISC-V = little-endian
        self.write(b, addr)

    def read(self, start_idx, length=1):
        return self.ram[start_idx:start_idx+length]

    def dump(self):
        print(self.__str__())
