from dataclasses import dataclass, field
from heapq import heappop, heappush
from typing import List, Optional, TypeVar

T = TypeVar('T')


@dataclass
class Heap:
    """
    Heap, returning minimum element based on python stdlib
    """
    data: List[T] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.data)

    def push(self, a: T) -> None:
        heappush(self.data, a)

    def min(self) -> Optional[T]:
        if not self.empty():
            return self.data[0]
        return None

    def pop(self) -> Optional[T]:
        if not self.empty():
            return heappop(self.data)
        return None

    def empty(self) -> bool:
        return len(self.data) == 0
