from settings import *
from sprites import Sprite, AnimatedSprite, Node, PlayerIcon, PathSprite
from groups import WordlSprites
from random import randint

class Overworld:
    def __init__(self, tmx_map, game_data, overworld_frames, change_stage):
        self.display_surface = pygame.display.get_surface()

        # Level data
        self.game_data = game_data
        self.change_stage = change_stage

        # Groups
        self.all_sprites = WordlSprites(game_data)
        self.node_sprites = pygame.sprite.Group()

        self.setup(tmx_map, overworld_frames)        

        self.current_node = [node for node in self.node_sprites if node.level == 0][0]
        self.path_frames = overworld_frames["path"]

        self.create_path_sprites()
        

    def input(self):
        keys = pygame.key.get_pressed()
        if self.current_node and not self.player_icon.path:
            if keys[pygame.K_s] and self.current_node.can_move("down"):
                self.move("down")
            if keys[pygame.K_a] and self.current_node.can_move("left"):
                self.move("left")
            if keys[pygame.K_d] and self.current_node.can_move("right"):
                self.move("right")
            if keys[pygame.K_w] and self.current_node.can_move("up"):
                self.move("up")
            if keys[pygame.K_RETURN]:
                self.game_data.current_level = self.current_node.level
                self.change_stage("level")

    def move(self, direction):
        path_key = int(self.current_node.paths[direction][0])
        path_reverse = True if self.current_node.paths[direction][-1] == "r" else False
        path = self.paths[path_key]["pos"][:] if not path_reverse else self.paths[path_key]["pos"][::-1]
        self.player_icon.start_move(path)

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
        
        # Paths
        self.paths = {}
        for obj in tmx_map.get_layer_by_name("paths"):        
            pos = [(int(p.x + TILE_SIZE / 2), int(p.y + TILE_SIZE / 2)) for p in obj.points]
            start = obj.properties["start"]
            end = obj.properties["end"]
            self.paths[end] = {"pos": pos, "start": start}

        # Nodes and player
        for obj in tmx_map.get_layer_by_name("nodes"):
            # Player
            if obj.name == "Node" and obj.properties["stage"] == self.game_data.current_level:
                self.player_icon = PlayerIcon((obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2), self.all_sprites, overworld_frames["player_icon"])
            
            # Nodes
            if obj.name == "Node":
                available_paths = {k: v for k, v in obj.properties.items() if k in ("left", "right", "up", "down")}
                Node(
                    pos = (obj.x, obj.y),
                    surface = overworld_frames["path"]["node"],
                    groups = (self.all_sprites, self.node_sprites),
                    level = obj.properties["stage"],
                    game_data = self.game_data,
                    paths = available_paths
                )

    def create_path_sprites(self):
        nodes = {node.level: Vector2(node.grid_pos) for node in self.node_sprites}
        path_tiles = {}
        for path_id, data in self.paths.items():
            path = data["pos"]
            start_node, end_node = nodes[data["start"]], nodes[path_id]
            path_tiles[path_id] = [start_node]
            
            for index, points in enumerate(path):
                if index < len(path) - 1:
                    start, end = Vector2(points), Vector2(path[index + 1])
                    path_direction = (end - start) / TILE_SIZE
                    start_tile = Vector2(int(start[0] / TILE_SIZE), int(start[1] / TILE_SIZE))

                    if path_direction.y:
                        direction_y = 1 if path_direction.y > 0 else -1
                        for y in range(direction_y, int(path_direction.y) + direction_y, direction_y):
                            path_tiles[path_id].append(start_tile + (0, y))

                    if path_direction.x:
                        direction_x = 1 if path_direction.x > 0 else -1
                        for x in range(direction_x, int(path_direction.x) + direction_x, direction_x):
                            path_tiles[path_id].append(start_tile + (x, 0))
            
            path_tiles[path_id].append(end_node)

        # Create path sprites
            for key, path in path_tiles.items():
                for index, tile in enumerate(path):
                    if index > 0 and index < len(path) - 1:
                        prev_tile = path[index - 1] - tile
                        next_tile = path[index + 1] - tile

                        if prev_tile.x == next_tile.x:
                            surface = self.path_frames["vertical"]
                        elif prev_tile.y == next_tile.y:
                            surface = self.path_frames["horizontal"]
                        else:
                            if prev_tile.x == -1 and next_tile.y == -1 or prev_tile.y == -1 and next_tile.x == -1:
                                surface = self.path_frames['tl']
                            elif prev_tile.x == 1 and next_tile.y == 1 or prev_tile.y == 1 and next_tile.x == 1:
                                surface = self.path_frames['br']
                            elif prev_tile.x == -1 and next_tile.y == 1 or prev_tile.y == 1 and next_tile.x == -1:
                                surface = self.path_frames['bl']
                            elif prev_tile.x == 1 and next_tile.y == -1 or prev_tile.y == -1 and next_tile.x == 1:
                                surface = self.path_frames['tr']
                            else:
                                surface = self.path_frames['horizontal']


                        PathSprite(
                            pos = (tile.x * TILE_SIZE, tile.y * TILE_SIZE), 
                            surface = surface,
                            groups = self.all_sprites,
                            level = key
                        )


    def get_current_node(self):
        nodes = pygame.sprite.spritecollide(self.player_icon, self.node_sprites, False)
        if nodes:
            self.current_node = nodes[0]

    def run(self, dt):
        self.input()
        self.get_current_node()
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.player_icon.rect.center)