import pygame
from pytmx.util_pygame import load_pygame

from menu import Menu
from settings import *
from player import Player
from sky import Rain, Sky
from soil import SoilLayer
from random import randint
from overlay import Overlay
from sprites import Particle
from support import import_folder
from transition import Transition
from sprites import Generic, Water, WildFlower, Tree, Interaction


class Level:
    def __init__(self):

        self.display_surface = pygame.display.get_surface()

        self.all_sprites = Camera()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()

        self.interaction_sprites = pygame.sprite.Group()

        self.player = None

        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)

        self.setup()

        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        self.menu = Menu(self.player, self.player.toggle_shop)
        self.shop_active = False

        self.music = pygame.mixer.Sound(BASE_PATH + 'audio/bg.mp3')
        self.music.set_volume(0.1)
        self.music.play(-1)

        self.success = pygame.mixer.Sound(BASE_PATH + 'audio/success.wav')
        self.success.set_volume(0.1)

    # noinspection PyTypeChecker
    def setup(self):
        tmx_data = load_pygame(BASE_PATH + 'data/map.tmx', self.all_sprites)

        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites,), LAYERS['house bottom'], True)

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites,), LAYERS['main'], True)

        for layer in ['Fence']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites), True)

        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y),
                 obj.image,
                 (self.all_sprites, self.collision_sprites, self.tree_sprites),
                 obj.name,
                 self, self.player_add)

        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.collision_sprites, self.tree_sprites)

        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player((obj.x, obj.y),
                                     (self.all_sprites,),
                                     self.collision_sprites,
                                     self.tree_sprites,
                                     self.interaction_sprites,
                                     self.soil_layer,
                                     self.toggle_shop,)

            if obj.name == "Bed":
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

            if obj.name == 'Trader':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

        Generic(pos=(0, 0), surf=pygame.image.load(
            BASE_PATH + 'graphics/world/ground.png'),
                groups=(self.all_sprites,),
                z=LAYERS['ground'],
                draw=True,
                )

        water_frames = import_folder(BASE_PATH + 'graphics/water/')

        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, (self.all_sprites,))

    def player_add(self, item):
        self.success.play()
        self.player.item_inventory[item] += 1

    def toggle_shop(self):
        self.shop_active = not self.shop_active

    def reset(self):
        self.soil_layer.update_plants()
        self.soil_layer.remove_water()

        self.raining = randint(0, 10) > 7
        self.soil_layer.raining = self.raining

        for sprite in self.all_sprites.sprites():
            sprite.draw = False

        if self.raining:
            self.soil_layer.water_all()

        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        self.sky.start_color = [255, 255, 255]

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player.item_inventory[plant.plant_type] += 1

                    x = plant.rect.centerx // TILE_SIZE
                    y = plant.rect.centery // TILE_SIZE

                    self.soil_layer.grid[y][x].remove("P")

                    Particle(plant.rect.topleft, plant.image, (self.all_sprites,), LAYERS['main'], 500)
                    plant.kill()

    def run(self, dt):

        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        self.overlay.display()

        if self.raining and not self.shop_active:
            self.rain.update()

        self.sky.display(dt)

        if self.player.sleep:
            self.transition.play()
        else:
            for sprite in self.all_sprites.sprites():
                sprite.draw = True

        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt, self.all_sprites.offset)
            self.plant_collision()


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
                if sprite.z == layer and sprite.draw:
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
