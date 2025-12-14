import pygame
import random
import time


pygame.init()  
WIDTH, HEIGHT = 600, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Engine | Generator & Solver")


WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
BLUE = (52, 152, 219)       
GREEN = (46, 204, 113)      
RED = (231, 76, 60)         
GRAY = (200, 200, 200)      
BTN_COLOR = (44, 62, 80)
BTN_HOVER = (52, 73, 94)

NUM_FONT = pygame.font.SysFont("roboto", 40)
UI_FONT = pygame.font.SysFont("roboto", 24)

class SudokuGenerator:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]

    def is_safe(self, row, col, num):
        for x in range(9):
            if self.board[row][x] == num or self.board[x][col] == num:
                return False
        start_row, start_col = row - row % 3, col - col % 3
        for i in range(3):
            for j in range(3):
                if self.board[i + start_row][j + start_col] == num:
                    return False
        return True

    def fill_diagonal(self):
        for i in range(0, 9, 3):
            self.fill_box(i, i)

    def fill_box(self, row, col):
        num = 0
        for i in range(3):
            for j in range(3):
                while True:
                    num = random.randint(1, 9)
                    if self.is_safe_in_box(row, col, num):
                        break
                self.board[row + i][col + j] = num

    def is_safe_in_box(self, row_start, col_start, num):
        for i in range(3):
            for j in range(3):
                if self.board[row_start + i][col_start + j] == num:
                    return False
        return True

    def fill_remaining(self, i, j):
        if j >= 9 and i < 8:
            i += 1
            j = 0
        if i >= 9 and j >= 9:
            return True
        if i < 3:
            if j < 3: j = 3
        elif i < 6:
            if j == (i // 3) * 3: j += 3
        else:
            if j == 6:
                i += 1
                j = 0
                if i >= 9: return True

        for num in range(1, 10):
            if self.is_safe(i, j, num):
                self.board[i][j] = num
                if self.fill_remaining(i, j + 1):
                    return True
                self.board[i][j] = 0
        return False

    def remove_digits(self, count):
        while count != 0:
            cell_id = random.randint(0, 80)
            i = cell_id // 9
            j = cell_id % 9
            if self.board[i][j] != 0:
                count -= 1
                self.board[i][j] = 0

    def generate_puzzle(self, difficulty=40):
        self.fill_diagonal()
        self.fill_remaining(0, 3)
        solution = [row[:] for row in self.board] 
        self.remove_digits(difficulty)
        return self.board, solution

class Button:
    def __init__(self, x, y, w, h, text, func):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.func = func
        self.hovered = False

    def draw(self, win):
        color = BTN_HOVER if self.hovered else BTN_COLOR
        pygame.draw.rect(win, color, self.rect, border_radius=5)
        text_surf = UI_FONT.render(self.text, True, WHITE)
        win.blit(text_surf, (self.rect.x + (self.rect.width - text_surf.get_width()) // 2, 
                             self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.func()

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

grid = []
original_grid = []
solution_grid = []

def get_empty_cell(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)
    return None

def is_valid_move(bo, num, pos):
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i: return False
        if bo[i][pos[1]] == num and pos[0] != i: return False

    box_x, box_y = pos[1] // 3, pos[0] // 3
    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x*3, box_x*3 + 3):
            if bo[i][j] == num and (i,j) != pos: return False
    return True

def draw_grid(win, curr_grid):
    gap = WIDTH // 9
    for i in range(10):
        if i % 3 == 0:
            thickness = 4
        else:
            thickness = 1
            
        pygame.draw.line(win, BLACK, (0, i * gap), (WIDTH, i * gap), thickness)
        pygame.draw.line(win, BLACK, (i * gap, 0), (i * gap, WIDTH), thickness)

    for i in range(9):
        for j in range(9):
            val = curr_grid[i][j]
            if val != 0:
                color = BLUE if original_grid[i][j] != 0 else GREEN
                text = NUM_FONT.render(str(val), 1, color)
                x = j * gap + (gap/2 - text.get_width()/2)
                y = i * gap + (gap/2 - text.get_height()/2)
                win.blit(text, (x, y))

def solve_visualizer(win, bo):
    pygame.event.pump() 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return True

    find = get_empty_cell(bo)
    if not find: return True
    row, col = find

    for i in range(1, 10):
        if is_valid_move(bo, i, (row, col)):
            bo[row][col] = i
            
            win.fill(WHITE)
            draw_grid(win, bo)
            pygame.draw.rect(win, RED, (col * (WIDTH//9), row * (WIDTH//9), WIDTH//9, WIDTH//9), 3)
            pygame.display.update()
            


            if solve_visualizer(win, bo): return True

            bo[row][col] = 0 
            
            win.fill(WHITE)
            draw_grid(win, bo)
            pygame.draw.rect(win, RED, (col * (WIDTH//9), row * (WIDTH//9), WIDTH//9, WIDTH//9), 3)
            pygame.display.update()

    return False

def generate_new_game():
    global grid, original_grid, solution_grid
    gen = SudokuGenerator(9, 9)
    grid, solution_grid = gen.generate_puzzle(difficulty=40) 
    original_grid = [row[:] for row in grid]

def start_solving():
    if get_empty_cell(grid):
        solve_visualizer(WIN, grid)

def main():
    run = True
    generate_new_game()
    
    btn_new = Button(50, 650, 200, 50, "Generate New", generate_new_game)
    btn_solve = Button(350, 650, 200, 50, "Visualize Solver", start_solving)

    while run:
        WIN.fill(WHITE)
        draw_grid(WIN, grid)
        
        btn_new.draw(WIN)
        btn_solve.draw(WIN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                btn_new.check_click(pos)
                btn_solve.check_click(pos)
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                btn_new.check_hover(pos)
                btn_solve.check_hover(pos)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()