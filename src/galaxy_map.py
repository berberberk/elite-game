import pygame
from math import sqrt
from timer import Timer
from settings import *


class Planet(pygame.sprite.Sprite):
    def __init__(self, image, pos, radius, group):
        super().__init__(group)
        self.pos = pos
        self.radius = radius
        self.image = image
        self.image = pygame.transform.scale(self.image, (self.radius * 10, self.radius * 10))
        self.rect = self.image.get_rect(center=self.pos)


class CameraGroup(pygame.sprite.Group):
    def __init__(self, surface, galaxy, player):
        super().__init__()
        self.display_surface = surface
        self.galaxy = galaxy
        self.player = player

        for system in self.galaxy.systems:
            system.x += MAP_WIDTH // 8
            system.y += MAP_HEIGHT // 8
            if system == self.player.current_planet:  # если это текущая планета игрока, то рисуем одним цветом
                system.sprite = Planet(CURRENT_PLANET_IMAGE.convert_alpha(), (system.x, system.y), 5, self)
            elif system in self.player.visited_planets:  # если это посещенная планета, то другим
                system.sprite = Planet(STANDARD_PLANET_IMAGE.convert_alpha(), (system.x, system.y), 3, self)
            else:
                if system.gold_planet != 0:
                    system.sprite = Planet(SUPER_FUEL_PLANET_IMAGE.convert_alpha(), (system.x, system.y), 4, self)
                elif system.fuel_station_value != 0:
                    system.sprite = Planet(FUEL_STATION_PLANET_IMAGE.convert_alpha(), (system.x, system.y), 3, self)
                else:
                    system.sprite = Planet(STANDARD_PLANET_IMAGE.convert_alpha(), (system.x, system.y), 3, self)

        # camera offset
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # box setup
        self.camera_borders = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        self.camera_rect = self.camera_rect_setup()

        background_image = pygame.image.load('../Images/galaxy_map_square_background.png').convert_alpha()
        self.background_surf = pygame.transform.scale(background_image, (MAP_WIDTH * 1.25, MAP_HEIGHT * 1.25))
        self.background_rect = self.background_surf.get_rect(topleft=(0, 0))

        # camera speed
        self.keyboard_speed = 20
        self.mouse_speed = 0.2

        # zoom
        self.zoom_scale = 1
        self.internal_surf_size = (MAP_WIDTH, MAP_HEIGHT)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center=(self.half_w, self.half_h))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_h

        self.scaled_surf = None
        self.scaled_rect = None

    def camera_rect_setup(self):
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        return pygame.Rect(l, t, w, h)

    def center_target_camera(self, target):
        self.offset = pygame.math.Vector2(target.sprite.rect.centerx - self.half_w,
                                          target.sprite.rect.centery - self.half_h)

    def keyboard_control(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.camera_rect.x -= self.keyboard_speed
        if keys[pygame.K_RIGHT]:
            self.camera_rect.x += self.keyboard_speed
        if keys[pygame.K_UP]:
            self.camera_rect.y -= self.keyboard_speed
        if keys[pygame.K_DOWN]:
            self.camera_rect.y += self.keyboard_speed

        self.offset.x += self.camera_rect.left - self.camera_borders['left']
        self.offset.y += self.camera_rect.top - self.camera_borders['top']

    def zoom_keyboard_control(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_EQUALS] and self.zoom_scale - 2 < 0.05:
            self.zoom_scale += 0.05
        if keys[pygame.K_MINUS] and self.zoom_scale - 0.20 > 0.05:
            self.zoom_scale -= 0.05

    def draw(self):
        self.center_target_camera(self.player.current_planet)
        self.keyboard_control()
        self.zoom_keyboard_control()

        self.internal_surf.fill((0, 0, 0))
        background_offset = self.background_rect.topleft - self.offset + self.internal_offset
        self.internal_surf.blit(self.background_surf, background_offset)

        self.player.current_planet.sprite.kill()
        self.player.current_planet.sprite = Planet(CURRENT_PLANET_IMAGE,
                                                   (self.player.current_planet.x, self.player.current_planet.y), 5,
                                                   self)
        for match in self.galaxy.matches[self.player.current_planet]:
            if match in self.player.visited_planets:
                match.sprite.kill()
                match.sprite = Planet(STANDARD_PLANET_IMAGE, (match.x, match.y), 3, self)
            pygame.draw.line(self.internal_surf, EDGES_COLOR,
                             self.player.current_planet.sprite.rect.center - self.offset + self.internal_offset,
                             match.sprite.rect.center - self.offset + self.internal_offset, 2)
        # active elements
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset + self.internal_offset
            self.internal_surf.blit(sprite.image, offset_pos)

        self.scaled_surf = pygame.transform.scale(self.internal_surf,
                                                  self.internal_surface_size_vector * self.zoom_scale)
        self.scaled_rect = self.scaled_surf.get_rect(center=(self.half_w, self.half_h))

        self.display_surface.blit(self.scaled_surf, self.scaled_rect)


class Map:
    def __init__(self, galaxy, player):
        self.jump_rect_planet = None
        self.cursor_is_within_jump_rect = False
        self.galaxy = galaxy
        self.player = player
        self.all_sprites = pygame.sprite.Group()
        self.map_screen = pygame.surface.Surface((MAP_PANEL_WIDTH, MAP_PANEL_HEIGHT))
        self.camera_group = CameraGroup(self.map_screen, self.galaxy, self.player)
        self.border = pygame.surface.Surface(
            (SCREEN_WIDTH - MAP_PANEL_WIDTH, SCREEN_HEIGHT))  # Для работы с областью справа
        self.rect = self.map_screen.get_rect()

        self.timers = {'out of fuel': Timer(1000)}

    def distance_to(self, destination_planet):
        return int(4 * sqrt(
            (self.player.current_planet.x - destination_planet.x) * (
                    self.player.current_planet.x - destination_planet.x) + (
                    self.player.current_planet.y - destination_planet.y) * (
                    self.player.current_planet.y - destination_planet.y) / 4))

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def draw(self):
        self.camera_group.update()
        self.update_timers()
        self.camera_group.draw()

    def draw_side_panel(self, surface, fuel, ration, checked_mouse):
        LEN_CONST = 200 / FUEL_CONST
        len_of_bar = fuel * LEN_CONST  # Нормировка длины полоски

        if self.player.fuel > self.player.fuel_const:
            const_len_of_bar = self.player.fuel * LEN_CONST  # Расширяет основную шкалу топлива, если топливо стало больше, чем было изначально(можно, конено, ограничить всё нововедённой переменной)
            des_of_bar_save = self.player.fuel * LEN_CONST
            self.player.fuel_const = self.player.fuel

        else:
            const_len_of_bar = self.player.fuel_const * LEN_CONST  # Постоянная длина синих границ полоски
            des_of_bar_save = self.player.bar_save * LEN_CONST  # Для сохранения координаты, до куда в прошлый раз коцнулась полоска
        len_of_got_bar = 0
        len_of_spent_bar = (des_of_bar_save - len_of_bar)  # Длина коцки
        if len_of_spent_bar < 0:
            len_of_spent_bar = 0
            len_of_got_bar = len_of_bar - des_of_bar_save

        pygame.draw.rect(self.map_screen, (255, 255, 255), self.rect, 2)
        self.border.fill((0, 0, 0))

        pygame.draw.rect(self.border, (255, 255, 255), (-2, 448, 302, 302), 2)  # границы полей справа, область снизу
        pygame.draw.rect(self.border, (255, 255, 255), (-2, 352, 302, 98), 2)  # область по середине
        pygame.draw.rect(self.border, (255, 255, 255), (-2, 0, 302, 354), 2)  # верхняя область

        pygame.draw.rect(self.border, (0, 0, 255), (3, 315, const_len_of_bar, 35), 5)  # Параметры полоски топлива
        pygame.draw.rect(self.border, (255, 0, 0), (6, 320, const_len_of_bar - 7, 25), 13)
        pygame.draw.rect(self.border, (0, 255, 0), (6, 320, len_of_bar - 7, 25), 13)

        pygame.font.init()  # инициализация текста
        my_font = pygame.font.SysFont('Century Gothic', 15, True)  # его параметры
        text_surface = my_font.render(f'У вас топлива: {self.player.fuel}, max: {MAX_FUEL_VALUE}', False,
                                      (255, 255, 255))
        text2 = my_font.render(f'Вы находитесь на планете: ', False, (255, 255, 255))
        text3 = my_font.render(f'{self.player.current_planet.name}', False, (255, 255, 255))
        text4 = my_font.render(f'Тип планеты: ', False, (255, 255, 255))
        text5 = my_font.render(f'{self.player.current_planet.type}', False, (255, 255, 255))
        text6 = my_font.render(f'Ресурсы: ', False, (255, 255, 255))
        text7 = my_font.render(f'Топливо: ', False, (255, 255, 255))
        text12 = my_font.render(f"", False, (0, 0, 0))
        text9 = my_font.render("", False, (255, 255, 255))
        text8 = my_font.render(f'{self.player.current_planet.fuel_station_value_save}', False, (255, 255, 255))
        text13 = text10 = text11 = my_font.render(f"", False, (0, 0, 0))
        text15 = my_font.render(f"Кол-во посещённых планет: {len(self.player.visited_planets)}", False, (255, 255, 255))
        if checked_mouse in self.player.visited_planets:
            text9 = my_font.render(f'Планета : {checked_mouse.name}', False,
                                   (255, 255, 255))  # Пошла информация о наведённой курсором планете
            # text10 = my_font.render(f'Доступные ресурсы: ', False, (255, 255, 255))
            # text11 = my_font.render(f'Топливо: {checked_mouse.fuel_station_value}', False, (255, 255, 255))
            text12 = my_font.render(f'Необходимо топлива: {self.distance_to(checked_mouse)}', False, (255, 255, 255))
            checked_mouse_name_txt = my_font.render(checked_mouse.name, False, (255, 255, 255))
        elif checked_mouse in self.galaxy.matches[self.player.current_planet]:
            text9 = my_font.render(f'Планета : {checked_mouse.name}', False, (255, 255, 255))
            text12 = my_font.render(f'Необходимо топлива: {self.distance_to(checked_mouse)}', False, (255, 255, 255))
            checked_mouse_name_txt = my_font.render(checked_mouse.name, False, (255, 255, 255))
        elif checked_mouse in self.galaxy.systems:
            text13 = my_font.render(f'Неисследованная планета', False, (255, 255, 255))
            text12 = my_font.render('Необходимо топлива: неизвестно', False, (255, 255, 255))
            checked_mouse_name_txt = my_font.render(f"", False, (0, 0, 0))
        else:
            text9 = my_font.render("Космическое пространство", False, (255, 255, 255))
            text12 = text13 = text10 = text11 = checked_mouse_name_txt = my_font.render(f"", False, (0, 0, 0))

        pygame.draw.rect(self.border, (255, 255, 0),
                         (des_of_bar_save - len_of_spent_bar - 1, 320, len_of_spent_bar * int(ration) / 100, 25),
                         13)  # Анимированный расход топлива
        pygame.draw.rect(self.border, (255, 0, 255), (
            des_of_bar_save + len_of_got_bar * int(-ration) / 100 + len_of_got_bar, 320,
            len_of_got_bar * int(ration) / 100,
            25), 14)

        self.border.blit(text_surface, (40, 5))  # У вас топлива
        self.border.blit(text2, (40, 25))  # Вы находитесь
        self.border.blit(text3, (40, 40))
        self.border.blit(text4, (40, 65))  # Тип планеты
        self.border.blit(text5, (40, 80))
        self.border.blit(text6, (40, 105))  # Ресурсы
        self.border.blit(text7, (40, 120))
        self.border.blit(text15, (40, 140))
        self.border.blit(text8, (115, 120))
        self.border.blit(text9, (5, 375))
        self.border.blit(text10, (5, 395))
        self.border.blit(text11, (5, 415))
        self.border.blit(text12, (5, 415))
        self.border.blit(text13, (5, 375))

        # Нижняя правая панель с выбором планеты для прыжка
        jump_panel_surf = pygame.Surface((298, 298))
        scroll_surf = pygame.Surface((298, 500))
        scroll_offset_y = 0
        txt_rects = []
        txt_rects_planets = []

        jump_txt = my_font.render('Совершить гиперпрыжок:', False, (255, 255, 255))
        scroll_surf.blit(jump_txt, (30, 30))

        self.cursor_is_within_jump_rect = False
        self.jump_rect_planet = None
        for i in range(len(self.galaxy.matches[self.player.current_planet])):
            matched_planet = self.galaxy.matches[self.player.current_planet][i]
            planet_txt = my_font.render(f'#{i + 1} {matched_planet.name} ' +
                                        f'[{self.player.current_planet.distance_to(matched_planet)}]',
                                        False, (255, 255, 255))
            planet_txt_rect = planet_txt.get_rect(topleft=(30, 50 + 20 * i))
            txt_rects_planets.append(matched_planet)
            txt_rects.append(planet_txt_rect)
            scroll_surf.blit(planet_txt, planet_txt_rect)

        for i in range(len(txt_rects_planets)):
            rect = txt_rects[i]
            matched_planet = txt_rects_planets[i]
            cursor = pygame.Vector2(pygame.mouse.get_pos())
            if (rect.left <= cursor.x - MAP_PANEL_WIDTH <= rect.right) and (rect.top <= cursor.y - 450 <= rect.bottom):
                self.cursor_is_within_jump_rect = True
                self.jump_rect_planet = matched_planet
                planet_yellow_txt = my_font.render(f'#{i + 1} {matched_planet.name} ' +
                                                   f'[{self.player.current_planet.distance_to(matched_planet)}]',
                                                   False, (255, 255, 0))
                scroll_surf.blit(planet_yellow_txt, rect)
                matched_planet_label = my_font.render(matched_planet.name, False, (255, 255, 255))
                self.show_planet_label(matched_planet, matched_planet_label)

        jump_panel_surf.blit(scroll_surf, (0, 0))
        self.border.blit(jump_panel_surf, (0, 450))

        if checked_mouse:  # Отображение названия планеты из matches при наведении курсора на нее
            self.show_planet_label(checked_mouse, checked_mouse_name_txt)

        # Блок надписей в левом нижнем углу карты
        map_ui_font = pygame.font.SysFont('Century Gothic', 20)
        scale_txt = map_ui_font.render(f'Масштаб  1:{int(1 / self.camera_group.zoom_scale * 100000)}',
                                       False, (255, 255, 255))
        self.map_screen.blit(scale_txt, (30, 640))

        press_r_txt = map_ui_font.render('[R]  Сбросить масштаб', False, (255, 255, 255))
        self.map_screen.blit(press_r_txt, (30, 670))

        press_e_txt = map_ui_font.render(f'[E]  Приземлиться на {self.player.current_planet.name}',
                                         False, (255, 255, 255))
        self.map_screen.blit(press_e_txt, (30, 700))

        out_of_fuel_font = pygame.font.SysFont('Century Gothic', 35, True)
        out_of_fuel_txt = out_of_fuel_font.render("! НЕДОСТАТОЧНО ТОПЛИВА !", False, (255, 0, 0))
        out_of_fuel_rect = out_of_fuel_txt.get_rect()
        if self.timers['out of fuel'].active:
            out_of_fuel_txt.set_alpha(min(200, self.timers['out of fuel'].time_left() * 0.5))
            self.map_screen.blit(out_of_fuel_txt,
                                 (MAP_PANEL_WIDTH // 2 - out_of_fuel_rect.width // 2,
                                  MAP_PANEL_HEIGHT // 2 - 100))

        # Блитаем карту и боковую панель на экран
        surface.blit(self.map_screen, self.rect)
        surface.blit(self.border, (MAP_PANEL_WIDTH, 0))

    def show_planet_label(self, planet, label_txt):
        checked_mouse_name_rect = label_txt.get_rect()
        # Высчитываем положение планеты в координатах экрана (а не галактики)
        checked_planet_x = \
            self.calculate_planet_pos_on_display_surf(pygame.Vector2(planet.x, planet.y))[0]
        checked_planet_y = \
            self.calculate_planet_pos_on_display_surf(pygame.Vector2(planet.x, planet.y))[1]
        # Рассчитываем координаты поверхности с названием планеты относительно центра планеты так, чтобы его было
        # хорошо видно при разных обстоятельствах
        self.map_screen.blit(
            label_txt,
            (
                checked_planet_x - checked_mouse_name_rect.width // 2 if
                checked_planet_x - checked_mouse_name_rect.width // 2 > 0 and
                checked_planet_x + checked_mouse_name_rect.width // 2 < MAP_PANEL_WIDTH else 5 if
                0 > checked_planet_x - checked_mouse_name_rect.width else
                MAP_PANEL_WIDTH - checked_mouse_name_rect.width - 5,
                checked_planet_y - planet.sprite.rect.height // 2 - 20 if
                checked_planet_y - planet.sprite.rect.height // 2 - 20 > 0 else
                checked_planet_y + planet.sprite.rect.height // 2 + 5
            )
        )

    def out_of_fuel(self):
        self.timers['out of fuel'].activate()

    def check_click(self, click_pos):
        for planet in self.galaxy.matches[self.player.current_planet]:
            # Calculate the offset of the planet sprite relative to the visible area
            offset_sprite_cords = planet.sprite.rect.center - self.camera_group.offset + self.camera_group.internal_offset

            # Adjust the offset
            adjusted_offset_sprite_cords = (
                offset_sprite_cords[0] * self.camera_group.zoom_scale + self.camera_group.scaled_rect.left,
                offset_sprite_cords[1] * self.camera_group.zoom_scale + self.camera_group.scaled_rect.top
            )

            # Calculate the zoomed coordinates of the planet sprite within the visible area
            zoomed_sprite_cords = (
                (adjusted_offset_sprite_cords[0]),
                (adjusted_offset_sprite_cords[1])
            )

            # Calculate the distance between the click position and the zoomed sprite coordinates
            distance = ((zoomed_sprite_cords[0] - click_pos[0]) ** 2 +
                        (zoomed_sprite_cords[1] - click_pos[1]) ** 2) ** 0.5

            # Calculate the radius of the planet based on its sprite size
            planet_radius = planet.sprite.rect.width // 2
            # Check if the distance is within the planet radius scaled by the zoom factor
            if distance < planet_radius:
                return planet
        return None

    def check_mouse(self, mouse_pos):
        for planet in self.galaxy.systems:
            # Calculate the offset of the planet sprite relative to the visible area
            offset_sprite_cords = planet.sprite.rect.center - self.camera_group.offset + self.camera_group.internal_offset

            # Adjust the offset
            adjusted_offset_sprite_cords = (
                offset_sprite_cords[0] * self.camera_group.zoom_scale + self.camera_group.scaled_rect.left,
                offset_sprite_cords[1] * self.camera_group.zoom_scale + self.camera_group.scaled_rect.top
            )

            # Calculate the zoomed coordinates of the planet sprite within the visible area
            zoomed_sprite_cords = (
                (adjusted_offset_sprite_cords[0]),
                (adjusted_offset_sprite_cords[1])
            )

            # Calculate the distance between the click position and the zoomed sprite coordinates
            distance = ((zoomed_sprite_cords[0] - mouse_pos[0]) ** 2 +
                        (zoomed_sprite_cords[1] - mouse_pos[1]) ** 2) ** 0.5

            # Calculate the radius of the planet based on its sprite size
            planet_radius = planet.sprite.rect.width // 2
            # Check if the distance is within the planet radius scaled by the zoom factor
            if distance < planet_radius:
                return planet
        return None

    def calculate_planet_pos_on_display_surf(self, pos):
        offset_sprite_cords = pos - self.camera_group.offset + self.camera_group.internal_offset
        adjusted_offset_sprite_cords = (
            offset_sprite_cords[0] * self.camera_group.zoom_scale + self.camera_group.scaled_rect.left,
            offset_sprite_cords[1] * self.camera_group.zoom_scale + self.camera_group.scaled_rect.top
        )
        return adjusted_offset_sprite_cords
