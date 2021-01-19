import os
import sys
import random
import pygame

timer_time = 300
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

# метод возвращающий изображение
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


# случайная генерация поля
def do_generate():
    res = []
    for i in range(35):
        subres = []
        for j in range(35):
            if i == 5 or i == 29 or j == 5 or j == 29:
                subres.append('#')
            elif i < 5 or j < 5:
                subres.append('.')
            else:
                a = random.choice([False] * 9 + [True])
                if not a:
                    subres.append('.')
                else:
                    subres.append(random.choice(['e', 's']))
        res.append(subres)
    res[6][6] = '@'
    return res


# отрисовка уровня по полю
def draw_level(level):
    new_player, x, y = None, None, None
    playerxy = (0, 0)
    diff = 0
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile(random.choice(masOfGrass), x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == 'e':
                Tile(random.choice(masOfGrass), x, y)
                # Enemy(load_image('enemy.png', -1), 3, 2, x, y, random.randint(0, diff))
                Enemy(load_image('book3.png', -1), 1, 2, x, y, random.randint(0, diff))
                diff += 1
            elif level[y][x] == 's':
                Tile(random.choice(masOfGrass), x, y)
                # Learning(load_image('skillup.png', -1), 3, 2, x, y, random.randint(0, diff))
                Learning(load_image('book.png', -1), 1, 2, x, y, random.randint(0, diff))
                diff += 1
            elif level[y][x] == '@':
                Tile(random.choice(masOfGrass), x, y)
                playerxy = (x, y)

    new_player = Player(load_image("Main5.png", -1), 10, 8, *playerxy)
    # new_player = Player(load_image("test.png", -1), 10, 8, *playerxy)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


# загрузка уровня из файла - пока не реализовано
def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# клетка поля
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            TILE_SIZE * pos_x, TILE_SIZE * pos_y)


# объект урока- даёт плюс к скиллу и тратит время
class Learning(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, difficulty):
        super().__init__(all_sprites)
        self.frames = [[] for _ in range(5)]
        self.status = 0
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.status][self.cur_frame]
        self.rect = self.rect.move(x * TILE_SIZE, y * TILE_SIZE)
        self.isAlive = True
        self.difficulty = difficulty

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        cnt = 0
        for j in range(rows):
            if j == 1:
                p = 1
            else:
                p = columns
            for i in range(p):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames[cnt].append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
            cnt += 1

    def update(self):
        global isQuestionAsked
        self.change_frame()
        f1 = not isQuestionAsked
        f2 = not self.status
        f3 = player.NotGoingBackYet
        f = f1 and f2 and f3
        if f and pygame.sprite.collide_mask(self, player):
            ans = False
            if not isQuestionAsked:
                q = 'Listen Course?'
                s = f'Required score: {self.difficulty}'
                t = 'You will lost 10 sec'
                ans = question_screen([q, s, t])
                isQuestionAsked = True
            if ans:
                if player.xp < self.difficulty:
                    message_screen(['You don\'t have', 'enough score'])
                    player.NeedGoBack = True
                    return
                self.status = 1
                player.skill += 3
                player.time_left -= 10
            else:
                player.NeedGoBack = True

    def change_frame(self):
        self.cur_frame = int((self.cur_frame + 0.2) % len(self.frames[self.status]))
        self.image = self.frames[self.status][int(self.cur_frame)]


# объект задачи - даёт плюс к опыту и времени
class Enemy(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, difficulty):
        super().__init__(all_sprites)
        self.frames = [[] for _ in range(5)]
        self.status = 0
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.status][self.cur_frame]
        self.rect = self.rect.move(x * TILE_SIZE, y * TILE_SIZE)
        self.isAlive = True
        self.difficulty = difficulty

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
        f = not isQuestionAsked and not self.status and player.NotGoingBackYet
        if f and pygame.sprite.collide_mask(self, player):
            ans = False
            if not isQuestionAsked:
                t = 'You will get 11 sec'
                ans = question_screen(['Solve it?', f'You need skill {self.difficulty}', t])
                isQuestionAsked = True
            if ans:
                if player.skill < self.difficulty:
                    message_screen(['You do not have', 'enough skill'])
                    player.NeedGoBack = True
                    return
                self.status = 1
                player.xp += 2
                player.time_left += 11
            else:
                player.NeedGoBack = True

    def change_frame(self):
        self.cur_frame = int((self.cur_frame + 0.2) % len(self.frames[self.status]))
        self.image = self.frames[self.status][int(self.cur_frame)]

