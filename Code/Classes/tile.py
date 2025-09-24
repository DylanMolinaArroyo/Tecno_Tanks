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
        super().__init__(groups)

        self.sprite_type = sprite_type
        self.image = surface

        self.rect = self.image.get_rect(topleft=pos)

        self.hitbox = self.rect.copy()
        self.hitbox.x += hitbox_left
        self.hitbox.y += hitbox_top
        self.hitbox.width -= (hitbox_left + hitbox_right)
        self.hitbox.height -= (hitbox_top + hitbox_bottom)
