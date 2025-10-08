import pygame, sys
import time
import socket
from Code.Utilities.settings import *
from Code.UI.button import Button
from Code.Classes.level import Level
from Code.Network.client import NetworkClient

class Game: 
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('TecnoTanks')
        self.clock = pygame.time.Clock()

        self.state = 'menu'  # 'menu', 'choose', 'play', 'end', 'multiplayer_menu', 'create_join', 'lobby', 'settings', 'multiplayer_difficulty'
        self.win = False  
        
        self.font = pygame.font.Font(UI_FONT, 45)

        # Main menu buttons
        self.play_button = Button(pos=(200, 400), 
                            text_input="PLAY", font=self.get_font(55), base_color="black", hovering_color="White")
        self.quit_button = Button(pos=(200, 500), 
                            text_input="QUIT", font=self.get_font(55), base_color="black", hovering_color="White")
        self.settings_button = Button(pos=(200, 600), 
                            text_input="SETTINGS", font=self.get_font(55), base_color="black", hovering_color="White")
        
        # Mode selection buttons
        self.choose_mode_one_player_button = Button(pos=(640, 400), 
                            text_input="ONE PLAYER", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_mode_multiplayer_button = Button(pos=(640, 500), 
                            text_input="MULTIPLAYER", font=self.get_font(55), base_color="black", hovering_color="White")
        
        # Difficulty selection buttons (para single player)
        self.choose_easy_mode_button = Button(pos=(640, 200), 
                            text_input="EASY", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_medium_mode_button = Button(pos=(640, 300), 
                            text_input="MEDIUM", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_hard_mode_button = Button(pos=(640, 400), 
                            text_input="HARD", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_nightmare_mode_button = Button(pos=(640, 500), 
                            text_input="NIGHTMARE", font=self.get_font(55), base_color="black", hovering_color="White")
        
        # Multiplayer difficulty selection buttons
        self.multiplayer_easy_button = Button(pos=(640, 250), 
                            text_input="EASY", font=self.get_font(55), base_color="black", hovering_color="White")
        self.multiplayer_medium_button = Button(pos=(640, 350), 
                            text_input="MEDIUM", font=self.get_font(55), base_color="black", hovering_color="White")
        self.multiplayer_hard_button = Button(pos=(640, 450), 
                            text_input="HARD", font=self.get_font(55), base_color="black", hovering_color="White")
        self.multiplayer_back_button = Button(pos=(640, 550), 
                            text_input="BACK", font=self.get_font(55), base_color="black", hovering_color="White")
        
        # End menu buttons
        self.restart_button = Button(pos=(640, 400),
                            text_input="RESTART", font=self.get_font(55), base_color="black", hovering_color="White")
        self.quit_end_button = Button(pos=(640, 500),
                            text_input="QUIT", font=self.get_font(55), base_color="black", hovering_color="White")

        # Multiplayer menu buttons
        self.create_game_button = Button(pos=(640, 300),
                            text_input="CREATE GAME", font=self.get_font(55), base_color="black", hovering_color="White")
        self.join_game_button = Button(pos=(640, 400),
                            text_input="JOIN GAME", font=self.get_font(55), base_color="black", hovering_color="White")
        self.back_button = Button(pos=(640, 500),
                            text_input="BACK", font=self.get_font(55), base_color="black", hovering_color="White")

        # Lobby buttons
        self.start_game_button = Button(pos=(640, 500),
                            text_input="START GAME", font=self.get_font(55), base_color="black", hovering_color="White")
        self.lobby_back_button = Button(pos=(640, 600),
                            text_input="BACK", font=self.get_font(55), base_color="black", hovering_color="White")
        self.ready_button = Button(pos=(640, 500),
                            text_input="READY", font=self.get_font(55), base_color="black", hovering_color="White")

        # Settings menu buttons
        self.save_settings_button = Button(pos=(500, 500),
                            text_input="SAVE", font=self.get_font(55), base_color="black", hovering_color="White")
        self.settings_back_button = Button(pos=(780, 500),
                            text_input="BACK", font=self.get_font(55), base_color="black", hovering_color="White")

        self.bg_image = pygame.image.load("Assets/Map_tiles/MapaJuego.png")
        self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH + 50, HEIGTH + 50))

        self.level = None
        self.difficulty = None
        self.network_client = NetworkClient()
        self.game_code = ""
        self.input_active = False
        self.players_connected = 1
        self.is_host = False
        self.player_number = None

        # Configuración de red
        self.server_ip = "localhost"
        self.username = "Player" + str(int(time.time()) % 1000)
        self.multiplayer_level = None
        
        # Estados de input
        self.ip_input_active = False
        self.server_ip_input = "localhost"
        self.username_input_active = False
        self.username_input = self.username

        # Music
        main_sound = pygame.mixer.Sound('Assets/Audio/8-bit_-Sabaton-The-Last-Battle.ogg')
        main_sound.play(loops=-1)
        
    def get_font(self, size):
        return pygame.font.Font(UI_FONT, size)

    def draw_text_with_outline(self, surface, text, font, color, outline_color, pos, outline_width=3):
        text_surf = font.render(text, True, color)
        outline_surf = font.render(text, True, outline_color)
        text_rect = text_surf.get_rect(center=pos)

        for offset_x in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset_x**2 + offset_y**2 <= outline_width**2:
                    if offset_x != 0 or offset_y != 0:
                        surface.blit(outline_surf, text_rect.move(offset_x, offset_y))

        surface.blit(text_surf, text_rect)

    def draw_text_input(self, surface, prompt, text, font, color, pos, max_width=300):
        # Dibujar prompt
        prompt_surf = font.render(prompt, True, color)
        prompt_rect = prompt_surf.get_rect(midleft=(pos[0] - 150, pos[1]))
        surface.blit(prompt_surf, prompt_rect)
        
        # Dibujar caja de texto
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(midleft=(pos[0] + 50, pos[1]))
        
        # Dibujar fondo de la caja de texto
        input_rect = pygame.Rect(text_rect.left - 5, text_rect.top - 5, 
                               max_width, text_rect.height + 10)
        pygame.draw.rect(surface, (50, 50, 50), input_rect)
        pygame.draw.rect(surface, (200, 200, 200), input_rect, 2)
        
        surface.blit(text_surf, text_rect)

    def draw_input_field(self, surface, label, text, font, color, pos, max_width=300, is_active=False):
        """Dibuja un campo de entrada con label"""
        # Dibujar label
        label_surf = font.render(label, True, color)
        label_rect = label_surf.get_rect(midleft=(pos[0] - 200, pos[1]))
        surface.blit(label_surf, label_rect)
        
        # Dibujar caja de texto
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(midleft=(pos[0], pos[1]))
        
        # Dibujar fondo de la caja de texto
        input_rect = pygame.Rect(text_rect.left - 10, text_rect.top - 5, 
                               max_width, text_rect.height + 10)
        
        # Color diferente si está activo
        bg_color = (80, 80, 80) if is_active else (50, 50, 50)
        border_color = (255, 255, 0) if is_active else (200, 200, 200)
        
        pygame.draw.rect(surface, bg_color, input_rect)
        pygame.draw.rect(surface, border_color, input_rect, 2)
        
        surface.blit(text_surf, text_rect)

    def main_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "TECNO TANKS", self.get_font(100), "black", "white", (450, 200), outline_width=5)

        for button in [self.play_button, self.quit_button, self.settings_button]:
            button.changeColor(menu_mouse_pos)
            button.update(self.screen)

    def play_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "SELECT MODE", self.get_font(100), "black", "white", (640, 200), outline_width=5)

        for button in [self.choose_mode_one_player_button, self.choose_mode_multiplayer_button]:
            button.changeColor(menu_mouse_pos)
            button.update(self.screen)

    def multiplayer_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "MULTIPLAYER", self.get_font(100), "black", "white", (640, 200), outline_width=5)

        for button in [self.create_game_button, self.join_game_button, self.back_button]:
            button.changeColor(menu_mouse_pos)
            button.update(self.screen)

    def create_game_menu(self):
        # Añadir esta línea al inicio para mantener la conexión
        if self.network_client.connected and not hasattr(self, 'connection_maintained'):
            self.last_ping_time = pygame.time.get_ticks()
            self.connection_maintained = True

        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "CREATING GAME...", self.get_font(80), "black", "white", (640, 200), outline_width=5)
    
    # Mantener conexión activa
        current_time = pygame.time.get_ticks()
        if hasattr(self, 'last_ping_time') and current_time - self.last_ping_time > 5000:
            if self.network_client.connected:
                self.network_client.send_message({'command': 'ping'})
                self.last_ping_time = current_time

        if not self.network_client.connected:
        # Usar la IP configurada
            if self.network_client.connect(self.server_ip, 5555, self.username_input):
                self.network_client.create_game(self.username_input)
                self.setup_network_handlers()
            else:
                self.draw_text_with_outline(self.screen, "CONNECTION FAILED", self.get_font(60), "red", "white", (640, 300), outline_width=3)
                self.draw_text_with_outline(self.screen, f"Server: {self.server_ip}", self.get_font(30), "red", "white", (640, 350), outline_width=2)
    
        status = "Connected" if self.network_client.connected else "Disconnected"
        status_color = "black" if self.network_client.connected else "red"
        self.draw_text_with_outline(self.screen, f"Status: {status}", self.get_font(30), status_color, "white", (640, 400), outline_width=2)
        self.draw_text_with_outline(self.screen, f"Server: {self.server_ip}", self.get_font(25), "black", "white", (640, 450), outline_width=2)
        self.draw_text_with_outline(self.screen, f"User: {self.username_input}", self.get_font(25), "black", "white", (640, 500), outline_width=2)
    
    # Instrucción para continuar
        if self.network_client.connected and self.game_code:
            self.draw_text_with_outline(self.screen, "Going to lobby...", self.get_font(25), "green", "white", (640, 570), outline_width=2)

        self.back_button.changeColor(menu_mouse_pos)
        self.back_button.update(self.screen)

    def join_game_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "JOIN GAME", self.get_font(100), "black", "white", (640, 200), outline_width=5)
        
        self.draw_text_input(self.screen, "Game Code:", self.game_code, self.get_font(45), "white", (640, 300))
        
        for button in [self.join_game_button, self.back_button]:
            button.changeColor(menu_mouse_pos)
            button.update(self.screen)
        
        # Mostrar información de conexión
        self.draw_text_with_outline(self.screen, f"Server: {self.server_ip}", self.get_font(25), "black", "white", (640, 400), outline_width=2)
        self.draw_text_with_outline(self.screen, f"User: {self.username_input}", self.get_font(25), "black", "white", (640, 450), outline_width=2)

    def lobby_menu(self):
    # Mantener la conexión activa enviando ping periódicamente
        current_time = pygame.time.get_ticks()
        if hasattr(self, 'last_ping_time'):
            if current_time - self.last_ping_time > 5000:  # Cada 5 segundos
                if self.network_client.connected:
                    self.network_client.send_message({'command': 'ping'})
                    self.last_ping_time = current_time
        else:
            self.last_ping_time = current_time

        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "LOBBY", self.get_font(100), "black", "white", (640, 200), outline_width=5)
        self.draw_text_with_outline(self.screen, f"Game Code: {self.game_code}", self.get_font(40), "black", "white", (640, 280), outline_width=3)
        self.draw_text_with_outline(self.screen, f"Players: {self.players_connected}/2", self.get_font(40), "black", "white", (640, 330), outline_width=3)
        self.draw_text_with_outline(self.screen, f"Username: {self.username_input}", self.get_font(30), "black", "white", (640, 380), outline_width=2)

    # Mostrar estado de conexión
        status_color = "green" if self.network_client.connected else "red"
        status_text = "CONNECTED" if self.network_client.connected else "DISCONNECTED"
        self.draw_text_with_outline(self.screen, f"Status: {status_text}", self.get_font(25), status_color, "white", (640, 430), outline_width=2)

    # Mostrar estado del host/jugador
        if self.is_host:
            self.draw_text_with_outline(self.screen, "Role: HOST", self.get_font(30), "green", "white", (640, 470), outline_width=2)
        
        # Botón para iniciar juego (solo host)
            start_text = "START GAME" if self.players_connected == 2 else "WAITING FOR PLAYER..."
            self.start_game_button = Button(pos=(640, 550), 
                                        text_input=start_text, font=self.get_font(55), 
                                        base_color="black", 
                                        hovering_color="Green" if self.players_connected == 2 else "Gray")
            self.start_game_button.changeColor(menu_mouse_pos)
            self.start_game_button.update(self.screen)
        
        else:
            self.draw_text_with_outline(self.screen, "Role: PLAYER", self.get_font(30), "blue", "white", (640, 470), outline_width=2)
        
        # Botón para marcar como listo (solo jugadores, no host)
            if self.players_connected == 2:
                ready_text = "READY"
                self.ready_button = Button(pos=(640, 550), 
                                        text_input=ready_text, font=self.get_font(55), 
                                        base_color="black", hovering_color="Green")
                self.ready_button.changeColor(menu_mouse_pos)
                self.ready_button.update(self.screen)
            else:
                self.draw_text_with_outline(self.screen, "Waiting for host...", self.get_font(30), "black", "white", (640, 550), outline_width=2)
    
        self.lobby_back_button.changeColor(menu_mouse_pos)
        self.lobby_back_button.update(self.screen)

    def multiplayer_difficulty_menu(self):
        """Menú para que el host elija la dificultad en multiplayer"""
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "SELECT DIFFICULTY", self.get_font(80), "black", "white", (640, 150), outline_width=5)
        self.draw_text_with_outline(self.screen, f"Game: {self.game_code}", self.get_font(30), "black", "white", (640, 200), outline_width=2)

        for button in [self.multiplayer_easy_button, self.multiplayer_medium_button, 
                      self.multiplayer_hard_button, self.multiplayer_back_button]:
            button.changeColor(menu_mouse_pos)
            button.update(self.screen)

    def settings_menu(self):
        """Pantalla de configuración para multiplayer"""
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()
        
        self.draw_text_with_outline(self.screen, "SETTINGS", self.get_font(100), "black", "white", (640, 100), outline_width=5)
        
        # Input de IP del servidor
        self.draw_input_field(self.screen, "Server IP:", self.server_ip_input, self.get_font(45), "white", (640, 200), is_active=self.ip_input_active)
        
        # Input de nombre de usuario
        self.draw_input_field(self.screen, "Username:", self.username_input, self.get_font(45), "white", (640, 300), is_active=self.username_input_active)
        
        # Instrucciones
        self.draw_text_with_outline(self.screen, "Click on fields to edit, Enter to confirm", self.get_font(20), "black", "white", (640, 380), outline_width=2)
        
        # Botones SEPARADOS
        for button in [self.save_settings_button, self.settings_back_button]:
            button.changeColor(menu_mouse_pos)
            button.update(self.screen)

    def setup_network_handlers(self):
        def handle_game_created(message):
            self.game_code = message['game_id']
            self.player_number = message['player_number']
            self.is_host = True
            self.state = 'lobby'
            print(f"Game created: {self.game_code}")

        def handle_game_joined(message):
            self.game_code = message['game_id']
            self.player_number = message['player_number']
            self.state = 'lobby'
            print(f"Joined game: {self.game_code}")

        def handle_player_joined(message):
            self.players_connected = 2
            print("Another player joined!")

        def handle_player_disconnected(message):
            self.players_connected = 1
            print("Player disconnected")

        def handle_game_started(message):
            print(f"DEBUG: handle_game_started recibido - mensaje: {message}")
            difficulty = message.get('difficulty', {
                "name": "Multiplayer", 
                "enemyTankType1": 15, 
                "enemyTankType2": 15, 
                "enemyTankType3": 10, 
                "enemyTankType4": 5
            })
            self.difficulty = difficulty
            print(f"DEBUG: Dificultad establecida: {self.difficulty}")
            self.start_multiplayer_game()

        def handle_player_ready(message):
            ready_count = message.get('ready_count', 0)
            print(f"Players ready: {ready_count}/2")

        def handle_join_failed(message):
            reason = message.get('reason', 'Unknown error')
            print(f"Join failed: {reason}")

        self.network_client.register_handler('game_created', handle_game_created)
        self.network_client.register_handler('game_joined', handle_game_joined)
        self.network_client.register_handler('player_joined', handle_player_joined)
        self.network_client.register_handler('player_disconnected', handle_player_disconnected)
        self.network_client.register_handler('game_started', handle_game_started)
        self.network_client.register_handler('player_ready', handle_player_ready)
        self.network_client.register_handler('join_failed', handle_join_failed)

    def start_multiplayer_game(self):
        print("DEBUG: start_multiplayer_game llamado")
        try:
            from Code.Classes.multiplayer_level import MultiplayerLevel
            print(f"DEBUG: Importando MultiplayerLevel...")
            self.multiplayer_level = MultiplayerLevel(
                self.difficulty, 
                self.network_client, 
                self.player_number
            )
            self.state = 'play'
            print(f"DEBUG: Estado cambiado a 'play', multiplayer_level creado")
        except ImportError as e:
            print(f"DEBUG: Error importando MultiplayerLevel: {e}")
            print("DEBUG: Usando Level normal...")
            self.level = Level(self.difficulty)
            self.state = 'play'
        except Exception as e:
            print(f"DEBUG: Error en start_multiplayer_game: {e}")
            self.state = 'lobby'

    def select_difficulty_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()
        
        difficulties = { 
            "easy": {"name": "Easy", "enemyTankType1": 20, "enemyTankType2": 20, "enemyTankType3": 10, "enemyTankType4": 5}, 
            "medium": {"name": "Medium", "enemyTankType1": 10, "enemyTankType2": 10, "enemyTankType3": 15, "enemyTankType4": 10}, 
            "hard": {"name": "Hard", "enemyTankType1": 10, "enemyTankType2": 10, "enemyTankType3": 20, "enemyTankType4": 20}, 
            "nightmare": {"name": "Nightmare", "enemyTankType4": 40, "enemyTankType5": 10} 
        }

        for button in [
            self.choose_easy_mode_button,
            self.choose_medium_mode_button,
            self.choose_hard_mode_button,
            self.choose_nightmare_mode_button
        ]:
            button.changeColor(menu_mouse_pos)
            button.update(self.screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.choose_easy_mode_button.checkForInput(menu_mouse_pos):
                    self.difficulty = difficulties["easy"]
                    self.state = 'play'
                elif self.choose_medium_mode_button.checkForInput(menu_mouse_pos):
                    self.difficulty = difficulties["medium"]
                    self.state = 'play'
                elif self.choose_hard_mode_button.checkForInput(menu_mouse_pos):
                    self.difficulty = difficulties["hard"]
                    self.state = 'play'
                elif self.choose_nightmare_mode_button.checkForInput(menu_mouse_pos):
                    self.difficulty = difficulties["nightmare"]
                    self.state = 'play'

    def play(self):
        """Método play modificado para soportar multiplayer"""
        if self.multiplayer_level:
            # Juego multiplayer
            self.multiplayer_level.run()
            
            # Lógica de fin de juego para multiplayer
            if self.multiplayer_level.player.health <= 0:
                self.win = False
                self.state = 'end'
                self.multiplayer_level = None
            elif self.multiplayer_level.structure.destroyed:
                self.win = False
                self.state = 'end'
                self.multiplayer_level = None
            elif self.multiplayer_level.all_enemies_defeated() and not self.multiplayer_level.enemy_queue and not self.multiplayer_level.enemies:
                self.win = True
                self.state = 'end'
                self.multiplayer_level = None
        else:
            # Juego single player (código original)
            if not self.level:
                try:
                    self.level = Level(self.difficulty)  
                except Exception as e:
                    print(f"Error creating level: {e}")
                    self.state = 'choose'
                    return
                    
            self.level.run()
            
            if self.level.player.health <= 0:
                self.win = False
                self.state = 'end'
            elif self.level.structure.destroyed:
                self.win = False
                self.state = 'end'
            elif self.level.all_enemies_defeated() and not self.level.enemy_queue and not self.level.enemies:
                self.win = True
                self.state = 'end'

    def end_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        end_mouse_pos = pygame.mouse.get_pos()

        if self.win:
            self.draw_text_with_outline(self.screen, "YOU WON", self.get_font(100), "black", "white", (640, 200), outline_width=5)
        else:
            self.draw_text_with_outline(self.screen, "GAME OVER", self.get_font(100), "black", "white", (640, 200), outline_width=5)

        for button in [self.restart_button, self.quit_end_button]:
            button.changeColor(end_mouse_pos)
            button.update(self.screen)

    def handle_text_input(self, event):
        """Manejar entrada en pantalla de unirse a juego"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.game_code = self.game_code[:-1]
            elif event.key == pygame.K_RETURN:
                self.input_active = False
            else:
                if len(self.game_code) < 10:
                    self.game_code += event.unicode

    def handle_settings_input(self, event):
        """Manejar entrada en pantalla de configuración"""
        if event.type == pygame.KEYDOWN:
            if self.ip_input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.server_ip_input = self.server_ip_input[:-1]
                elif event.key == pygame.K_RETURN:
                    self.ip_input_active = False
                else:
                    self.server_ip_input += event.unicode
            
            elif self.username_input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.username_input = self.username_input[:-1]
                elif event.key == pygame.K_RETURN:
                    self.username_input_active = False
                else:
                    if len(self.username_input) < 15:
                        self.username_input += event.unicode

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.network_client.connected:
                    self.network_client.disconnect()
                pygame.quit()
                sys.exit()
            
            # Manejar entrada de texto
            if self.state == 'join_game' and self.input_active:
                self.handle_text_input(event)
            elif self.state == 'settings':
                self.handle_settings_input(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.state == 'menu':
                    if self.play_button.checkForInput(mouse_pos):
                        self.state = 'choose'
                    elif self.quit_button.checkForInput(mouse_pos):
                        if self.network_client.connected:
                            self.network_client.disconnect()
                        pygame.quit()
                        sys.exit()
                    elif self.settings_button.checkForInput(mouse_pos):
                        self.state = 'settings'

                elif self.state == 'choose':
                    if self.choose_mode_one_player_button.checkForInput(mouse_pos):
                        self.state = "select_difficulty"
                        self.level = None
                    elif self.choose_mode_multiplayer_button.checkForInput(mouse_pos):
                        self.state = 'multiplayer_menu'
                        
                elif self.state == 'multiplayer_menu':
                    if self.create_game_button.checkForInput(mouse_pos):
                        self.state = 'create_game'
                    elif self.join_game_button.checkForInput(mouse_pos):
                        self.state = 'join_game'
                        self.input_active = True
                    elif self.back_button.checkForInput(mouse_pos):
                        self.state = 'choose'
                
                elif self.state == 'create_game':
                    if self.back_button.checkForInput(mouse_pos):
                        self.state = 'multiplayer_menu'
                        if self.network_client.connected:
                            self.network_client.disconnect()
                
                elif self.state == 'join_game':
                    if self.join_game_button.checkForInput(mouse_pos) and self.game_code:
                        if self.network_client.connect(self.server_ip, 5555, self.username_input):
                            self.network_client.join_game(self.game_code, self.username_input)
                            self.setup_network_handlers()
                        self.input_active = False
                    elif self.back_button.checkForInput(mouse_pos):
                        self.state = 'multiplayer_menu'
                        self.input_active = False
                
                elif self.state == 'lobby':
                    if self.is_host and hasattr(self, 'start_game_button') and self.start_game_button.checkForInput(mouse_pos) and self.players_connected == 2:
                        # Host va a seleccionar dificultad
                        self.state = 'multiplayer_difficulty'
                    elif not self.is_host and self.players_connected == 2 and hasattr(self, 'ready_button') and self.ready_button.checkForInput(mouse_pos):
                        # Jugador marca como listo
                        self.network_client.send_player_ready()
                    elif self.lobby_back_button.checkForInput(mouse_pos):
                        self.state = 'multiplayer_menu'
                        if self.network_client.connected:
                            self.network_client.disconnect()
                
                elif self.state == 'multiplayer_difficulty':
                    # DEFINIR dificultades para multiplayer
                    multiplayer_difficulties = {
                        "easy": {"name": "Easy", "enemyTankType1": 15, "enemyTankType2": 15, "enemyTankType3": 8, "enemyTankType4": 4},
                        "medium": {"name": "Medium", "enemyTankType1": 12, "enemyTankType2": 12, "enemyTankType3": 10, "enemyTankType4": 6},
                        "hard": {"name": "Hard", "enemyTankType1": 10, "enemyTankType2": 10, "enemyTankType3": 12, "enemyTankType4": 8}
                    }
    
                    if self.multiplayer_easy_button.checkForInput(mouse_pos):
                        self.difficulty = multiplayer_difficulties["easy"]
                        print(f"DEBUG: Botón EASY presionado, enviando start_game...")
                        print(f"DEBUG - Estado antes de enviar: connected={self.network_client.connected}, game_id={self.game_code}")
                        self.network_client.send_start_game(self.difficulty)  # Enviar dificultad
                        print("Host selected Easy difficulty")
                    elif self.multiplayer_medium_button.checkForInput(mouse_pos):
                        self.difficulty = multiplayer_difficulties["medium"]
                        self.network_client.send_start_game(self.difficulty)  # Enviar dificultad
                        print("Host selected Medium difficulty")
                    elif self.multiplayer_hard_button.checkForInput(mouse_pos):
                        self.difficulty = multiplayer_difficulties["hard"]
                        self.network_client.send_start_game(self.difficulty)  # Enviar dificultad
                        print("Host selected Hard difficulty")
                    elif self.multiplayer_back_button.checkForInput(mouse_pos):
                        self.state = 'lobby'
                
                elif self.state == 'settings':
                    # Manejar clicks en inputs de configuración
                    ip_input_rect = pygame.Rect(440, 185, 400, 50)
                    username_input_rect = pygame.Rect(440, 285, 400, 50)
                    
                    if ip_input_rect.collidepoint(mouse_pos):
                        self.ip_input_active = True
                        self.username_input_active = False
                    elif username_input_rect.collidepoint(mouse_pos):
                        self.username_input_active = True
                        self.ip_input_active = False
                    elif self.save_settings_button.checkForInput(mouse_pos):
                        # Guardar configuración
                        self.server_ip = self.server_ip_input
                        self.username = self.username_input
                        self.state = 'menu'
                        print(f"Settings saved - Server: {self.server_ip}, Username: {self.username}")
                    elif self.settings_back_button.checkForInput(mouse_pos):
                        self.state = 'menu'
                        
                elif self.state == 'select_difficulty':
                    # El manejo de dificultad se hace en select_difficulty_menu
                    pass
                        
                elif self.state == 'end':
                    if self.restart_button.checkForInput(mouse_pos):
                        self.state = 'choose'
                        self.level = None
                        self.multiplayer_level = None
                    elif self.quit_end_button.checkForInput(mouse_pos):
                        if self.network_client.connected:
                            self.network_client.disconnect()
                        pygame.quit()
                        sys.exit()
    
    def run(self):
        while True:
            self.check_events()
            
            # Usar if-elif en lugar de match para compatibilidad
            if self.state == 'menu':
                self.main_menu()
            elif self.state == 'choose':
                self.play_menu()
            elif self.state == 'multiplayer_menu':
                self.multiplayer_menu()
            elif self.state == 'create_game':
                self.create_game_menu()
            elif self.state == 'join_game':
                self.join_game_menu()
            elif self.state == 'lobby':
                self.lobby_menu()
            elif self.state == 'multiplayer_difficulty':
                self.multiplayer_difficulty_menu()
            elif self.state == 'select_difficulty':
                self.select_difficulty_menu()
            elif self.state == 'settings':
                self.settings_menu()
            elif self.state == 'end':     
                self.end_menu()
            elif self.state == 'play':
                self.play()

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()