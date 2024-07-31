import pygame
from support import *
from settings import *
from random import choice
from pytmx.util_pygame import load_pygame


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']

        self.draw = True

    def update(self, dt, offset):
        pass


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, image, groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil water']

        self.draw = True


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(*groups)

        self.plant_type = plant_type
        self.frames = import_folder(BASE_PATH + 'graphics/fruit/{}'.format(plant_type))
        self.z = LAYERS['ground plant']
        self.soil = soil

        self.check_watered = check_watered

        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False

        self.image = self.frames[self.age]
        self.y_offset = -16 if plant_type == 'corn' else -8
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        self.hitbox = pygame.Rect(0, 0, -64, -64)
        self.draw = True

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age = min(self.age + self.grow_speed, self.max_age)

            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.4)

            if self.age >= self.max_age:
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))


class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):

        self.all_sprites = all_sprites
        self.colision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        self.soil_surfs = import_folder_dict(BASE_PATH + 'graphics/soil/')
        self.water_surfs = import_folder(BASE_PATH + 'graphics/soil_water/')

        self.grid = []
        self.hit_rects = []

        self.create_soil_grid()
        self.create_hit_rects()

        self.raining = False

        self.hoe = pygame.mixer.Sound(BASE_PATH + 'audio/hoe.wav')
        self.hoe.set_volume(0.05)

        self.plant_noise = pygame.mixer.Sound(BASE_PATH + 'audio/plant.wav')
        self.plant_noise.set_volume(0.1)

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
                    self.hoe.play()
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()
                    break

    def water(self, point):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                if 'W' not in self.grid[soil_sprite.rect.y // TILE_SIZE][soil_sprite.rect.x // TILE_SIZE]:
                    x = soil_sprite.rect.x // TILE_SIZE
                    y = soil_sprite.rect.y // TILE_SIZE
                    self.grid[y][x].append('W')

                    pos = soil_sprite.rect.topleft
                    surf = choice(self.water_surfs)
                    WaterTile(pos, surf,
                              (self.all_sprites, self.water_sprites))
                    break

    def water_all(self):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')

                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE

                    pos = (x, y)
                    surf = choice(self.water_surfs)

                    WaterTile(pos, surf, (self.all_sprites, self.water_sprites))

    def remove_water(self):
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def check_water(self, pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = "W" in cell
        return is_watered

    def plant_seed(self, point, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                if 'X' in self.grid[soil_sprite.rect.y // TILE_SIZE][soil_sprite.rect.x // TILE_SIZE]:
                    x = soil_sprite.rect.x // TILE_SIZE
                    y = soil_sprite.rect.y // TILE_SIZE
                    if 'P' not in self.grid[y][x]:
                        self.plant_noise.play()
                        self.grid[y][x].append('P')
                        Plant(seed, (self.all_sprites, self.plant_sprites, self.colision_sprites), soil_sprite, self.check_water)
                    break

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self):
        self.soil_sprites.empty()

        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:

                    top = 'X' in self.grid[index_row - 1][index_col]
                    bottom = 'X' in self.grid[index_row + 1][index_col]
                    right = 'X' in self.grid[index_row][index_col + 1]
                    left = 'X' in self.grid[index_row][index_col - 1]

                    top_left = 'X' in self.grid[index_row - 1][index_col - 1]
                    top_right = 'X' in self.grid[index_row - 1][index_col + 1]
                    bottom_left = 'X' in self.grid[index_row + 1][index_col - 1]
                    bottom_right = 'X' in self.grid[index_row + 1][index_col + 1]

                    tile_type = 'o'

                    # All
                    if all([top, bottom, right, left]): tile_type = 'x'

                    # Horizontal
                    if all([right, left]) and not any([top, bottom]): tile_type = 'lr'
                    if left and not any([top, bottom, right]): tile_type = 'r'
                    if right and not any([top, bottom, left]): tile_type = 'l'

                    # Vertical
                    if bottom and not any([top, right, left]): tile_type = 't'
                    if top and not any([bottom, right, left]): tile_type = 'b'
                    if all([bottom, top]) and not any([right, left]): tile_type = 'tb'

                    # Corners
                    if all([top, left]) and not any([right, bottom]): tile_type = 'br'
                    if all([top, right]) and not any([left, bottom]): tile_type = 'bl'
                    if all([bottom, left]) and not any([right, top]): tile_type = 'tr'
                    if all([bottom, right]) and not any([left, top]): tile_type = 'tl'

                    if any([top_right, bottom_right, top_left, bottom_left]):
                        # Middles
                        if not left and all([top, bottom, right]): tile_type = 'lm'
                        if not right and all([top, bottom, left]): tile_type = 'rm'
                        if not top and all([bottom, right, left]): tile_type = 'tm'
                        if not bottom and all([top, right, left]): tile_type = 'bm'
                    else:
                        # T Shapes
                        if not left and all([top, bottom, right]): tile_type = 'tbr'
                        if not right and all([top, bottom, left]): tile_type = 'tbl'
                        if not top and all([bottom, right, left]): tile_type = 'lrb'
                        if not bottom and all([top, right, left]): tile_type = 'lrt'

                    SoilTile((index_col * TILE_SIZE, index_row * TILE_SIZE),
                             self.soil_surfs[tile_type],
                             (self.soil_sprites, self.all_sprites))
