# enemy.py
import pygame
import random

class Enemy:

    def __init__(self, x, y):
        self.image = pygame.image.load("assets/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.image = pygame.transform.flip(self.image, False, True)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = random.choice([0.5, 1])

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)
