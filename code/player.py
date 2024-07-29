import pygame
from settings import *
from support import *
from timer import timer


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)

        self.animations = None
        self.import_assets()

        self.status = 'down_idle'
        self.frame_index = 0
        self.image = self.animations[self.status][self.frame_index]

        self.rect = self.image.get_rect(center=pos)

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        self.timers = {
            'tool_use': Timer(250, self.use_tool),
        }

        self.selected_tool = 'axe'

    def use_tool(self):
        pass

    def import_assets(self):
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
            'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
            'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []
        }

        for animation in self.animations.keys():
            base_path = 'F:/PycharmProject/Pydew Valley/'
            full_path = base_path + 'graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        if '_idle' in self.status:
            self.frame_index += 2 * dt
        else:
            self.frame_index += 10 * dt
        self.image = self.animations[self.status][int(self.frame_index) % len(self.animations[self.status])]

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

        if keys[pygame.K_SPACE]:
            pass

        self.status = self.find_status(self.direction)

    def find_status(self, direction):
        direction = (int(direction.x), int(direction.y))

        directions = {
            (0, 1): 'down', (0, -1): 'up', (1, 0): 'right', (-1, 0): 'left',
            (0, 0): None,
            (1, 1): 'down', (-1, 1): 'down', (1, -1): 'up', (-1, -1): 'up'
        }

        if directions[direction] is None:
            return self.status.split('_')[0] + '_idle'

        return directions.get(direction)

    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x

        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
