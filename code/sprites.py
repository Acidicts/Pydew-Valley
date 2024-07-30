import pygame
from settings import *
from timer import Timer
from random import randint, random


class Generic(pygame.sprite.Sprite):
    # noinspection PyTypeChecker
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)

        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z

        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)


class Water(Generic):
    def __init__(self, pos, frames, groups):
        self.frames = frames
        self.frame_index = 0

        super().__init__(pos, self.frames[self.frame_index], groups, LAYERS['water'])

    def animate(self, dt):
        self.frame_index += 5 * dt

        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def update(self, dt):
        self.animate(dt)


class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)

        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Tree(Generic):
    def __init__(self, pos, surf, groups, name):
        super().__init__(pos, surf, groups)

        self.health = 5
        self.alive = True
        self.stump_surf = pygame.image.load(BASE_PATH + 'graphics/stumps/{}.png'.format(name.lower()))
        self.invul_timer = Timer(200)

        self.apple_surf = pygame.image.load(BASE_PATH + 'graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

    def damage(self):
        self.health -= 1

        if len(self.apple_sprites) > 0:
            random_apple = choice(Self.apples_sprites.sprites())
            random_apple.kill()

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                x, y = pos[0] + self.rect.left, pos[1] + self.rect.top
                # noinspection PyTypeChecker
                Generic(
                    (x, y),
                    self.apple_surf,
                    [self.apple_sprites, self.groups()[0]],
                    LAYERS['fruit']
                )
