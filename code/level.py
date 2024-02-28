from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite, Spike, Item, ParticleEffectSprite
from player import Player
from groups import AllSprites

class Level:
    def __init__(self, tmx_map, level_frames, audio_files, game_data, change_stage):
        self.display_surface = pygame.display.get_surface()
        self.game_data = game_data
        self.change_stage = change_stage

        # Level data
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE
        tmx_level_properties = tmx_map.get_layer_by_name("data")[0].properties
        self.level_unlock = tmx_level_properties["level_unlock"]
        if tmx_level_properties["bg"]:
            background_tile = level_frames["background_tiles"][tmx_level_properties["bg"]]
        else:
            background_tile = None

        # Groups
        self.all_sprites = AllSprites(
            width = tmx_map.width,
            height = tmx_map.height,
            bg_tile = background_tile,
            top_limit = tmx_level_properties["top_limit"],
            clouds = {"large_cloud": level_frames["large_cloud"], "small_cloud": level_frames["small_cloud"]},
            horizon_line = tmx_level_properties["horizon_line"]
        )
        self.collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.setup(tmx_map, level_frames, audio_files)

        # Frames
        self.particle_frames = level_frames["particle"]

        # Sounds
        self.coin_sound = audio_files["coin"]
        self.coin_sound.set_volume(0.02)
        self.damage_sound = audio_files["damage"]
        self.damage_sound.set_volume(0.05)
        self.level_finish_sound = audio_files["door"]
        self.level_finish_sound.set_volume(0.05)


    def setup(self, tmx_map, level_frames, audio_files):
        # Tiles
        for layer in ["background", "terrain" , "platforms", "foreground"]:
            for x, y, surface in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == "terrain": groups.append(self.collision_sprites)
                if layer == "platforms": groups.append(self.collision_sprites)

                match layer:
                    case "background" : z_index = Z_LAYERS["background_tiles"]
                    case "foreground" : z_index = Z_LAYERS["foreground"]
                    case _ : z_index = Z_LAYERS["main"]

                Sprite((x * TILE_SIZE, y * TILE_SIZE), surface, groups, z_index)

        # Objects 
        for obj in tmx_map.get_layer_by_name("objects"):
            if obj.name == "player":
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, level_frames["player"], self.game_data, audio_files["jump"])
            else:
                if obj.name in ("door"):
                    self.level_finish = pygame.FRect((obj.x, obj.y), (obj.width, obj.height))
                    Sprite((obj.x, obj.y), obj.image, self.all_sprites, Z_LAYERS["background_details"])
                else:
                    frames = level_frames[obj.name]
                    if obj.name == "candle":
                        AnimatedSprite((obj.x, obj.y), frames, self.all_sprites, Z_LAYERS["background_details"])
                    else:
                        AnimatedSprite((obj.x, obj.y), frames, self.all_sprites, Z_LAYERS["background_details"], 3)

        # Items
        for obj in tmx_map.get_layer_by_name("items"):
            Item(obj.name, (obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2), level_frames["items"][obj.name], (self.all_sprites, self.item_sprites), self.game_data)

        # Moving objects
        for obj in tmx_map.get_layer_by_name("moving"): 
            if obj.name == "spike":
                Spike(
                    pos = (obj.x + obj.width / 2, obj.y + obj.height / 2),
                    surface = level_frames["spike"],
                    radius = obj.properties["radius"],
                    speed = obj.properties["speed"],
                    start_angle = obj.properties["start_angle"],
                    end_angle = obj.properties["end_angle"],
                    groups = (self.all_sprites, self.collision_sprites, self.damage_sprites)
                )

                # Draw spike chains
                for radius in range(0, obj.properties['radius'], 20):
                 Spike(
                    pos = (obj.x + obj.width / 2, obj.y + obj.height / 2),
                    surface = level_frames["spike_chain"],
                    radius = radius,
                    speed = obj.properties["speed"],
                    start_angle = obj.properties["start_angle"],
                    end_angle = obj.properties["end_angle"],
                    groups = self.all_sprites,
                    z_index = Z_LAYERS['background_details']
                )   

            else:
                frames = level_frames[obj.name]
                groups = (self.all_sprites, self.collision_sprites) if obj.properties["platform"] else (self.all_sprites, self.damage_sprites)
                # groups = (self.all_sprites, self.damage_sprites, self.collision_sprites)
                if obj.width > obj.height:
                    # Horizontal movement
                    move_dir = "x"
                    start_pos = (obj.x, obj.y + obj.height / 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
                else:
                    # Vertical movement
                    move_dir = "y"
                    start_pos = (obj.x + obj.width / 2, obj.y)
                    end_pos = (obj.x + obj.width / 2, obj.y + obj.height)
                speed = obj.properties["speed"]
                MovingSprite(frames, groups, start_pos, end_pos, move_dir, speed)

                # Draw saw chains
                if obj.name == 'saw':
                    if move_dir == 'x':
                        y = start_pos[1] - level_frames['saw_chain'].get_height() / 2
                        left, right = int(start_pos[0]), int(end_pos[0])
                        for x in range(left, right, 20):
                            Sprite((x,y), level_frames['saw_chain'], self.all_sprites, Z_LAYERS['background_details'])
                    else:
                        x = start_pos[0] - level_frames['saw_chain'].get_width() / 2
                        top, bottom = int(start_pos[1]), int(end_pos[1])
                        for y in range(top, bottom, 20):
                            Sprite((x,y), level_frames['saw_chain'], self.all_sprites, Z_LAYERS['background_details'])

    def player_hit(self):
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox):
                self.player.set_damage()
                self.damage_sound.play()

    def item_collision(self):
        if self.item_sprites:
            item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            if item_sprites:
                item_sprites[0].activate()
                ParticleEffectSprite((item_sprites[0].rect.center), self.particle_frames, self.all_sprites)
                self.coin_sound.play()
    
    def check_level_constraints(self):
        # Left border
        if self.player.hitbox.left <= 0:
            self.player.hitbox.left = 0

        # Right border
        if self.player.hitbox.right >= self.level_width:
            self.player.hitbox.right = self.level_width

        # Bottom border
        if self.player.hitbox.bottom > self.level_height:
            self.change_stage("overworld", -1)
            
        # Level success
        if self.player.hitbox.colliderect(self.level_finish):
            self.level_finish_sound.play()
            self.change_stage("overworld", self.level_unlock)

    def run(self, dt):
        # self.display_surface.fill("black")
        self.all_sprites.update(dt)

        self.player_hit()
        self.item_collision()

        self.check_level_constraints()

        self.all_sprites.draw(self.player.hitbox.center, dt)