import pygame
from settings import *
from timer import Timer


class Menu:
    def __init__(self, player, toggle_menu):

        self.main_rect = None
        self.menu_top = None

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

        self.index = 0
        self.timer = Timer(200)

    def display_money(self):
        text_surf = self.font.render('Money: ${}'.format(self.player.money), False, 'Black')
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2 - text_surf.get_width(), 150))

        text_box = text_rect.copy().inflate(10, 0)
        text_box.midbottom = (SCREEN_WIDTH / 2 - text_surf.get_width(), 150)

        pygame.draw.rect(self.display_surface, 'white', text_box, 0, 6)
        self.display_surface.blit(text_surf, text_rect)

    def setup(self):
        self.text_surfs = []
        self.total_height = 0

        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2,
                                     self.menu_top,
                                     self.width,
                                     self.total_height)

        self.buy_text = self.font.render('Buy', False, 'Black')
        self.sell_text = self.font.render('Sell', False, 'Black')

    def inputs(self):
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if keys[pygame.K_SPACE] and not self.timer.active:
            current_item = self.options[self.index]

            if self.index <= self.sell_border:
                if self.player.item_inventory[current_item] > 0:
                    self.player.item_inventory[current_item] -= 1
                    self.player.money += SALE_PRICES[current_item]
            elif self.player.money >= PURCHASE_PRICES[current_item]:
                seed_price = PURCHASE_PRICES[current_item]
                self.player.money -= PURCHASE_PRICES[current_item]
            self.timer.activate()

        num = int(not self.timer.active) * (int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]))

        self.index = (self.index + num) % len(self.options)
        if num != 0:
            self.timer.activate()

    def show_entry(self, text_surf, amount, top, selected):
        bg_rect = pygame.Rect(self.main_rect.left,
                              top,
                              self.width,
                              text_surf.get_height() + (self.padding * 2)
                              )
        pygame.draw.rect(self.display_surface, 'white', bg_rect, 0, 4)

        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))

        self.display_surface.blit(amount_surf, amount_rect)

        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 4)
            if self.index <= self.sell_border:
                sell_rect = self.sell_text.get_rect(
                    midleft=((SCREEN_WIDTH / 2 - self.buy_text.get_width() / 2) + 50, bg_rect.centery))
                pygame.draw.rect(self.display_surface, 'orange', sell_rect, 0, 4)
                self.display_surface.blit(self.sell_text, ((SCREEN_WIDTH / 2 - self.sell_text.get_width() / 2) + 50, bg_rect.centery - 15))
            else:
                buy_rect = self.buy_text.get_rect(midleft=((SCREEN_WIDTH / 2 - self.buy_text.get_width() / 2) + 50, bg_rect.centery))
                pygame.draw.rect(self.display_surface, 'green', buy_rect, 0, 4)
                self.display_surface.blit(self.buy_text, ((SCREEN_WIDTH / 2 - self.buy_text.get_width() / 2) + 50, bg_rect.centery - 15))

    def update(self):
        self.inputs()
        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount_list[text_index]
            self.show_entry(text_surf, amount, top, self.index == text_index)

        self.display_money()
