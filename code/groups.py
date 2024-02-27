from settings import *
from sprites import Sprite, Cloud
from random import choice, randint
from custom_timer import Timer

class WordlSprites(pygame.sprite.Group):
    def __init__(self, game_data):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.game_data = game_data
        self.offset = Vector2()

    def draw(self, target_position):
        self.offset.x = - (target_position[0] - WINDOW_WIDTH / 2)
        self.offset.y = - (target_position[1] - WINDOW_HEIGHT / 2)

        # Background
        for sprite in sorted(self, key = lambda sprite: sprite.z_index):
            if sprite.z_index < Z_LAYERS["main"]:
                if sprite.z_index == Z_LAYERS["path"]:
                    if sprite.level <= self.game_data.unlocked_levels:
                        self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)    
                else:
                    self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

        # Main
        for sprite in sorted(self, key = lambda sprite: sprite.rect.centery):
            if sprite.z_index == Z_LAYERS["main"]:
                if hasattr(sprite, "player_icon"):
                    self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset + Vector2(0, -28))
                else:
                    self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)


class AllSprites(pygame.sprite.Group):
    def __init__(self, width, height, clouds, horizon_line, bg_tile = None, top_limit = 0):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = Vector2()
        self.width = width * TILE_SIZE
        self.height = height * TILE_SIZE
        self.borders = {
            "left": 0,
            "right": -self.width + WINDOW_WIDTH,
            "top": top_limit,
            "bottom": -self.height + WINDOW_HEIGHT
        }
        self.sky = not bg_tile
        self.horizon_line = horizon_line

        if bg_tile:
            for col in range(width):
                for row in range(-int(top_limit / TILE_SIZE) - 1, height):
                    x, y = col * TILE_SIZE, row * TILE_SIZE
                    Sprite((x, y), bg_tile, self, -1)
        else:
            # Sky
            self.large_cloud = clouds["large_cloud"]
            self.small_clouds = clouds["small_cloud"]
            self.cloud_direction = -1

            # Large clouds
            self.large_cloud_speed = 50
            self.large_cloud_x = 0
            self.large_cloud_tiles = int(self.width / self.large_cloud.get_width()) + 2
            self.large_cloud_width, self.large_cloud_height = self.large_cloud.get_size()

            # Small clouds
            for cloud in range(10):
                self.cloud_timer = Timer(2500, self.create_small_cloud, True)
                self.cloud_timer.activate()
                pos = (randint(0, self.width), randint(self.borders["top"], self.horizon_line))
                surface = choice(self.small_clouds)
                Cloud(pos, surface, self)

    def camera_constraints(self):
        self.offset.x = self.offset.x if self.offset.x < self.borders["left"] else self.borders["left"]
        self.offset.x = self.offset.x if self.offset.x > self.borders["right"] else self.borders["right"]
        self.offset.y = self.offset.y if self.offset.y < self.borders["top"] else self.borders["top"]
        self.offset.y = self.offset.y if self.offset.y > self.borders["bottom"] else self.borders["bottom"]

    def draw_sky(self):
        self.display_surface.fill("#D1EDFC")
        # horizon_pos = 800 + self.offset.y

        # sea_rect = pygame.FRect(0, horizon_pos, WINDOW_WIDTH, WINDOW_HEIGHT - horizon_pos)
        # pygame.draw.rect(self.display_surface, "#3B7EA1", sea_rect)

    def draw_large_cloud(self, dt):
        self.large_cloud_x += self.cloud_direction * self.large_cloud_speed * dt
        if self.large_cloud_x <= -self.large_cloud_width:
            self.large_cloud_x = 0

        for cloud in range(self.large_cloud_tiles):
            left = self.large_cloud_x + self.large_cloud_width * cloud + self.offset.x
            top = self.horizon_line - self.large_cloud_height + self.offset.y
            self.display_surface.blit(self.large_cloud, (left, top))

    def create_small_cloud(self):
        pos = (randint(self.width + 500, self.width + 600), randint(self.borders["top"], self.horizon_line))
        surface = choice(self.small_clouds)
        Cloud(pos, surface, self)

    def draw(self, target_position, dt):
        self.offset.x = - (target_position[0] - WINDOW_WIDTH / 2)
        self.offset.y = - (target_position[1] - WINDOW_HEIGHT / 2)
        self.camera_constraints()

        if self.sky:
            self.cloud_timer.update()
            self.draw_sky()
            self.draw_large_cloud(dt)

        for sprite in sorted(self, key = lambda sprite: sprite.z_index):
            offset_position = sprite.rect.topleft + self.offset
            self.display_surface.blit(sprite.image, offset_position)
    
