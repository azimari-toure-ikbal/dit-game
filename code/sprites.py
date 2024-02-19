from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surface = pygame.Surface((TILE_SIZE, TILE_SIZE)), groups = None):
        super().__init__(groups)
        self.image = surface
        self.image.fill("white")
        
        # Rects
        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect = self.rect.copy()