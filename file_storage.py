from typing import Tuple, List
from block import Block
from record import Record

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

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
    
    def visualize_file_blocks(self):
        # --- Compute layout parameters ---
        n_blocks = len(self.blocks)
        slot_height = 0.4
        vertical_spacing = 1.0

        # Find max slot text width to auto-adjust figure width
        max_text_len = 0
        for block in self.blocks:
            for slot in block.dump():
                max_text_len = max(max_text_len, 500)
        fig_width = max(10, min(0.12 * max_text_len, 15))  # auto width scaling
        fig_height = max(3, n_blocks * 2.2)

        # --- Create Matplotlib figure ---
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        y_offset = fig_height - 1

        for block in self.blocks:
            block_id = block.block_id
            slots = block.dump()
            block_height = len(slots) * slot_height

            # Draw the block rectangle
            rect = patches.Rectangle(
                (0.1, y_offset - block_height),
                0.8,
                block_height,
                linewidth=1.5,
                edgecolor='black',
                facecolor='#E3F2FD'
            )
            ax.add_patch(rect)

            # Label block ID
            ax.text(0.5, y_offset + 0.2, f"Block ID: {block_id}",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

            # Draw slot lines and text
            for i, slot in enumerate(slots):
                slot_y = y_offset - (i + 1) * slot_height
                ax.plot([0.1, 0.9], [slot_y, slot_y], color='black', lw=1)
                ax.text(0.12, slot_y + slot_height / 2, f"Slot {i}: {slot}",
                        fontsize=9, va='center', ha='left', wrap=True)

            y_offset -= (block_height + vertical_spacing)

        ax.set_xlim(0, 1.1)
        ax.set_ylim(-1, fig_height + 1)
        ax.axis('off')
        plt.tight_layout()

        # --- Add scrollable window if figure too tall ---
        root = tk.Tk()
        root.title("File Blocks Visualization")

        canvas = tk.Canvas(root)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Embed the Matplotlib figure in the Tkinter frame
        fig_canvas = FigureCanvasTkAgg(fig, master=scroll_frame)
        fig_canvas.draw()
        fig_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Layout
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        root.mainloop()