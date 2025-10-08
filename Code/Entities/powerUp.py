import pygame
from Code.Utilities.settings import TILESIZE
from random import randint


class PowerUp(pygame.sprite.Sprite):
    """
    Represents a collectible power-up entity in the game. Inherits from pygame.sprite.Sprite.
    """ 
    
    def __init__(self, power_type, pos, groups, data):
        """
        Initializes a PowerUp sprite.

        power_type: The type of power-up (e.g., 'shield', 'wrench').
        pos: The (x, y) position to place the power-up.
        groups: Sprite groups to add this power-up to.
        data: Dictionary containing power-up properties (e.g., duration, sound).
        """

        super().__init__(groups)
        self.sprite_type = "powerup"
        self.power_type = power_type
        self.data = data
        self.image = pygame.image.load("Assets/Objects/PowerUps/" + power_type + ".png").convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -10)

    def apply_effect(self, player):
        """
        Applies the power-up effect to the given player.

        Activates the corresponding effect based on power_type.
        Plays a sound effect if specified in data.
        Removes the power-up from all sprite groups after applying the effect.
        """
        
        match self.power_type:
            case 'shield':
                player.activate_shield(self.data["duration_time"])
            case 'shoot_upgrade':
                player.upgrade_shoot(self.data["duration_time"])
            case 'clock':
                player.slow_motion(self.data["duration_time"])
            case 'wrench':
                player.get_health()
            case 'machine_gun':
                player.get_machine_gun(self.data["duration_time"])
            case 'fortress_shield':
                player.fortress_shield(self.data["duration_time"])
            case 'bomb':
                player.bomb_everyone(self.data["duration_time"])
        
        if "sound" in self.data:
            sound = pygame.mixer.Sound(self.data["sound"])
            sound.play()

        self.kill()
