from csv_loader import CSVLoader
from file_storage import FileStorage
from bplustree import BPlusTree

if __name__ == "__main__":
    records = CSVLoader.load_records("EMPLOYEE.csv")

    storage = FileStorage()
    tree = BPlusTree()

    # Step 1: Insert first 10 records
    for rec in records[:10]:
        addr = storage.insert_record(rec)
        tree.insert(rec.ssn, addr)

    print("\nInitial File Blocks:")
    storage.print_blocks()

    print("\nInitial B+ Tree:")
    tree.print_tree()


    # line 2 is record[0] , line 27 is record[25]

    # # Step 2: Insert records 27, 14, 22
    for i in [26, 13, 21]:
        rec = records[i - 1]
        addr = storage.insert_record(rec)
        tree.insert(rec.ssn, addr)

    print("\nAfter Insertions (27, 14, 22):")
    tree.print_tree()
    tree.visualize("tree before deletions.png")

    # # Step 3: Delete records 11, 6, 3 (deletion logic to be added)
    for i in [8, 6, 3,7,21,5,2]:
        rec = records[i - 1]
        ssn = rec.ssn
        # tree.delete(ssn) needs to remove key and pointer from tree
        # but we also must mark the block record as deleted in storage
        # find pointer using file storage helper
        ptr = storage.find_pointer_by_ssn(ssn)
        if ptr:
            storage.delete_record(ptr)
            print(f"Marked Record SSN={ssn} deleted in Block {ptr[0]}, Slot {ptr[1]}")
        else:
            print(f"Pointer for SSN={ssn} not found in blocks (may not be inserted)")

        tree.delete(ssn)
        

    print("\nAfter Deletions (8, 6, 3):")
    tree.print_tree()
    tree.visualize(f"bplustree_after_deletions{i}.png")
    

    print("\nFinal File Blocks:")
    storage.print_blocks()
