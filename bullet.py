import pygame

class Bullet:
    def __init__(self, x, y, fast=False):
        self.image = pygame.Surface((5, 20))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -7

        if fast:
            self.speed = -12

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)
