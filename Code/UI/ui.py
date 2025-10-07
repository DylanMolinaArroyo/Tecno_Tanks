import pygame
from Code.Utilities.settings import *

class UI:
    def __init__(self):
        """
        Initializes the UI object, sets up fonts, images, positions, and power-up icons.
        """

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

        # Power-ups setup
        self.icon_size = (40, 40)
        self.powerup_icons = {
            "shield": pygame.transform.scale(pygame.image.load("Assets/Objects/PowerUps/shield.png"), self.icon_size),
            "weapon": pygame.transform.scale(pygame.image.load("Assets/Objects/PowerUps/shoot_upgrade.png"), self.icon_size),
            "slow": pygame.transform.scale(pygame.image.load("Assets/Objects/PowerUps/clock.png"), self.icon_size),
            "machine_gun": pygame.transform.scale(pygame.image.load("Assets/Objects/PowerUps/machine_gun.png"), self.icon_size),
            "fortress_shield": pygame.transform.scale(pygame.image.load("Assets/Objects/PowerUps/fortress_shield.png"), self.icon_size)
        }
        self.powerup_start_y = 250

        self.powerup_spacing = 60
        self.bar_height = 6
        self.margin = 10



    def show_health(self, current, max_amount):
        """
        Displays the player's health as heart icons.

        Args:
            current (int): Current health value.
            max_amount (int): Maximum health value.
        """

        for i in range(max_amount):
            if i < current:
                self.display_surface.blit(self.heart_image, (self.heart_rect.x + i * (self.heart_rect.width + 1), self.heart_rect.y))
            else:
                self.display_surface.blit(self.empty_heart_image, (self.heart_rect.x + i * (self.heart_rect.width + 1), self.heart_rect.y))

    def show_timer(self):
        """
        Displays the elapsed game time in MM:SS format with an outlined font.
        """

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
        """
        Displays the current difficulty level.

        Args:
            difficulty_name (str): Name of the difficulty.
        """

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
        """
        Displays the current wave/round information.

        Args:
            total_rounds (int): Total number of rounds.
            current_round (int): Current round number.
        """

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
        """
        Displays a countdown timer for the next wave.

        Args:
            duration (int): Duration of the countdown in seconds.

        Returns:
            bool: True if the countdown has finished, False otherwise.
        """

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

    def show_powerups(self, player):
        """
        Displays active power-ups and their remaining duration as icons and bars.

        Args:
            player (Player): Reference to the player object.
        """

        current_time = pygame.time.get_ticks()
        x = self.display_surface.get_width() - self.margin
        y = self.margin
        bar_height = 8
        spacing = 60

        def draw_bar(icon, remaining, total, pos_x, pos_y):

            icon_rect = icon.get_rect(topright=(pos_x, pos_y))
            self.display_surface.blit(icon, icon_rect)

            # Barra debajo del ícono
            bar_width = icon_rect.width

            fill_ratio = max(0, min(1, remaining / total))

            background_rect = pygame.Rect(icon_rect.left, icon_rect.bottom + 4, bar_width, bar_height)
            health_rect = pygame.Rect(icon_rect.left, icon_rect.bottom + 4, int(bar_width * fill_ratio), bar_height)

            pygame.draw.rect(self.display_surface, (0, 0, 0), background_rect)
            pygame.draw.rect(self.display_surface, (0, 255, 0), health_rect)
            pygame.draw.rect(self.display_surface, (0, 0, 0), background_rect, 2)

        # Shield
        if player.shield_active:
            total = player.shield_duration
            remaining = max(0, (player.shield_end_time - current_time))
            draw_bar(self.powerup_icons["shield"], remaining, total, x, y)
            y += spacing

        # Weapon upgrade
        if player.shoot_upgrade_active:
            total = player.shoot_upgrade_duration
            remaining = max(0, (player.shoot_upgrade_end - current_time))
            draw_bar(self.powerup_icons["weapon"], remaining, total, x, y)
            y += spacing

        # Slow motion
        if player.slow_motion_active:
            total = player.slow_motion_duration
            remaining = max(0, (player.slow_motion_end - current_time))
            draw_bar(self.powerup_icons["slow"], remaining, total, x, y)

        # Machine gun
        if player.machine_gun_active:
            total = player.machine_gun_duration
            remaining = max(0, (player.machine_gun_end - current_time))
            draw_bar(self.powerup_icons["machine_gun"], remaining, total, x, y)

        # Fortress shield
        if player.fortress_shield_active:
            total = player.fortress_shield_duration
            remaining = max(0, (player.fortress_shield_end - current_time))
            draw_bar(self.powerup_icons["fortress_shield"], remaining, total, x, y)
            
    def display(self, player, difficulty_name, total_rounds, current_round):
        """
        Displays all UI elements: health, timer, difficulty, rounds, and power-ups.

        Args:
            player (Player): Reference to the player object.
            difficulty_name (str): Name of the difficulty.
            total_rounds (int): Total number of rounds.
            current_round (int): Current round number.
        """

        self.show_health(player.health, player.stats['health'])
        self.show_timer()
        self.show_difficulty(difficulty_name)
        self.show_rounds(total_rounds, current_round)
        self.show_powerups(player)