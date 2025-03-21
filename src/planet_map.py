import pygame
from settings import *
from planet_player import PlanetPlayer
from src.planet_enemy import PlanetEnemy
from src.overlay import Overlay
from pytmx.util_pygame import load_pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, group):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.rect.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.width / 2)
        y = -target.rect.centery + int(self.height / 2)
        self.rect = pygame.Rect(x, y, self.width, self.height)


class PlanetMap:
    def __init__(self, planet):
        self.planet = planet
        self.all_sprites = pygame.sprite.Group()
        self.magic_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.tiles_sprites = pygame.sprite.Group()
        self.display_surface = pygame.display.get_surface()
        self.monsters_sprites = pygame.sprite.Group()

        self.stat = 0  # флаг на одноразовый вызов метоа сэтап (там мы передаём позиции в планет_мап)
        self.stat2 = 1  # флаг на одноразовое заполнение массива позиций

        self.setup()

        self.camera = Camera(self.display_surface.get_width(), self.display_surface.get_height())

    def setup(self):
        tmx_data = load_pygame("../Tiles/map1.tmx")
        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    pos = (x * TILE_SIZE, y * TILE_SIZE)
                    if layer.name == "second":
                        tile = Tile(surf, pos[0], pos[1], self.obstacle_sprites)
                    else:
                        tile = Tile(surf, pos[0], pos[1], self.tiles_sprites)

        self.planet_player = PlanetPlayer((250, 380), self.all_sprites,
                                          self.obstacle_sprites, self.magic_sprites)  # теперь в аргументах указываем ещё и позиции осязаемых объектов

        self.planet_enemies = {}
        self.enemies_overlays = {}
        for i in range(NUM_OF_ENEMIES):  # в сеттингс добавил кол-во врагов, пока закомментил
            self.planet_enemies['enemy_' + str(i)] = PlanetEnemy(self.planet_player,
                                                                 self.monsters_sprites,
                                                                 self.obstacle_sprites,
                                                                 self.damage_player,
                                                                 (100 + i * 100, 65)
                                                                )
        self.overlay = Overlay(self.display_surface, self.planet_player)

    def player_attack_logic(self):
        if "attack" in self.planet_player.image_status:
            if self.planet_player.selected_tool == "sword":
                collision_sprites = pygame.sprite.spritecollide(self.planet_player, self.monsters_sprites, False)
            else:
                collision_sprites = []
            if collision_sprites:
                for target in collision_sprites:
                    target.get_damage(self.planet_player)

    def magic_attack_logic(self):
        if self.magic_sprites:
            collision_sprites = []
            for magic_sprite in self.magic_sprites:
                now_coll_sprites = pygame.sprite.spritecollide(magic_sprite, self.monsters_sprites, False)
                if now_coll_sprites:
                    magic_sprite.kill()
                collision_sprites.extend(now_coll_sprites)

            if collision_sprites:
                for target in collision_sprites:
                    target.get_damage(self.planet_player)

    def damage_player(self, amount):
        if self.planet_player.vulnerable:
            if self.planet_player.hp:
                self.planet_player.hp -= amount
                pygame.mixer.Sound('../Music/sounds/bruh.mp3').play()
            else:
                pygame.mixer.music.load('../Music/sounds/you_died.mp3')
                pygame.mixer.music.play(1)
                self.planet_player.kill()
            self.planet_player.vulnerable = False
            self.planet_player.timers["hit"].activate()
            # spawn particles

    def draw(self, dt):
        self.display_surface.fill('black')
        # блитуем

        for sprite in self.tiles_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))
        for sprite in self.obstacle_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))
        for sprite in self.all_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))
        for sprite in self.monsters_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))
        for sprite in self.magic_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))

        self.tiles_sprites.update(dt)
        self.obstacle_sprites.update(dt)
        self.all_sprites.update(dt)
        self.monsters_sprites.update(dt)
        self.magic_sprites.update(dt)

        self.player_attack_logic()
        self.magic_attack_logic()

        # for overlay in self.enemies_overlays.values():
        # overlay.display()
        self.overlay.display()
        self.camera.update(self.planet_player)

