import pygame
from Code.Utilities.settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, entity, tile_sprites, groups, bullet_speed):
        super().__init__(groups)

        self.sprite_type = 'bullet'
        self.origin_type = entity.sprite_type
        
        direction = entity.status.split('_')[0]

        # Imagen y máscara
        self.image = pygame.image.load('Assets/Entities/Bullet/bullet.png').convert_alpha() 
        self.image = pygame.transform.scale(self.image, (25, 25))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)  # ← importante

        offset = 10
        self.bullet_speed = bullet_speed

        if direction == 'right':
            self.rect.midleft = entity.rect.midright + pygame.math.Vector2(offset, 0)
            self.direction = pygame.math.Vector2(1, 0)
        elif direction == 'left':
            self.rect.midright = entity.rect.midleft - pygame.math.Vector2(offset, 0)
            self.direction = pygame.math.Vector2(-1, 0)
        elif direction == 'up':
            self.rect.midbottom = entity.rect.midtop - pygame.math.Vector2(0, offset)
            self.direction = pygame.math.Vector2(0, -1)
        elif direction == 'down':
            self.rect.midtop = entity.rect.midbottom + pygame.math.Vector2(0, offset)
            self.direction = pygame.math.Vector2(0, 1)
        else:
            self.rect.center = entity.rect.center
            self.direction = pygame.math.Vector2(0, 0)

        self.speed = self.bullet_speed 
        self.tile_sprites = tile_sprites

    def update(self):
        # Movimiento
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Colisión con muros usando máscara
        if pygame.sprite.spritecollide(self, self.tile_sprites, False, pygame.sprite.collide_mask):
            self.kill()
