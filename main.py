"""import pygame, sys
from Code.Utilities.settings import *
from Code.UI.button import Button
from Code.Classes.level import Level

class Game:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('TecnoTanks')
        self.clock = pygame.time.Clock()

        self.state = 'menu'  # 'menu', 'choose', 'play', 'end'
        self.win = False  
        
        self.font = pygame.font.Font(UI_FONT, 45)

        # Main menu buttons
        self.play_button = Button(pos=(200, 400), 
                            text_input="PLAY", font=self.get_font(55), base_color="black", hovering_color="White")
        self.quit_button = Button(pos=(200, 500), 
                            text_input="QUIT", font=self.get_font(55), base_color="black", hovering_color="White")
        
        # Mode selection buttons
        self.choose_mode_one_player_button = Button(pos=(640, 400), 
                            text_input="ONE PLAYER", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_mode_multiplayer_button = Button(pos=(640, 500), 
                            text_input="MULTIPLAYER", font=self.get_font(55), base_color="black", hovering_color="White")
        
        # Dificulty selection buttons
        self.choose_easy_mode_button = Button(pos=(640, 200), 
                            text_input="EASY", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_medium_mode_button = Button(pos=(640, 300), 
                            text_input="MEDIUM", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_hard_mode_button = Button(pos=(640, 400), 
                            text_input="HARD", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_nightmare_mode_button = Button(pos=(640, 500), 
                            text_input="NIGHTMARE", font=self.get_font(55), base_color="black", hovering_color="White")
        
        # End menu buttons
        self.restart_button = Button(pos=(640, 400),
                            text_input="RESTART", font=self.get_font(55), base_color="black", hovering_color="White")
        self.quit_end_button = Button(pos=(640, 500),
                            text_input="QUIT", font=self.get_font(55), base_color="black", hovering_color="White")

        self.bg_image = pygame.image.load("Assets/Map_tiles/MapaJuego.png")
        self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH + 50, HEIGTH + 50))

        self.level = None
        self.difficulty = None

        #Music
        main_sound = pygame.mixer.Sound('Assets/Audio/8-bit_-Sabaton-The-Last-Battle.ogg')
        main_sound.play(loops= -1)
        
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

    def main_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "TECNO TANKS", self.get_font(100), "black", "white", (450, 200), outline_width=5)

        for button in [self.play_button, self.quit_button]:
            button.changeColor(menu_mouse_pos)
            button.update(self.screen)

    def play_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "SELECT MODE", self.get_font(100), "black", "white", (640, 200), outline_width=5)

        for button in [self.choose_mode_one_player_button, self.choose_mode_multiplayer_button]:
            button.changeColor(menu_mouse_pos)
            button.update(self.screen)

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
        if not self.level:
            self.level = Level(self.difficulty)  
        self.level.run()
        
        if self.level.player.health <= 0:
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

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.state == 'menu':
                    if self.play_button.checkForInput(mouse_pos):
                        self.state = 'choose'
                    elif self.quit_button.checkForInput(mouse_pos):
                        pygame.quit()
                        sys.exit()

                elif self.state == 'choose':
                    if self.choose_mode_one_player_button.checkForInput(mouse_pos):
                        self.state = "select_difficulty"
                        self.level = None
                    elif self.choose_mode_multiplayer_button.checkForInput(mouse_pos):
                        print("Multiplayer")
                        
                elif self.state == 'end':
                    if self.restart_button.checkForInput(mouse_pos):
                        self.state = 'choose'
                        self.level = None
                    elif self.quit_end_button.checkForInput(mouse_pos):
                        pygame.quit()
                        sys.exit()
    
    def run(self):
        while True:
            self.check_events()
            match self.state:
                case 'menu':
                    self.main_menu()
                case 'choose':
                    self.play_menu()
                case 'select_difficulty':
                    self.select_difficulty_menu()
                case 'play':
                    self.play()
                case 'end':
                    self.end_menu()

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()"""
    
##############################################################################################################

import pygame, sys
from Code.Utilities.settings import *
from Code.UI.button import Button
from Code.Classes.level import Level
from Code.Network.client import NetworkClient