# основной класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(player_group, all_sprites)
        self.frames = [[] for _ in range(5)]
        self.skill = 3
        self.xp = 0
        self.time_left = timer_time
        self.direction = 0
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.direction][self.cur_frame]
        self.coords = (x, y)
        self.rect = self.rect.move(x * TILE_SIZE + 20, y * TILE_SIZE)
        self.last_action = (0, 0)
        self.NeedGoBack = False
        self.NotGoingBackYet = True
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
        # print(self.rect.y // TILE_SIZE + y, self.rect.x // TILE_SIZE + x)
        if field[self.coords[0] + x][self.coords[1] + y] == '#':
            return
        self.direction = self.actions[(x, y)]
        self.last_action = (x, y)
        speedk = 2  # коэффициент ускорения
        for i in range(80 // speedk):
            self.rect = self.rect.move(x * speedk, y * speedk)
            redraw()
            camera_move()  # не супер производительно, но плавно
        self.coords = (self.coords[0] + x, self.coords[1] + y)
        self.direction = 0
        if self.NeedGoBack:
            self.NeedGoBack = False
            self.NotGoingBackYet = False
            player.moving(player.last_action[0] * -1, player.last_action[1] * -1)
            self.NotGoingBackYet = True
        isQuestionAsked = False
        # self.rect = self.rect.move(x * TILE_SIZE, y * TILE_SIZE)

# класс кнопки выбора
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

# камера - сдвигает все объекты в нужную сторону
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

# корректное завершение программы
def terminate():
    pygame.quit()
    sys.exit()

# перерисовка всех объеектов на поле
def redraw():
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    all_sprites.update()
    make_stat()
    pygame.display.flip()
    clock.tick(fps)

# превести время к нормальному виду
def format_time(m):
    res1 = str(m // 60)
    res2 = str(m % 60)
    res1 = '0' * (2 - len(res1)) + res1
    res2 = '0' * (2 - len(res2)) + res2
    res = res1 + ':' + res2
    return res

# вывести статистику персонажа
def make_stat():
    fon = pygame.transform.scale(load_image('stat_bg.png'), (190, 130))
    screen.blit(fon, (N - 190, 0))
    t = 'deadline in: ' + format_time(player.time_left)
    s = 'skill: ' + str(player.skill)
    xp = 'Yandex.Score: ' + str(player.xp)
    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in [t, s, xp]:
        string_rendered = font.render(line, True, pygame.Color('green'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = N - 170
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

# экран входа - приветствие и правила
def start_screen():
    global screen, clock
    fon = pygame.transform.scale(load_image('intro.png'), (N, M))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)

# экран сообщающий что либо
def message_screen(message):
    global screen, clock

    fon = pygame.transform.scale(load_image('bg.jpg'), (N // 4, M // 4))
    window_x, window_y = N // 2 - 100, M // 2 - 100
    screen.blit(fon, (window_x, window_y))
    font = pygame.font.Font(None, 30)
    text_coord = window_y + 10
    for line in message:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = window_x + 10
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

# экран спрашивающий что-либо
def question_screen(message):
    global screen, clock

    fon = pygame.transform.scale(load_image('bg.jpg'), (N // 4, M // 4))
    font = pygame.font.Font(None, 30)
    question_group = pygame.sprite.Group()
    window_x, window_y = N // 2 - 100, M // 2 - 100
    answer = (False, False)
    text_coord = window_y + 20
    screen.blit(fon, (window_x, window_y))
    for line in message:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = window_x + 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    btn1 = Button('acceptBtn.png', window_x + 10, window_y + 170, question_group, True)
    btn2 = Button('declineBtn.png', window_x + 110, window_y + 170, question_group, False)
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

# сдвигаем всех на координаты поля
def camera_move():
    # изменяем ракурс камеры
    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)

# основной код
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
    field = do_generate()
    player, w, h = draw_level(field)
    r = 0
    fps = 60
    clock = pygame.time.Clock()
    running = True
    # начинаем
    start_screen()
    # запускаем таймер
    MYEVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(MYEVENT, 1000)
    while running:
        camera_move()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                player.do_move(event.key)
            elif event.type == MYEVENT:
                player.time_left -= 1
        redraw()
        make_stat()
        if player.time_left <= 0:
            running = False
    # игра окончена
    message_screen(['GAME OVER', f'YOUR SCORE  {player.xp}', f'YOUR SKILL  {player.skill}'])
    terminate()
