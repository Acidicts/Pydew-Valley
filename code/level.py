import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree
from pytmx.util_pygame import load_pygame
from support import import_folder


class Level:
    def __init__(self):

        self.display_surface = pygame.display.get_surface()

        self.all_sprites = Camera()
        self.player = None

        self.setup()

        self.overlay = Overlay(self.player)

    # noinspection PyTypeChecker
    def setup(self):
        tmx_data = load_pygame(BASE_PATH + 'data/map.tmx', self.all_sprites)

        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites,), LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites,), LAYERS['main'])

        for layer in ['Fence']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites,))

        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, (self.all_sprites,), obj.name)

        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, (self.all_sprites,))

        Generic(pos=(0, 0), surf=pygame.image.load(
            BASE_PATH + 'graphics/world/ground.png'),
                groups=(self.all_sprites,),
                z=LAYERS['ground']
                )

        water_frames = import_folder(BASE_PATH + 'graphics/water/')

        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, (self.all_sprites,))

        self.player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self.all_sprites)

    def run(self, dt):
        self.display_surface.fill('black')

        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()


class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

        self.surf = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH // 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.surf.blit(sprite.image, offset_rect)
