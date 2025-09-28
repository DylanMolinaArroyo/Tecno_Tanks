from Code.Classes.tile import Tile
from Code.Utilities.settings import *

class Structure_tile(Tile):
    def __init__(self, pos, groups, estructure_name, surface, player,hitbox_left=10, hitbox_right=10, hitbox_top=10, hitbox_bottom=10
):
        sprite_type = "structure"
        
        super().__init__(
            pos, 
            groups, 
            sprite_type, 
            surface=surface,
            hitbox_left=hitbox_left,
            hitbox_right=hitbox_right,
            hitbox_top=hitbox_top,
            hitbox_bottom=hitbox_bottom
            )

        self.player = player

        self.name = estructure_name

        estructure_info = estructure_data[self.name]
        self.health = estructure_info['health']
        self.sound_path = estructure_info['sound']

    def get_grid_position(self):
        grid_x = self.rect.centerx // TILESIZE
        grid_y = self.rect.centery // TILESIZE
        
        return [grid_x, grid_y]
    def get_damage(self, player, attack_type):
        if attack_type == 'bullet':
            self.health -= player.return_damage()

    def check_death(self):
        if self.health <= 0:
            self.kill()
    
    def structure_update(self):
        self.check_death()