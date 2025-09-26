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
        self.heart_rect.y = 110

        # Timer setup
        self.start_time = pygame.time.get_ticks()

        self.difficulty_pos = (10, 10)
        self.timer_pos = (10, 180)
        self.round_pos = (10, 50)


    def show_health(self, current, max_amount):
        for i in range(max_amount):
            if i < current:
                self.display_surface.blit(self.heart_image, (self.heart_rect.x + i * (self.heart_rect.width + 1), self.heart_rect.y))
            else:
                self.display_surface.blit(self.empty_heart_image, (self.heart_rect.x + i * (self.heart_rect.width + 1), self.heart_rect.y))

    def show_timer(self):
        # Time passed since start (in ms)
        elapsed_time_ms = pygame.time.get_ticks() - self.start_time
        elapsed_seconds = elapsed_time_ms // 1000
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        time_text = f"{minutes:02}:{seconds:02}"

        # render of the prncipal text
        text_surf = self.font.render(time_text, True, (255, 255, 255))
        
        # render of the border
        border_surf = self.font.render(time_text, True, (0, 0, 0))
        x, y = self.timer_pos
        offsets = [(-2,0),(2,0),(0,-2),(0,2), (-2,-2), (-2,2), (2,-2), (2,2)]
        for ox, oy in offsets:
            self.display_surface.blit(border_surf, (x + ox, y + oy))
        
        self.display_surface.blit(text_surf, self.timer_pos)

    def show_difficulty(self, difficulty_name):
        difficulty_text = f"Difficulty: {difficulty_name}"  
        text_surf = self.font.render(difficulty_text, True, (255, 255, 255))
        
        # render of the border
        border_surf = self.font.render(difficulty_text, True, (0, 0, 0))
        x, y = self.difficulty_pos

        offsets = [(-2,0),(2,0),(0,-2),(0,2), (-2,-2), (-2,2), (2,-2), (2,2)]
        for ox, oy in offsets:
            self.display_surface.blit(border_surf, (x + ox, y + oy))
        
        self.display_surface.blit(text_surf, (x, y))

    def show_rounds(self, total_rounds, current_round):
        round_text = f"Wave {current_round} / {total_rounds}"  
        text_surf = self.font.render(round_text, True, (255, 255, 255))
        
        # render of the border
        border_surf = self.font.render(round_text, True, (0, 0, 0))
        x, y = self.round_pos

        offsets = [(-2,0),(2,0),(0,-2),(0,2), (-2,-2), (-2,2), (2,-2), (2,2)]
        for ox, oy in offsets:
            self.display_surface.blit(border_surf, (x + ox, y + oy))
        
        self.display_surface.blit(text_surf, (x, y))

    def show_next_wave_timer(self, duration=5):
        elapsed_time_ms = pygame.time.get_ticks() - self.start_time
        elapsed_seconds = elapsed_time_ms // 1000

        remaining = max(0, duration - elapsed_seconds)
        wave_text = f"Next wave in: {remaining}"

        border_surf = self.font.render(wave_text, True, (0, 0, 0))
        text_surf = self.font.render(wave_text, True, (255, 255, 255))

        x, y = (self.display_surface.get_width() // 2 - text_surf.get_width() // 2, 250)

        offsets = [(-2,0),(2,0),(0,-2),(0,2), (-2,-2), (-2,2), (2,-2), (2,2)]
        for ox, oy in offsets:
            self.display_surface.blit(border_surf, (x + ox, y + oy))

        self.display_surface.blit(text_surf, (x, y))

        return remaining == 0


    def display(self, player, difficulty_name, total_rounds, current_round):
        self.show_health(player.health, player.stats['health'])
        self.show_timer()
        self.show_difficulty(difficulty_name)
        self.show_rounds(total_rounds, current_round)
