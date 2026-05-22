
import pygame
from boutons import Bouton

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Menu Example")
clock = pygame.time.Clock()
running = True
police_victoir = pygame.font.SysFont("Arial", 100)
police = pygame.font.SysFont("Arial", 50)

#-----------------------------------------------#
text_vic = police_victoir.render("DEFAITE", True, (209, 10, 40))
text_merci = police.render("Merci d'avoir joué... malgré tout", True, (209, 10, 40))
bouton_exit = Bouton("client/ressources/images/exit_button.png", 300, 400, 200, 100)
background = pygame.image.load("client/ressources/images/defete.png").convert()
bg_menu = pygame.transform.scale(background, (800, 600))
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
    screen.blit(bg_menu, (0, 0))
    screen.blit(text_vic, (170, 50))
    screen.blit(text_merci, (60, 150))
    bouton_exit.draw(screen)
#--------------------------------------#
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()