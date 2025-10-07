import pygame
from Code.Utilities.settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(
        self,
        pos,
        groups,
        sprite_type,
        surface=pygame.Surface((TILESIZE, TILESIZE)),
        hitbox_left=10, hitbox_right=10, hitbox_top=10, hitbox_bottom=10
    ):
        """
        Initializes a tile object for the game map.

        Args:
            pos (tuple): (x, y) position of the tile.
            groups (list): Sprite groups to add this tile to.
            sprite_type (str): Type/name of the tile (e.g., 'wall', 'grass').
            surface (pygame.Surface): Surface image for the tile.
            hitbox_left (int): Left hitbox padding.
            hitbox_right (int): Right hitbox padding.
            hitbox_top (int): Top hitbox padding.
            hitbox_bottom (int): Bottom hitbox padding.
        """
        
        super().__init__(groups)

        self.sprite_type = sprite_type
        self.image = surface

        self.rect = self.image.get_rect(topleft=pos)

        self.hitbox = self.rect.copy()
        self.hitbox.x += hitbox_left
        self.hitbox.y += hitbox_top
        self.hitbox.width -= (hitbox_left + hitbox_right)
        self.hitbox.height -= (hitbox_top + hitbox_bottom)
