from settings import *
from sprites import Sprite, AnimatedSprite, Node, PlayerIcon
from groups import WordlSprites
from random import randint

class Overworld:
    def __init__(self, tmx_map, game_data, overworld_frames):
        self.display_surface = pygame.display.get_surface()
        self.game_data = game_data

        # Level data

        # Groups
        self.all_sprites = WordlSprites(game_data)

        self.setup(tmx_map, overworld_frames)        
        

    def setup(self, tmx_map, overworld_frames):
        # Tiles
        for layer in ["main", "top"]:
            for x, y, surface in tmx_map.get_layer_by_name(layer).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surface, self.all_sprites, Z_LAYERS["background_tiles"])

        # Water
        for col in range(tmx_map.width):
            for row in range(tmx_map.height):
                AnimatedSprite((col * TILE_SIZE, row * TILE_SIZE), overworld_frames["water"], self.all_sprites, Z_LAYERS["background"])

        # Objects
        for obj in tmx_map.get_layer_by_name("objects"):
            if obj.name == "palm":
                AnimatedSprite((obj.x, obj.y), overworld_frames["palms"], self.all_sprites, Z_LAYERS["main"], randint(4, 6))
            else:
                z_index = Z_LAYERS[f"{"background_details" if obj.name == "grass" else "background_tiles"}"]
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, z_index)
        
        # Nodes and player
        for obj in tmx_map.get_layer_by_name("nodes"):
            # Player
            if obj.name == "Node" and obj.properties["stage"] == self.game_data.current_level:
                self.player_icon = PlayerIcon((obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2), self.all_sprites, overworld_frames["player_icon"])
            
            # Nodes
            if obj.name == "Node":
                Node(
                    pos = (obj.x, obj.y),
                    surface = overworld_frames["path"]["node"],
                    groups = self.all_sprites,
                    level = obj.properties["stage"],
                    game_data = self.game_data
                )

    def run(self, dt):
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.player_icon.rect.center)