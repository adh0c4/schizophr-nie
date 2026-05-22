import sys
import os
import pygame
import math
from boutons import Bouton
from network import Network

WIDTH, HEIGHT = 960, 672
FPS           = 60
TITRE_FENETRE = "👨‍🍳 KDS — Chapitre 1 : Le Chef Froid"

BLACK, WHITE, BLUE, GREEN, RED, ORANGE, GRAY, DARK = (10,10,10), (255,255,255), (60,120,220), (50,200,80), (220,60,60), (240,130,0), (80,80,80), (30,30,40)

class PlayerJ1:
    def __init__(self, x, y, sprite_path, ligne_down, ligne_up, ligne_left, ligne_right, ligne_idle, scale=2.5):
        self.scale = scale
        self.x, self.y, self.speed = x, y, 5
        self.direction = "down"
        self.is_moving = False # Nouveau : suit l'état du mouvement
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = {
            "down": self.load_frames(sprite_path, ligne_down),
            "up": self.load_frames(sprite_path, ligne_up),
            "left": self.load_frames(sprite_path, ligne_left),
            "right": self.load_frames(sprite_path, ligne_right),
            "idle": self.load_frames(sprite_path, ligne_idle) # Ligne pour le repos
        }
        

    def load_frames(self, path, row):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        size = int(50 * self.scale)
        for col in range(6):
            rect = pygame.Rect(col * 64, row * 64, 64, 64)
            img = pygame.transform.scale(sheet.subsurface(rect), (size, size))
            frames.append(img)
        return frames


    def get_rect(self): return pygame.Rect(self.x - 25, self.y - 25, 50, 50)

    def update(self, keys, obs):
        dx, dy = 0, 0
        self.is_moving = False # Reset avant de vérifier les touches
        
        if keys[pygame.K_q]: dx, self.direction, self.is_moving = -self.speed, "left", True
        elif keys[pygame.K_d]: dx, self.direction, self.is_moving = self.speed, "right", True
        elif keys[pygame.K_z]: dy, self.direction, self.is_moving = -self.speed, "up", True
        elif keys[pygame.K_s]: dy, self.direction, self.is_moving = self.speed, "down", True
        
        # Application du mouvement avec collision simple
        next_rect = self.get_rect()
        next_rect.x += dx
        if not any(next_rect.colliderect(o) for o in obs): self.x += dx
        
        next_rect = self.get_rect()
        next_rect.y += dy
        if not any(next_rect.colliderect(o) for o in obs): self.y += dy
        
        self.frame_index += self.animation_speed

    def draw(self, screen):
        anim = self.frames[self.direction] if self.is_moving else self.frames["idle"]
        img = anim[int(self.frame_index) % len(anim)]
        half = int(25 * self.scale)
        screen.blit(img, (self.x - half, self.y - half))

def draw_qte_arrow(screen, color, pos, direction):
    x, y = pos
    if direction == "UP": points = [(x, y-15), (x-10, y+5), (x+10, y+5)]
    elif direction == "DOWN": points = [(x, y+15), (x-10, y-5), (x+10, y-5)]
    elif direction == "LEFT": points = [(x-15, y), (x+5, y-10), (x+5, y+10)]
    elif direction == "RIGHT": points = [(x+15, y), (x-5, y-10), (x-5, y+10)]
    pygame.draw.polygon(screen, color, points)


