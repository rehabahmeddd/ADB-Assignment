from node import Node, LeafNode, InternalNode

class BPlusTree:
    def __init__(self, p_internal=3, p_leaf=2):
        self.p_internal = p_internal
        self.p_leaf = p_leaf
        self.root: Node = LeafNode()

    def find_leaf(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.child_pointers[i]
        return node

    def insert(self, key, pointer):
        leaf = self.find_leaf(key)
        i = 0
        while i < len(leaf.keys) and leaf.keys[i] < key:
            i += 1
        leaf.keys.insert(i, key)
        leaf.pointers.insert(i, pointer)

        if len(leaf.keys) > self.p_leaf:
            self.split_leaf(leaf)

    def split_leaf(self, leaf):
        total = len(leaf.keys)
        split = total // 2
        left, right = LeafNode(), LeafNode()

        left.keys = leaf.keys[:split]
        right.keys = leaf.keys[split:]
        left.pointers = leaf.pointers[:split]
        right.pointers = leaf.pointers[split:]

        # maintain linked list
        right.next = leaf.next
        left.next = right

        # connect to parent
        if leaf.parent is None:
            root = InternalNode()
            root.keys = [right.keys[0]]
            root.child_pointers = [left, right]
            left.parent = right.parent = root
            self.root = root
        else:
            parent = leaf.parent
            pos = parent.child_pointers.index(leaf)
            parent.child_pointers[pos] = left
            parent.child_pointers.insert(pos + 1, right)
            parent.keys.insert(pos, right.keys[0])
            left.parent = right.parent = parent

            if len(parent.child_pointers) > self.p_internal:
                self.split_internal(parent)

    def split_internal(self, node):
        total = len(node.keys)
        mid = total // 2

        left, right = InternalNode(), InternalNode()
        promoted = node.keys[mid]

        left.keys = node.keys[:mid]
        right.keys = node.keys[mid + 1:]

        left.child_pointers = node.child_pointers[:mid + 1]
        right.child_pointers = node.child_pointers[mid + 1:]

        for ch in left.child_pointers:
            ch.parent = left
        for ch in right.child_pointers:
            ch.parent = right

        if node.parent is None:
            root = InternalNode()
            root.keys = [promoted]
            root.child_pointers = [left, right]
            left.parent = right.parent = root
            self.root = root
        else:
            parent = node.parent
            pos = parent.child_pointers.index(node)
            parent.child_pointers[pos] = left
            parent.child_pointers.insert(pos + 1, right)
            parent.keys.insert(pos, promoted)
            left.parent = right.parent = parent

            if len(parent.child_pointers) > self.p_internal:
                self.split_internal(parent)

    def print_tree(self):
        print("\n===== B+ TREE STRUCTURE =====")

        def _print_node(node, level=0, prefix="Root"):
            indent = "  " * level
            node_type = "Leaf" if node.is_leaf else "Internal"
            print(f"{indent}{prefix} ({node_type}): {node.keys}")

            if node.is_leaf:
                for i, ptr in enumerate(node.pointers):
                    print(f"{indent}   ↳ Key={node.keys[i]}, Ptr={ptr}")
            else:
                for i, child in enumerate(node.child_pointers):
                    _print_node(child, level + 1, f"Child {i}")

        _print_node(self.root)

        # print leaf chain for validation
        print("==============================")
        print("\n-- Leaf Chain (in order) --")
        node = self.root
        while not node.is_leaf:
            node = node.child_pointers[0]

        chain = []
        while node:
            chain.append(f"{node.keys}")
            node = node.next

        print(" → ".join(chain))
        print("--------------------------------\n")
