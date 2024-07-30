import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *


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
        self.soil_surfs = import_folder_dict(BASE_PATH + 'graphics/soil/')

        self.grid = []
        self.hit_rects = []

        self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
        ground = pygame.image.load(BASE_PATH + 'graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE

        self.grid = [[[] for _ in range(h_tiles)] for __ in range(v_tiles)]
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

                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in self.grid[index_row][index_col + 1]
                    l = 'X' in self.grid[index_row][index_col - 1]

                    tl = 'X' in self.grid[index_row - 1][index_col - 1]
                    tr = 'X' in self.grid[index_row - 1][index_col + 1]
                    bl = 'X' in self.grid[index_row + 1][index_col - 1]
                    br = 'X' in self.grid[index_row + 1][index_col + 1]

                    tile_type = 'o'

                    # All
                    if all([t, b, r, l]): tile_type = 'x'

                    # Horizontal
                    if all([r, l]) and not any([t, b]): tile_type = 'lr'
                    if l and not any([t, b, r]): tile_type = 'r'
                    if r and not any([t, b, l]): tile_type = 'l'

                    # Vertical
                    if b and not any([t, r, l]): tile_type = 't'
                    if t and not any([b, r, l]): tile_type = 'b'
                    if all([b, t]) and not any([r, l]): tile_type = 'tb'

                    # Corners
                    if all([t, l]) and not any([r, b]): tile_type = 'br'
                    if all([t, r]) and not any([l, b]): tile_type = 'bl'
                    if all([b, l]) and not any([r, t]): tile_type = 'tr'
                    if all([b, r]) and not any([l, t]): tile_type = 'tl'

                    if any([tr, br, tl, bl]):
                        # Middles
                        if not l and all([t, b, r]): tile_type = 'lm'
                        if not r and all([t, b, l]): tile_type = 'rm'
                        if not t and all([b, r, l]): tile_type = 'tm'
                        if not b and all([t, r, l]): tile_type = 'bm'
                    else:
                        # T Shapes
                        if not l and all([t, b, r]): tile_type = 'tbr'
                        if not r and all([t, b, l]): tile_type = 'tbl'
                        if not t and all([b, r, l]): tile_type = 'lrb'
                        if not b and all([t, r, l]): tile_type = 'lrt'

                    SoilTile((index_col * TILE_SIZE, index_row * TILE_SIZE),
                             self.soil_surfs[tile_type],
                             (self.soil_sprites, self.all_sprites))
