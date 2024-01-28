from random import shuffle, randint
from cached_board import CachedBoard
from solver import solve


DIFFICULTY_REMOVAL_RANGES = {"Easy": (41, 45), "Medium": (46, 50), "Hard": (51, 55)}


def _create_random_solved_board() -> list[list[int]]:
    board = CachedBoard()
    tested = [[[False] * 9 for _ in range(9)] for _ in range(9)]
    i = 0
    while i < 81:
        row, col = divmod(i, 9)
        nums = list(range(1, 10))
        shuffle(nums)

        if board.board[row][col]:  # Previously tested -> erase previous
            board.erase(row, col)
            next_row, next_col = divmod(i + 1, 9)
            tested[next_row][next_col] = [False] * 9

        for num in nums:
            if tested[row][col][num - 1] or not board.can_put(num, row, col):
                continue
            board.put(num, row, col)
            tested[row][col][num - 1] = True
            i += 1
            break
        else:
            i -= 1
            continue

    return board.board


def create_game(difficulty: str) -> tuple[list[list[int]]]:
    """
    Return an unsolved board and the solution.
    Difficulty levels:
        Easy (41 - 45 cells removed)
        Medium (46 - 50 cells removed)
        Hard (51 - 55 cells removed)
    """

    def remove_cell_final() -> None:
        nonlocal board, row, col, removed
        board.erase(row, col)
        board.empty_cells.append([row, col])
        removed += 1

    solution = _create_random_solved_board()
    board = CachedBoard([row_contents.copy() for row_contents in solution])

    removed = 0
    num_removal = randint(*DIFFICULTY_REMOVAL_RANGES[difficulty])

    cells = [[row, col] for row in range(9) for col in range(9)]
    shuffle(cells)
    # Remove cells such that no other solutions are created
    for row, col in cells:
        if removed == num_removal:
            return board.board, solution

        current_num = board.board[row][col]
        # Try putting other nums at current cell and solve
        for num in range(1, 10):
            if num == current_num or not board.can_put(num, row, col):
                continue

            board.erase(row, col)
            board.put(num, row, col)
            try:
                solve([row_contents.copy() for row_contents in board.board])
                break  # Solvable -> different (unwanted) solution
            except ValueError:
                pass  # Unsolvable -> unique solution still ensured
            finally:
                # Restore board state
                board.erase(row, col)
                board.put(current_num, row, col)
        else:  # Only current num is valid -> unique solution is guaranteed
            remove_cell_final()

    # If unable to reach the removal target, try again
    return create_game(difficulty)
