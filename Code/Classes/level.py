import random
import pygame

from Code.Classes import path_request
from Code.Classes.structure_tile import Structure_tile
from Code.Entities.enemy import Enemy
from Code.Entities.bullet import Bullet
from Code.UI import ui
from Code.Utilities.settings import *
from Code.Functions.support import get_random_position, import_csv_layout, import_folder
from Code.Classes.tile import Tile
from Code.Entities.player import Player
from Code.UI.ui import UI
from Code.Entities.powerUp import PowerUp
from random import choice

class Level:
    def __init__(self, difficulty_config):
        """
        Initializes the Level object, sets up all game entities, map, waves, power-ups, and UI.

        Args:
            difficulty_config (dict): Configuration for enemy types and counts per difficulty.
        """

        # Difficulty configuration
        self.difficulty_config = difficulty_config

        # get the display surface 
        self.display_surface = pygame.display.get_surface()

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.power_up_sprites = pygame.sprite.Group()

        # attack sprites
        self.bullet_sprites = pygame.sprite.Group()
        self.attackble_sprites = pygame.sprite.Group()
        
        # Wave setup
        self.current_wave = 0
        self.wave_size = 5  # number of enemies per wave
        self.current_round = 0 # current round number 
        self.total_rounds = 0 # total number of rounds
        self.enemy_queue = []  # list of enemies to spawn
        self.generate_enemy_queue()
        self.wave_started = False  
        self.waiting_next_wave = False

        # Power uo setup
        self.last_power_up_time = pygame.time.get_ticks()
        self.power_up_interval = 10 * 1000  # 1 minute in ms

        # Bonuses setup
        self.last_bonues_time = pygame.time.get_ticks()
        self.bonus_interval = 20 * 1000  # 2 minutes in ms

        # Fortress setup
        self.fortress_shield_applied = False

        # user interface
        self.ui = UI()
        
        self.tile_map = {} # Un diccionario para encontrar tiles por su posición
        self.destroyed_tiles_since_last_snapshot = [] # Registra los muros destruidos

        # Path request setup
        self.path_request = path_request.PathRequest()
        self.matrix_route = import_csv_layout('Assets/Map_matrix/MapaJuego_Obstaculos.csv'),

        # sprite setup
        self.create_map()

    def create_map(self):
        """
        Creates the game map by loading layouts and placing tiles, player, and structure.
        """

        layouts = {
            'boundary': import_csv_layout('Assets/Map_matrix/MapaJuego_Obstaculos.csv'),
            'grass': import_csv_layout('Assets/Map_matrix/MapaJuego_Pasto.csv'),
        }
        graphics = {
            'grass': import_folder('Assets/Objects/Attackable/grass'),
            'rock': pygame.image.load('Assets/Objects/Unbreakable/rock.png').convert_alpha(),
            'wall': pygame.image.load('Assets/Objects/Attackable/Wall/Wall.png').convert_alpha(),
            'fortress': pygame.image.load('Assets/Objects/Attackable/fortress/Fortress.png').convert_alpha()
        }

        self.player = Player((2020, 2700), [self.visible_sprites, self.attackble_sprites], self.obstacle_sprites, self.create_bullet)

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
                                    Tile((x, y), [self.visible_sprites, self.attackble_sprites, self.obstacle_sprites], 'rocks', graphics['rock'])
                                case "3":
                                    #Tile((x, y), [self.visible_sprites, self.attackble_sprites, self.obstacle_sprites], 'walls', graphics['wall'])
                                    tile = Tile((x, y), [self.visible_sprites, self.attackble_sprites, self.obstacle_sprites], 'walls', graphics['wall'])
                                    self.tile_map[(row_index, col_index)] = tile # Guardar la tile
                                case "5":
                                    self.structure = Structure_tile(
                                        (x, y),
                                        [self.visible_sprites, self.attackble_sprites, self.obstacle_sprites],
                                        'fortress',
                                        graphics['fortress'],
                                        hitbox_top=60,
                                        player=self.player,
                                    )
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile((x, y), [self.visible_sprites, self.attackble_sprites, self.obstacle_sprites], 'grass', random_grass_image)

    def generate_enemy_queue(self):
        """
        Generates the queue of enemies to spawn based on difficulty configuration.
        """

        self.enemy_queue.clear()

        for enemy_type, amount in self.difficulty_config.items():
            if enemy_type == "name":
                continue
            for _ in range(amount):
                self.enemy_queue.append(enemy_type)
    
        from random import shuffle
        shuffle(self.enemy_queue)
        self.total_rounds = len(self.enemy_queue) // self.wave_size + (1 if len(self.enemy_queue) % self.wave_size > 0 else 0)

    def spawn_wave(self):
        """
        Spawns a new wave of enemies from the queue at random positions.
        """

        spawn_count = min(self.wave_size, len(self.enemy_queue))
        layouts = import_csv_layout('Assets/Map_matrix/MapaJuego_Enemigos.csv')

        self.current_round += 1

        for _ in range(spawn_count):
            if not self.enemy_queue:
                break
            enemy_type = self.enemy_queue.pop(0)
            x, y = get_random_position(layouts, '4')
            self.enemy =  Enemy(
                enemy_type,
                (x * TILESIZE, y * TILESIZE),
                [self.visible_sprites, self.attackble_sprites],
                self.obstacle_sprites,
                self.create_bullet,
                self.player,
                self.structure,
                self.matrix_route,
                path_request=self.path_request
            )

    def create_bullet(self, origin, bullet_speed):
        """
        Creates a bullet entity from the given origin with specified speed.

        Args:
            origin: The entity firing the bullet.
            bullet_speed (float): Speed of the bullet.
        """
        Bullet(origin, self.obstacle_sprites, [self.visible_sprites, self.bullet_sprites], bullet_speed, self.visible_sprites)

    def player_attack_logic(self):
        """
        Handles collision detection and logic for player and enemy bullets.
        """

        if self.bullet_sprites:
            for bullet_sprite in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(
                    bullet_sprite, self.attackble_sprites, False
                )                
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type in ['grass', 'walls']:
                            if bullet_sprite.rect.colliderect(target_sprite.hitbox):
                                # Get the position in pixels
                                x, y = target_sprite.rect.topleft

                                # Convert to matrix indexes
                                row = y // TILESIZE
                                col = x // TILESIZE
                                
                                # --- AÑADIR ESTA LÍNEA ---
                                self.destroyed_tiles_since_last_snapshot.append((row, col))
                                # ---------------------------

                                # Update matrix with -1
                                self.matrix_route[0][row][col] = '-1'

                                # Kill the sprite
                                target_sprite.kill()
                                bullet_sprite.explode_and_kill()
                                break
                        elif target_sprite.sprite_type == 'structure' and bullet_sprite.origin_type == 'enemy':
                            target_sprite.get_damage(self.enemy, bullet_sprite.sprite_type)
                            bullet_sprite.explode_and_kill()

                        elif target_sprite.sprite_type == 'player' and bullet_sprite.origin_type != 'player':
                            target_sprite.get_damage(self.enemy, bullet_sprite.sprite_type)
                            bullet_sprite.explode_and_kill()

                        elif target_sprite.sprite_type == 'enemy' and bullet_sprite.origin_type == 'player':
                            target_sprite.get_damage(self.player, bullet_sprite.sprite_type)
                            bullet_sprite.explode_and_kill()

                        elif target_sprite.sprite_type == 'rocks' and bullet_sprite.origin_type == 'player' or bullet_sprite.origin_type == 'enemy':
                            bullet_sprite.explode_and_kill()
                        
                        elif target_sprite.sprite_type == 'barrier' and bullet_sprite.origin_type == 'player' or bullet_sprite.origin_type == 'enemy':
                            bullet_sprite.explode_and_kill()

    def spawn_power_up(self):
        """
        Spawns a random power-up at a valid position on the map.
        """

        layouts = import_csv_layout('Assets/Map_matrix/MapaJuego_Objetos.csv')
        x, y = get_random_position(layouts, '6')
        power_type = choice(list(power_up_data.keys()))
        PowerUp(power_type, (x * TILESIZE, y * TILESIZE), 
                [self.visible_sprites, self.power_up_sprites], 
                power_up_data[power_type])
        
    def spawn_bonus(self):
        """
        Spawns a random bonus item at a valid position on the map.
        """
        layouts = import_csv_layout('Assets/Map_matrix/MapaJuego_Objetos.csv')
        x, y = get_random_position(layouts, '6')
        bonus_type = choice(list(bonus_data.keys()))
        PowerUp(bonus_type, (x * TILESIZE, y * TILESIZE), 
                [self.visible_sprites, self.power_up_sprites], 
                bonus_data[bonus_type])
  
    def all_enemies_defeated(self):
        """
        Checks if all enemies have been defeated.

        Returns:
            bool: True if no enemies remain, False otherwise.
        """

        return not any(
            sprite for sprite in self.visible_sprites if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy'
        )
        
    def manage_power_ups_and_bonus(self):
        """
        Manages spawning and collision logic for power-ups and bonuses.
        """

        current_time = pygame.time.get_ticks()
        
        # --- PowerUps logic ---
        if current_time - self.last_power_up_time >= self.power_up_interval:
            self.spawn_power_up()
            self.last_power_up_time = current_time

        # --- Bonus logic ---
        if current_time - self.last_bonues_time >= self.bonus_interval:
            randomNum = random.random()
            if randomNum < 0.5:
                self.spawn_bonus()
            self.last_bonues_time = current_time

        # Detectar colisión jugador con powerups
        for power in self.power_up_sprites:
            if self.player.rect.colliderect(power.hitbox):
                power.apply_effect(self.player)
        
    def check_enemies_death(self):
        """
        Checks for defeated enemies and manages wave progression and timers.
        """

        enemy_sprites = [sprite for sprite in self.visible_sprites if getattr(sprite, 'sprite_type', None) == 'enemy']

        if not enemy_sprites and self.enemy_queue:
            if not self.wave_started:
                self.player.kaboom = False
                self.spawn_wave()
                self.wave_started = True  
            else:
                if not self.waiting_next_wave:
                    self.ui.start_time = pygame.time.get_ticks()
                    self.waiting_next_wave = True

                finished = self.ui.show_next_wave_timer()
                if finished:
                    self.spawn_wave()
                    self.waiting_next_wave = False

    def apply_fortress_shield(self):
        """
        Applies a shield (barrier) around the fortress structure.
        """

        self.fortress_shield_applied = True
        layout = import_csv_layout('Assets/Map_matrix/MapaJuego_Barrera.csv')
        barrier_image = pygame.image.load('Assets/Objects/Unbreakable/barrier.png').convert_alpha()

        for row_index, row in enumerate(layout):
            for col_index, col in enumerate(row):
                if col != '-1':
                    x = col_index * TILESIZE
                    y = row_index * TILESIZE

                    Tile(
                        (x, y),
                        [self.visible_sprites, self.attackble_sprites, self.obstacle_sprites],
                        'barrier',
                        barrier_image
                        ,hitbox_bottom=0,hitbox_left=0,hitbox_right=0,hitbox_top=0
                    )

    def remove_fortress_shield(self):
        """
        Removes the fortress shield (barrier) from the map.
        """

        self.fortress_shield_applied = False
        for sprite in self.obstacle_sprites.sprites():
            if getattr(sprite, 'sprite_type', None) == 'barrier':
                sprite.kill()


    def run(self):
        """
        Main update and draw loop for the level.
        Handles entity updates, drawing, UI, and wave logic.
        """

        # 1 - Logic and sprites
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player)
        self.visible_sprites.structure_update()
        self.player_attack_logic()
        self.bullet_sprites.update()
        self.manage_power_ups_and_bonus()

        if self.player.fortress_shield_active and not self.fortress_shield_applied:
            self.apply_fortress_shield()
        elif not self.player.fortress_shield_active and self.fortress_shield_applied:
            self.remove_fortress_shield()

        # 2 - Draw everything
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player, self.difficulty_config["name"], self.total_rounds, self.current_round)

        self.check_enemies_death()


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        """
        Initializes the camera group for rendering sprites with Y-sorting and zoom.
        """

        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surf = pygame.image.load('Assets/Map_tiles/MapaJuego.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

        # Zoom camera
        self.zoom_factor = 0.7  # Zoom out 

    def custom_draw(self, player):
        """
        Draws all visible sprites with camera offset and zoom, including health bars.

        Args:
            player (Player): Reference to the player for camera centering.
        """

        screen_w, screen_h = self.display_surface.get_size()

        self.offset.x = player.rect.centerx - (self.half_width / self.zoom_factor)
        self.offset.y = player.rect.centery - (self.half_height / self.zoom_factor)

        # Rectangle of the camera coordinates
        camera_world_rect = pygame.Rect(
            int(self.offset.x),
            int(self.offset.y),
            int(screen_w / self.zoom_factor),
            int(screen_h / self.zoom_factor)
        )

        # Draw floor
        scaled_floor = pygame.transform.scale(
            self.floor_surf,
            (int(self.floor_surf.get_width() * self.zoom_factor),
             int(self.floor_surf.get_height() * self.zoom_factor))
        )
        floor_screen_pos = ((self.floor_rect.left - self.offset.x) * self.zoom_factor,
                            (self.floor_rect.top  - self.offset.y) * self.zoom_factor)

        # Only blit if it intersects with the screen
        floor_screen_rect = scaled_floor.get_rect(topleft=(int(floor_screen_pos[0]), int(floor_screen_pos[1])))
        if self.display_surface.get_rect().colliderect(floor_screen_rect):
            self.display_surface.blit(scaled_floor, floor_screen_rect.topleft)

        # Draw only sprites inside the camera (world culling)
        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            # If the sprite's rect (in world) doesn't intersect the camera, skip it
            if not camera_world_rect.colliderect(sprite.rect):
                continue

            # Position and size on screen (with zoom)
            screen_x = int((sprite.rect.left  - self.offset.x) * self.zoom_factor)
            screen_y = int((sprite.rect.top   - self.offset.y) * self.zoom_factor)
            screen_w_s = int(sprite.rect.width  * self.zoom_factor)
            screen_h_s = int(sprite.rect.height * self.zoom_factor)

            # Scale the image (warning: expensive if done every frame)
            scaled_sprite = pygame.transform.scale(sprite.image, (screen_w_s, screen_h_s))

            self.display_surface.blit(scaled_sprite, (screen_x, screen_y))

            if sprite.sprite_type == 'enemy' or sprite.sprite_type == 'structure':
                # Health ratio
                match sprite.sprite_type:
                    case 'enemy':
                        health_ratio = max(sprite.health, 0) / tanks_data[sprite.name]['health']
                    case 'structure':
                        health_ratio = max(sprite.health, 0) / estructure_data[sprite.name]['health']

                # Bar size and position
                bar_width = int(sprite.rect.width * self.zoom_factor)
                bar_height = max(int(10 * self.zoom_factor), 2)
                bar_x = screen_x
                bar_y = screen_y - int(20 * self.zoom_factor)

                background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
                health_rect = pygame.Rect(bar_x, bar_y, int(bar_width * health_ratio), bar_height)

                pygame.draw.rect(self.display_surface, (255, 0, 0), background_rect)
                pygame.draw.rect(self.display_surface, (0, 255, 0), health_rect)
                pygame.draw.rect(self.display_surface, (0, 0, 0), background_rect, 2)

    def enemy_update(self, player):
        """
        Updates all enemy sprites in the group.

        Args:
            player (Player): Reference to the player object.
        """

        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)

    def structure_update(self):
        """
        Updates all structure sprites in the group.
        """

        estructure_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'structure']
        for estructure in estructure_sprites:
            estructure.structure_update()