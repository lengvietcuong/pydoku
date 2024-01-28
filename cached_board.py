class CachedBoard:
    def __init__(self, board: list[list[int]] | None = None) -> None:
        self.board = board if board is not None else [[0] * 9 for _ in range(9)]
        self._precompute()

    def _precompute(self) -> None:
        """Mark empty cells and already filled nums."""
        self.empty_cells = []
        self._rows = [[False] * 9 for _ in range(9)]
        self._cols = [[False] * 9 for _ in range(9)]
        self._boxes = [[[False] * 9 for _ in range(3)] for _ in range(3)]

        for row in range(9):
            for col in range(9):
                if not self.board[row][col]:
                    self.empty_cells.append([row, col])
                    continue

                num = self.board[row][col]
                # Check if num is already present in its row, col, or box
                if not self.can_put(num, row, col):
                    raise ValueError("Invalid Board Input")

                self._mark(num, row, col, True)

    def _mark(self, num: int, row: int, col: int, flag: bool) -> None:
        self._rows[row][num - 1] = flag
        self._cols[col][num - 1] = flag
        self._boxes[row // 3][col // 3][num - 1] = flag

    def can_put(self, num: int, row: int, col: int) -> bool:
        return not any(
            (
                self._rows[row][num - 1],
                self._cols[col][num - 1],
                self._boxes[row // 3][col // 3][num - 1],
            )
        )

    def put(self, num: int, row: int, col: int) -> None:
        self.board[row][col] = num
        self._mark(num, row, col, True)

    def erase(self, row: int, col: int) -> None:
        num = self.board[row][col]
        self.board[row][col] = 0
        self._mark(num, row, col, False)
