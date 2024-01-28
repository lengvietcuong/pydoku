import sys
import pygame
from game_generator import create_game
from cached_board import CachedBoard
from solver import solve_step_by_step, all_solutions


WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
GRID_LENGTH = 540
GRID_SIZE = 9
CELL_LENGTH = GRID_LENGTH // GRID_SIZE
GRID_TOPLEFT = ((WINDOW_WIDTH - GRID_LENGTH) // 2, (WINDOW_HEIGHT - GRID_LENGTH) // 2)
PADDING = 3

THIN_THICKNESS = 1
MEDIUM_THICKNESS = 3
THICK_THICKNESS = 5

LARGE_FONT_SIZE = 36
MEDIUM_FONT_SIZE = 24
SMALL_FONT_SIZE = 16

NEAR_WHITE = (210, 210, 210)
DARK_BLUE = (23, 27, 35)
DARKER_BLUE = (12, 14, 17)
LIGHT_GRAY = (51, 59, 71)
LIGHT_BLUE = (41, 54, 82)
LIGHTER_BLUE = (116, 147, 191)
RED = (97, 37, 37)
BRIGHT_RED = (205, 74, 73)
GREEN = (56, 83, 67)
ERASE_COLOR = (0, 0, 0, 0)

MAX_SOLUTONS = 100
DIRECTIONS = {
    pygame.K_UP: (-1, 0),
    pygame.K_DOWN: (1, 0),
    pygame.K_LEFT: (0, -1),
    pygame.K_RIGHT: (0, 1),
}
ONE_SECOND = 1_000


pygame.init()


class Button:
    buttons_font = pygame.font.SysFont("ArialBlack", SMALL_FONT_SIZE)

    def __init__(self, rect: pygame.Rect, label: str, on_click=None) -> None:
        self.rect = rect
        self.label = label
        self.on_click = on_click
        self.is_highlighted = False

    def draw(self, surface: pygame.Surface) -> None:
        color = LIGHT_GRAY if self.is_highlighted else DARKER_BLUE
        pygame.draw.rect(surface, color, self.rect)

        text_color = LIGHTER_BLUE if self.is_highlighted else NEAR_WHITE
        text = self.buttons_font.render(self.label, True, text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def handle_click(self) -> None:
        if self.on_click:
            self.on_click()


class Grid:
    def __init__(self) -> None:
        pygame.display.set_caption("Sudoku")
        self._screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self._init_fonts()
        self._init_surfaces()
        self._init_buttons()

        self._game_mode = "Easy"
        self._background_surface.fill(DARK_BLUE)
        self._draw_grid_lines()
        self._draw_buttons()
        self._start_new_game()

    def _init_fonts(self) -> None:
        self._grid_numbers_font = pygame.font.Font(None, LARGE_FONT_SIZE)
        self._timer_font = pygame.font.SysFont("Arial", SMALL_FONT_SIZE)
        self._lives_font = pygame.font.SysFont("Arial", MEDIUM_FONT_SIZE)
        self._solutions_count_font = pygame.font.SysFont("ArialBlack", SMALL_FONT_SIZE)
        self._game_over_font = pygame.font.SysFont("ArialBlack", SMALL_FONT_SIZE)

    def _init_surfaces(self) -> None:
        self._background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self._grid_highlighting_surface = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
        )
        self._grid_numbers_surface = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
        )
        self._grid_lines_surface = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
        )
        self._stats_surface = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
        )
        self._buttons_surface = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
        )

    def _init_buttons(self) -> None:
        self._buttons = []

        game_mode_labels = ["Easy", "Medium", "Hard", "Custom"]
        for index, label in enumerate(game_mode_labels, start=1):
            rect = pygame.Rect(100 * index, 20, 100, 35)
            button = Button(
                rect, label, lambda mode=label: self._update_game_mode(mode)
            )
            self._buttons.append(button)

        _show_solution = Button(
            pygame.Rect(110, 640, 160, 35),
            "Show Solution",
            self._show_solution,
        )
        solve_step_by_step = Button(
            pygame.Rect(290, 640, 200, 35),
            "Solve Step-by-step",
            self._solve_step_by_step,
        )
        self._buttons.extend([_show_solution, solve_step_by_step])

    def _start_new_game(self) -> None:
        self._grid_numbers_surface.fill(ERASE_COLOR)
        self._stats_surface.fill(ERASE_COLOR)
        self._grid_locked = False

        if self._game_mode == "Custom":
            grid_rect = pygame.Rect(
                GRID_TOPLEFT[0], GRID_TOPLEFT[1], GRID_LENGTH, GRID_LENGTH
            )
            self._grid_highlighting_surface.fill(DARKER_BLUE, grid_rect)

            self._cached_board = CachedBoard()
            self._board = self._cached_board.board
            self._clues = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
            self._solution = []
            self._solutions = []
            self._current_solution_index = 0
        else:
            self._clues, self._solution = create_game(self._game_mode)
            self._board = [row.copy() for row in self._clues]

            self._total_seconds = 0
            self._last_time = pygame.time.get_ticks()
            self._lives = 3

            self._display_clues()
            self._draw_timer()
            self._draw_lives()

        self._select_first_empty_cell()

    def _update_game_mode(self, new_game_mode: str) -> None:
        self._game_mode = new_game_mode

        self._draw_buttons()
        self._start_new_game()
        self._update_display()

    def _draw_grid_lines(self) -> None:
        self._draw_inner_grid_lines()
        self._draw_outer_grid_lines()

    def _draw_inner_grid_lines(self) -> None:
        for i in range(1, GRID_SIZE):
            thickness = THICK_THICKNESS if i % 3 == 0 else THIN_THICKNESS
            pygame.draw.line(
                self._buttons_surface,
                LIGHT_BLUE,
                (GRID_TOPLEFT[0], GRID_TOPLEFT[1] + i * CELL_LENGTH),
                (GRID_TOPLEFT[0] + GRID_LENGTH, GRID_TOPLEFT[1] + i * CELL_LENGTH),
                thickness,
            )
            pygame.draw.line(
                self._buttons_surface,
                LIGHT_BLUE,
                (GRID_TOPLEFT[0] + i * CELL_LENGTH, GRID_TOPLEFT[1]),
                (GRID_TOPLEFT[0] + i * CELL_LENGTH, GRID_TOPLEFT[1] + GRID_LENGTH),
                thickness,
            )

    def _draw_outer_grid_lines(self) -> None:
        outer_lines = [
            (
                (GRID_TOPLEFT[0], GRID_TOPLEFT[1] + THICK_THICKNESS // 2),
                (GRID_TOPLEFT[0] + GRID_LENGTH, GRID_TOPLEFT[1] + THICK_THICKNESS // 2),
            ),
            (
                (GRID_TOPLEFT[0], GRID_TOPLEFT[1] + GRID_LENGTH + THICK_THICKNESS // 2),
                (
                    GRID_TOPLEFT[0] + GRID_LENGTH + THICK_THICKNESS,
                    GRID_TOPLEFT[1] + GRID_LENGTH + THICK_THICKNESS // 2,
                ),
            ),
            (
                (GRID_TOPLEFT[0] + THICK_THICKNESS // 2, GRID_TOPLEFT[1]),
                (GRID_TOPLEFT[0] + THICK_THICKNESS // 2, GRID_TOPLEFT[1] + GRID_LENGTH),
            ),
            (
                (GRID_TOPLEFT[0] + GRID_LENGTH + THICK_THICKNESS // 2, GRID_TOPLEFT[1]),
                (
                    GRID_TOPLEFT[0] + GRID_LENGTH + THICK_THICKNESS // 2,
                    GRID_TOPLEFT[1] + GRID_LENGTH,
                ),
            ),
        ]

        for start, end in outer_lines:
            pygame.draw.line(
                self._buttons_surface,
                LIGHT_BLUE,
                start,
                end,
                THICK_THICKNESS,
            )

    def _select_cell(self, row, col) -> None:
        self._selected_row, self._selected_col = (row, col)
        num_at_selected = self._num_at_selected()
        # Highlight the cell light gray unless it has an incorrect number
        if not (
            self._game_mode != "Custom"
            and num_at_selected
            and num_at_selected != self._solution_at_selected()
        ):
            self._highlight_selected(LIGHT_GRAY)

    def _select_first_empty_cell(self) -> None:
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if not self._clues[row][col]:
                    self._select_cell(row, col)
                    return

    def _unselect_selected(self) -> None:
        if self._selected_row is None and self._selected_col is None:
            return

        num_at_selected = self._num_at_selected()
        if not num_at_selected:
            self._highlight_selected(DARKER_BLUE)
        elif (
            self._grid_locked
            or self._game_mode == "Custom"
            or num_at_selected == self._solution_at_selected()
        ):
            self._highlight_selected(DARK_BLUE)
        self._selected_row = self._selected_col = None

    def _selected_cell_rect(self) -> pygame.Rect:
        return pygame.Rect(
            GRID_TOPLEFT[0] + self._selected_col * CELL_LENGTH,
            GRID_TOPLEFT[1] + self._selected_row * CELL_LENGTH,
            CELL_LENGTH,
            CELL_LENGTH,
        )

    def _highlight_selected(self, color) -> None:
        rect = self._selected_cell_rect()
        pygame.draw.rect(self._grid_highlighting_surface, color, rect)

    def _selected_is_clue(self):
        return self._clues[self._selected_row][self._selected_col]

    def _num_at_selected(self):
        return self._board[self._selected_row][self._selected_col]

    def _solution_at_selected(self):
        return self._solution[self._selected_row][self._selected_col]

    def _draw_number_at_selected(self, num: int) -> None:
        text = self._grid_numbers_font.render(str(num), True, NEAR_WHITE)
        text_rect = text.get_rect(
            center=(
                GRID_TOPLEFT[0] + self._selected_col * CELL_LENGTH + CELL_LENGTH // 2,
                GRID_TOPLEFT[1] + self._selected_row * CELL_LENGTH + CELL_LENGTH // 2,
            )
        )
        self._grid_numbers_surface.blit(text, text_rect)

    def _display_clues(self) -> None:
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                clue = self._clues[row][col]
                self._select_cell(row, col)
                if not clue:
                    self._highlight_selected(DARKER_BLUE)
                else:
                    self._draw_number_at_selected(clue)
                self._unselect_selected()

    def _draw_buttons(self) -> None:
        for button in self._buttons:
            button.is_highlighted = button.label == self._game_mode
            button.draw(self._buttons_surface)

    def _draw_timer(self) -> None:
        if self._total_seconds > 0:
            self._stats_surface.fill(DARK_BLUE, self._timer_text_rect)

        minutes, seconds = divmod(self._total_seconds, 60)
        timer_text = self._timer_font.render(
            f"{minutes:02d}:{seconds:02d}", True, NEAR_WHITE
        )
        self._timer_text_rect = timer_text.get_rect(
            bottomleft=(GRID_TOPLEFT[0] + THICK_THICKNESS, GRID_TOPLEFT[1] - PADDING)
        )
        self._stats_surface.blit(timer_text, self._timer_text_rect)

    def _draw_lives(self) -> None:
        if self._lives < 3:
            self._stats_surface.fill(DARK_BLUE, self._lives_text_rect)

        if not self._lives:
            text_content = "Game Over"
            text = self._game_over_font.render(text_content, True, BRIGHT_RED)
            self._grid_locked = True
        else:
            text_content = "♥" * self._lives
            text = self._lives_font.render(text_content, True, BRIGHT_RED)

        self._lives_text_rect = text.get_rect(
            bottomright=(
                GRID_TOPLEFT[0] + GRID_LENGTH,
                GRID_TOPLEFT[1] - PADDING,
            )
        )
        self._stats_surface.blit(text, self._lives_text_rect)

    def main_loop(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_click(*event.pos)
                elif event.type == pygame.KEYDOWN:
                    self._handle_key_press(event.key)

            if not self._grid_locked and self._game_mode != "Custom":
                current_time = pygame.time.get_ticks()
                if current_time - self._last_time >= ONE_SECOND:
                    self._total_seconds += 1
                    self._last_time = current_time
                    self._draw_timer()

            self._update_display()
            clock.tick(60)

    def _handle_mouse_click(self, x: float, y: float) -> None:
        row = (y - GRID_TOPLEFT[1]) // CELL_LENGTH
        col = (x - GRID_TOPLEFT[0]) // CELL_LENGTH
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            if self._grid_locked:
                return
            self._unselect_selected()
            self._select_cell(row, col)
            self._update_display()
            return

        for button in self._buttons:
            if button.rect.collidepoint(x, y):
                button.handle_click()
                return

    def _handle_key_press(self, key_pressed) -> None:
        if (
            self._game_mode == "Custom"
            and self._solutions
            and key_pressed in {pygame.K_LEFT, pygame.K_RIGHT}
        ):
            self._handle_solutions_navigation(key_pressed)
            return

        if self._grid_locked:
            return

        if key_pressed == pygame.K_BACKSPACE:
            self._erase_at_selected()
        elif pygame.K_1 <= key_pressed <= pygame.K_9:
            self._put_at_selected(int(pygame.key.name(key_pressed)))
        elif key_pressed in DIRECTIONS:
            self._handle_board_navigation(key_pressed)

        self._update_display()

    def _handle_board_navigation(self, key_pressed) -> None:
        d_row, d_col = DIRECTIONS[key_pressed]
        row, col = self._selected_row + d_row, self._selected_col + d_col
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            self._unselect_selected()
            self._select_cell(row, col)

    def _handle_solutions_navigation(self, key_pressed) -> None:
        if key_pressed == pygame.K_LEFT and self._current_solution_index > 0:
            self._current_solution_index -= 1
        elif key_pressed == pygame.K_RIGHT and self._current_solution_index < len(
            self._solutions
        ):
            self._current_solution_index += 1

        self._solution = self._solutions[self._current_solution_index]
        self._show_solution()

    def _put_at_selected(self, num: int) -> None:
        if self._selected_is_clue() or num == self._num_at_selected():
            return

        self._erase_at_selected()

        if self._game_mode == "Custom":
            if self._cached_board.can_put(num, self._selected_row, self._selected_col):
                self._cached_board.put(num, self._selected_row, self._selected_col)
                self._draw_number_at_selected(num)
            return

        self._board[self._selected_row][self._selected_col] = num
        self._draw_number_at_selected(num)

        if num == self._solution_at_selected():
            self._highlight_selected(GREEN)
            if all(
                self._board[row][col]
                for col in range(GRID_SIZE)
                for row in range(GRID_SIZE)
            ):
                self._grid_locked = True
        else:
            self._highlight_selected(RED)
            self._lives -= 1
            self._draw_lives()

    def _erase_at_selected(self) -> None:
        if self._selected_is_clue() or (
            not self._num_at_selected() and not self._grid_locked
        ):
            return

        if self._game_mode == "Custom":
            self._cached_board.erase(self._selected_row, self._selected_col)
        else:
            self._board[self._selected_row][self._selected_col] = 0
        rect = self._selected_cell_rect()
        pygame.draw.rect(self._grid_numbers_surface, ERASE_COLOR, rect)
        self._highlight_selected(LIGHT_GRAY)

    def _get_empty_cells(self) -> list[list[int]]:
        return [
            [row, col]
            for row in range(GRID_SIZE)
            for col in range(GRID_SIZE)
            if not self._board[row][col]
        ]

    def _load_all_solutions(self) -> None:
        self._clues = [row.copy() for row in self._board]
        self._cached_board.empty_cells = self._get_empty_cells()

        for solution in all_solutions(self._cached_board):
            self._solutions.append([row.copy() for row in solution])
            if len(self._solutions) == MAX_SOLUTONS:
                break

    def _display_solutions_count(self) -> None:
        count = len(self._solutions)
        text = (
            f"{count} Solutions < | >"
            if count < MAX_SOLUTONS
            else f"{MAX_SOLUTONS}+ Solutions < | >"
        )
        solutions_count_text = self._solutions_count_font.render(text, True, BRIGHT_RED)
        solutions_count_rect = solutions_count_text.get_rect(
            bottomleft=(GRID_TOPLEFT[0] + THICK_THICKNESS, GRID_TOPLEFT[1] - PADDING)
        )
        self._stats_surface.blit(solutions_count_text, solutions_count_rect)

    def _show_solution(self) -> None:
        self._grid_locked = True
        self._unselect_selected()

        if not self._solution:
            self._load_all_solutions()
            if len(self._solutions) > 1:
                self._display_solutions_count()

            self._solution = self._solutions[self._current_solution_index]

        self._grid_numbers_surface.fill(ERASE_COLOR)
        self._display_clues()
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self._clues[row][col]:
                    continue
                self._select_cell(row, col)
                self._draw_number_at_selected(self._solution_at_selected())
                self._highlight_selected(GREEN)

    def _solve_step_by_step(self) -> None:
        self._grid_locked = True

        if not self._solution:
            self._clues = [row.copy() for row in self._board]
            self._cached_board.empty_cells = self._get_empty_cells()
            board = self._cached_board
        else:
            board = CachedBoard([row.copy() for row in self._clues])

        self._grid_numbers_surface.fill(ERASE_COLOR)
        self._display_clues()

        for instruction, args in solve_step_by_step(board):
            if instruction == "Select":
                self._unselect_selected()
                self._select_cell(*args)
            elif instruction == "Erase":
                rect = self._selected_cell_rect()
                self._grid_numbers_surface.fill(ERASE_COLOR, rect)
                self._highlight_selected(LIGHT_GRAY)
            else:
                self._draw_number_at_selected(*args)

            self._update_display()

        self._solution = board.board
        self._show_solution()

    def _update_display(self) -> None:
        self._screen.blit(self._background_surface, (0, 0))
        self._screen.blit(self._grid_highlighting_surface, (0, 0))
        self._screen.blit(self._grid_numbers_surface, (0, 0))
        self._screen.blit(self._stats_surface, (0, 0))
        self._screen.blit(self._buttons_surface, (0, 0))
        pygame.display.flip()
