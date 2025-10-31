from node import Node, LeafNode, InternalNode
from graphviz import Digraph

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


    def find_leaf_with_parent_info(self, key):
        """Return leaf and the path (list of (node, index_in_parent)) for convenience."""
        node = self.root
        path = []  # list of (node, index_in_parent) from root to node
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            # i is child index to follow
            path.append((node, i))
            node = node.child_pointers[i]
        return node, path

    def delete(self, key):
        leaf, path = self.find_leaf_with_parent_info(key)

        # 1) remove key from leaf if present
        if key not in leaf.keys:
            print(f"Warning: key {key} not found in index.")
            return

        idx = leaf.keys.index(key)
        # remove key and its pointer
        leaf.keys.pop(idx)
        leaf.pointers.pop(idx)
        
        # if root is leaf, handle trivial case
        if leaf is self.root:
            if len(leaf.keys) == 0:
                # Tree becomes empty -> keep an empty leaf as root
                self.root = LeafNode()
            return

        # check minimum keys for leaf
        min_keys_leaf = (self.p_leaf + 1) // 2  # ceil(pleaf/2)
        if len(leaf.keys) >= min_keys_leaf:
            # still enough keys, but must update parent separator if needed
            self._fix_parent_separators_after_leaf_change(leaf)
            return

        # Need to fix underflow in leaf.
        self._fix_leaf_underflow(leaf)

    # Helper: update parent separators if first key changed in a leaf
    def _fix_parent_separators_after_leaf_change(self, leaf):
        # When a leaf's smallest key changed, parent separator may need update.
        if leaf.parent is None:
            return
        parent = leaf.parent
        # find index of leaf in parent.child_pointers
        idx = parent.child_pointers.index(leaf)
        # separator key for child at idx is parent.keys[idx-1] (separates left and right)
        if idx > 0:
            left_key = parent.keys[idx - 1]
            # separator should equal leaf.keys[0] (smallest key of right child)
            if len(leaf.keys) > 0 and parent.keys[idx - 1] != leaf.keys[0]:
                parent.keys[idx - 1] = leaf.keys[0]

    def _fix_leaf_underflow(self, leaf):
        parent = leaf.parent
        if parent is None:
            return  # shouldn't happen (we handled root earlier)

        pos = parent.child_pointers.index(leaf)
        left = parent.child_pointers[pos - 1] if pos - 1 >= 0 else None
        right = parent.child_pointers[pos + 1] if pos + 1 < len(parent.child_pointers) else None

        min_keys_leaf = (self.p_leaf + 1) // 2

        # 1) Try borrow from left
        if left and len(left.keys) > min_keys_leaf:
            # borrow last key from left
            borrowed_key = left.keys.pop(-1)
            borrowed_ptr = left.pointers.pop(-1)
            leaf.keys.insert(0, borrowed_key)
            leaf.pointers.insert(0, borrowed_ptr)
            # update parent's separator between left and leaf
            parent.keys[pos - 1] = leaf.keys[0]
            return

        # 2) Try borrow from right
        if right and len(right.keys) > min_keys_leaf:
            # borrow first key from right
            borrowed_key = right.keys.pop(0)
            borrowed_ptr = right.pointers.pop(0)
            leaf.keys.append(borrowed_key)
            leaf.pointers.append(borrowed_ptr)
            # update parent's separator
            parent.keys[pos] = right.keys[0] if right.keys else parent.keys[pos]
            return

        # 3) Merge with sibling (prefer left if exists else right)
        if left:
            # merge left + leaf => left will hold all keys, remove leaf
            left.keys.extend(leaf.keys)
            left.pointers.extend(leaf.pointers)
            left.next = leaf.next
            # remove leaf from parent
            remove_index = pos
            parent.child_pointers.pop(remove_index)
            # parent separator at remove_index-1 must be removed
            parent.keys.pop(remove_index - 1)
            # check parent underflow
            self._fix_internal_after_delete(parent)
        elif right:
            # merge leaf + right => leaf will absorb right (we can choose to append right into leaf)
            leaf.keys.extend(right.keys)
            leaf.pointers.extend(right.pointers)
            leaf.next = right.next
            # remove right
            parent.child_pointers.pop(pos + 1)
            parent.keys.pop(pos)
            self._fix_internal_after_delete(parent)

    def _fix_internal_after_delete(self, node):
        # If node is root, special rules:
        if node is self.root:
            # If root has only one child and is an internal node -> shrink tree
            if not node.is_leaf and len(node.child_pointers) == 1:
                child = node.child_pointers[0]
                child.parent = None
                self.root = child
            return

        min_ptr = (self.p_internal + 1) // 2  # ceil(p_internal/2)
        if len(node.child_pointers) >= min_ptr:
            # node ok
            return

        parent = node.parent
        pos = parent.child_pointers.index(node)
        left = parent.child_pointers[pos - 1] if pos - 1 >= 0 else None
        right = parent.child_pointers[pos + 1] if pos + 1 < len(parent.child_pointers) else None

        # Try borrow from left: left must have > min_ptr children => > (min_ptr - 1) keys
        if left and len(left.child_pointers) > min_ptr:
            # Move last child from left to front of node
            borrowed_child = left.child_pointers.pop(-1)
            borrowed_key = parent.keys[pos - 1]
            # Update parent key: parent's separator becomes left's new last key's next smallest
            parent.keys[pos - 1] = left.keys.pop(-1) if left.keys else parent.keys[pos - 1]
            # Insert borrowed child & adjust keys in node
            node.child_pointers.insert(0, borrowed_child)
            borrowed_child.parent = node
            # Insert borrowed_key at front of node.keys?
            # For internal redistribution we must shift keys properly
            node.keys.insert(0, borrowed_key)
            return

        # Try borrow from right
        if right and len(right.child_pointers) > min_ptr:
            # Move first child from right to end of node
            borrowed_child = right.child_pointers.pop(0)
            borrowed_key = parent.keys[pos]
            # Update parent key to be right.keys[0] (new separator)
            parent.keys[pos] = right.keys.pop(0) if right.keys else parent.keys[pos]
            node.child_pointers.append(borrowed_child)
            borrowed_child.parent = node
            node.keys.append(borrowed_key)
            return

        # Merge cases: prefer left if exists, else merge with right
        if left:
            # merge left + node into left
            # append separator key from parent between left and node
            sep = parent.keys.pop(pos - 1)
            # left.keys extend with sep and node.keys
            left.keys.append(sep)
            left.keys.extend(node.keys)
            left.child_pointers.extend(node.child_pointers)
            for ch in node.child_pointers:
                ch.parent = left
            # remove node from parent.child_pointers
            parent.child_pointers.pop(pos)
            # check parent recursively
            self._fix_internal_after_delete(parent)
        elif right:
            # merge node + right into node
            sep = parent.keys.pop(pos)
            node.keys.append(sep)
            node.keys.extend(right.keys)
            node.child_pointers.extend(right.child_pointers)
            for ch in right.child_pointers:
                ch.parent = node
            parent.child_pointers.pop(pos + 1)
            self._fix_internal_after_delete(parent)
        
        
    def print_tree(self):
        """Level-order printing of tree nodes (keys only)."""
        from collections import deque
        q = deque([(self.root, 0)])
        cur_level = 0
        lines = []
        while q:
            node, lvl = q.popleft()
            if lvl != cur_level:
                print(f"Level {cur_level}: " + " | ".join(lines))
                lines = []
                cur_level = lvl
            if node.is_leaf:
                lines.append(f"[Leaf {node.keys}]")
            else:
                lines.append(f"[Int {node.keys}]")
                for ch in node.child_pointers:
                    q.append((ch, lvl + 1))
        if lines:
            print(f"Level {cur_level}: " + " | ".join(lines))

    def export_dot(self, filename="bptree.dot"):
        """
        Export tree to Graphviz DOT file. Internal nodes point to child nodes, leaf nodes show keys/pointers.
        """
        node_id = {}
        nodes = []

        def assign(node):
            if id(node) in node_id:
                return
            nid = f"n{len(node_id)}"
            node_id[id(node)] = nid
            nodes.append(node)
            if not node.is_leaf:
                for ch in node.child_pointers:
                    assign(ch)
        assign(self.root)

        with open(filename, "w", encoding="utf-8") as f:
            f.write("digraph BPlus {\nnode [shape=record];\n")
            # write nodes
            for node in nodes:
                nid = node_id[id(node)]
                if node.is_leaf:
                    # label keys + pointers
                    parts = []
                    for i, k in enumerate(node.keys):
                        ptr = node.pointers[i] if i < len(node.pointers) else ""
                        parts.append(f"<f{i}> {k}\\n{ptr}")
                    label = " | ".join(parts) if parts else "empty"
                    f.write(f'{nid} [label="{{{label}}}"];\n')
                else:
                    label = " | ".join(str(k) for k in node.keys) if node.keys else "internal"
                    f.write(f'{nid} [label="{{{label}}}"];\n')
                    for i, ch in enumerate(node.child_pointers):
                        f.write(f"{nid} -> {node_id[id(ch)]};\n")
            f.write("}\n")
        print(f"Wrote DOT to {filename} (render with `dot -Tpng {filename} -o tree.png`)")



