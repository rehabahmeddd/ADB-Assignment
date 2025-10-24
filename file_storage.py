from typing import Tuple, List
from block import Block
from record import Record

class FileStorage:
    def __init__(self):
        self.blocks: List[Block] = []

    def allocate_block(self) -> Block:
        b = Block(len(self.blocks))
        self.blocks.append(b)
        return b

    def insert_record(self, rec: Record) -> Tuple[int, int]:
        for b in self.blocks:
            if b.has_free_slot():
                slot = b.insert_record(rec)
                return (b.block_id, slot)
        b = self.allocate_block()
        slot = b.insert_record(rec)
        return (b.block_id, slot)

    def read_pointer(self, ptr: Tuple[int, int]):
        bid, slot = ptr
        if bid < 0 or bid >= len(self.blocks):
            return None
        return self.blocks[bid].read_slot(slot)

    def print_blocks(self):
        print("\n===== FILE STORAGE BLOCKS =====")
        for block in self.blocks:
            print(f"\nBlock ID: {block.block_id}")
            records = block.dump()
            if not records:
                print("  [Empty]")
            else:
                for i, rec in enumerate(records):
                   if rec: print(f"  Slot {i}: {rec.name}, SSN={rec.ssn}, Dept={rec.departmentcode}, Salary={rec.salary}")
        print("================================\n")