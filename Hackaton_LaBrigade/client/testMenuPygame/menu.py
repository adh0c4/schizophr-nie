
import pygame
from boutons import Bouton

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Menu Example")
clock = pygame.time.Clock()
running = True
police = pygame.font.SysFont("Arial", 50)

#--------------------- Variables for the menu --------------------------#
text_menu = police.render("Joueur 1, Chef Froid", True, (10, 196, 190))
bouton_start = Bouton("ressours/images/start_button.png", 300, 200, 200, 100)
bouton_exit = Bouton("ressours/images/exit_button.png", 300, 400, 200, 100)
background = pygame.image.load("ressours/images/bg_image.png").convert()
bg_menu = pygame.transform.scale(background, (800, 600))
menu = "on"
#-----------------------------------------------------------------------#

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #-------------- Button Menu on screeen in the game loop --------#
            if bouton_start.rect.collidepoint(event.pos):
                print("Start button clicked")
            elif bouton_exit.rect.collidepoint(event.pos):
                print("Exit button clicked")
                running = False
        #--------------------------------------------------------------#

#----------- Affichage MENU -----------#
    screen.fill((255, 255, 255))
    screen.blit(bg_menu, (0, 0))
    screen.blit(text_menu, (170, 50))
    bouton_start.draw(screen)
    bouton_exit.draw(screen)
#--------------------------------------#
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()