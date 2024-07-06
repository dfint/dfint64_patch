from typing import NewType

Rva = NewType("Rva", int)  # relative virtual address
Offset = NewType("Offset", int)  # physical offset in a file

RVA0 = Rva(0)
