from cached_board import CachedBoard


def solve(board: list[list[int]] | CachedBoard) -> None:
    """Solve in-place, stop when 1 solution is found."""
    if not isinstance(board, CachedBoard):
        board = CachedBoard(board)

    i, num_empty = 0, len(board.empty_cells)
    while i < num_empty:
        row, col = board.empty_cells[i]
        # Determine starting value to test
        if not board.board[row][col]:  # First time at cell
            start = 1
        else:  # Previously tested -> erase previous, start at previous + 1
            start = board.board[row][col] + 1
            board.erase(row, col)

        for num in range(start, 10):  # Test possible values
            if not board.can_put(num, row, col):
                continue
            board.put(num, row, col)
            i += 1
            break
        else:  # None possible -> go to previous cell & try a new num
            i -= 1
            if i < 0:
                raise ValueError("No Solution")


def solve_step_by_step(board: list[list[int]] | CachedBoard):
    """Solve in-place, generating each step."""
    if not isinstance(board, CachedBoard):
        board = CachedBoard(board)

    i, num_empty = 0, len(board.empty_cells)
    while i < num_empty:
        row, col = board.empty_cells[i]
        yield ("Select", (row, col))
        # Determine starting value to test
        if not board.board[row][col]:  # First time at cell
            start = 1
        else:  # Previously tested -> erase previous, start at previous + 1
            start = board.board[row][col] + 1
            board.erase(row, col)
            yield ("Erase", ())

        for num in range(start, 10):  # Test possible values
            if not board.can_put(num, row, col):
                continue
            board.put(num, row, col)
            yield ("Put", (num,))
            i += 1
            break
        else:  # None possible -> go to previous cell & try a new num
            i -= 1
            if i < 0:
                raise ValueError("No Solution")


def all_solutions(board: list[list[int]] | CachedBoard):
    """A generator that outputs all possible solutions, does not modify board"""
    if not isinstance(board, CachedBoard):
        board = CachedBoard(board)
    yield from _all_solutions_finder(board, 0)


def _all_solutions_finder(board: CachedBoard, i: int) -> None:
    if i == len(board.empty_cells):  # solved
        yield board.board
        return

    row, col = board.empty_cells[i]
    for num in range(1, 10):
        if not board.can_put(num, row, col):
            continue
        board.put(num, row, col)
        yield from _all_solutions_finder(board, i + 1)
        board.erase(row, col)
