import pygame
from random import randint


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[randint(0, 1) for i in range(width)] for _ in range(height)]
        # значения по умолчанию
        self.left = 40
        self.top = 40
        self.cell_size = 40
        self.turn = 0

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        left = self.left
        top = self.top
        s = self.cell_size
        for y in range(self.height):
            for x in range(self.width):
                col = (255, 0, 0) if not (self.board[y][x]) else (0, 0, 255)
                # pygame.draw.rect(screen, col, (x * s + left, y * s + top, s, s))
                coords = (x * s + left + s // 2, y * s + top + s // 2)
                pygame.draw.circle(screen, col, coords, s // 2)
                pygame.draw.rect(screen, (255, 255, 255), (x * s + left, y * s + top, s, s), 1)

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None
        res = [(cell_x, cell_y)]
        for i in range(self.height):
            res.append((cell_x, i))
        for i in range(self.width):
            res.append((i, cell_y))
        return res

    def on_click(self, cells):
        for i, j in cells:
            self.board[j][i] = (self.board[j][i] + 1) % 2

    def get_click(self, mouse_pos):
        cells = self.get_cell(mouse_pos)
        cell = cells[0]
        if self.board[cell[1]][cell[0]] == self.turn:
            self.on_click(cells)
            self.turn = (self.turn + 1) % 2


if __name__ == '__main__':
    n = int(input())
    pygame.init()
    size = width, height = (n + 2) * 40, (n + 2) * 40
    screen = pygame.display.set_mode(size)
    r = 0
    fps = 60
    clock = pygame.time.Clock()
    board = Board(n, n)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
        screen.fill((0, 0, 0))
        board.render(screen)
        pygame.display.flip()
    pygame.quit()
