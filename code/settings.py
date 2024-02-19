import pygame, sys
from pygame.math import Vector2 

WINDOW_WIDTH, WINDOW_HEIGHT = 1080, 720
GAME_TITLE = "Celeste hell"
TILE_SIZE = 32
PLAYER_SPEED = 200
GRAVITY = 1600
JUMP_HEIGHT = 450
ANIMATION_SPEED = 6

Z_LAYERS = {
    "background": 0,
    "clouds": 1,
    "background tiles": 2,
    "path": 3,
    "background details": 4,
    "main": 5,
    "water": 6,
    "foreground": 7,
}