from node import Node, LeafNode, InternalNode
from graphviz import Digraph
import imageio.v2 as iio  
import os                 
import glob               
from PIL import Image     

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

    def insert(self, key, pointer, animate=False):
        """
        Inserts a key-pointer pair.
        If animate=True, generates a GIF of the insertion process.
        """
        storyboard = []
        if animate:
            # Ensure the frames directory exists
            if not os.path.exists("frames"):
                os.makedirs("frames")
            
            # Clean up old frames from a previous run
            old_frames = glob.glob("frames/frame_*.png*")
            if old_frames:
                self._cleanup_frames(old_frames)

        
        leaf = self.find_leaf(key)

        # Animation logic
        if animate:
            frame_file = f"frames/frame_{len(storyboard):03d}" # No .png extension here
            self.visualize(frame_file, title=f"1. Find leaf for key: {key}", highlight_nodes=[leaf])
            storyboard.append(frame_file + ".png") # Add .png for the list

        i = 0
        while i < len(leaf.keys) and leaf.keys[i] < key:
            i += 1
        leaf.keys.insert(i, key)
        leaf.pointers.insert(i, pointer)

        # Animation logic
        if animate:
            frame_file = f"frames/frame_{len(storyboard):03d}"
            self.visualize(frame_file, title=f"2. Insert key {key} into leaf", highlight_nodes=[leaf])
            storyboard.append(frame_file + ".png")

        if len(leaf.keys) > self.p_leaf:
            # Pass the storyboard to the split function
            self.split_leaf(leaf, storyboard if animate else None)

        # Animation logic
        if animate:
            frame_file = f"frames/frame_{len(storyboard):03d}"
            self.visualize(frame_file, title=f"3. Insertion of {key} complete!")
            storyboard.append(frame_file + ".png")
            
            # --- Create the GIF ---
            output_gif = f"insert_animation_{key}.gif"
            self._create_gif(storyboard, output_gif)
            self._cleanup_frames(storyboard)

    def split_leaf(self, leaf, storyboard=None):
        """
        Splits a leaf node.
        If a storyboard is provided, generates animation frames.
        """
        if storyboard is not None:
            frame_file = f"frames/frame_{len(storyboard):03d}"
            self.visualize(frame_file, title=f"A. Leaf is full! Splitting...", highlight_nodes=[leaf])
            storyboard.append(frame_file + ".png")

        total = len(leaf.keys)
        split = total // 2
        left, right = LeafNode(), LeafNode()

        left.keys = leaf.keys[:split]
        right.keys = leaf.keys[split:]
        left.pointers = leaf.pointers[:split]
        right.pointers = leaf.pointers[split:]

        # --- FIX THE LINKED LIST ---
        right.next = leaf.next 
        left.next = right
        if leaf.parent:
            parent = leaf.parent
            try:
                pos = parent.child_pointers.index(leaf)
                if pos > 0:
                    left_sibling = parent.child_pointers[pos - 1]
                    if left_sibling and left_sibling.is_leaf:
                        left_sibling.next = left 
            except ValueError:
                pass 
        # --- END FIX ---

        # connect to parent
        if leaf.parent is None:
            root = InternalNode()
            root.keys = [right.keys[0]]
            root.child_pointers = [left, right]
            left.parent = right.parent = root
            self.root = root
            
            if storyboard is not None:
                frame_file = f"frames/frame_{len(storyboard):03d}"
                self.visualize(frame_file, title=f"B. Split complete. New root created.", highlight_nodes=[left, right, root])
                storyboard.append(frame_file + ".png")
        else:
            parent = leaf.parent
            pos = parent.child_pointers.index(leaf) 
            parent.child_pointers[pos] = left
            parent.child_pointers.insert(pos + 1, right)
            parent.keys.insert(pos, right.keys[0])
            left.parent = right.parent = parent
            
            if storyboard is not None:
                frame_file = f"frames/frame_{len(storyboard):03d}"
                self.visualize(frame_file, title=f"B. Split complete. Promoting key {right.keys[0]}", highlight_nodes=[left, right, parent])
                storyboard.append(frame_file + ".png")

            if len(parent.child_pointers) > self.p_internal:
                # Pass storyboard to internal split, too!
                self.split_internal(parent, storyboard) # Pass along

    def split_internal(self, node, storyboard=None):
        """
        Splits an internal node.
        If a storyboard is provided, generates animation frames.
        """
        if storyboard is not None:
            frame_file = f"frames/frame_{len(storyboard):03d}"
            self.visualize(frame_file, title=f"C. Internal node is full! Splitting...", highlight_nodes=[node])
            storyboard.append(frame_file + ".png")

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

            if storyboard is not None:
                frame_file = f"frames/frame_{len(storyboard):03d}"
                self.visualize(frame_file, title=f"D. Internal split creates new root", highlight_nodes=[left, right, root])
                storyboard.append(frame_file + ".png")
        else:
            parent = node.parent
            pos = parent.child_pointers.index(node)
            parent.child_pointers[pos] = left
            parent.child_pointers.insert(pos + 1, right)
            parent.keys.insert(pos, promoted)
            left.parent = right.parent = parent

            if storyboard is not None:
                frame_file = f"frames/frame_{len(storyboard):03d}"
                self.visualize(frame_file, title=f"D. Internal split complete. Promoting {promoted}", highlight_nodes=[left, right, parent])
                storyboard.append(frame_file + ".png")

            if len(parent.child_pointers) > self.p_internal:
                self.split_internal(parent, storyboard) # Pass storyboard recursively


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
        # NOTE: Animation is not implemented for delete yet.
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
        # Call your new refresh function to ensure all keys are correct
        self._refresh_separators_from_children(self.root)

    def _fix_parent_separators_after_leaf_change(self, node):
        """Recursively fixes parent separators if the first key of a node changes."""
        if node.parent is None:
            return
        parent = node.parent
        try:
            idx = parent.child_pointers.index(node)
            if idx > 0 and len(node.keys) > 0:
                if parent.keys[idx - 1] != node.keys[0]:
                    parent.keys[idx - 1] = node.keys[0]
                    # propagate upward if needed
                    self._fix_parent_separators_after_leaf_change(parent)
            elif idx > 0 and len(node.keys) == 0:
                # If leaf becomes empty, this key will be removed by merge logic anyway
                pass
        except ValueError:
             pass # Node may have been removed already


    def _fix_leaf_underflow(self, leaf):
        parent = leaf.parent
        if parent is None:
            return  # shouldn't happen (we handled root earlier)

        try:
            pos = parent.child_pointers.index(leaf)
        except ValueError:
             print("DEBUG: Node not found in parent, likely already merged.")
             return # Node already processed

        left = parent.child_pointers[pos - 1] if pos - 1 >= 0 else None
        right = parent.child_pointers[pos + 1] if pos + 1 < len(parent.child_pointers) else None

        min_keys_leaf = (self.p_leaf + 1) // 2

        # 1) Try borrow from left
        if left and len(left.keys) > min_keys_leaf:
            borrowed_key = left.keys.pop(-1)
            borrowed_ptr = left.pointers.pop(-1)
            leaf.keys.insert(0, borrowed_key)
            leaf.pointers.insert(0, borrowed_ptr)
            parent.keys[pos - 1] = leaf.keys[0]
            return

        # 2) Try borrow from right
        if right and len(right.keys) > min_keys_leaf:
            borrowed_key = right.keys.pop(0)
            borrowed_ptr = right.pointers.pop(0)
            leaf.keys.append(borrowed_key)
            leaf.pointers.append(borrowed_ptr)
            parent.keys[pos] = right.keys[0] # right.keys[0] is the new smallest key
            return

        # 3) Merge with sibling (prefer left if exists else right)
        if left:
            left.keys.extend(leaf.keys)
            left.pointers.extend(leaf.pointers)
            left.next = leaf.next
            remove_index = pos
            parent.child_pointers.pop(remove_index)
            parent.keys.pop(remove_index - 1)
            self._fix_internal_after_delete(parent)
        elif right:
            leaf.keys.extend(right.keys)
            leaf.pointers.extend(right.pointers)
            leaf.next = right.next
            parent.child_pointers.pop(pos + 1)
            parent.keys.pop(pos)
            self._fix_internal_after_delete(parent)

    def _fix_internal_after_delete(self, node):
        if node is self.root:
            if not node.is_leaf and len(node.child_pointers) == 1:
                child = node.child_pointers[0]
                child.parent = None
                self.root = child
            return

        min_ptr = (self.p_internal + 1) // 2  # ceil(p_internal/2)
        if len(node.child_pointers) >= min_ptr:
            return

        parent = node.parent
        if not parent: return 

        try:
            pos = parent.child_pointers.index(node)
        except ValueError:
            print("DEBUG: Internal node not found in parent, likely already merged.")
            return

        left = parent.child_pointers[pos - 1] if pos - 1 >= 0 else None
        right = parent.child_pointers[pos + 1] if pos + 1 < len(parent.child_pointers) else None

        # Try borrow from left
        if left and len(left.child_pointers) > min_ptr:
            borrowed_child = left.child_pointers.pop(-1)
            borrowed_key_from_parent = parent.keys[pos - 1]
            parent.keys[pos - 1] = left.keys.pop(-1) 
            node.child_pointers.insert(0, borrowed_child)
            borrowed_child.parent = node
            node.keys.insert(0, borrowed_key_from_parent)
            return

        # Try borrow from right
        if right and len(right.child_pointers) > min_ptr:
            borrowed_child = right.child_pointers.pop(0)
            borrowed_key_from_parent = parent.keys[pos]
            parent.keys[pos] = right.keys.pop(0) 
            node.child_pointers.append(borrowed_child)
            borrowed_child.parent = node
            node.keys.append(borrowed_key_from_parent)
            return

        # Merge cases
        if left:
            sep = parent.keys.pop(pos - 1)
            left.keys.append(sep)
            left.keys.extend(node.keys)
            left.child_pointers.extend(node.child_pointers)
            for ch in node.child_pointers:
                ch.parent = left
            parent.child_pointers.pop(pos)
            self._fix_internal_after_delete(parent)
        elif right:
            sep = parent.keys.pop(pos)
            node.keys.append(sep)
            node.keys.extend(right.keys)
            node.child_pointers.extend(right.child_pointers)
            for ch in right.child_pointers:
                ch.parent = node
            parent.child_pointers.pop(pos + 1)
            self._fix_internal_after_delete(parent)
        
        # This was in your original, but it's better to call it once
        # at the end of delete(), not in the recursive fix.
        # self._refresh_separators_from_children(self.root)
    
    def _refresh_separators_from_children(self, node=None):
        """
        Your new recursive function to refresh all separator keys.
        """
        if node is None:
            node = self.root

        if node.is_leaf:
            return

        new_keys = []
        for i in range(1, len(node.child_pointers)):
            child = node.child_pointers[i]
            
            leftmost = child
            while not leftmost.is_leaf:
                if not leftmost.child_pointers: # Handle empty internal node
                    leftmost = None
                    break
                leftmost = leftmost.child_pointers[0]
            
            if leftmost and leftmost.keys:
                 new_keys.append(leftmost.keys[0])
            elif i-1 < len(node.keys):
                 # Fallback: keep old key if child is empty
                 new_keys.append(node.keys[i-1])

        node.keys = new_keys

        # Recurse to children
        for ch in node.child_pointers:
            if not ch.is_leaf:
                self._refresh_separators_from_children(ch)
        
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


    def export_dot(self, filename="bptree.dot"):
        """
        Your original export_dot function.
        """
        node_id = {}
        nodes = []

        def assign(node):
            if not node: return
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
                        if ch and id(ch) in node_id:
                             f.write(f"{nid} -> {node_id[id(ch)]};\n")
            
            # Add leaf chain
            leaf = self.root
            if leaf:
                while leaf and not leaf.is_leaf:
                    if not leaf.child_pointers:
                        leaf = None
                        break
                    leaf = leaf.child_pointers[0]
            
            if leaf:
                while leaf and leaf.next:
                    if id(leaf) in node_id and id(leaf.next) in node_id:
                        f.write(f"{node_id[id(leaf)]} -> {node_id[id(leaf.next)]} [style=dashed, color=blue, constraint=false];\n")
                    leaf = leaf.next

            f.write("}\n")
        print(f"Wrote DOT to {filename} (render with `dot -Tpng {filename} -o tree.png`)")


    # ==========> NEW/UPDATED visualizer <==========
    def visualize(self, filename="bplustree", view=False, highlight_nodes=None, title=""):
        """
        Generates a visualization of the B+ Tree using Graphviz.
        - Uses HTML-like labels to prevent common Graphviz rendering errors.
        - highlight_nodes: A list of nodes to color yellow.
        - title: A title to display at the top of the image.
        - view: Set to True to open the file after render. False for animation frames.
        """
        dot = Digraph(comment="B+ Tree", format="png")
        # Use 'shape=plain' because we are providing our own HTML-like label
        dot.attr('node', shape='plain', style='filled') 
        dot.attr(rankdir='TB') # Top-to-Bottom layout

        # Add a title if one is provided
        if title:
            dot.attr(label=title, fontsize='20')
            
        if highlight_nodes is None:
            highlight_nodes = []

        node_ids = {}

        def assign_ids_tree(node):
            """Recursively assign IDs by traversing child pointers."""
            if not node: return
            if id(node) in node_ids:
                return # Already visited
            
            node_ids[id(node)] = f"n{len(node_ids)}"
            
            if not node.is_leaf:
                for child in node.child_pointers:
                    assign_ids_tree(child)

        # 1. First, traverse the main tree structure
        assign_ids_tree(self.root)

        # 2. Second, find the leftmost leaf and traverse the *entire* .next chain
        #    This finds any orphaned leaves that assign_ids_tree missed.
        leaf = self.root
        if leaf:
            while leaf and not leaf.is_leaf:
                if not leaf.child_pointers:
                    leaf = None
                    break
                leaf = leaf.child_pointers[0]
        
        while leaf: # Go through the *entire* leaf chain
            if id(leaf) not in node_ids:
                # Found an orphan!
                node_ids[id(leaf)] = f"n{len(node_ids)}"
            leaf = leaf.next
        
        # --- End of new ID assignment logic ---

        if not self.root or id(self.root) not in node_ids:
             # print("Tree is empty, visualization will be minimal.")
             return 

        def escape_html(s):
            """Escapes special characters for HTML labels."""
            s = str(s)
            s = s.replace("&", "&amp;")
            s = s.replace("<", "&lt;")
            s = s.replace(">", "&gt;")
            s = s.replace("\"", "&quot;")
            s = s.replace("'", "&#39;")
            return s

        def add_node_to_dot(node, parent_name=None, parent_port_idx=None):
            """Recursively adds nodes and parent-child edges to the graph."""
            if not node or id(node) not in node_ids: return
            
            node_id = node_ids[id(node)]
            
            # Check if this node should be highlighted
            node_color = "yellow" if node in highlight_nodes else ("lightblue" if node.is_leaf else "lightcoral")
            
            if node.is_leaf:
                # --- Leaf Node HTML-like Label ---
                parts = []
                for i, k in enumerate(node.keys):
                    ptr_str = escape_html(node.pointers[i] if i < len(node.pointers) else "P_err")
                    k_str = escape_html(k)
                    parts.append(f"<TD>{k_str}, {ptr_str}</TD>")
                
                label = f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" STYLE="ROUNDED"><TR>{"".join(parts) if parts else "<TD>empty</TD>"}</TR></TABLE>>'
                dot.node(node_id, label=label, fillcolor=node_color)
            else:
                # --- Internal Node HTML-like Label ---
                label_parts = []
                for i, k in enumerate(node.keys):
                    k_str = escape_html(k)
                    label_parts.append(f'<TD PORT="p{i}"></TD><TD>{k_str}</TD>')
                label_parts.append(f'<TD PORT="p{len(node.keys)}"></TD>') # Final pointer port
                
                label = f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" STYLE="ROUNDED"><TR>{"".join(label_parts)}</TR></TABLE>>'
                dot.node(node_id, label=label, fillcolor=node_color)

            if parent_name:
                # Connect from parent's specific port (e.g., 'p0') to the child node
                dot.edge(f"{parent_name}:p{parent_port_idx}", node_id)
            
            if not node.is_leaf:
                for i, child in enumerate(node.child_pointers):
                    # Recurse, passing the clean node_id and the port index 'i'
                    add_node_to_dot(child, node_id, parent_port_idx=i) 

        # --- Draw all nodes and parent-child edges ---
        add_node_to_dot(self.root)

        # --- Draw adjacent leaf pointers ---
        leaf = self.root
        if not leaf: return 
        
        while leaf and not leaf.is_leaf:
            if not leaf.child_pointers: 
                leaf = None 
                break
            leaf = leaf.child_pointers[0]
        
        if leaf: 
            while leaf and leaf.next:
                if id(leaf) in node_ids and id(leaf.next) in node_ids:
                    current_id = node_ids[id(leaf)]
                    next_id = node_ids[id(leaf.next)]
                    
                    dot.edge(current_id, next_id, style="dashed", color="blue", constraint="false")
                
                leaf = leaf.next 
        
        # --- Render the final image ---
        try:
            # We pass filename *without* extension, dot.render adds it.
            output_path = dot.render(filename, view=view, cleanup=True)
            if view: # Only print if we're not making frames
                print(f"B+ tree visualization saved to: {output_path}")
        except Exception as e:
            print(f"\n--- Error rendering graph (is Graphviz installed?) ---")
            print(f"Error: {e}")
            print("Writing .dot file as fallback.")
            dot.save(filename + ".dot")
            # print(f"Wrote DOT to {filename}.dot (render with `dot -Tpng {filename}.dot -o tree.png`)")
            print("----------------------------------------------------------\n")

    # --- Animation Helper Functions ---

    def _create_gif(self, frame_files, output_filename):
        """Stitches a list of PNG files into a GIF, standardizing all frame sizes."""
        
        raw_images = []
        max_width = 0
        max_height = 0

        # First pass: Read images and find max dimensions
        for filename in frame_files:
            try:
                img = Image.open(filename)
                raw_images.append(img)
                if img.width > max_width:
                    max_width = img.width
                if img.height > max_height:
                    max_height = img.height
            except FileNotFoundError:
                print(f"Warning: Frame file not found {filename}, skipping.")

        if not raw_images:
            print("Error: No frames found to create GIF.")
            return

        # Second pass: Create new images with padding
        standardized_images = []
        for img in raw_images:
            # Create a new blank canvas (white background)
            new_frame = Image.new('RGBA', (max_width, max_height), (255, 255, 255, 255))
            
            # Calculate position to paste the old image (centered)
            x_offset = (max_width - img.width) // 2
            y_offset = (max_height - img.height) // 2
            
            # Paste the original image
            new_frame.paste(img, (x_offset, y_offset))
            standardized_images.append(new_frame)
            
            # Close the original image file handle
            img.close()

        # Save the GIF
        print(f"Creating GIF... This may take a moment.")
        
        # FIX: 'duration' is in MILLISECONDS. 
        # 3000ms = 3 seconds per frame.
        # loop=0 means loop forever.
        iio.mimsave(output_filename, standardized_images, duration=3000, loop=0)
        print(f"\n✨ Animation saved to {output_filename}")

    def _cleanup_frames(self, frame_files):
        """Deletes the temporary PNG frame files and their .dot files."""
        count = 0
        for f_png in frame_files:
            f_dot = f_png.replace(".png", "") # Get the base filename
            try:
                os.remove(f_png)
                os.remove(f_dot) # Graphviz also creates .dot files
                count += 1
            except OSError:
                pass
        if count > 0:
            print(f"🧹 Cleaned up {count} temporary frames.")
