import pygame
from math import sin

class Entity(pygame.sprite.Sprite):
	def __init__(self,groups):
		"""
        Initializes a base entity sprite.

        Args:
            groups (list): Sprite groups to add this entity to.
        """

		super().__init__(groups)
		self.frame_index = 0
		self.animation_speed = 0.15
		self.direction = pygame.math.Vector2()

	def move(self,speed):
		"""
        Moves the entity in its current direction, handling collisions.

        Args:
            speed (float): Movement speed.
        """
				
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal')
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')
		self.rect.center = self.hitbox.center

	def collision(self,direction):
		"""
        Handles collision detection and resolution for the entity.

        Args:
            direction (str): 'horizontal' or 'vertical' axis for collision.
        """

		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0: # moving right
						self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0: # moving left
						self.hitbox.left = sprite.hitbox.right

		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.y > 0: # moving down
						self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0: # moving up
						self.hitbox.top = sprite.hitbox.bottom

	def wave_value(self):
		"""
        Returns a value based on a sine wave for animation effects.

        Returns:
            int: 255 if sine value is positive, otherwise 0.
        """
		
		value = sin(pygame.time.get_ticks())
		if value >= 0: 
			return 255
		else:
			return 0 