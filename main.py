import pygame, sys
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
    game.run()
