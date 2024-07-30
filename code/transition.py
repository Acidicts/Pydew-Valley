import pygame
from settings import *


class Transition:
    def __init__(self, reset, player):
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        self.image = pygame.surface.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self):
        if self.color > 1:
            self.color += self.speed

        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0))
