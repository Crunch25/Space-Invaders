import pygame

class Player:
    def __init__(self, x, y):
        self.image = pygame.image.load("assets/player.png").convert_alpha()
        self.image.set_colorkey((128, 128, 128))
        self.image.set_colorkey((255, 255, 255))
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))

    def move(self, dx):
        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 800:
            self.rect.right = 800

    def draw(self, screen):
        screen.blit(self.image, self.rect)
