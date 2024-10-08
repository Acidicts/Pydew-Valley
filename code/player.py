import pygame

from settings import *
from support import *
from timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop):
        super().__init__(group)

        self.animations = None
        self.import_assets()

        self.status = 'down_idle'
        self.frame_index = 0

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        self.hitbox = self.rect.copy().inflate(-126, -70)
        self.collision_sprites = collision_sprites

        self.timers = {
            'tool_use': Timer(350, self.use_tool),
            'seed_use': Timer(350, self.use_seed),
            'tool_switch': Timer(200),
            'seed_switch': Timer(200),
        }

        self.target_pos = self.get_target_pos()

        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        self.seed_inventory = {
            'corn': 5,
            'tomato': 5,
        }

        self.item_inventory = {
            'wood': 0,
            'apple': 0,
            'corn': 0,
            'tomato': 0,
        }

        self.tree_sprites = tree_sprites
        self.interaction = interaction

        self.sleep = False
        self.draw = True

        self.soil_layer = soil_layer

        self.toggle_shop = toggle_shop

        self.money = 200

        self.watering = pygame.mixer.Sound(BASE_PATH + 'audio/water.mp3')
        self.watering.set_volume(0.1)

    def use_tool(self):
        if self.selected_tool == "hoe":
            self.soil_layer.get_hit(self.target_pos)
        elif self.selected_tool == "axe":
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        elif self.selected_tool == "water":
            self.soil_layer.water(self.target_pos)
            self.watering.play()

    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
        return self.target_pos

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
        elif self.selected_tool in self.status:
            self.frame_index += 4 * dt
        else:
            self.frame_index += 10 * dt
        self.image = self.animations[self.status][int(self.frame_index) % len(self.animations[self.status])]

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['tool_use'].active and not self.sleep:
            self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        else:
            self.direction = pygame.math.Vector2()

        if keys[pygame.K_SPACE]:
            if not self.timers['tool_use'].active:
                self.status = self.find_status(self.direction)
                self.timers['tool_use'].activate()
                self.frame_index = 0

        if keys[pygame.K_LCTRL]:
            if not self.timers['seed_use'].active:
                self.status = self.find_status(self.direction)
                self.timers['seed_use'].activate()
                self.frame_index = 0

        if keys[pygame.K_q] and not self.timers['tool_switch'].active:
            self.timers['tool_switch'].activate()
            self.tool_index = (self.tool_index + 1) % len(self.tools)
            self.selected_tool = self.tools[self.tool_index]

        if keys[pygame.K_e] and not self.timers['seed_switch'].active:
            self.timers['seed_switch'].activate()
            self.seed_index = (self.seed_index + 1) % len(self.seeds)
            self.selected_seed = self.seeds[self.seed_index]

        if keys[pygame.K_RETURN]:
            # noinspection PyTypeChecker
            collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)

            if collided_interaction_sprite:
                if collided_interaction_sprite[0].name == 'Trader':
                    self.toggle_shop()
                elif collided_interaction_sprite[0].name == 'Bed':
                    self.status = 'left_idle'
                    self.sleep = True
                else:
                    pass

        self.status = self.find_status(self.direction)

    def find_status(self, direction):
        pos = (int(direction.x), int(direction.y))

        directions = {
            (0, 1): 'down', (0, -1): 'up', (1, 0): 'right', (-1, 0): 'left',
            (0, 0): None,
            (1, 1): 'down', (-1, 1): 'down', (1, -1): 'up', (-1, -1): 'up'
        }

        if direction.magnitude() == 0 and not self.timers['tool_use'].active:
            return self.status.split('_')[0] + '_idle'

        if self.timers['tool_use'].active:
            return self.status.split('_')[0] + '_' + self.selected_tool

        return directions.get(pos)

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:  # Moving right
                            self.hitbox.right = sprite.hitbox.left

                        if self.direction.x < 0:  # Moving left
                            self.hitbox.left = sprite.hitbox.right

                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                        break

                    if direction == 'vertical':
                        if self.direction.y > 0:  # Moving down
                            self.hitbox.bottom = sprite.hitbox.top

                        if self.direction.y < 0:  # Moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
                        break

    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def update(self, dt, offset=(0, 0)):
        self.input()
        self.update_timers()

        self.get_target_pos()

        self.move(dt)
        self.animate(dt)