# ==========> visualizer
    def visualize(self, filename="bplustree", view=True):
            dot = Digraph(comment="B+ Tree", format="png")
            dot.attr('node', shape='record', style='filled', fillcolor='lightgrey')

            def add_node(node, parent_name=None, edge_label=""):
                node_id = str(id(node))
                if node.is_leaf:
                    label = " | ".join(str(k) for k in node.keys)
                    dot.node(node_id, f"{{Leaf|{label}}}", fillcolor="lightblue")
                else:
                    label = " | ".join(str(k) for k in node.keys)
                    dot.node(node_id, f"{{Internal|{label}}}", fillcolor="lightcoral")

                if parent_name:
                    dot.edge(parent_name, node_id, label=edge_label)

                
                if not node.is_leaf:
                    for i, child in enumerate(node.child_pointers):
                        add_node(child, node_id, edge_label=f"child {i}")

            
            add_node(self.root)

            
            leaf = self.root
            while not leaf.is_leaf:
                leaf = leaf.child_pointers[0]
            while leaf and leaf.next:
                dot.edge(str(id(leaf)), str(id(leaf.next)), style="dashed", color="blue")
                leaf = leaf.next

            
            output_path = dot.render(filename, view=view)
            print(f"B+ tree visualization saved to: {output_path}")
            