class Game:
    def __init__(self):
        pygame.init()
        
        # CORRECCIÓN: Usar HEIGTH si es que así está definido en settings.py
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))  # Cambié HEIGHT por HEIGTH
        pygame.display.set_caption('TecnoTanks')
        self.clock = pygame.time.Clock()

        self.state = 'menu'  # 'menu', 'choose', 'play', 'end', 'multiplayer_menu', 'create_join', 'lobby'
        self.win = False  
        
        self.font = pygame.font.Font(UI_FONT, 45)

        # Main menu buttons
        self.play_button = Button(pos=(200, 400), 
                            text_input="PLAY", font=self.get_font(55), base_color="black", hovering_color="White")
        self.quit_button = Button(pos=(200, 500), 
                            text_input="QUIT", font=self.get_font(55), base_color="black", hovering_color="White")
        
        # Mode selection buttons
        self.choose_mode_one_player_button = Button(pos=(640, 400), 
                            text_input="ONE PLAYER", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_mode_multiplayer_button = Button(pos=(640, 500), 
                            text_input="MULTIPLAYER", font=self.get_font(55), base_color="black", hovering_color="White")
        
        # Difficulty selection buttons
        self.choose_easy_mode_button = Button(pos=(640, 200), 
                            text_input="EASY", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_medium_mode_button = Button(pos=(640, 300), 
                            text_input="MEDIUM", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_hard_mode_button = Button(pos=(640, 400), 
                            text_input="HARD", font=self.get_font(55), base_color="black", hovering_color="White")
        self.choose_nightmare_mode_button = Button(pos=(640, 500), 
                            text_input="NIGHTMARE", font=self.get_font(55), base_color="black", hovering_color="White")
        
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
        self.start_game_button = Button(pos=(640, 400),
                            text_input="START GAME", font=self.get_font(55), base_color="black", hovering_color="White")
        self.lobby_back_button = Button(pos=(640, 500),
                            text_input="BACK", font=self.get_font(55), base_color="black", hovering_color="White")

        # CORRECCIÓN: Usar HEIGTH aquí también
        self.bg_image = pygame.image.load("Assets/Map_tiles/MapaJuego.png")
        self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH + 50, HEIGTH + 50))

        self.level = None
        self.difficulty = None
        self.network_client = NetworkClient()
        self.game_code = ""
        self.input_active = False
        self.players_connected = 1
        self.is_host = False

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

    def main_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "TECNO TANKS", self.get_font(100), "black", "white", (450, 200), outline_width=5)

        for button in [self.play_button, self.quit_button]:
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

    """def create_game_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "CREATING GAME...", self.get_font(80), "black", "white", (640, 200), outline_width=5)
        
        # Conectar al servidor y crear juego
        if not self.network_client.connected:
            if self.network_client.connect():
                self.network_client.create_game()
                # Configurar manejadores de mensajes
                self.setup_network_handlers()
            else:
                self.draw_text_with_outline(self.screen, "CONNECTION FAILED", self.get_font(60), "red", "white", (640, 300), outline_width=3)
        
        self.back_button.changeColor(menu_mouse_pos)
        self.back_button.update(self.screen)"""
        
    def create_game_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "CREATING GAME...", self.get_font(80), "black", "white", (640, 200), outline_width=5)
    
    # Solo intentar conectar una vez
        if not self.network_client.connected:
            if self.network_client.connect():
                self.network_client.create_game()
                self.setup_network_handlers()
            else:
                self.draw_text_with_outline(self.screen, "CONNECTION FAILED", self.get_font(60), "red", "white", (640, 300), outline_width=3)
                # Mostrar mensaje de ayuda
                self.draw_text_with_outline(self.screen, "Check if server is running", self.get_font(30), "red", "white", (640, 350), outline_width=2)
    
        # Mostrar estado de conexión
        status = "Connected" if self.network_client.connected else "Disconnected"
        self.draw_text_with_outline(self.screen, f"Status: {status}", self.get_font(30), "black", "white", (640, 400), outline_width=2)
    
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

    def lobby_menu(self):
        self.screen.blit(self.bg_image, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        self.draw_text_with_outline(self.screen, "LOBBY", self.get_font(100), "black", "white", (640, 200), outline_width=5)
        self.draw_text_with_outline(self.screen, f"Game Code: {self.game_code}", self.get_font(40), "black", "white", (640, 280), outline_width=3)
        self.draw_text_with_outline(self.screen, f"Players: {self.players_connected}/2", self.get_font(40), "black", "white", (640, 330), outline_width=3)

        if self.is_host:
            self.start_game_button.changeColor(menu_mouse_pos)
            self.start_game_button.update(self.screen)
        
        self.lobby_back_button.changeColor(menu_mouse_pos)
        self.lobby_back_button.update(self.screen)

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

        self.network_client.register_handler('game_created', handle_game_created)
        self.network_client.register_handler('game_joined', handle_game_joined)
        self.network_client.register_handler('player_joined', handle_player_joined)
        self.network_client.register_handler('player_disconnected', handle_player_disconnected)

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
        if not self.level:
            try:
                self.level = Level(self.difficulty)  
            except Exception as e:
                print(f"Error creating level: {e}")
                # Fallback para evitar el crash
                self.state = 'choose'
                return
                
        self.level.run()
        
        if self.level.player.health <= 0:
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.game_code = self.game_code[:-1]
            elif event.key == pygame.K_RETURN:
                self.input_active = False
            else:
                if len(self.game_code) < 10:  # Limitar longitud
                    self.game_code += event.unicode

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.network_client.connected:
                    self.network_client.disconnect()
                pygame.quit()
                sys.exit()
            
            if self.state == 'join_game' and self.input_active:
                self.handle_text_input(event)
            
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
                        if self.network_client.connect():
                            self.network_client.join_game(self.game_code)
                            self.setup_network_handlers()
                        self.input_active = False
                    elif self.back_button.checkForInput(mouse_pos):
                        self.state = 'multiplayer_menu'
                        self.input_active = False
                
                elif self.state == 'lobby':
                    if self.is_host and self.start_game_button.checkForInput(mouse_pos) and self.players_connected == 2:
                        # Iniciar juego multiplayer
                        self.difficulty = {"name": "Multiplayer", "enemyTankType1": 15, "enemyTankType2": 15, "enemyTankType3": 10, "enemyTankType4": 5}
                        self.state = 'play'
                    elif self.lobby_back_button.checkForInput(mouse_pos):
                        self.state = 'multiplayer_menu'
                        if self.network_client.connected:
                            self.network_client.disconnect()
                
                elif self.state == 'select_difficulty':
                    # El manejo de dificultad se hace en select_difficulty_menu
                    pass
                        
                elif self.state == 'end':
                    if self.restart_button.checkForInput(mouse_pos):
                        self.state = 'choose'
                        self.level = None
                    elif self.quit_end_button.checkForInput(mouse_pos):
                        if self.network_client.connected:
                            self.network_client.disconnect()
                        pygame.quit()
                        sys.exit()
    
    def run(self):
        while True:
            self.check_events()
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
            elif self.state == 'select_difficulty':
                self.select_difficulty_menu()
            elif self.state == 'play':
                self.play()
            elif self.state == 'end':
                self.end_menu()

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()