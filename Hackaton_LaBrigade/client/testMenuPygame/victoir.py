
import pygame
from boutons import Bouton

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Menu Example")
clock = pygame.time.Clock()
running = True
police_victoir = pygame.font.SysFont("Arial", 100)
police = pygame.font.SysFont("Arial", 80)

#-----------------------------------------------#
text_vic = police_victoir.render("VICTOIR", True, (10, 196, 190))
text_merci = police.render("Merci d'avoir joué", True, (10, 196, 190))
bouton_exit = Bouton("client/ressources/images/exit_button.png", 300, 400, 200, 100)
background_vic = pygame.image.load("client/ressources/images/victoire.png").convert()
bg_vic = pygame.transform.scale(background_vic, (800, 600))
menu = "on"
#-----------------------------------------------#

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #-----------------------------------------------------#        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if bouton_exit.rect.collidepoint(event.pos):
                print("Exit button clicked")
                running = False
        #-----------------------------------------------------#

#----------- Affichage MENU -----------#
    screen.fill((255, 255, 255))
    screen.blit(bg_vic, (0, 0))
    screen.blit(text_vic, (170, 50))
    screen.blit(text_merci, (60, 150))
    bouton_exit.draw(screen)
#--------------------------------------#
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()