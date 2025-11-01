from csv_loader import CSVLoader
from file_storage import FileStorage
from bplustree import BPlusTree
import os # Added for animation

if __name__ == "__main__":
    
    # --- Ensure the 'frames' directory exists ---
    if not os.path.exists("frames"):
        os.makedirs("frames")
        
    records = CSVLoader.load_records("EMPLOYEE.csv")

    storage = FileStorage()
    tree = BPlusTree()

    # Step 1: Insert first 10 records
    print("\n--- Inserting first 10 records... ---")
    for rec in records[:10]:
        addr = storage.insert_record(rec)
        tree.insert(rec.ssn, addr, animate=False) # Explicitly set animate=False

    print("\nInitial File Blocks:")
    storage.print_blocks()

    print("\nInitial B+ Tree:")
    tree.print_tree()
    tree.visualize("initial_tree", view=False) # Added view=False


    # line 2 is record[0] , line 27 is record[25]



    

    print("\n--- Animating insertion of record 27... ---")
    i = 26 # Record 27 (idx 26)
    rec = records[i - 1]
    addr = storage.insert_record(rec)
    tree.insert(rec.ssn, addr, animate=True) # <-- SETTING THIS TO TRUE
    print("--- Animation complete! ---")

    print("\n--- Animating insertion of record 14... ---")
    i = 13 # Record 14 (idx 13)
    rec = records[i - 1]
    addr = storage.insert_record(rec)
    tree.insert(rec.ssn, addr, animate=True) # <-- SETTING THIS TO TRUE
    print("--- Animation complete! ---")

    # *** NOW, ANIMATE THE INSERTION OF RECORD 22 ***
    print("\n--- Animating insertion of record 22... ---")
    i = 21 # Record 22 (idx 21)
    rec = records[i - 1]
    addr = storage.insert_record(rec)
    tree.insert(rec.ssn, addr, animate=True) # <-- SETTING THIS TO TRUE
    print("--- Animation complete! ---")


    print("\nAfter Insertions (27, 14, 22):")
    tree.print_tree()
    tree.visualize("tree_after_insertions", view=False) # Added view=False

    # # Step 3: Delete records 11, 6, 3
    print("\n--- Deleting records 11, 6, 3... ---")
    for i in [10, 5, 2]: # Records 11 (idx 10), 6 (idx 5), 3 (idx 2)
        rec = records[i - 1]
        ssn = rec.ssn
        
        ptr = storage.find_pointer_by_ssn(ssn)
        if ptr:
            storage.delete_record(ptr)
            print(f"Marked Record SSN={ssn} deleted in Block {ptr[0]}, Slot {ptr[1]}")
        else:
            print(f"Pointer for SSN={ssn} not found in blocks (may not be inserted)")

        tree.delete(ssn)
        # tree.visualize(f"tree_after_deletions{i}", view=False)
        
    # Moved visualization outside the loop to capture the final state
    print("\nAfter Deletions (11, 6, 3):")
    tree.print_tree()
    tree.visualize("tree_after_deletions", view=False)
    

    print("\nFinal File Blocks:")
    storage.print_blocks()
    storage.visualize_file_blocks()
