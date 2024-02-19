from settings import *
from custom_timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill("green")

        # Rects
        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect = self.rect.copy()

        # Movement
        self.direction = Vector2()
        self.speed = PLAYER_SPEED
        self.gravity = GRAVITY
        self.jump = False
        self.jump_height = JUMP_HEIGHT

        # Collision
        self.collision_sprites = collision_sprites
        self.on_surface = {
            "floor": False,
            "left_wall": False,
            "right_wall": False
        }

        # self.display_surface = pygame.display.get_surface()

        # Timer 
        self.timers = {
            "wall_jump": Timer(400),
            "block_wall_slide": Timer(250)
        }

        
    def input(self):
        keys = pygame.key.get_pressed()
        input_vector = Vector2(0, 0)
        
        # if not self.timers["wall_jump"].active:
        if keys[pygame.K_d]:
            input_vector.x += 1
        if keys[pygame.K_a]:
            input_vector.x -= 1
        
        self.direction.x = input_vector.normalize().x if input_vector else input_vector.x

        if keys[pygame.K_w]:
            self.jump = True            

    def move(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.collision("horizontal")


        if not self.on_surface["floor"] and any((self.on_surface["left_wall"], self.on_surface["right_wall"])) and not self.timers["block_wall_slide"].active:
            self.direction.y = 0
            self.rect.y += self.gravity / 15 * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.rect.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt

        if self.jump:
            if self.on_surface["floor"]:
                self.direction.y = -self.jump_height
                self.timers["block_wall_slide"].activate()
            elif  any((self.on_surface["left_wall"], self.on_surface["right_wall"])) and not self.timers["block_wall_slide"].active:
                self.timers["wall_jump"].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surface["left_wall"] else -1
                
            self.jump = False   

        self.collision("vertical")


    def check_contact(self):
        floor_rect = pygame.Rect(self.rect.bottomleft, (self.rect.width, 2))
        right_wall_rect = pygame.Rect(self.rect.topright + Vector2(0, self.rect.height / 4), (2, self.rect.height / 2))
        left_wall_rect = pygame.Rect(self.rect.topleft + Vector2(-2, self.rect.height / 4), (2, self.rect.height / 2))

        # Debug collision rects
        # pygame.draw.rect(self.display_surface, "red", floor_rect)
        # pygame.draw.rect(self.display_surface, "red", right_wall_rect)
        # pygame.draw.rect(self.display_surface, "red", left_wall_rect)

        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        # Check for collisions here
        self.on_surface["floor"] = True if floor_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface["right_wall"] = True if right_wall_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface["left_wall"] = True if left_wall_rect.collidelist(collide_rects) >= 0 else False

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if axis == "horizontal":
                    # Left
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right

                    # Right
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                else: 
                    # Top
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rec.top = sprite.rect.bottom

                    # Bottom
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                    
                    self.direction.y = 0

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.update_timers()
        self.input()
        self.move(dt)
        self.check_contact()