from typing import Optional


class LinkedListNode:
    def __init__(self, id: int):
        self._next: Optional['LinkedListNode'] = None
        self._prev: Optional['LinkedListNode'] = None

        self.id: int = id

    def insert_after(self, new_node: 'LinkedListNode') -> 'LinkedListNode':
        """Returns new node."""
        if self._next is not None:
            self._link(new_node, self._next)

        self._link(self, new_node)

        return new_node

    def insert_before(self, new_node: 'LinkedListNode') -> 'LinkedListNode':
        """Returns new node."""
        if self._prev is not None:
            self._link(self._prev, new_node)

        self._link(new_node, self)

        return new_node

    def replace_by(self, new_node: 'LinkedListNode') -> 'LinkedListNode':
        """Returns new node."""
        if self._next is not None:
            self._link(new_node, self._next)

        if self._prev is not None:
            self._link(self._prev, new_node)

        return new_node

    def search_forward(self, key) -> Optional['LinkedListNode']:
        """Returns found node or None."""
        current = self
        while current is not None and current.id != id:
            current = current._next
        return current

    def search_backward(self, key) -> Optional['LinkedListNode']:
        """Returns found node or None."""
        current = self
        while current is not None and current.id != id:
            current = current._prev
        return current

    def delete(self) -> 'LinkedListNode':
        """Returns deleted."""
        self._checked_link(self._next, self._prev)
        return self

    def revert_until(self, end: 'LinkedListNode'):

        current = self._next
        while current != end:
            current._prev, current._next = current._next, current._prev

    # ----------------------------------- protected ----------------------------------------------

    def _replace_last(self, new_node):
        """Faster method for replacing last."""
        self._link(self._prev, new_node)
        return new_node

    def _replace_first(self, new_node):
        """Faster method for replacing first."""
        self._link(new_node, self._next)
        return new_node

    def _append_last(self, new_node):
        """Faster method for appending after last."""
        self._link(self, new_node)
        return new_node

    def _append_first(self, new_node):
        """Faster method for appending before first."""
        self._link(new_node, self)
        return new_node

    @staticmethod
    def _link(a: 'LinkedListNode', b: 'LinkedListNode'):
        a._next = b
        b._prev = a

    @staticmethod
    def _checked_link(a: Optional['LinkedListNode'], b: Optional['LinkedListNode']):
        if a is not None:
            a._next = b

        if b is not None:
            b._prev = a


class LinkedListIterator:
    def __init__(self, node: LinkedListNode):
        self.node: LinkedListNode = node

    def __iter__(self):
        return self

    def __next__(self):
        try:
            res = LinkedListIterator(
                self.node  # TODO: for loop iteration may be slow (кешировать?)
            )
            self.node = self.node.next
            return res
        except AttributeError:
            raise StopIteration

    @property
    def key(self):
        return self.node.key

    @key.setter
    def key(self, key):
        self.node.key = key

    @property
    def value(self):
        return self.node.value

    @value.setter
    def value(self, val):
        self.node.value = val

    def move_next(self) -> 'LinkedListIterator':
        self.node = self.node.next
        return self

    def move_prev(self) -> 'LinkedListIterator':
        self.node = self.node.prev
        return self

    def is_first(self) -> bool:
        return self.node._prev is None

    def is_last(self) -> bool:
        return self.node._next is None

    def is_empty(self) -> bool:
        return self.node is None


class LinkedList:
    def __init__(self):
        self._len: int = 0
        self._first: Optional[LinkedListNode] = None
        self._last: Optional[LinkedListNode] = None

    def __len__(self):
        # TODO:  __setitem__, __getitem__, __delitem__, +, *, bla-bla, __reversed__, __int__
        return self._len

    def __iter__(self) -> Optional[LinkedListNode]:
        return self._first

    def first(self):
        return LinkedListIterator(self._first)

    def last(self):
        return LinkedListIterator(self._last)

    def push_back(self, key, value=None) -> None:
        if self._add_if_first(key, value):
            return

        self._len += 1
        self._last = self._last._append_last(LinkedListNode(key, value))

    def push_front(self, key, value=None) -> None:
        if self._add_if_first(key, value):
            return

        self._len += 1
        self._first = self._last._append_first(LinkedListNode(key, value))

    def pop_front(self, key, value=None):
        if self._del_if_last():
            return

        # TODO:
        return self._first.delete()

    def find(self, key, backward=False):
        if self._len == 0:
            return None

        searcher = self._first.search_forward if not backward else self._last.search_backward
        return LinkedListIterator(searcher(key))

    def _add_if_first(self, key, value=None) -> bool:
        """Returns true if it was the first element."""
        if self._len == 0:
            node = LinkedListNode(key, value)
            self._len = 1
            self._first = self._last = node
            return True
        else:
            return False

    def _del_if_last(self):
        """Returns true if it was the last element."""
        if self._len == 1:
            self._len = 0
            self._first = self._last = None
            return True
        else:
            return False
