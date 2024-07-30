import pygame
from settings import *

class Transition:
    def __init__(self, func, player):
        self.display_surface = pygame.display.get_surface()
        self.func = func
        self.player = player

        self.image = pygame.surface.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2
        self.fading_in = False  # Initialize fading_in flag

    def play(self):
        if self.fading_in:
            self.color -= self.speed
        else:
            self.color += self.speed

        if self.color <= 0:
            self.color = 0
            self.fading_in = True
            self.func()

        elif self.color >= 255:
            self.color = 255
            self.fading_in = False
            self.player.sleep = False
            self.speed = -2

        self.player.direction = pygame.math.Vector2(0, 0)

        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)