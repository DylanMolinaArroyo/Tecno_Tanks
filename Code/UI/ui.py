import pygame
from Code.Utilities.settings import *

class UI:
    def __init__(self):
        # General
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONTSIZE)

        # Health setup
        self.heart_image = pygame.image.load('Assets/UI/heart/full_heart.png')  
        self.empty_heart_image = pygame.image.load('Assets/UI/heart/empty_heart.png')
        self.heart_rect = self.heart_image.get_rect()

        # Resize hearts
        self.heart_size = (48, 48)
        self.heart_image = pygame.transform.scale(self.heart_image, self.heart_size)
        self.empty_heart_image = pygame.transform.scale(self.empty_heart_image, self.heart_size)
        
        # Heart rectangle setup
        self.heart_rect.x = 10
        self.heart_rect.y = 10
        
    def show_health(self, current, max_amount):
        for i in range(max_amount):
            if i < current:
                self.display_surface.blit(self.heart_image, (self.heart_rect.x + i * (self.heart_rect.width + 1), self.heart_rect.y))
            else:
                self.display_surface.blit(self.empty_heart_image, (self.heart_rect.x + i * (self.heart_rect.width + 1), self.heart_rect.y))

    def display(self, player):
        self.show_health(player.health, player.stats['health'])
