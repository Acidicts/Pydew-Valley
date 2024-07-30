import pygame

from settings import *
from timer import Timer
from random import randint, choice


class Generic(pygame.sprite.Sprite):
    # noinspection PyTypeChecker
    def __init__(self, pos, surf, groups, z=LAYERS['main'], draw=False):
        super().__init__(groups)

        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z

        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

        self.draw = True
        self.override = draw

    def update(self, dt, offset):
        screen_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)


class Interaction(Generic):
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)

        self.name = name


class Water(Generic):
    def __init__(self, pos, frames, groups):
        self.frames = frames
        self.frame_index = 0

        super().__init__(pos, self.frames[self.frame_index], groups, LAYERS['water'])

    def animate(self, dt):
        self.frame_index += 5 * dt

        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def update(self, dt, offset=(0, 0)):
        self.animate(dt)


class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)

        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration=200):
        super().__init__(pos, surf, groups, z)

        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        mask = pygame.mask.from_surface(self.image)
        new_surf = mask.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf

    def update(self, dt, offset=(0, 0)):
        current_time = pygame.time.get_ticks()
        time = self.start_time - current_time
        fade = time / self.duration * 255
        self.image.set_alpha(fade)
        if current_time - self.start_time >= self.duration:
            self.kill()

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Tree(Generic):
    def __init__(self, pos, surf, groups, name, level, player_add):
        super().__init__(pos, surf, groups)

        self.level = level

        self.health = 5
        self.alive = True
        self.stump_surf = pygame.image.load(BASE_PATH + 'graphics/stumps/{}.png'.format(name.lower()))
        self.invulnerable_timer = Timer(200)

        self.apple_surf = pygame.image.load(BASE_PATH + 'graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.player_add = player_add

    def damage(self):
        self.health -= 1

        if len(self.apple_sprites) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(random_apple.rect.topleft,
                     random_apple.image,
                     (self.level.all_sprites,),
                     LAYERS['fruit'],
                     200)
            self.player_add('apple')
            random_apple.kill()

    def check_death(self):
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, (self.level.all_sprites,), LAYERS['main'], 500)
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False
            self.player_add('wood')

    def update(self, dt, offset=(0, 0)):
        if self.alive:
            self.check_death()

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                x, y = pos[0] + self.rect.left, pos[1] + self.rect.top
                # noinspection PyTypeChecker
                Generic(
                    (x, y),
                    self.apple_surf,
                    (self.apple_sprites, self.level.all_sprites),
                    LAYERS['fruit']
                )
