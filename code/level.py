import pygame 
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic
from pytmx.util_pygame import load_pygame


class Level:
	def __init__(self):

		self.display_surface = pygame.display.get_surface()

		self.all_sprites = Camera()
		self.player = None

		self.setup()

		self.overlay = Overlay(self.player)

	def setup(self):
		tmx_data = load_pygame(BASE_PATH+'data/map.tmx', self.all_sprites)

		for layer in ['HouseFloor', 'HouseFurnitureBottom']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites,), LAYERS['house bottom'])

		Generic(pos=(0, 0), surf=pygame.image.load(
			BASE_PATH+'graphics/world/ground.png'),
				groups=(self.all_sprites,),
				z=LAYERS['ground']
				)

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
			for sprite in self.sprites():
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center -= self.offset
					self.surf.blit(sprite.image, offset_rect
								   )
