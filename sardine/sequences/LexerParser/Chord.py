from typing import Optional

class Chord:
    """
    Everything is a chord (aka. a list):
    - A silence is an empty list
    - A note is a singleton
    - A chord is a list of variable size
    """
    def __init__(self, elements: list, root: Optional[int]):
        self._elements = elements
        self._root = root

    def __repr__(self) -> str:
        return f"Chord ({self._elements}, {self._root})"

    def __str__(self) -> str:
        return f"Chord ({self._elements}, {self._root})"
