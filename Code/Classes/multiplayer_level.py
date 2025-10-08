import pygame
import random
from Code.Classes.level import Level
from Code.Utilities.settings import *
from Code.Entities.player import Player
from Code.Classes.tile import Tile
from Code.Classes.structure_tile import Structure_tile
from Code.Functions.support import import_csv_layout, get_random_position
from random import choice

class MultiplayerLevel:
    def __init__(self, difficulty_config, network_client, player_number):
        print(f"DEBUG MultiplayerLevel: Iniciando con dificultad: {difficulty_config}")
        
        # Configuración básica
        self.difficulty_config = difficulty_config
        self.network_client = network_client
        self.player_number = player_number
        self.display_surface = pygame.display.get_surface()
        
        # Usar el Level original como base
        try:
            self.level = Level(difficulty_config)
            self.player = self.level.player
            self.structure = self.level.structure
            self.enemies = self.level.enemies
            self.enemy_queue = self.level.enemy_queue
            
            print(f"DEBUG MultiplayerLevel: Level base inicializado correctamente")
        except Exception as e:
            print(f"ERROR MultiplayerLevel: No se pudo inicializar Level base: {e}")
            # Crear una versión mínima si falla
            self.setup_minimal_level()
        
        # Configurar manejadores de red
        self.setup_network_handlers()
        
        print(f"DEBUG MultiplayerLevel: Inicializado completamente - Jugador {player_number}")
    
    def setup_minimal_level(self):
        """Configuración mínima si Level falla"""
        self.player = type('MockPlayer', (), {'health': 100})()
        self.structure = type('MockStructure', (), {'destroyed': False})()
        self.enemies = []
        self.enemy_queue = []
        print("DEBUG MultiplayerLevel: Usando configuración mínima")
    
    def setup_network_handlers(self):
        """Configurar manejadores de mensajes de red"""
        def handle_state_update(message):
            # Por implementar
            pass
        
        def handle_player_action(message):
            # Por implementar
            pass
        
        self.network_client.register_handler('state_update', handle_state_update)
        self.network_client.register_handler('player_action', handle_player_action)
    
    def run(self):
        """Método principal - versión simple para probar"""
        try:
            print("DEBUG MultiplayerLevel: run() llamado")
            
            # Si tenemos un Level base válido, usarlo
            if hasattr(self, 'level') and self.level:
                print("DEBUG MultiplayerLevel: Usando Level base")
                self.level.run()
                
                # Verificar fin del juego
                if self.level.player.health <= 0:
                    return 'lose'
                elif self.level.structure.destroyed:
                    return 'lose'  
                elif self.level.all_enemies_defeated() and not self.level.enemy_queue and not self.level.enemies:
                    return 'win'
                    
            else:
                # Modo de prueba simple
                print("DEBUG MultiplayerLevel: Usando modo prueba")
                return self.run_test_mode()
                
        except Exception as e:
            print(f"ERROR MultiplayerLevel en run(): {e}")
            return 'error'
    
    def run_test_mode(self):
        """Modo de prueba cuando Level falla"""
        # Pantalla de prueba
        self.display_surface.fill((30, 30, 60))
        
        # Título
        font_large = pygame.font.Font(None, 74)
        title = font_large.render(f"MULTIPLAYER - Jugador {self.player_number}", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH//2, HEIGTH//2 - 100))
        self.display_surface.blit(title, title_rect)
        
        # Información de dificultad
        font_medium = pygame.font.Font(None, 48)
        diff_text = font_medium.render(f"Dificultad: {self.difficulty_config.get('name', 'Unknown')}", True, (200, 200, 100))
        diff_rect = diff_text.get_rect(center=(WIDTH//2, HEIGTH//2))
        self.display_surface.blit(diff_text, diff_rect)
        
        # Instrucciones
        font_small = pygame.font.Font(None, 36)
        inst_text = font_small.render("Presiona ESC para volver al menú", True, (150, 150, 255))
        inst_rect = inst_text.get_rect(center=(WIDTH//2, HEIGTH//2 + 100))
        self.display_surface.blit(inst_text, inst_rect)
        
        # Verificar si presiona ESC para volver
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return 'menu'
            
        return 'playing'