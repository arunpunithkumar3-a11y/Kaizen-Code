"""Linked List Implementation in Python"""


class Node:
    """A single node in a linked list."""
    
    def __init__(self, data):
        self.data = data
        self.next = None
    
    def __repr__(self):
        return f"Node({self.data})"


class LinkedList:
    """Singly linked list implementation."""
    
    def __init__(self):
        self.head = None
        self._size = 0
    
    def __len__(self):
        return self._size
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next
    
    def __repr__(self):
        elements = " -> ".join(str(x) for x in self)
        return f"LinkedList({elements})" if elements else "LinkedList()"
    
    # --- Core Operations ---
    
    def append(self, data):
        """Add element to the end of the list. O(n)"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1
        return self
    
    def prepend(self, data):
        """Add element to the beginning of the list. O(1)"""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1
        return self
    
    def insert(self, index, data):
        """Insert element at given index. O(n)"""
        if index < 0 or index > self._size:
            raise IndexError("Index out of bounds")
        
        if index == 0:
            return self.prepend(data)
        
        new_node = Node(data)
        current = self.head
        for _ in range(index - 1):
            current = current.next
        new_node.next = current.next
        current.next = new_node
        self._size += 1
        return self
    
    def delete(self, data):
        """Delete first occurrence of data. Returns True if deleted. O(n)"""
        if not self.head:
            return False
        
        if self.head.data == data:
            self.head = self.head.next
            self._size -= 1
            return True
        
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self._size -= 1
                return True
            current = current.next
        return False
    
    def delete_at(self, index):
        """Delete element at given index. O(n)"""
        if index < 0 or index >= self._size:
            raise IndexError("Index out of bounds")
        
        if index == 0:
            self.head = self.head.next
        else:
            current = self.head
            for _ in range(index - 1):
                current = current.next
            current.next = current.next.next
        self._size -= 1
        return self
    
    def search(self, data):
        """Return index of first occurrence, or -1 if not found. O(n)"""
        current = self.head
        index = 0
        while current:
            if current.data == data:
                return index
            current = current.next
            index += 1
        return -1
    
    def get(self, index):
        """Get element at index. O(n)"""
        if index < 0 or index >= self._size:
            raise IndexError("Index out of bounds")
        
        current = self.head
        for _ in range(index):
            current = current.next
        return current.data
    
    def set(self, index, data):
        """Set element at index. O(n)"""
        if index < 0 or index >= self._size:
            raise IndexError("Index out of bounds")
        
        current = self.head
        for _ in range(index):
            current = current.next
        current.data = data
        return self
    
    # --- Utility Methods ---
    
    def reverse(self):
        """Reverse the linked list in place. O(n)"""
        prev = None
        current = self.head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head = prev
        return self
    
    def clear(self):
        """Remove all elements."""
        self.head = None
        self._size = 0
        return self
    
    def to_list(self):
        """Convert to Python list."""
        return list(self)
    
    @classmethod
    def from_list(cls, items):
        """Create linked list from Python list."""
        ll = cls()
        for item in items:
            ll.append(item)
        return ll


# --- Doubly Linked List (Bonus) ---

class DoublyNode:
    """Node for doubly linked list."""
    
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None
    
    def __repr__(self):
        return f"DoublyNode({self.data})"


class DoublyLinkedList:
    """Doubly linked list implementation."""
    
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0
    
    def __len__(self):
        return self._size
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next
    
    def __repr__(self):
        elements = " <-> ".join(str(x) for x in self)
        return f"DoublyLinkedList({elements})" if elements else "DoublyLinkedList()"
    
    def append(self, data):
        new_node = DoublyNode(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1
        return self
    
    def prepend(self, data):
        new_node = DoublyNode(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1
        return self
    
    def delete(self, data):
        current = self.head
        while current:
            if current.data == data:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                
                self._size -= 1
                return True
            current = current.next
        return False
    
    def reverse(self):
        current = self.head
        while current:
            current.next, current.prev = current.prev, current.next
            current = current.prev
        self.head, self.tail = self.tail, self.head
        return self


# --- Tests ---

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Singly Linked List")
    print("=" * 50)
    
    # Basic operations
    ll = LinkedList()
    ll.append(1).append(2).append(3)
    print(f"After append: {ll}")
    assert len(ll) == 3
    
    ll.prepend(0)
    print(f"After prepend: {ll}")
    assert ll.get(0) == 0
    
    ll.insert(2, 1.5)
    print(f"After insert at 2: {ll}")
    assert ll.get(2) == 1.5
    
    # Search
    assert ll.search(2) == 3
    assert ll.search(99) == -1
    print(f"Search 2: index {ll.search(2)}")
    print(f"Search 99: index {ll.search(99)}")
    
    # Delete
    ll.delete(1.5)
    print(f"After delete 1.5: {ll}")
    assert len(ll) == 4
    
    ll.delete_at(0)
    print(f"After delete_at 0: {ll}")
    assert ll.get(0) == 1
    
    # Reverse
    ll.reverse()
    print(f"After reverse: {ll}")
    assert ll.to_list() == [3, 2, 1]
    
    # Iteration
    print(f"Iteration: {list(ll)}")
    
    # From list
    ll2 = LinkedList.from_list([10, 20, 30])
    print(f"From list: {ll2}")
    
    # Edge cases
    empty = LinkedList()
    assert empty.search(1) == -1
    assert empty.delete(1) == False
    print("Edge cases passed")
    
    print("\n" + "=" * 50)
    print("Testing Doubly Linked List")
    print("=" * 50)
    
    dll = DoublyLinkedList()
    dll.append(1).append(2).append(3)
    print(f"After append: {dll}")
    
    dll.prepend(0)
    print(f"After prepend: {dll}")
    
    dll.delete(2)
    print(f"After delete 2: {dll}")
    
    dll.reverse()
    print(f"After reverse: {dll}")
    assert list(dll) == [3, 1, 0]
    
    print("\n✅ All tests passed!")