import pygame

from Code.Classes import path_request
from Code.Entities.enemy import Enemy
from Code.Entities.bullet import Bullet
from Code.Utilities.settings import *
from Code.Functions.support import get_random_position, import_csv_layout, import_folder
from Code.Classes.tile import Tile
from Code.Entities.player import Player
from Code.UI.ui import UI
from random import choice

class Level:
    def __init__(self):
        # get the display surface 
        self.display_surface = pygame.display.get_surface()

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.bullet_sprites = pygame.sprite.Group()
        self.attackble_sprites = pygame.sprite.Group()
        
        # user interface
        self.ui = UI()

        self.path_request = path_request.PathRequest()

        # sprite setup
        self.create_map()

    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('Assets/Map_matrix/EscenarioJuego._Obstaculos.csv'),
            'grass': import_csv_layout('Assets/Map_matrix/EscenarioJuego._Pasto.csv'),
            'enemies': import_csv_layout('Assets/Map_matrix/EscenarioJuego._Enemigos.csv')
        }
        graphics = {
            'grass': import_folder('Assets/Objects/Attackable/grass'),
            'rock': pygame.image.load('Assets/Objects/Unbreakable/rock.png').convert_alpha(),
            'wall': pygame.image.load('Assets/Objects/Attackable/Wall/Wall64.png').convert_alpha()
        }

        enemieCoords = layouts['enemies']

        self.player = Player((2020, 1900), [self.visible_sprites, self.attackble_sprites], self.obstacle_sprites, self.create_bullet)

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':                        
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        
                        if style == 'boundary':
                            match col:
                                case "395":
                                    Tile((x, y), [self.obstacle_sprites], 'invisible')
                                case "1":
                                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'rocks', graphics['rock'])
                                case "3":
                                    Tile((x, y), [self.visible_sprites, self.attackble_sprites, self.obstacle_sprites], 'walls', graphics['wall'])
                                    
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile((x, y), [self.visible_sprites, self.attackble_sprites, self.obstacle_sprites], 'grass', random_grass_image)
       
        for i in range(20):
            coordenates = get_random_position(enemieCoords)
            self.enemy = Enemy(
                'enemyTankType1', 
                (coordenates[0] * TILESIZE, coordenates[1] * TILESIZE),
                [self.visible_sprites, self.attackble_sprites],
                self.obstacle_sprites,
                self.damage_player,
                self.create_bullet,
                self.player,
                self.path_request
            )

    def create_bullet(self, origin, bullet_speed):
        Bullet(origin, self.obstacle_sprites, [self.visible_sprites, self.bullet_sprites], bullet_speed)

    def player_attack_logic(self):
        if self.bullet_sprites:
            for bullet_sprite in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet_sprite, self.attackble_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass' or target_sprite.sprite_type == 'walls':
                            target_sprite.kill()

                        elif target_sprite.sprite_type == 'player' and bullet_sprite.origin_type != 'player':
                            target_sprite.get_damage(self.enemy, bullet_sprite.sprite_type)

                        elif target_sprite.sprite_type == 'enemy' and bullet_sprite.origin_type == 'player':
                            target_sprite.get_damage(self.player, bullet_sprite.sprite_type)

                        bullet_sprite.kill()

    
    def damage_player(self,amount):
        if self.player.vulnerable:
            self.player.health -+ amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            
    def all_enemies_defeated(self):
        return not any(sprite for sprite in self.visible_sprites if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy')

    def run(self):
        # update and draw the game
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player)
        self.player_attack_logic()
        self.bullet_sprites.update()
        self.ui.display(self.player)

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surf = pygame.image.load('Assets/Map_tiles/EscenarioJuego.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

        # Zoom camera
        self.zoom_factor = 0.6  # Zoom out 

    def custom_draw(self, player):

        # getting the offset
        self.offset.x = (player.rect.centerx - self.half_width) * self.zoom_factor
        self.offset.y = (player.rect.centery - self.half_height) * self.zoom_factor

        # drawing the floor
        floor_offset_pos = (self.floor_rect.topleft - self.offset) * self.zoom_factor
        scaled_floor = pygame.transform.scale(self.floor_surf, 
                                              (int(self.floor_surf.get_width() * self.zoom_factor), 
                                               int(self.floor_surf.get_height() * self.zoom_factor)))
        self.display_surface.blit(scaled_floor, floor_offset_pos)

        # draw sprites
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = (sprite.rect.topleft - self.offset) * self.zoom_factor
            scaled_sprite = pygame.transform.scale(sprite.image, 
                                                   (int(sprite.image.get_width() * self.zoom_factor), 
                                                    int(sprite.image.get_height() * self.zoom_factor)))
            self.display_surface.blit(scaled_sprite, offset_pos)
    
    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
