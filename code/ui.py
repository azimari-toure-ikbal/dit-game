from settings import *
from sprites import Heart
from custom_timer import Timer

class UI:
    def __init__(self, font, frames):
        self.display_surface = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.font = font

        # Health
        self.hearts_frames = frames["heart"]
        self.heart_surface_width = self.hearts_frames[0].get_width()
        self.heart_padding = 5

        # Score
        self.player_score = 0
        self.score_timer = Timer(1000)



    def create_hearts(self, amount):
        for sprite in self.sprites:
            sprite.kill()

        for heart in range(amount):
            x = 10 + heart * (self.heart_surface_width + self.heart_padding)
            y = 10
            Heart((x, y), self.hearts_frames, self.sprites)

    def display_text(self):
        if self.score_timer.active:
            text_surface = self.font.render(f"Score: {self.player_score}", False, "white")
            text_rect = text_surface.get_frect(topleft = (16, 34))
            self.display_surface.blit(text_surface, text_rect)

    def update_score(self, amount):
        self.player_score = amount
        self.score_timer.activate()

    def update(self, dt):
        self.score_timer.update()
        self.sprites.update(dt)
        self.sprites.draw(self.display_surface)
        self.display_text()