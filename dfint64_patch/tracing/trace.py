from capstone import CS_ARCH_X86, CS_MODE_64, Cs
from collections import defaultdict

MAX_INSTRUCTION_SIZE = 15


class Tracer:
    code: bytes
    base_address: int
    index: int = 0
    cs: Cs
    registers: dict[int, int]

    def __init__(self, code: bytes, base_address: int) -> None:
        self.code = code
        self.base_address = base_address
        self.cs = Cs(arch=CS_ARCH_X86, mode=CS_MODE_64)
        self.cs.detail = True
        self.registers = defaultdict(int)

    def next(self):
        instruction = next(
            self.cs.disasm(
                self.code[self.index : self.index + MAX_INSTRUCTION_SIZE],
                self.base_address + self.index,
            )
        )
        self.index += instruction.size
        return instruction
