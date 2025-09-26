import pygame

from Code.Utilities.settings import *
from Code.Entities.entity import Entity
from Code.Functions.support import import_folder

class Enemy(Entity):
    def __init__(self, enemy_name, pos, groups, obstacle_sprites, damage_player, create_bullet, player, path_request):
        super().__init__(groups)

        self.sprite_type = 'enemy'

        self.player = player

        # graphics setup
        self.import_graphics(enemy_name)
        self.status = 'down_idle'
        self.image = self.animations[self.status][self.frame_index]

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        # stats
        self.enemy_name = enemy_name
        enemy_info = tanks_data[self.enemy_name]
        self.health = enemy_info['health']
        self.speed = enemy_info['speed']
        self.bullet_speed = enemy_info['bullet_speed']
        self.attack_damage = enemy_info['damage']
        self.resistance = enemy_info['resistance']
        self.attack_radius = enemy_info['attack_radius']
        self.notice_radius = enemy_info['notice_radius']

        # player interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 1300
        self.damage_player = damage_player

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
    
    def get_path(self, player_pos, enemy_pos):
        self.path = self.path_request.solicitar_ruta(player_pos, enemy_pos)

    def get_status(self, player):
        if not self.state_locked:
            distance, direction = self.get_player_distance_direction(player)

            # Attack
            if distance <= self.attack_radius and self.can_attack:
                if self.status != 'attack':
                    self.frame_index = 0
                self.status = 'attack'

            # Movement
            elif distance <= self.notice_radius:
                if abs(direction.y) > abs(direction.x):
                    if direction.y < 0:
                        self.status = 'up'
                    else:
                        self.status = 'down'
                else:
                    if direction.x < 0:
                        self.status = 'left'
                    else:
                        self.status = 'right'
            # Idle
            else:
                self.status = self.status.split('_')[0] + '_idle'
                self.path = []

    def actions(self, player):
        if self.status == 'attack':
            self.path = []
            _, direction = self.get_player_distance_direction(player)

            if abs(direction.y) > abs(direction.x):
                if direction.y < 0:
                    self.status = 'up'
                else:
                    self.status = 'down'
            else:
                if direction.x < 0:
                    self.status = 'left'
                else:
                    self.status = 'right'

            self.attack()
        elif self.status in ['up', 'down', 'left', 'right']:
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def attack(self):
        self.sounds['attack_sound'].play()
        if self.create_bullet:
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

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha) 
        else:
            self.image.set_alpha(255)

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

    def check_death(self):
        if self.health <= 0:
            self.sounds['death_sound'].play()
            self.kill()

    def update(self):
        distance_to_player, _ = self.get_player_distance_direction(self.player)
        if distance_to_player <= self.notice_radius:
            if not self.path:
                playerPos = self.player.get_grid_position()
                enemyPos = self.get_grid_position()
                self.get_path(playerPos, enemyPos)

            self.enemy_move(self.speed)
        
        self.hit_reaction()
        self.animate()
        self.cooldowns()


    def enemy_update(self, player):
        self.get_status(player)
        self.check_death()
        self.actions(player)