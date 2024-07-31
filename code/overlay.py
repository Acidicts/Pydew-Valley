import pygame
from settings import *


class Overlay:
    def __init__(self, player):
        self.surf = pygame.display.get_surface()

        self.player = player

        overlay_path = 'F:/PycharmProject/Pydew Valley/graphics/overlay/'
        self.font = pygame.font.Font(BASE_PATH + 'font/LycheeSoda.ttf', 30)
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}

    def display(self):
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom=OVERLAY_POSITIONS['tool'])
        self.surf.blit(tool_surf, tool_rect)

        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom=OVERLAY_POSITIONS['seed'])
        self.surf.blit(seed_surf, seed_rect)

        money_surf = self.font.render(f'Money: ${self.player.money}', False, 'Black')
        money_rect = money_surf.get_rect(midbottom=OVERLAY_POSITIONS['money'])
        money_rect.midleft = OVERLAY_POSITIONS['money']
        pygame.draw.rect(self.surf, 'white', money_rect.inflate(10, 0), 0, 6)
        self.surf.blit(money_surf, money_rect)
