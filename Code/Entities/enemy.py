import pygame
import random
import math

from Code.Functions.A_star import a_star
from Code.Utilities.settings import *
from Code.Entities.entity import Entity
from Code.Functions.support import import_folder

class Enemy(Entity):
    def __init__(self, enemy_name, pos, groups, obstacle_sprites, create_bullet, player, structure, matrix_route, path_request):
        super().__init__(groups)

        self.sprite_type = 'enemy'

        self.player = player
        self.structure_pos = structure.get_grid_position()
        self.matrix_route = matrix_route

        self.target = "player"

        # graphics setup
        self.import_graphics(enemy_name)
        self.status = 'down_idle'
        self.image = self.animations[self.status][self.frame_index]

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        # stats
        self.name = enemy_name
        self.enemy_info = tanks_data[self.name]
        self.health = self.enemy_info['health']
        self.resistance = self.enemy_info['resistance']
        self.speed = self.enemy_info['speed']
        self.bullet_speed = self.enemy_info['bullet_speed']
        self.attack_damage = self.enemy_info['damage']
        self.attack_radius = self.enemy_info['attack_radius']
        self.notice_radius = self.enemy_info['notice_radius']
        self.attack_cooldown = self.enemy_info['attack_cooldown']

        # player interaction
        self.can_attack = True
        self.attack_time = None

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        # attack setup 
        self.create_bullet = create_bullet

        # Rute for the path
        self.path_request = path_request  
        self.path = []

        # state lock
        self.state_locked = False  # Bloquea el cambio de estado tras el ataque
        self.state_lock_time = None  # Marca el tiempo de bloqueo
        self.state_lock_duration = 500  # Duración del bloqueo en milisegundos

        # slow motion state control
        self.slow_motion_applied = False
        self.clock_image = pygame.image.load("Assets/Effects/Clock/Clock_effect.png").convert_alpha()

        # pathfinding cache
        self.last_target = None
        self.last_path_time = 0
        self.path_refresh_rate = 400

        # wandering setup
        self.is_wandering = False
        self.wander_direction = pygame.math.Vector2()
        self.wander_last_time = 0
        self.wander_interval = random.randint(600, 1400)         # ms between direction changes
        self.wander_speed = max(0.4, self.speed * 0.6)           # wandering speed

        self.wander_shoot_last_time = 0
        self.wander_shoot_interval = random.randint(900, 2000)   # ms between shoots while wandering

        # Sounds
        self.sounds = {
            'attack_sound': pygame.mixer.Sound('Assets/Audio/Fire.wav'),
            'hit_sound': pygame.mixer.Sound('Assets/Audio/hit.wav'),
            'death_sound': pygame.mixer.Sound('Assets/Audio/death.wav')
        }

        self.sounds['attack_sound'].set_volume(0.4)
        self.sounds['hit_sound'].set_volume(0.4)
        self.sounds['death_sound'].set_volume(0.4)


    def import_graphics(self, name):
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
            'attack': []
        }
        main_path = f'Assets/Entities/Enemies/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)
    
    def get_structure_distance_direction(self):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        structure_vec = pygame.math.Vector2(
            self.structure_pos[0] * TILESIZE + TILESIZE // 2,
            self.structure_pos[1] * TILESIZE + TILESIZE // 2
        )
        distance = (structure_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (structure_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def request_path(self, matrix_route, target_pos, enemy_pos):
        """Solicita una nueva ruta si cambió el target o pasó el tiempo mínimo."""
        current_time = pygame.time.get_ticks()
        if (self.last_target != target_pos or
            current_time - self.last_path_time >= self.path_refresh_rate):
            
            self.path = self.path_request.solicitar_ruta(matrix_route, target_pos, enemy_pos)
            self.last_target = target_pos
            self.last_path_time = current_time
        
    def get_status(self, player):
        if not self.state_locked:
            if self.target == "player":
                distance, direction = self.get_player_distance_direction(player)
            else:
                distance, direction = self.get_structure_distance_direction()

            # ataque
            if distance <= self.attack_radius and self.can_attack:
                if self.status != 'attack':
                    self.frame_index = 0
                self.status = 'attack'

            # movimiento
            elif distance <= self.notice_radius or self.target == "structure":
                if abs(direction.y) > abs(direction.x):
                    self.status = 'up' if direction.y < 0 else 'down'
                else:
                    self.status = 'left' if direction.x < 0 else 'right'

            # idle
            else:
                self.status = self.status.split('_')[0] + '_idle'
                self.path = []


    def actions(self, player):
        if self.status == 'attack':
            self.path = []
            _, direction = self.get_player_distance_direction(player)

            if abs(direction.y) > abs(direction.x):
                self.status = 'up' if direction.y < 0 else 'down'
            else:
                self.status = 'left' if direction.x < 0 else 'right'

            self.attack()

        elif self.status in ['up', 'down', 'left', 'right']:
            distance, direction = self.get_player_distance_direction(player)

            if distance <= self.notice_radius:
                self.direction = direction
            else:
                enemy_vec = pygame.math.Vector2(self.rect.center)
                structure_vec = pygame.math.Vector2(
                    self.structure_pos[0] * TILESIZE + TILESIZE // 2,
                    self.structure_pos[1] * TILESIZE + TILESIZE // 2
                )
                self.direction = (structure_vec - enemy_vec).normalize()
        else:
            self.direction = pygame.math.Vector2()


    def attack(self):
        self.sounds['attack_sound'].play()

        if self.target == "player" and self.create_bullet:
            self.create_bullet(self, self.bullet_speed)

        elif self.target == "structure":
            self.create_bullet(self, self.bullet_speed)

        self.attack_time = pygame.time.get_ticks()
        self.can_attack = False 
        self.state_locked = True
        self.state_lock_time = pygame.time.get_ticks()


    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0

        base_image = animation[int(self.frame_index)].copy()
        self.rect = base_image.get_rect(center=self.hitbox.center)

        if self.slow_motion_applied:
            closk_scaled = pygame.transform.scale(self.clock_image, base_image.get_size())
            base_image.blit(closk_scaled, (0, 0))

        if not self.vulnerable:
            alpha = self.wave_value()
            base_image.set_alpha(alpha) 
        else:
            base_image.set_alpha(255)

        self.image = base_image


    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True
        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True
        if self.state_locked:
            if current_time - self.state_lock_time >= self.state_lock_duration:
                self.state_locked = False 

    def return_damage(self):
        damage = self.attack_damage
        return damage
    
    def get_grid_position(self):
        grid_x = self.rect.centerx // TILESIZE
        grid_y = self.rect.centery // TILESIZE
        return [grid_x, grid_y]
    
    def get_damage(self, player, attack_type):
        if self.vulnerable:
            player_direction = self.get_player_distance_direction(player)[1]
            self.sounds['hit_sound'].play()
            if attack_type == 'bullet':
                self.health -= player.return_damage()
                self.direction = -player_direction * self.resistance
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def hit_reaction(self):
        if not self.vulnerable:
            self.move(-self.speed * 2)

    def enemy_move(self, speed):
        if self.path:
            target_x, target_y = self.path[0]

            target_x = target_x * TILESIZE + TILESIZE // 2
            target_y = target_y * TILESIZE + TILESIZE // 2

            direction_x = target_x - self.hitbox.centerx
            direction_y = target_y - self.hitbox.centery

            distance = (direction_x**2 + direction_y**2) ** 0.5

            if distance > 1:
                self.direction.x = direction_x / distance
                self.direction.y = direction_y / distance

                self.hitbox.x += self.direction.x * speed
                self.collision('horizontal')
                self.hitbox.y += self.direction.y * speed
                self.collision('vertical')
                self.rect.center = self.hitbox.center

                if abs(self.direction.y) > abs(self.direction.x):
                    if self.direction.y < 0:
                        self.status = 'up'
                    else:
                        self.status = 'down'
                else:
                    if self.direction.x < 0:
                        self.status = 'left'
                    else:
                        self.status = 'right'
            else:
                self.path.pop(0)
        else:
            self.direction = pygame.math.Vector2()
            self.status = self.status.split('_')[0] + '_idle'

    def wander_move(self):
        """Movimiento aleatorio cuando no hay ruta disponible. También gestiona disparos 'lentos'."""
        current_time = pygame.time.get_ticks()

        # elegir nueva dirección aleatoria si pasó el intervalo o no hay dirección
        if self.wander_direction.length_squared() == 0 or (current_time - self.wander_last_time) >= self.wander_interval:
            angle = random.uniform(0, 2 * math.pi)
            dx = math.cos(angle)
            dy = math.sin(angle)
            self.wander_direction = pygame.math.Vector2(dx, dy)
            # normalizar y evitar vectores casi nulos
            if self.wander_direction.length() == 0:
                self.wander_direction = pygame.math.Vector2(1, 0)
            else:
                self.wander_direction = self.wander_direction.normalize()

            # nuevo intervalo aleatorio para el próximo cambio (no tan rápido)
            self.wander_interval = random.randint(600, 1600)
            self.wander_last_time = current_time

        # mover usando la dirección de wander (con colisiones, similar a enemy_move)
        self.direction = self.wander_direction
        # horizontal
        self.hitbox.x += self.direction.x * self.wander_speed
        self.collision('horizontal')
        # vertical
        self.hitbox.y += self.direction.y * self.wander_speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

        # ajustar status para animación
        if abs(self.direction.y) > abs(self.direction.x):
            self.status = 'up' if self.direction.y < 0 else 'down'
        else:
            self.status = 'left' if self.direction.x < 0 else 'right'

        # disparo aleatorio controlado (no tan rápido)
        if (current_time - self.wander_shoot_last_time) >= self.wander_shoot_interval and self.can_attack:
            self.attack()
            self.wander_shoot_last_time = current_time
            self.wander_shoot_interval = random.randint(900, 2200)

    def check_death(self):
        if self.health <= 0 or self.player.bomb_active:
            self.sounds['death_sound'].play()
            self.kill()

    def apply_slow_motion(self):
        self.speed = 1
        self.attack_cooldown = self.enemy_info['attack_cooldown'] * 2
        self.slow_motion_applied = True

    def remove_slow_motion(self):
        self.speed = self.enemy_info['speed']
        self.attack_cooldown = self.enemy_info['attack_cooldown']
        self.slow_motion_applied = False

    def update(self):
        distance_to_player, _ = self.get_player_distance_direction(self.player)
        enemyPos = self.get_grid_position()

        if distance_to_player <= self.notice_radius:
            playerPos = self.player.get_grid_position()
            self.request_path(self.matrix_route, playerPos, enemyPos)
            self.target = "player"
        else:
            self.request_path(self.matrix_route, self.structure_pos, enemyPos)
            self.target = "structure"

        if self.path:
            self.is_wandering = False
            self.enemy_move(self.speed)
        else:
            self.is_wandering = True
            self.wander_move()

        # slow motion
        if self.player.slow_motion_active and not self.slow_motion_applied:
            self.apply_slow_motion()
        elif not self.player.slow_motion_active and self.slow_motion_applied:
            self.remove_slow_motion()

        self.hit_reaction()
        self.animate()
        self.cooldowns()



    def enemy_update(self, player):
        self.get_status(player)
        self.check_death()
        self.actions(player)