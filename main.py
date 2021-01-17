import os
import sys
import random
import pygame

FPS = 50
N = M = 800
TILE_SIZE = 80
# <<<<<<< HEAD
masOfGrass = list()
# =======
isQuestionAsked = False


# >>>>>>> 78f49a6489c56628f26d62b80322abb424ff5fe9

# Изображение не получится загрузить
# без предварительной инициализации pygame


def load_image(name, colorkey=None):
    fullname = os.path.join('pictures', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def generate_level(level):
    new_player, x, y = None, None, None
    playerxy = (0, 0)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile(random.choice(masOfGrass), x, y)
            elif level[y][x] == 'e':
                Tile(random.choice(masOfGrass), x, y)
                Enemy(load_image('enemy.png', -1), 3, 2, x, y)
            elif level[y][x] == '@':
                Tile(random.choice(masOfGrass), x, y)
                playerxy = (x, y)
    new_player = Player(load_image("Main5.png", -1), 10, 8, *playerxy)
    # new_player = Player(load_image("test.png", -1), 10, 8, *playerxy)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            TILE_SIZE * pos_x, TILE_SIZE * pos_y)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = [[] for _ in range(5)]
        self.status = 0
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.status][self.cur_frame]
        self.rect = self.rect.move(x * TILE_SIZE, y * TILE_SIZE)
        self.isAlive = True

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        cnt = 0
        for j in range(rows):
            p = 1 if j == 1 else columns
            for i in range(p):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames[cnt].append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
            cnt += 1

    def update(self):
        global isQuestionAsked
        self.change_frame()
        f = not isQuestionAsked and not self.status and player.canBeKiller
        if f and pygame.sprite.collide_mask(self, player):
            if not isQuestionAsked:
                ans = question_screen()
                isQuestionAsked = True
            if ans:
                self.status = 1
            else:
                player.isKiller = True

    def change_frame(self):
        self.cur_frame = (self.cur_frame + 0.2) % len(self.frames[self.status])
        self.image = self.frames[self.status][int(self.cur_frame)]


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(player_group, all_sprites)
        self.frames = [[] for _ in range(5)]
        self.direction = 0
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.direction][self.cur_frame]
        self.rect = self.rect.move(x * TILE_SIZE, y * TILE_SIZE)
        self.last_action = (0, 0)
        self.isKiller = False
        self.canBeKiller = True
        self.btns = {
            119: (0, -1),  # W
            97: (-1, 0),  # A
            115: (0, 1),  # S
            100: (1, 0)  # D
        }
        self.actions = {
            (0, -1): 3,
            (-1, 0): 2,
            (0, 1): 1,
            (1, 0): 4
        }

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        cnt = 0
        for j in range(rows):
            if 1 <= j <= 3:
                continue
            p = 3 if j == 0 else columns
            for i in range(p):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames[cnt].append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
            cnt += 1

    def update(self):
        self.change_frame()

    def change_frame(self):
        self.cur_frame = (self.cur_frame + 0.2) % len(self.frames[self.direction])
        self.image = self.frames[self.direction][int(self.cur_frame)]

    def do_move(self, key_number):
        x, y = self.btns.get(key_number, (None, None))
        if x is None:
            return
        self.moving(x, y)

    def moving(self, x, y):
        global isQuestionAsked
        self.direction = self.actions[(x, y)]
        self.last_action = (x, y)
        for i in range(80):
            self.rect = self.rect.move(x, y)
            redraw()
            camera_move()  # не супер производительно, но плавно
        self.direction = 0
        if self.isKiller:
            self.isKiller = False
            self.canBeKiller = False
            player.moving(player.last_action[0] * -1, player.last_action[1] * -1)
            self.canBeKiller = True
        isQuestionAsked = False
        # self.rect = self.rect.move(x * TILE_SIZE, y * TILE_SIZE)


class Button(pygame.sprite.Sprite):
    def __init__(self, name_file, x, y, group, type):
        super().__init__(group)
        self.frames = [[] for _ in range(5)]
        self.cur_frame = 0
        self.image = load_image(name_file)
        self.rect = pygame.Rect(0, 0, 60, 20)
        self.rect = self.rect.move(x, y)
        self.type = type

    def update(self, *args):
        if args and self.rect.collidepoint(args[0].pos):
            return True, self.type
        return False, False


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def terminate():
    pygame.quit()
    sys.exit()


def redraw():
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(fps)


def start_screen():
    global screen, clock
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('bg.jpg'), (N, M))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def question_screen():
    global screen, clock

    fon = pygame.transform.scale(load_image('bg.jpg'), (N // 4, M // 4))
    text = pygame.font.Font(None, 50).render('Kill him?', True, (255, 255, 255))
    question_group = pygame.sprite.Group()
    window_x, window_y = N // 2 - 100, M // 2 - 100
    answer = (False, False)
    screen.blit(fon, (window_x, window_y))
    screen.blit(text, [window_x + 10, window_y + 50])
    btn1 = Button('acceptBtn.png', window_x + 10, window_y + 100, question_group, True)
    btn2 = Button('declineBtn.png', window_x + 110, window_y + 100, question_group, False)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                answer = max(btn1.update(event), btn2.update(event))
        if answer[0]:
            for i in question_group:
                i.kill()
            return answer[1]
        question_group.update()
        question_group.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


def camera_move():
    # изменяем ракурс камеры
    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)


if __name__ == '__main__':
    pygame.init()
    camera = Camera()
    size = width, height = N, M
    screen = pygame.display.set_mode(size)
    masOfGrass = ["empty1", "empty2", "empty3"]
    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png'),
        'empty1': load_image('grass1.png'),
        'empty2': load_image('grass2.png'),
        'empty3': load_image('grass3.png'),
    }

    # основной персонаж

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    field = ['................',
             '................',
             '..eee...........',
             '................',
             '..@.............',
             '................',
             '................',
             '................',
             '................',
             '................']
    player, w, h = generate_level(field)
    r = 0
    fps = 60
    clock = pygame.time.Clock()
    running = True
    start_screen()
    while running:
        camera_move()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                player.do_move(event.key)
            elif event.type == pygame.MOUSEWHEEL:
                question_screen()
        redraw()
    pygame.quit()
