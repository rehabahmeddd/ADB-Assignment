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

    #print("\nInitial B+ Tree:")
    #tree.print_tree()


    # line 2 is record[0] , line 27 is record[25]

    # # Step 2: Insert records 27, 14, 22
    for i in [26, 13, 21]:
        rec = records[i - 1]
        addr = storage.insert_record(rec)
        tree.insert(rec.ssn, addr)

    print("\nAfter Insertions (27, 14, 22):")
    tree.print_tree()

    # # Step 3: Delete records 11, 6, 3 (deletion logic to be added)
    # for i in [11, 6, 3]:
    #     ssn = records[i - 1].ssn
    #     tree.delete(ssn)

    # print("\nAfter Deletions (11, 6, 3):")
    # tree.print_tree()

    # print("\nFinal File Blocks:")
    # storage.print_blocks()
