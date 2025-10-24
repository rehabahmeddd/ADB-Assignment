
from typing import List, Optional
from record import Record, RECORD_SIZE

BLOCK_SIZE = 512
RECORDS_PER_BLOCK = BLOCK_SIZE // RECORD_SIZE

class Block:
    def __init__(self, block_id: int):
        self.block_id = block_id
        self.slots: List[Optional[bytes]] = [None] * RECORDS_PER_BLOCK

    def has_free_slot(self) -> bool:
        return any(slot is None for slot in self.slots)

    def insert_record(self, rec: Record) -> Optional[int]:
        for i, s in enumerate(self.slots):
            if s is None:
                self.slots[i] = rec.pack()
                return i
        return None

    def delete_slot(self, index: int):
        self.slots[index] = None

    def read_slot(self, index: int) -> Optional[Record]:
        data = self.slots[index]
        return Record.unpack(data) if data else None

    def dump(self):
        return [Record.unpack(s) if s else None for s in self.slots]

    def __repr__(self):
        used = sum(1 for s in self.slots if s is not None)
        return f"Block(id={self.block_id}, used={used}/{len(self.slots)})"