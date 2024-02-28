import pygame, sys
from pygame.math import Vector2 

WINDOW_WIDTH, WINDOW_HEIGHT = 1080, 720
GAME_TITLE = "Celeste hell"
TILE_SIZE = 64
PLAYER_SPEED = 400
GRAVITY = 1600
JUMP_HEIGHT = 650
ANIMATION_SPEED = 8
PLAYER_ANIMATION_SPEED = 6
PLAYER_ATTACK_ANIMATION_SPEED = 12

Z_LAYERS = {
    "background": 0,
    "clouds": 1,
    "background_tiles": 2,
    "path": 3,
    "background_details": 4,
    "main": 5,
    "foreground": 7,
}