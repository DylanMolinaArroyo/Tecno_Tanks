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
        self.bullet_speed = 8
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

        # Set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha) 
        else:
            self.image.set_alpha(255)

    def return_damage(self):
        return self.damage
    
    def get_damage(self, enemy, attack_type):
        if self.vulnerable:
            self.sounds['hit_sound'].play()
            if attack_type == 'bullet':
                self.health -= enemy.return_damage()
            self.hurt_time = pygame.time.get_ticks()
            self.vulnerable = False

    def get_grid_position(self):
        grid_x = self.rect.centerx // TILESIZE
        grid_y = self.rect.centery // TILESIZE
        return [grid_x, grid_y]

    def check_death(self):
        if self.health <= 0:
            self.kill()

    def debug_draw(self, surface, offset):
        debug_rect = self.rect.copy()
        debug_rect.topleft -= offset 
        pygame.draw.rect(surface, (255, 0, 0), debug_rect, 2)

        debug_hitbox = self.hitbox.copy()
        debug_hitbox.topleft -= offset
        pygame.draw.rect(surface, (0, 255, 0), debug_hitbox, 2)

    def update(self):
        self.input()
        self.check_death()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
