from settings import *
from custom_timer import Timer
from math import sin

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, frames, game_data):
        # Setup
        super().__init__(groups)
        self.z_index = Z_LAYERS["main"]
        self.game_data = game_data

        # Images
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = "idle", True
        self.image = self.frames[self.state][self.frame_index]

        # Rects
        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox = self.rect.inflate(-76, -36)
        self.old_rect = self.hitbox.copy()

        # Movement
        self.direction = Vector2()
        self.speed = PLAYER_SPEED
        self.gravity = GRAVITY
        self.jump = False
        self.jump_height = JUMP_HEIGHT
        self.attacking = False

        # Collision
        self.collision_sprites = collision_sprites
        self.on_surface = {
            "floor": False,
            "left_wall": False,
            "right_wall": False
        }
        self.platform = None

        # self.display_surface = pygame.display.get_surface()

        # Timer 
        self.timers = {
            "wall_jump": Timer(400),
            "block_wall_slide": Timer(250),
            "block_attack": Timer(500),
            "hit": Timer(600)
        }
   
    def input(self):
        keys = pygame.key.get_pressed()
        input_vector = Vector2(0, 0)
        

        if keys[pygame.K_d]:
            input_vector.x += 1
            self.facing_right = True
        
        if keys[pygame.K_a]:
            input_vector.x -= 1
            self.facing_right = False

        if keys[pygame.K_k]:
            self.attack()
        
        self.direction.x = input_vector.normalize().x if input_vector else input_vector.x

        if keys[pygame.K_w]:
            self.jump = True            

    def attack(self):
        if not self.timers["block_attack"].active:
            self.attacking = True
            self.frame_index = 0
            self.timers["block_attack"].activate()

    def move(self, dt):
        self.hitbox.x += self.direction.x * self.speed * dt
        self.collision("horizontal")


        if not self.on_surface["floor"] and any((self.on_surface["left_wall"], self.on_surface["right_wall"])) and not self.timers["block_wall_slide"].active:
            self.direction.y = 0
            self.hitbox.y += self.gravity / 15 * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.hitbox.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt

        if self.jump:
            if self.on_surface["floor"]:
                self.direction.y = -self.jump_height
                self.timers["block_wall_slide"].activate()
                self.hitbox.bottom -= 1
            elif  any((self.on_surface["left_wall"], self.on_surface["right_wall"])) and not self.timers["block_wall_slide"].active:
                self.timers["wall_jump"].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surface["left_wall"] else -1
                
            self.jump = False   

        self.collision("vertical")
        self.rect.center = self.hitbox.center

    def platform_movement(self, dt):
        if self.platform:
            self.hitbox.topleft += self.platform.direction * self.platform.speed * dt

    def check_contact(self):
        floor_rect = pygame.Rect(self.hitbox.bottomleft, (self.hitbox.width, 2))
        right_wall_rect = pygame.Rect(self.hitbox.topright + Vector2(0, self.hitbox.height / 4), (2, self.hitbox.height / 2))
        left_wall_rect = pygame.Rect(self.hitbox.topleft + Vector2(-2, self.hitbox.height / 4), (2, self.hitbox.height / 2))

        # Debug collision rects
        # pygame.draw.rect(self.display_surface, "red", floor_rect)
        # pygame.draw.rect(self.display_surface, "red", right_wall_rect)
        # pygame.draw.rect(self.display_surface, "red", left_wall_rect)

        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        # Check for collisions here
        self.on_surface["floor"] = True if floor_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface["right_wall"] = True if right_wall_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface["left_wall"] = True if left_wall_rect.collidelist(collide_rects) >= 0 else False

        self.platform = None
        for sprite in [sprite for sprite in self.collision_sprites.sprites() if hasattr(sprite, "moving")]:
            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if axis == "horizontal":
                    # Left
                    if self.hitbox.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right):
                        self.hitbox.left = sprite.rect.right

                    # Right
                    if self.hitbox.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox.right = sprite.rect.left
                else: 
                    # Top
                    if self.hitbox.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.rect.top = sprite.rect.bottom

                    # Bottom
                    if self.hitbox.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox.bottom = sprite.rect.top
                    
                    self.direction.y = 0

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def animate(self, dt):
        self.frame_index += (PLAYER_ANIMATION_SPEED if self.state != "attack" else PLAYER_ATTACK_ANIMATION_SPEED) * dt

        if self.state == "attack" and self.frame_index >= len(self.frames[self.state]):
            self.state = "idle"
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

        if self.attacking and self.frame_index >= len(self.frames[self.state]):
            self.attacking = False
            self.frame_index = 0

    def set_state(self):
        if self.on_surface["floor"]:
            if self.attacking:
                self.state = "attack"
            else:
                  self.state = "idle" if self.direction.x == 0 else "run"
        else:
            if self.attacking:
                self.state = "attack"
            else:
                self.state = "jump" if self.direction.y < 0 else "fall"

    def set_damage(self):
        if not self.timers["hit"].active:
            self.game_data.health -= 1
            self.timers["hit"].activate()

    def flicker(self):
        if self.timers["hit"].active and sin(pygame.time.get_ticks() / 75) >= 0:
            white_mask = pygame.mask.from_surface(self.image)
            white_surf = white_mask.to_surface()
            white_surf.set_colorkey("black")
            self.image = white_surf

    def update(self, dt):
        self.old_rect = self.hitbox.copy()
        self.update_timers()

        self.input()
        self.move(dt)
        self.platform_movement(dt)
        self.check_contact()

        self.set_state()
        self.animate(dt)
        self.flicker()