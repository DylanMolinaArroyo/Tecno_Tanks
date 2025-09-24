import pygame
import os

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, groups, folder_path="Assets/Effects/Circle_explosion"):
        super().__init__(groups)

        self.frames = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                img = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                img = pygame.transform.scale(img, (180, 180))
                self.frames.append(img)

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        self.animation_speed = 0.2

    def update(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]
