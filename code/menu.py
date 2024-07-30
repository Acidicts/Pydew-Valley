import pygame
from settings import *


class Menu:
    def __init__(self, player, toggle_menu):

        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(BASE_PATH + 'font/LycheeSoda.ttf', 30)

        self.width = 400
        self.space = 10
        self.padding = 8

        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1

        self.text_surfs = []
        self.total_height = 0

        self.setup()

    def setup(self):
        self.text_surfs = []
        for item in self.options:
            text_surf = self.font.render(item, True, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

    def inputs(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

    def update(self):
        self.inputs()
        for text_index, text_surf in enumerate(self.text_surfs):
            self.display_surface.blit(text_surf, (100, text_index * 50))
