import pygame
import os
from Code.Functions.support import ASSET_CACHE

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, groups, folder_path="Assets/Effects/Circle_explosion"):
        """
        Initializes an explosion effect at the given position.

        Args:
            pos (tuple): (x, y) position for the explosion center.
            groups (list): Sprite groups to add this explosion to.
            folder_path (str): Path to the folder containing explosion frames.
        """

        super().__init__(groups)
        self.sprite_type = 'explosion'

        
        self.frames = ASSET_CACHE['explosion']

        self.frame_index = 0
        
        if self.frames:
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=pos)
        else:
            self.image = pygame.Surface((1, 1)) 
            self.rect = self.image.get_rect(center=pos)
            self.kill() 

        self.animation_speed = 0.2
        

    def update(self):
        """
        Updates the explosion animation frame and removes the sprite when finished.
        """
        
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]
