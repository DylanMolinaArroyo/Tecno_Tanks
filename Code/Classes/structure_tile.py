from Code.Classes.tile import Tile
from Code.Utilities.settings import *

class Structure_tile(Tile):
    def __init__(self, pos, groups, estructure_name, surface, player,hitbox_left=10, hitbox_right=10, hitbox_top=10, hitbox_bottom=10):
        """
        Initializes a structure tile object.

        Args:
            pos (tuple): (x, y) position of the tile.
            groups (list): Sprite groups to add this tile to.
            estructure_name (str): Name/type of the structure.
            surface (pygame.Surface): Surface image for the tile.
            player (Player): Reference to the player object.
            hitbox_left (int): Left hitbox padding.
            hitbox_right (int): Right hitbox padding.
            hitbox_top (int): Top hitbox padding.
            hitbox_bottom (int): Bottom hitbox padding.
        """
        
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

        self.destroyed = False

    def get_grid_position(self):
        """
        Returns the grid position of the structure tile.

        Returns:
            list: [grid_x, grid_y]
        """
        
        grid_x = self.rect.centerx // TILESIZE
        grid_y = self.rect.centery // TILESIZE
        
        return [grid_x, grid_y]
    
    def get_damage(self, player, attack_type):
        """
        Applies damage to the structure tile if hit by a bullet.

        Args:
            player (Player): Reference to the player object.
            attack_type (str): Type of attack (e.g., 'bullet').
        """

        if attack_type == 'bullet':
            self.health -= player.return_damage()

    def check_death(self):
        """
        Checks if the structure's health is depleted and destroys it if so.
        """

        if self.health <= 0:
            self.destroyed = True
            self.kill()
    
    def structure_update(self):
        """
        Updates the structure tile.
        """

        self.check_death()