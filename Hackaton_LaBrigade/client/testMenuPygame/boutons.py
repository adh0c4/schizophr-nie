
import pygame

# Boutons pour le menu

class Bouton: # classe avec constructeur pour créer un bouton avec une image, une position et une taille
    def __init__(self, image, x, y, width, height):
        self.image = pygame.image.load(image).convert_alpha() #convert_alpha() pour gérer la transparence de l'image
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont('Arial', 30)
        self.image = pygame.transform.smoothscale(self.image, (width, height))#smoothscale() pour redimensionner l'image du bouton à la taille spécifiée
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pressed = False
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    