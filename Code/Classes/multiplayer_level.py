import pygame
import random
from Code.Classes.level import Level
from Code.Utilities.settings import *

class MultiplayerLevel:
    def __init__(self, difficulty_config, network_client, player_number):
        print(f"🎮 DEBUG MultiplayerLevel: Iniciando - Jugador {player_number}")
        print(f"🎮 DEBUG Dificultad: {difficulty_config}")
        
        # Configuración básica
        self.difficulty_config = difficulty_config
        self.network_client = network_client
        self.player_number = player_number
        self.display_surface = pygame.display.get_surface()
        
        # Crear Level base
        try:
            self.level = Level(difficulty_config)
            print("🎮 DEBUG: Level base creado exitosamente")
        except Exception as e:
            print(f"❌ ERROR creando Level: {e}")
            self.level = None
        
        # Estado del juego
        self.game_state = 'playing'
        
        # Configurar manejadores de red
        self.setup_network_handlers()
        
        print(f"🎮 DEBUG MultiplayerLevel: Inicialización completada")

    def setup_network_handlers(self):
        """Configurar manejadores de mensajes de red"""
        def handle_state_update(message):
            print(f"🎮 DEBUG: Recibido state_update: {message}")
            # Aquí sincronizaríamos el estado del juego
            
        def handle_player_action(message):
            print(f"🎮 DEBUG: Recibido player_action: {message}")
            # Aquí procesaríamos acciones de otros jugadores
            
        self.network_client.register_handler('state_update', handle_state_update)
        self.network_client.register_handler('player_action', handle_player_action)

    def run(self):
        """Método principal - versión simple para probar"""
        try:
            print("🎮 DEBUG: MultiplayerLevel.run() ejecutándose")
            
            # Si tenemos un Level base válido, usarlo
            if hasattr(self, 'level') and self.level:
                print("🎮 DEBUG: Usando Level base en multiplayer")
                self.level.run()
                
                # Verificar fin del juego - ACCEDER CORRECTAMENTE
                if hasattr(self.level, 'player') and self.level.player.health <= 0:
                    return 'lose'
                elif hasattr(self.level, 'structure') and self.level.structure.destroyed:
                    return 'lose'  
                elif (hasattr(self.level, 'all_enemies_defeated') and 
                    self.level.all_enemies_defeated() and 
                    not self.level.enemy_queue):
                    return 'win'
                    
                return 'playing'
            else:
                # Modo de prueba simple
                print("🎮 DEBUG: Usando modo prueba en multiplayer")
                return self.run_test_mode()
                
        except Exception as e:
            print(f"❌ ERROR MultiplayerLevel en run(): {e}")
            return 'error'

    def run_test_mode(self):
        """Pantalla de prueba cuando Level falla"""
        self.display_surface.fill((30, 30, 60))
        
        # Título
        font_large = pygame.font.Font(None, 74)
        title = font_large.render(f"MULTIPLAYER - Jugador {self.player_number}", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH//2, HEIGTH//2 - 100))
        self.display_surface.blit(title, title_rect)
        
        # Información
        font_medium = pygame.font.Font(None, 48)
        diff_text = font_medium.render(f"Dificultad: {self.difficulty_config.get('name', 'Unknown')}", True, (200, 200, 100))
        diff_rect = diff_text.get_rect(center=(WIDTH//2, HEIGTH//2))
        self.display_surface.blit(diff_text, diff_rect)
        
        # Estado de conexión
        conn_text = font_medium.render("CONECTADO - Esperando sincronización", True, (100, 255, 100))
        conn_rect = conn_text.get_rect(center=(WIDTH//2, HEIGTH//2 + 50))
        self.display_surface.blit(conn_text, conn_rect)
        
        # Instrucciones
        font_small = pygame.font.Font(None, 36)
        inst_text = font_small.render("Presiona ESC para volver al menú", True, (150, 150, 255))
        inst_rect = inst_text.get_rect(center=(WIDTH//2, HEIGTH//2 + 150))
        self.display_surface.blit(inst_text, inst_rect)
        
        # Verificar si presiona ESC para volver
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 'menu'
                
        return 'playing'