def run_game(net: Network):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITRE_FENETRE)
    clock, font, font_s = pygame.time.Clock(), pygame.font.SysFont("Arial", 22, bold=True), pygame.font.SysFont("Arial", 14, bold=True)
    police = pygame.font.SysFont("Arial", 40, bold=True)
    
    #----------------MENU---------------------------#
    text_menu = police.render("Joueur 1, Chef Froid", True, (10, 196, 190)) 
    bouton_start = Bouton("Hackaton_LaBrigade/client/ressources/images/start_button.png", 400, 200, 200, 100)
    bouton_exit = Bouton("Hackaton_LaBrigade/client/ressources/images/exit_button.png", 400, 400, 200, 100)
    background_menu = pygame.image.load("Hackaton_LaBrigade/client/ressources/images/bg_image.png").convert()
    bg_menu = pygame.transform.scale(background_menu, (WIDTH, HEIGHT))
    menu = "on"
    #-----------------------------------------------#


    try: map_j1 = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(__file__), "Carte_J1.png")).convert(), (WIDTH, HEIGHT))
    except: map_j1 = pygame.Surface((WIDTH, HEIGHT))

    game = "off"
    # Initialisation dans run_game
    img_joueur = os.path.join(os.path.dirname(__file__), "ressources", "images", "cat_3.png")
    chef = PlayerJ1(WIDTH//2, 300, img_joueur, ligne_down=2, ligne_up=3, ligne_left=4, ligne_right=5, ligne_idle=13, scale=2.2)
    
    station_passe, station_reserve = pygame.Rect(390, 25, 180, 70), pygame.Rect(390, 370, 180, 80)
    station_centrifugeuse, station_reparation = pygame.Rect(90, 144, 115, 150), pygame.Rect(755, 144, 115, 150)
    station_poubelle = pygame.Rect(625, 370, 50, 60)
    obstacles = [station_centrifugeuse, station_reserve, station_reparation, station_passe, station_poubelle, pygame.Rect(0,0,WIDTH,25), pygame.Rect(0,430,WIDTH,HEIGHT), pygame.Rect(0,0,95,HEIGHT), pygame.Rect(865,0,WIDTH,HEIGHT)]

    state = net.send({"action": "get"}) or {}
    running = True

    while running:
        action = {"action": "get"}
        station_cible = None
        if chef.get_rect().colliderect(station_centrifugeuse.inflate(40,40)): station_cible = "CENTRIFUGEUSE"
        elif chef.get_rect().colliderect(station_reserve.inflate(40,40)): station_cible = "RESERVE"
        elif chef.get_rect().colliderect(station_passe.inflate(40,40)): station_cible = "PASSE"
        elif chef.get_rect().colliderect(station_reparation.inflate(40,40)): station_cible = "REPARATION"
        elif chef.get_rect().colliderect(station_poubelle.inflate(40,40)): station_cible = "POUBELLE"

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False

            elif menu == "on" or game == "off":
            #----------- Affichage MENU -----------#
                screen.fill((255, 255, 255))
                screen.blit(bg_menu, (0, 0))
                screen.blit(text_menu, (270, 50))
                bouton_start.draw(screen)
                bouton_exit.draw(screen)
            #--------------------------------------#
                
                #------------------Activation menu--------------------#        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if bouton_start.rect.collidepoint(event.pos):
                        game = "on"
                    elif bouton_exit.rect.collidepoint(event.pos):
                        print("Exit button clicked")
                        running = False
                #-----------------------------------------------------#


            if event.type == pygame.KEYDOWN and game == "on":
                if event.key == pygame.K_p: action = {"action": "DECLENCHER_PANNE_DEBUG_FROID"}
                elif station_cible == "REPARATION" and state.get("ustensiles", {}).get("plaque_chauffante", {}).get("etat") == "en_panne":
                    if event.key == pygame.K_UP: action = {"action": "QTE_INPUT_J1", "touche": "UP"}
                    elif event.key == pygame.K_DOWN: action = {"action": "QTE_INPUT_J1", "touche": "DOWN"}
                    elif event.key == pygame.K_LEFT: action = {"action": "QTE_INPUT_J1", "touche": "LEFT"}
                    elif event.key == pygame.K_RIGHT: action = {"action": "QTE_INPUT_J1", "touche": "RIGHT"}
                
                # J1 CHOISIT DANS LA RÉSERVE AVEC 1, 2, 3
                elif station_cible == "RESERVE":
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1: action = {"action": "PRENDRE_INGREDIENT", "ingredient": "Tomate"}
                    elif event.key == pygame.K_2 or event.key == pygame.K_KP2: action = {"action": "PRENDRE_INGREDIENT", "ingredient": "Salade"}
                    elif event.key == pygame.K_3 or event.key == pygame.K_KP3: action = {"action": "PRENDRE_INGREDIENT", "ingredient": "Viande"}
                
                elif event.key == pygame.K_SPACE:
                    if station_cible == "CENTRIFUGEUSE": action = {"action": "INTERACT_CENTRIFUGEUSE"}
                    elif station_cible == "PASSE": action = {"action": "ENVOYER_PASSE"}
                    elif station_cible == "POUBELLE": action = {"action": "JETER_POUBELLE", "joueur": "J1"}

        if game == "on": chef.update(pygame.key.get_pressed(), obstacles)
        new_state = net.send(action)
        if new_state: state = new_state
        if state.get("game_won") or state.get("game_lost"):
            game = "over"

        if game == "on":
            screen.blit(map_j1, (0, 0))
            
            # --- HUD TOP (TIMER ET SATISFACTION) ---
            pygame.draw.rect(screen, (40, 40, 40), (0, 0, WIDTH, 40))
            # Dessin du Timer
            pygame.draw.circle(screen, WHITE, (30, 20), 15, 2) # Cercle horloge
            pygame.draw.line(screen, WHITE, (30, 20), (30, 10), 2) # Aiguille
            screen.blit(font.render(f"{state.get('timer_global', 0)}s", True, WHITE), (50, 10))
            # Dessin de la Satisfaction
            satisfaction = state.get("satisfaction", 100)
            coul_sat = GREEN if satisfaction > 50 else (ORANGE if satisfaction > 20 else RED)
            sat_txt = police.render(f"SATISFACTION : {satisfaction:.0f}%", True, coul_sat)
            screen.blit(sat_txt, (WIDTH//2 - sat_txt.get_width()//2, -5))
            # Barre de satisfaction
            bar_x = WIDTH//2 - 120
            bar_y = 25
            bar_w = 240
            bar_h = 10
            pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
            pygame.draw.rect(screen, coul_sat, (bar_x + 2, bar_y + 2, int((bar_w - 4) * min(max(satisfaction, 0), 100) / 100), bar_h - 4), border_radius=4)

            # --- DESSIN PASSE ---
            ing_passe = next((p.get("ingredients", []) for p in state.get("liste_postes", []) if p.get("nom") == "chaud"), [])
            for i, nom_ing in enumerate(ing_passe):
                px, py = station_passe.x + 30 + (i * 35), station_passe.y + 40
                pygame.draw.circle(screen, BLUE, (px, py), 12)
                screen.blit(font_s.render(str(nom_ing)[:3], True, WHITE), (px-10, py-8))

            # --- DESSIN CENTRIFUGEUSE ---
            centri_data = state.get("ustensiles", {}).get("centrifugeuse", {})
            cx, cy = 110, 200 
            pygame.draw.rect(screen, ORANGE if centri_data.get("etat") == "occupe" else (RED if centri_data.get("etat") == "en_panne" else BLUE), (cx, cy, 80, 60), border_radius=10)
            screen.blit(font_s.render("Centri.", True, WHITE), (cx+15, cy-25))
            if centri_data.get("contenu"): pygame.draw.circle(screen, GREEN, (cx+40, cy+30), 10)
            if centri_data.get("etat") == "en_panne": screen.blit(font_s.render("APPELLE J2!", True, RED), (cx, cy-45))

            chef.draw(screen)

            # --- HUD RECETTE (POUR J1) ---
            nom_recette = state.get("mini_jeu_dressage", {}).get("nom_recette", "Recette inconnue")
            cibles = state.get("mini_jeu_dressage", {}).get("cibles", [])
            instructions = state.get("mini_jeu_dressage", {}).get("instructions", [])
            hud_rect = pygame.Rect(WIDTH - 180, 50, 170, 220)
            pygame.draw.rect(screen, (30,30,30), hud_rect, border_radius=10)
            screen.blit(font_s.render("RECETTE (J1)", True, ORANGE), (hud_rect.x + 5, hud_rect.y + 5))
            screen.blit(font_s.render(nom_recette, True, WHITE), (hud_rect.x + 5, hud_rect.y + 30))
            for r in range(5):
                for c in range(5):
                    case_rect = pygame.Rect(hud_rect.x + 10 + c*30, hud_rect.y + 55 + r*30, 28, 28)
                    pygame.draw.rect(screen, GRAY, case_rect, 1)
                    
                    # Dessin des cibles
                    for cib in cibles:
                        if cib["pos"] == [r, c]:
                            pygame.draw.rect(screen, GREEN, case_rect.inflate(-4, -4))
                            txt_ing = font_s.render(cib["ing"][:3], True, BLACK)
                            screen.blit(txt_ing, (case_rect.x + 2, case_rect.y + 5))

            instr_y = hud_rect.y + 55 + 5 + 150
            screen.blit(font_s.render("Étapes :", True, ORANGE), (hud_rect.x + 5, instr_y))
            for idx, ligne in enumerate(instructions):
                screen.blit(font_s.render(f"{idx+1}. {ligne}", True, WHITE), (hud_rect.x + 5, instr_y + 20 + idx*18))

            # --- BULLE & MAIN ---
            if station_cible:
                txt = "UTILISER CENTRIFUGEUSE" if station_cible=="CENTRIFUGEUSE" else ("[1]Tomate [2]Salade [3]Viande" if station_cible=="RESERVE" else ("ENVOYER AU CHEF CHAUD" if station_cible=="PASSE" else ("AIDER À RÉPARER (QTE)" if station_cible=="REPARATION" else "JETER INGRÉDIENT")))
                prefix = "" if station_cible == "RESERVE" else "[ESPACE] "
                txt_s = font_s.render(f"{prefix}{txt}", True, BLACK)
                br = txt_s.get_rect(center=(chef.x, chef.y - 45)).inflate(20,10)
                pygame.draw.rect(screen, WHITE, br, border_radius=10)
                screen.blit(txt_s, txt_s.get_rect(center=(chef.x, chef.y - 45)))

            if state.get("j1_en_main"):
                pygame.draw.circle(screen, RED, (chef.x+20, chef.y-20), 10)
                screen.blit(font_s.render(state.get("j1_en_main")[:3], True, WHITE), (chef.x+10, chef.y-28))

            plaque_data = state.get("ustensiles", {}).get("plaque_chauffante", {})
            if station_cible == "REPARATION" and plaque_data.get("etat") == "en_panne":
                qte_seq, qte_idx = plaque_data.get("qte_seq", []), plaque_data.get("qte_index", 0)
                pygame.draw.rect(screen, BLACK, (WIDTH//2 - 150, HEIGHT//2 - 100, 300, 60), border_radius=10)
                symb = {"UP": "⬆", "DOWN": "⬇", "LEFT": "⬅", "RIGHT": "➡"}
                for i, d in enumerate(qte_seq):
                    couleur = GREEN if i < qte_idx else WHITE
                    draw_qte_arrow(screen, couleur, (WIDTH//2 - 100 + i*50, HEIGHT//2 - 70), d)

        elif game == "over":
            screen.blit(map_j1, (0, 0))
            resultat = "VICTOIRE !" if state.get("game_won") else "DÉFAITE"
            message = (
                "La satisfaction a été maintenue suffisamment longtemps." if state.get("game_won")
                else "La satisfaction est tombée trop bas."
            )
            pygame.draw.rect(screen, BLACK, (WIDTH//2 - 280, HEIGHT//2 - 100, 560, 160), border_radius=20)
            pygame.draw.rect(screen, WHITE, (WIDTH//2 - 282, HEIGHT//2 - 102, 564, 164), 2, border_radius=20)
            screen.blit(police.render(resultat, True, GREEN if state.get("game_won") else RED), (WIDTH//2 - 140, HEIGHT//2 - 70))
            screen.blit(font.render(message, True, WHITE), (WIDTH//2 - 250, HEIGHT//2 - 20))
            screen.blit(font.render("Fermez la fenêtre pour quitter.", True, WHITE), (WIDTH//2 - 210, HEIGHT//2 + 20))





        pygame.display.flip()
        clock.tick(FPS)

def main():
    try: net = Network(server_ip=sys.argv[sys.argv.index("--ip")+1] if "--ip" in sys.argv else None)
    except: sys.exit(1)
    run_game(net)

if __name__ == "__main__": main()