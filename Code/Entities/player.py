import pygame
from Code.Entities.entity import Entity
from Code.Utilities.settings import *
from Code.Functions.support import import_folder

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_bullet):
        super().__init__(groups)

        self.sprite_type = 'player'

        self.original_image = pygame.image.load('Assets/Entities/Player/up/PlayerTankUp.png').convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        # Graphics setup
        self.import_player_assets()
        self.status = 'up'

        # Movement
        self.speed = 6
        self.bullet_speed = 6
        self.attacking = False
        self.attack_cooldown = 800
        self.attack_time = None
        self.create_bullet = create_bullet
        self.direction = pygame.math.Vector2()

        self.obstacle_sprites = obstacle_sprites

        self.stats = {'health': 3, 'damage': 1}
        self.health = self.stats['health']
        self.damage = self.stats['damage']

        # Damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # Animation setup
        self.frame_index = 0
        self.animation_speed = 0.1

        # Power-ups setup
        self.shield_active = False
        self.shield_end_time = 0
        self.shield_image = pygame.image.load("Assets/Effects/Shield/Shield.png").convert_alpha()

        # duration time of power-ups
        self.shield_duration = 0
        self.slow_motion_duration = 0
        self.weapon_upgrade_duration = 0 
        self.machine_gun_duration = 0
        self.fortress_shield_duration = 0

        self.shoot_upgrade_active = False
        self.shoot_upgrade_end = 0

        self.slow_motion_active = False
        self.slow_motion_end = 0

        self.machine_gun_active = False
        self.machine_gun_end = 0

        self.bomb_active = False
        self.bomb_end = 0

        self.fortress_shield_active = False
        self.fortress_shield_end = 0

        # Sounds
        self.sounds = {
            'attack_sound': pygame.mixer.Sound('Assets/Audio/Fire.wav'),
            'hit_sound': pygame.mixer.Sound('Assets/Audio/hit.wav')
        }
        self.sounds['attack_sound'].set_volume(0.4)
        self.sounds['hit_sound'].set_volume(0.4)

    def import_player_assets(self):
        character_path = 'Assets/Entities/Player/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': []}
        
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        keys = pygame.key.get_pressed()

        # Movement input
        if keys[pygame.K_w]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'
        else:
            self.direction.x = 0

        # Attack input
        if keys[pygame.K_SPACE] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            self.create_bullet(self, self.bullet_speed)
            self.sounds['attack_sound'].play()

    def get_status(self):
        # Idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status and 'attack' not in self.status:
                self.status = self.status + '_idle'

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def animate(self):
        animation = self.animations[self.status]

        # Loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Reiniciar imagen base en cada frame
        base_image = animation[int(self.frame_index)].copy()
        self.rect = base_image.get_rect(center=self.hitbox.center)

        # Damage shoot boost → rojo
        if self.shoot_upgrade_active:
            base_image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
        
        # Machine gun → naranja
        if self.machine_gun_active:
            base_image.fill((255, 155, 0), special_flags=pygame.BLEND_RGB_ADD)

        # Escudo → overlay
        if self.shield_active:
            shield_scaled = pygame.transform.scale(self.shield_image, base_image.get_size())
            base_image.blit(shield_scaled, (0, 0))

        # Parpadeo al recibir daño
        if not self.vulnerable:
            alpha = self.wave_value()
            base_image.set_alpha(alpha)
        else:
            base_image.set_alpha(255)

        self.image = base_image


    def return_damage(self):
        return self.damage
    
    def get_damage(self, enemy, attack_type):
        if self.vulnerable:
            if not self.shield_active:
                self.sounds['hit_sound'].play()
                if attack_type == 'bullet':
                    self.health -= enemy.return_damage()
                self.hurt_time = pygame.time.get_ticks()
                self.vulnerable = False
            else:
                self.sounds['attack_sound'].play()


    def get_grid_position(self):
        grid_x = self.rect.centerx // TILESIZE
        grid_y = self.rect.centery // TILESIZE
        return [grid_x, grid_y]

    def check_death(self):
        if self.health <= 0:
            self.kill()

    def handle_powerups(self):
        current_time = pygame.time.get_ticks()

        # Shield
        if self.shield_active and current_time > self.shield_end_time:
            self.shield_active = False

        # extra damage
        if self.shoot_upgrade_active and current_time > self.shoot_upgrade_end:
            self.shoot_upgrade_active = False
            self.damage = self.stats['damage']

        # slow motion
        if self.slow_motion_active and current_time > self.slow_motion_end:
            self.slow_motion_active = False

        # machine_gun
        if self.machine_gun_active and current_time > self.machine_gun_end:
            self.attack_cooldown = 800
            self.machine_gun_active = False

        # bomb
        if self.bomb_active and current_time > self.bomb_end: 
            self.bomb_active = False

        # forstress shield
        if self.fortress_shield_active and current_time > self.fortress_shield_end:
            self.fortress_shield_active = False
            print('Fortress shield deactivated')

    def activate_shield(self, duration):
        self.shield_active = True
        self.shield_duration = duration * 1000
        self.shield_end_time = pygame.time.get_ticks() + duration * 1000

    def upgrade_shoot(self, duration):
        self.shoot_upgrade_active = True
        if self.damage < self.stats['damage'] * 2:
            self.damage *= 2
        self.shoot_upgrade_duration = duration * 1000
        self.shoot_upgrade_end = pygame.time.get_ticks() + duration * 1000

    def slow_motion(self, duration):
        self.slow_motion_active = True
        self.slow_motion_duration= duration * 1000
        self.slow_motion_end = pygame.time.get_ticks() + duration * 1000

    def get_health(self):
        if self.health < self.stats["health"]:
            self.health += 1

    def bomb_everyone(self, duration):
        self.bomb_active = True
        self.bomb_end = pygame.time.get_ticks() + duration * 1000

    def fortress_shield (self, duration):
        self.fortress_shield_active = True
        self.fortress_shield_duration = duration * 1000
        self.fortress_shield_end = pygame.time.get_ticks() + duration * 1000

    def get_machine_gun(self, duration):
        self.attack_cooldown = 200
        self.machine_gun_active = True
        self.machine_gun_duration= duration * 1000
        self.machine_gun_end = pygame.time.get_ticks() + duration * 1000

    def update(self):
        self.input()
        self.check_death()
        self.cooldowns()
        self.get_status()
        self.handle_powerups()
        self.animate()
        self.move(self.speed)
