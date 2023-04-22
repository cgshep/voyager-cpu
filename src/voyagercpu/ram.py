class VoyagerRAM:
    DEFAULT_RAM_SIZE = 0x1000

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
