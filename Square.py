import pygame


class Square(pygame.sprite.Sprite):

    def __init__(self, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((5, 5))
        self.image.fill((255, 255, 255))
        self.width = width
        self.height = height
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, width, height), 1)
        self.rect = self.image.get_rect()

    def move(self, new_x, new_y):
        self.rect.x = new_x
        self.rect.y = new_y



