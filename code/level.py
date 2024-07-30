import pygame
from pytmx.util_pygame import load_pygame

from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree
from support import import_folder


class Level:
    def __init__(self):

        self.display_surface = pygame.display.get_surface()

        self.all_sprites = Camera()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()

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
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))

        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites, self.tree_sprites), obj.name, self)

        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player((obj.x, obj.y), (self.all_sprites,), self.collision_sprites, self.tree_sprites)

        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.collision_sprites, self.tree_sprites)

        Generic(pos=(0, 0), surf=pygame.image.load(
            BASE_PATH + 'graphics/world/ground.png'),
                groups=(self.all_sprites,),
                z=LAYERS['ground']
                )

        water_frames = import_folder(BASE_PATH + 'graphics/water/')

        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, (self.all_sprites,))

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
            for sprite in sorted(self.sprites(), key=lambda sprit: sprit.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.surf.blit(sprite.image, offset_rect)

                    # if sprite == player:
                    #     pygame.draw.rect(self.surf, 'red', offset_rect, 5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.surf, 'green', hitbox_rect, 5)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                    #     pygame.draw.circle(self.surf, 'blue', target_pos, 5)
