from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class Node:
    is_leaf: bool
    keys: List[str] = field(default_factory=list)
    parent: Optional['InternalNode'] = None

class LeafNode(Node):
    def __init__(self):
        super().__init__(is_leaf=True)
        self.pointers: List[Tuple[int, int]] = []
        self.next: Optional['LeafNode'] = None

class InternalNode(Node):
    def __init__(self):
        super().__init__(is_leaf=False)
        self.child_pointers: List[Node] = []