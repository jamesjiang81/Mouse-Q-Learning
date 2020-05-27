import pygame as pg
from settings import *


class Tile:
    def __init__(self, terrain, q_value=0):
        self.terrain = terrain
        self.q_value = q_value


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load("gameMouse.jpg")
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y

    def move(self, game, dx=0, dy=0):
        if (self.x + dx) >= int(game.map_width) or (self.x + dx) < 0:
            return False
        else:
            self.x += dx
        if (self.y + dy) >= int(game.map_height) or (self.y + dy) < 0:
            return False
        else:
            self.y += dy
        return True

    def get_pos(self):
        return self.x, self.y

    def reset(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE


class Goal(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.goals
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load("gameCheese.jpg")
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load("gameCat.jpg")
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
