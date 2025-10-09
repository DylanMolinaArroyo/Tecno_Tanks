import pygame
from Code.Entities.entity import Entity
from Code.Utilities.settings import *
from Code.Functions.support import import_folder

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_bullet, is_local=True):
        """
        Initializes the player entity, sets up graphics, movement, stats, power-ups, and sounds.

        Args:
            pos (tuple): (x, y) position to spawn the player.
            groups (list): Sprite groups to add this player to.
            obstacle_sprites (pygame.sprite.Group): Group of obstacle sprites for collision.
            create_bullet (callable): Function to create bullets.
        """

        super().__init__(groups)
        self.is_local = is_local

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
        """
        Loads player animation frames for all directions and idle states.
        """

        character_path = 'Assets/Entities/Player/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': []}
        
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        """
        Handles keyboard input for movement and attacking.
        """

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
        """
        Updates the player's status to idle if not moving.
        """

        # --- CAMBIO CRÍTICO ---
        # Un jugador remoto no debe calcular su propio estado; lo recibe por la red.
        if not self.is_local:
            return

        # Idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status and 'attack' not in self.status:
                self.status = self.status + '_idle'

    def cooldowns(self):
        """
        Manages attack and invulnerability cooldown timers.
        """
       
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def animate(self):
        """
        Updates the player's animation frame and applies visual effects for power-ups and damage.
        """

        animation = self.animations[self.status]

        # Loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Reset base image on each frame
        base_image = animation[int(self.frame_index)].copy()
        self.rect = base_image.get_rect(center=self.hitbox.center)

        # Damage shoot boost → red
        if self.shoot_upgrade_active:
            base_image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
        
        # Machine gun → orange
        if self.machine_gun_active:
            base_image.fill((255, 155, 0), special_flags=pygame.BLEND_RGB_ADD)

        # Shield → overlay
        if self.shield_active:
            shield_scaled = pygame.transform.scale(self.shield_image, base_image.get_size())
            base_image.blit(shield_scaled, (0, 0))

        # Blinking when taking damage
        if not self.vulnerable:
            alpha = self.wave_value()
            base_image.set_alpha(alpha)
        else:
            base_image.set_alpha(255)

        self.image = base_image


    def return_damage(self):
        """
        Returns the player's current damage value.

        Returns:
            int: Damage value.
        """
       
        return self.damage
    
    def get_damage(self, enemy, attack_type):
        """
        Applies damage to the player from an enemy attack, considering shield status.

        Args:
            enemy: The attacking enemy entity.
            attack_type (str): Type of attack (e.g., 'bullet').
        """

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
        """
        Returns the player's current grid position.

        Returns:
            list: [grid_x, grid_y]
        """

        grid_x = self.rect.centerx // TILESIZE
        grid_y = self.rect.centery // TILESIZE
        return [grid_x, grid_y]

    def check_death(self):
        """
        Checks if the player's health is depleted and removes the player if so.
        """

        if self.health <= 0:
            self.kill()

    def handle_powerups(self):
        """
        Manages the duration and deactivation of all power-up effects.
        """

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
        """
        Activates the shield power-up for the specified duration.

        Args:
            duration (int): Duration in seconds.
        """

        self.shield_active = True
        self.shield_duration = duration * 1000
        self.shield_end_time = pygame.time.get_ticks() + duration * 1000

    def upgrade_shoot(self, duration):
        """
        Activates the shoot upgrade power-up, doubling damage for the specified duration.

        Args:
            duration (int): Duration in seconds.
        """

        self.shoot_upgrade_active = True
        if self.damage < self.stats['damage'] * 2:
            self.damage *= 2
        self.shoot_upgrade_duration = duration * 1000
        self.shoot_upgrade_end = pygame.time.get_ticks() + duration * 1000

    def slow_motion(self, duration):
        """
        Activates the slow motion power-up for the specified duration.

        Args:
            duration (int): Duration in seconds.
        """

        self.slow_motion_active = True
        self.slow_motion_duration= duration * 1000
        self.slow_motion_end = pygame.time.get_ticks() + duration * 1000

    def get_health(self):
        """
        Restores one health point if not at maximum health.
        """

        if self.health < self.stats["health"]:
            self.health += 1

    def bomb_everyone(self, duration):
        """
        Activates the bomb power-up for the specified duration.

        Args:
            duration (int): Duration in seconds.
        """

        self.bomb_active = True
        self.bomb_end = pygame.time.get_ticks() + duration * 1000

    def fortress_shield (self, duration):
        """
        Activates the fortress shield power-up for the specified duration.

        Args:
            duration (int): Duration in seconds.
        """

        self.fortress_shield_active = True
        self.fortress_shield_duration = duration * 1000
        self.fortress_shield_end = pygame.time.get_ticks() + duration * 1000

    def get_machine_gun(self, duration):
        """
        Activates the machine gun power-up, reducing attack cooldown for the specified duration.

        Args:
            duration (int): Duration in seconds.
        """

        self.attack_cooldown = 200
        self.machine_gun_active = True
        self.machine_gun_duration= duration * 1000
        self.machine_gun_end = pygame.time.get_ticks() + duration * 1000

    def update(self):
        """
        Main update loop for the player. Handles input, death, cooldowns, status, power-ups, animation, and movement.
        """
        
        if self.is_local: 
            self.input()
        
        #self.input()
        self.check_death()
        self.cooldowns()
        self.get_status()
        self.handle_powerups()
        self.animate()
        self.move(self.speed)
