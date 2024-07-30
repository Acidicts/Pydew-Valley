import pygame
from settings import *
from pytmx.util_pygame import load_pygame


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']

    def update(self, dt):
        pass


class SoilLayer:
    def __init__(self, all_sprites):

        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()

        self.soil_surf = pygame.image.load(BASE_PATH + 'graphics/soil/o.png').convert_alpha()

        self.grid = []
        self.hit_rects = []

        self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
        ground = pygame.image.load(BASE_PATH + 'graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE

        self.grid = [[[]for _ in range(h_tiles)] for __ in range(v_tiles)]
        for x, y, _ in load_pygame(BASE_PATH + 'data/map.tmx').get_layer_by_name('Farmable').tiles():
            # noinspection PyTypeChecker
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x, y = index_col * TILE_SIZE, index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    break

    def create_soil_tiles(self):
        self.soil_sprites.empty()

        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    SoilTile((index_col * TILE_SIZE, index_row * TILE_SIZE),
                             self.soil_surf,
                             (self.soil_sprites, self.all_sprites))
