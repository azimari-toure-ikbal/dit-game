from settings import *
from math import sin, cos, radians
from random import randint

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surface = pygame.Surface((TILE_SIZE, TILE_SIZE)), groups = None, z_index = Z_LAYERS["main"]):
        super().__init__(groups)
        self.image = surface
        self.z_index = z_index
        
        # Rects
        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect = self.rect.copy()

class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups, z = Z_LAYERS["main"], animation_speed = ANIMATION_SPEED):
        self.frames, self.frame_index = frames, 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animation_speed = animation_speed

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt):
        self.animate(dt)

class Item(AnimatedSprite):
    def __init__(self, item_type, pos, frames, groups, game_data):
        super().__init__(pos, frames, groups)        
        self.rect.center = pos
        self.item_type = item_type
        self.game_data = game_data

    def activate(self):
        if self.item_type == "coin":
            self.game_data.score += 5
        if self.item_type == "silver":
            self.game_data.score += 1
        if self.item_type == "gem":
            self.game_data.score += 30
        if self.item_type == "skull":
            self.game_data.score += 100
        if self.item_type == "potion":
            self.game_data.health += 1

class ParticleEffectSprite(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.z = Z_LAYERS["foreground"]

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class MovingSprite(AnimatedSprite):
    def __init__(self, frames, groups, start_pos, end_pos, move_dir, speed):
        super().__init__(start_pos, frames ,groups)

        if move_dir == "x":
            self.rect.midleft = start_pos
        else:
            self.rect.midtop = start_pos

        self.rect.center = start_pos
        self.start_pos = start_pos
        self.end_pos = end_pos

        # Movement
        self.moving = True
        self.speed = speed
        self.direction = Vector2(1, 0) if move_dir == "x" else Vector2(0, 1)
        self.move_dir = move_dir

    def check_bounds(self):
        if self.move_dir == "x":
            if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            if self.rect.left <= self.start_pos[0] and self.direction.x == -1:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
        else:
            if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            if self.rect.top <= self.start_pos[1] and self.direction.y == -1:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.rect.topleft += self.direction * self.speed * dt
        self.check_bounds()

        self.animate(dt)

class Spike(Sprite):
    def __init__(self, pos, surface, groups, radius, speed, start_angle, end_angle, z_index = Z_LAYERS["main"]):
        self.center = pos
        self.radius = radius
        self.speed = speed
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.angle = self.start_angle
        self.direction = 1
        self.full_circle = True if self.end_angle == -1 else False

        # Trigo
        x = self.center[0] + cos(radians(self.angle)) * self.radius
        y = self.center[1] + sin(radians(self.angle)) * self.radius

        super().__init__((x, y), surface, groups, z_index)

    def update(self, dt):
        self.angle += self.direction * self.speed * dt

        if not self.full_circle:
            if self.angle >= self.end_angle:
                self.direction = -1
            if self.angle <= self.start_angle:
                self.direction = 1

        x = self.center[0] + cos(radians(self.angle)) * self.radius
        y = self.center[1] + sin(radians(self.angle)) * self.radius
        self.rect.center = (x, y)

class Heart(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.active = False

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.active = False
            self.frame_index = 0

    def update(self, dt):
        if self.active:
            self.animate(dt)
        else:
            if randint(0, 2000) == 1:
                self.active = True

class Cloud(Sprite):
    def __init__(self, pos, surface, groups, z_index = Z_LAYERS["clouds"]):
        super().__init__(pos, surface, groups, z_index)
        self.speed = randint(20, 50)
        self.direction = -1
        self.rect.midbottom = pos

    def update(self, dt):
        self.rect.x += self.direction * self.speed * dt

        if self.rect.right <= 0:
            self.kill()

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups, level, game_data):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center = (pos[0] + TILE_SIZE / 2, pos[1] + TILE_SIZE / 2))
        self.z_index = Z_LAYERS["path"]
        self.level = level
        self.game_data = game_data

class PlayerIcon(pygame.sprite.Sprite):
    def __init__(self, pos, groups, frames):
        super().__init__(groups)
        self.player_icon = True

        # Image
        self.frames, self.frame_index = frames, 0
        self.state = "idle"
        self.image = self.frames[self.state][self.frame_index]
        self.z_index = Z_LAYERS["main"]

        # Rect
        self.rect = self.image.get_frect(center = pos)