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
                   if rec: print(f"  Slot {i}: {rec.name}, SSN={rec.ssn}, deleted={rec.deleted}, Dept={rec.departmentcode}, Salary={rec.salary}")
        print("================================\n")
        
    def delete_record(self, ptr: Tuple[int, int]):
        """Mark the record referred by pointer as deleted."""
        bid, slot = ptr
        if bid < 0 or bid >= len(self.blocks):
            raise IndexError("Block id out of range")
        self.blocks[bid].delete_slot(slot)

    def find_pointer_by_ssn(self, ssn: str):
        """
        Linear scan to find a record by SSN and return pointer (block_id, slot).
        Useful for the deletion pipeline when the tree does not provide the pointer.
        """
        for blk in self.blocks:
            for idx, data in enumerate(blk.slots):
                if data is None:
                    continue
                rec = Block.read_slot(blk, idx)  # or blk.read_slot(idx)
                if rec and rec.ssn == ssn:
                    return (blk.block_id, idx)
        return None