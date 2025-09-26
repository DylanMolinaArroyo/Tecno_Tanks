import pygame
from Code.Classes.tile import Tile
from Code.Utilities.settings import *

class Estructure_tile(Tile):
    def __init__(self, pos, groups, estructure_name, player, hitbox_left=10, hitbox_right=10, hitbox_top=10, hitbox_bottom=10
):

        estructure_info = estructure_data[estructure_name]
        sprite_type = "estructure"

        super().__init__(
            pos, 
            groups, 
            sprite_type, 
            surface=pygame.Surface((TILESIZE, TILESIZE)),
            hitbox_left=hitbox_left,
            hitbox_right=hitbox_right,
            hitbox_top=hitbox_top,
            hitbox_bottom=hitbox_bottom
            )

        self.player = player
        self.estructure_name = estructure_name
        self.health = estructure_info['health']
        self.sound_path = estructure_info['sound']
    
    def get_damage(self, player, attack_type):
        if attack_type == 'bullet':
            self.health -= player.return_damage()

    def check_death(self):
        if self.health <= 0:
            self.kill()
