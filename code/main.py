from settings import *
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import join
from game_data import GameData
from support import *
from debug import debug
from ui import UI
from overworld import Overworld

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock() 
        self.import_assets()

        self.ui = UI(self.font, self.ui_frames)
        self.game_data = GameData(self.ui)

        self.tmx_maps = { 
                0:  load_pygame(join("data", "levels", "level-0.tmx")),
                1:  load_pygame(join("data", "levels", "level-1.tmx")),
                2:  load_pygame(join("data", "levels", "level-2.tmx")),
            }
        
        self.tmx_overworld = load_pygame(join("data", "overworld", "overworld.tmx"))
        self.current_stage = Level(self.tmx_maps[self.game_data.current_level], self.level_frames, self.audio_files, self.game_data, self.change_stage)
        # self.current_stage = Overworld(self.tmx_overworld, self.game_data, self.overworld_frames)

    def change_stage(self, target, unlock = 0):
        if target == "level":
            self.current_stage = Level(self.tmx_maps[self.game_data.current_level], self.level_frames, self.audio_files, self.game_data, self.change_stage)

        else:
            if unlock > 0:
                self.game_data.unlocked_levels = unlock
            else:
                self.game_data.health = 1
            self.current_stage = Overworld(self.tmx_overworld, self.game_data, self.overworld_frames, self.change_stage)

    def import_assets(self):
        self.level_frames = { 
            "gem": import_folder("data", "graphics", "items", "gem"),
            "coin": import_folder("data", "graphics", "items", "coin"),
            "player": import_sub_folders("data", "graphics", "player"),
            "saw": import_folder("data", "graphics", "enemies", "saw", "animation"),
            "saw_chain": import_image("data", "graphics", "enemies", "saw", "saw_chain"),
            "moving_platform": import_folder("data", "graphics", "level", "helicopter"),
            "spike": import_image("data", "graphics", "enemies", "spike_ball", "spike_ball"),
            "spike_chain": import_image("data", "graphics", "enemies", "spike_ball", "spike_chain"),
            "items": import_sub_folders("data", "graphics", "items"),
            "particle": import_folder("data", "graphics", "effects", "particle"),
            "background_tiles": import_folder_dict("data", "graphics",   "level", "bg", "tiles"),
            "candle": import_folder('data', 'graphics','level', "candle"),
            "window": import_folder("data", "graphics", "level", "window"),
            "small_cloud": import_folder("data", "graphics", "level", "clouds", "small"),
            "large_cloud": import_image("data", "graphics", "level", "clouds", "large_cloud"),
            "big_chains": import_folder("data", "graphics", "level", "big_chains"),
            "small_chains": import_folder("data", "graphics", "level", "small_chains"),
        }

        self.font = pygame.font.Font(join("data", "graphics", "ui", "runescape_uf.ttf"), 25)
        self.audio_files = {
            "coin": pygame.mixer.Sound(join("audio", "coin.wav")),
            "jump": pygame.mixer.Sound(join("audio", "jump.wav")),
            "damage": pygame.mixer.Sound(join("audio", "damage.wav")),
            "door": pygame.mixer.Sound(join("audio", "door.mp3")),
        }
        
        self.ui_frames = {
            "heart": import_folder("data", "graphics", "ui", "heart")
        }

        self.overworld_frames = {
            "palms": import_folder("data", "graphics", "overworld", "palm"),
            "water": import_folder("data", "graphics", "overworld", "water"),
            "path": import_folder_dict("data", "graphics", "overworld", "path"),
            "player_icon": import_sub_folders("data", "graphics", "overworld", "icon")
        }

    def check_game_over(self):
        if self.game_data.health <= 0:
            pygame.quit()
            sys.exit()

    def run(self):
        while True:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.check_game_over()
            self.current_stage.run(dt)
            self.ui.update(dt)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
