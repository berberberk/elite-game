import pygame
from settings import *
from timer import Timer


class PlanetPlayer(pygame.sprite.Sprite):
    def __init__(self, pos, group, coll_pos):
        super().__init__(group)

        self.image_status = "idle"  # для определения какого направления спрайт вставлять
        self.image_frame = 1  # для реализации анимации
        # для анимации нужны несколько картиок в одном направлении, чтобы они менялись каждые несколько милисекунд

        self.image = self.import_image().convert_alpha()
        self.rect = self.image.get_rect(center=pos)

        # movement attributes
        self.direction = pygame.math.Vector2()  # направление, определяется вектором. Во время обновления координаты игрока меняются в зависимости от направления
        self.pos = pygame.math.Vector2(self.rect.center)  # координаты игрока
        self.speed = 300
        self.max_hp = 1000
        self.hp = 1000
        self.max_stamina = 500
        self.stamina = 500
        self.coll_pos = coll_pos
        # fkags
        self.statx = 1
        self.staty = 1
        # mask
        self.objects = coll_pos
        self.mask = pygame.mask.from_surface(self.image)
        # Таймеры
        self.timers = {
            'tool use': Timer(30, self.use_tool),
            'tool switch': Timer(200)
        }

        # Инструменты
        self.tools = ['hand', 'sword', 'gun']
        self.tools_sprites = {}
        self.import_tools_sprites()
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

    def import_image(self):
        path = "Images/Player/" + self.image_status + str(int(self.image_frame) + 1) + ".png"
        now_image = pygame.image.load(path).convert_alpha()
        now_image = pygame.transform.scale(now_image, (64, 64))
        return now_image

    def import_tools_sprites(self):
        for tool in self.tools:
            path = "Images/tools/" + tool + ".png"
            try:
                tool_sprite = pygame.image.load(path).convert_alpha()
                tool_sprite = pygame.transform.scale(tool_sprite, (50, 50))
            except FileNotFoundError:
                if tool == 'hand':
                    tool_sprite = pygame.surface.Surface((50, 50))
                    tool_sprite.fill('green')
                if tool == 'gun':
                    tool_sprite = pygame.surface.Surface((50, 50))
                    tool_sprite.fill('pink')
            self.tools_sprites[tool] = tool_sprite

    def animate(self, dt):

        self.image_frame += 6 * dt
        if "attack" in self.image_status:
            if self.image_frame >= 3:
                self.image_status = "idle"
                self.image_frame = 0
        else:
            if self.image_frame >= 5:  # больше 6, потому что количество спрайтов для анимации равно 6
                self.image_frame = 0

        self.image = self.import_image()

    def input(self):
        keys = pygame.key.get_pressed()
        self.statx = 1
        self.staty = 1
        # Если игрок в процессе использования инструмента,
        # он не может двигаться и сменить инструмент
        if not self.timers['tool use'].active:
            # Передвижение на WASD
            if keys[pygame.K_w]:
                self.direction.y = -1
                _image_status = "up"
            elif keys[pygame.K_s]:
                self.direction.y = 1
                _image_status = "down"
            else:
                self.direction.y = 0

            if keys[pygame.K_a]:
                self.direction.x = -1
                _image_status = "left"
            elif keys[pygame.K_d]:
                self.direction.x = 1
                _image_status = "right"
            else:
                self.direction.x = 0

            if self.direction.x == 0 and self.direction.y == 0:  # если остаемся на месте
                _image_status = "idle"

            if not "attack" in self.image_status:
                self.image_status = _image_status

            # Использование инструмента
            if keys[pygame.K_p]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.image_frame = 0
                if self.selected_tool == "sword":
                    if not "attack" in self.image_status:
                        if self.image_status == "idle":
                            self.image_status = "down"
                        self.image_status = "attack_"+self.image_status
                        self.image_frame = 0


            # Смена инструмента
            if keys[pygame.K_TAB] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                if self.tool_index >= len(self.tools):
                    self.tool_index = 0
                self.selected_tool = self.tools[self.tool_index]


    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def use_tool(self):
        pass

    def move(self, dt, objects):
        for i in range(len(self.coll_pos)):

            current_x = [col_pos[0] for col_pos in self.coll_pos[i]]  # все иксы осязаемых объектов
            current_y = [col_pos[1] for col_pos in self.coll_pos[i]]  # все игреки
            for i in range(len(current_x)):

                if abs(current_x[
                           i] + 15 - self.pos.x - self.direction.x * self.speed * dt) <= EPS:  # если близко подошли к икс координате осязаемого объекта
                    self.statx = 0
                    break
                else:
                    self.statx = 1

            for i in range(len(current_y)):
                if abs(current_y[
                           i] - self.pos.y - self.direction.y * self.speed * dt) <= EPS:  # если к игрек координате
                    self.staty = 0
                    break
                else:
                    self.staty = 1
            if self.staty + self.statx == 0:
                break
        # Нормализация вектора. Это нужно, чтобы скорость по диагонали была такая же
        if self.direction.magnitude() > 0:  # если мы куда-то двигаемся то нормализуем
            self.direction = self.direction.normalize()

        # перемещение по горизонтали
        self.statx = self.statx + self.staty
        if self.statx:
            self.pos.x += self.direction.x * self.speed * dt  # обновляем позицию игрока в зависимости от направления и скорости
        else:
            self.pos.x += 0

        self.rect.centerx = self.pos.x  # устанавливаем центр спрайта в текущую позицию игрока

        # перемещение по вертикали
        self.staty = self.staty + self.statx
        if self.staty:
            self.pos.y += self.direction.y * self.speed * dt  # обновляем позицию игрока в зависимости от направления и скорости

        else:
            self.pos.y += 0

        self.rect.centery = self.pos.y  # устанавливаем центр спрайта в текущую позицию игрока

    def update(self, dt):
        self.input()
        self.update_timers()

        self.move(dt, self.objects)
        self.animate(dt)