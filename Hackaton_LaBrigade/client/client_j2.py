import os
import math
import sys
import pygame
from network import Network
from boutons import Bouton

WIDTH, HEIGHT = 960, 672
FPS           = 60
TITRE_FENETRE = "👨‍🍳 KDS — Chapitre 2 : Le Chef Chaud"

BLACK, WHITE, ORANGE, GREEN, RED, BLUE, GRAY, DARK = (10,10,10), (255,255,255), (240,130,0), (50,200,80), (220,60,60), (60,120,220), (80,80,80), (20,20,35)

class PlayerJ2:
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

class Customer:
    def __init__(self, x, y, chemin_sprite, ligne_anim=0, scale=2.2):
        self.x, self.y = x, y
        self.frame_index = 0.0
        self.animation_speed = 0.1
        self.frames = []
        self.scale = scale
        
        try:
            sheet = pygame.image.load(chemin_sprite).convert_alpha()
            FW, FH = 64, 64 
            
            # --- CORRECTION : Découpage strict par contenu ---
            for col in range(sheet.get_width() // FW):
                rect = pygame.Rect(col * FW, ligne_anim * FH, FW, FH)
                
                # On extrait la frame
                sub = sheet.subsurface(rect)
                
                # On vérifie si la frame n'est pas "vide" (que du noir transparent)
                # Si le rectangle de contenu est petit (ou inexistant), on saute
                if sub.get_bounding_rect().width > 10: # Seuil minimal de pixels
                    img = pygame.transform.scale(sub, (int(FW * self.scale), int(FH * self.scale)))
                    self.frames.append(img)
            
            self.has_sprite = len(self.frames) > 0
            print(f"✅ Ligne {ligne_anim} : {len(self.frames)} frames réelles chargées.")
            
        except Exception as e:
            print(f"❌ Erreur chargement client: {e}")
            self.has_sprite = False
    def update(self):
        if self.has_sprite and self.frames:
            self.frame_index += self.animation_speed

    def draw(self, screen):
        # On vérifie que frames n'est pas vide et que l'index est valide
        if self.has_sprite and self.frames:
            # On force l'index à rester dans les limites, même si frame_index devient gigantesque
            max_idx = len(self.frames) - 1
            idx = int(self.frame_index) % len(self.frames)
            
            # Affichage de sécurité
            img = self.frames[idx]
            screen.blit(img, (self.x - img.get_width()//2, self.y - img.get_height()//2))
        else:
            # Si sprite absent, dessine un petit cercle pour voir s'il est là
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 10)

def draw_qte_arrow(screen, color, pos, direction):
    x, y = pos
    if direction == "UP": points = [(x, y-15), (x-10, y+5), (x+10, y+5)]
    elif direction == "DOWN": points = [(x, y+15), (x-10, y-5), (x+10, y-5)]
    elif direction == "LEFT": points = [(x-15, y), (x+5, y-10), (x+5, y+10)]
    elif direction == "RIGHT": points = [(x+15, y), (x-5, y-10), (x-5, y+10)]
    pygame.draw.polygon(screen, color, points)


def get_game_result(state):
    etat = str(state.get("etat", "")).lower()
    if state.get("game_won") or etat == "victoire":
        return "victoire"
    if state.get("game_lost") or etat == "defaite":
        return "defaite"
    return None
            
def run_game(net: Network):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITRE_FENETRE)
    clock, font, font_s = pygame.time.Clock(), pygame.font.SysFont("Arial", 22, bold=True), pygame.font.SysFont("Arial", 14, bold=True)
    police_victoir = pygame.font.SysFont("Arial", 100)
    police = pygame.font.SysFont("Arial", 40, bold=True)

    #----------------MENU---------------------------#
    text_menu = police.render("Joueur 2, Chef Chaud", True, RED) 
    bouton_start = Bouton("Hackaton_LaBrigade/client/ressources/images/start_button.png", 400, 200, 200, 100)
    bouton_exit = Bouton("Hackaton_LaBrigade/client/ressources/images/exit_button.png", 400, 400, 200, 100)
    background_menu = pygame.image.load("Hackaton_LaBrigade/client/ressources/images/bg_image.png").convert()
    bg_menu = pygame.transform.scale(background_menu, (WIDTH, HEIGHT))
    menu = "on"

    #Victoire
    background_vic = pygame.image.load("Hackaton_LaBrigade/client/ressources/images/victoire.png").convert()
    bg_vic = pygame.transform.scale(background_vic, (800, 600))
    text_vic = police_victoir.render("VICTOIR", True, (10, 196, 190))
    text_merci = police.render("Merci d'avoir joué", True, (10, 196, 190))

    #Defaite
    text_def = police_victoir.render("DEFAITE", True, (209, 10, 40))
    text_merci_def = police.render("Merci d'avoir joué... malgré tout", True, (209, 10, 40))
    background_def = pygame.image.load("Hackaton_LaBrigade/client/ressources/images/defete.png").convert()
    bg_def = pygame.transform.scale(background_def, (800, 600))
    #-----------------------------------------------#

    try: map_j2 = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(__file__), "Carte_J2.png")).convert(), (WIDTH, HEIGHT))
    except: map_j2 = pygame.Surface((WIDTH, HEIGHT))

    game = "off"
    # Initialisation dans run_game
    img_joueur = os.path.join(os.path.dirname(__file__), "ressources", "images", "cat_2.png")
    chef = PlayerJ2(WIDTH//2, 460, img_joueur, ligne_down=2, ligne_up=3, ligne_left=4, ligne_right=5, ligne_idle=13, scale=2.2)

    try:
        bg_victoire = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(__file__), "ressources", "images", "victoire.png")).convert(), (WIDTH, HEIGHT))
    except Exception:
        bg_victoire = None
    try:
        bg_defaite = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(__file__), "ressources", "images", "defete.png")).convert(), (WIDTH, HEIGHT))
    except Exception:
        bg_defaite = None

    # Initialisation des clients
    dossier = os.path.dirname(os.path.abspath(__file__))
    img_chat_gris = os.path.join(dossier, "ressources", "images", "cat_3.png")
    img_chat_roux = os.path.join(dossier, "ressources", "images", "cat_2.png")
    
    # ligne_anim correspond à la ligne dans ta spritesheet (0 pour la 1ère ligne, 1 pour la 2ème, etc.)
    liste_pnj = [
        Customer(100, 100, img_chat_gris, ligne_anim=12, scale=2.2),
        Customer(200, 160, img_chat_roux, ligne_anim=13, scale=2.2),
        Customer(700, 150, img_chat_roux, ligne_anim=17, scale=2.2),
        Customer(350, 100, img_chat_gris, ligne_anim=36, scale=2.2)
    ]
    
    station_dressage, station_passe = pygame.Rect(420, 280, 120, 120), pygame.Rect(390, 514, 180, 80)
    station_cuisson, station_reparation = pygame.Rect(90, 336, 115, 150), pygame.Rect(755, 336, 115, 150)
    station_poubelle = pygame.Rect(625, 514, 50, 60)
    obstacles = [station_dressage, station_passe, station_cuisson, station_reparation, station_poubelle, pygame.Rect(0, 248, WIDTH, 25), pygame.Rect(0, 574, WIDTH, HEIGHT), pygame.Rect(0, 0, 95, HEIGHT), pygame.Rect(865, 0, WIDTH, HEIGHT)]

    state = net.send({"action": "get"}) or {}
    running = True

    popup_dressage_ouvert = False
    # Grille 5x5 au centre de l'écran
    rect_grille_popup = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 200, 400, 400)

    while running:
        action = {"action": "get"}
        station_cible = None
        if chef.get_rect().colliderect(station_dressage.inflate(40,40)): station_cible = "DRESSAGE"
        elif chef.get_rect().colliderect(station_passe.inflate(40,40)): station_cible = "PASSE"
        elif chef.get_rect().colliderect(station_cuisson.inflate(40,40)): station_cible = "CUISSON"
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

            if popup_dressage_ouvert:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if rect_grille_popup.collidepoint(mx, my):
                        col = (mx - rect_grille_popup.x) // 80
                        row = (my - rect_grille_popup.y) // 80
                        if 0 <= col < 5 and 0 <= row < 5:
                            action = {"action": "DRESSAGE_PLACEMENT_SOURIS", "position": [row, col]}
                elif event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE):
                    popup_dressage_ouvert = False
            else:
                if event.type == pygame.KEYDOWN and game == "on":
                    if event.key == pygame.K_p: action = {"action": "DECLENCHER_PANNE_DEBUG_CHAUD"} 
                    elif station_cible == "REPARATION" and state.get("ustensiles", {}).get("centrifugeuse", {}).get("etat") == "en_panne":
                        if event.key == pygame.K_UP: action = {"action": "QTE_INPUT_J2", "touche": "UP"}
                        elif event.key == pygame.K_DOWN: action = {"action": "QTE_INPUT_J2", "touche": "DOWN"}
                        elif event.key == pygame.K_LEFT: action = {"action": "QTE_INPUT_J2", "touche": "LEFT"}
                        elif event.key == pygame.K_RIGHT: action = {"action": "QTE_INPUT_J2", "touche": "RIGHT"}
                    elif event.key == pygame.K_SPACE:
                        if station_cible == "PASSE": action = {"action": "PRENDRE_PASSE"}
                        elif station_cible == "CUISSON": action = {"action": "INTERACTION_PLAQUE"}
                        elif station_cible == "POUBELLE": action = {"action": "JETER_POUBELLE", "joueur": "J2"}
                        elif station_cible == "DRESSAGE": popup_dressage_ouvert = True 

        if game == "on" and not popup_dressage_ouvert:
            chef.update(pygame.key.get_pressed(), obstacles)
            
        new_state = net.send(action)
        if new_state: state = new_state
        if get_game_result(state):
            game = "over"

        if game == "on":
            screen.blit(map_j2, (0, 0))

            # 2. Les PNJ (ils sont derrière les comptoirs)
            for pnj in liste_pnj:
                pnj.update()
                pnj.draw(screen)
                
            # 3. Ensuite, dessiner le joueur, le HUD, etc.
            chef.draw(screen)
            # ... reste du code

            pygame.draw.rect(screen, (40, 40, 40), (0, 0, WIDTH, 40))
            pygame.draw.circle(screen, WHITE, (30, 20), 15, 2) # Cercle horloge
            pygame.draw.line(screen, WHITE, (30, 20), (30, 10), 2) # Aiguille
            screen.blit(font.render(f"{state.get('timer_global', 0)}s", True, WHITE), (50, 10))
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

            # ── COMMANDE CLIENT (NOM DE RECETTE POUR J2) ──
            cibles = state.get("mini_jeu_dressage", {}).get("cibles", [])
            nom_recette = state.get("mini_jeu_dressage", {}).get("nom_recette", "Recette inconnue")
            hud_rect = pygame.Rect(WIDTH - 200, 50, 190, 80)
            pygame.draw.rect(screen, (30,30,50), hud_rect, border_radius=10)
            pygame.draw.rect(screen, ORANGE, hud_rect, 2, border_radius=10)
            screen.blit(font_s.render("COMMANDE :", True, ORANGE), (hud_rect.x + 10, hud_rect.y + 10))
            for i, cib in enumerate(cibles):
                screen.blit(font_s.render(f"- {cib['ing']}", True, WHITE), (hud_rect.x + 10, hud_rect.y + 35 + i*25))

            ing_passe = next((p.get("ingredients", []) for p in state.get("liste_postes", []) if p.get("nom") == "chaud"), [])
            for i, nom_ing in enumerate(ing_passe):
                px, py = station_passe.x + 30 + (i * 35), station_passe.y + 40
                pygame.draw.circle(screen, BLUE, (px, py), 12)
                screen.blit(font_s.render(nom_ing[:2], True, WHITE), (px-7, py-8))

            plaque_data = state.get("ustensiles", {}).get("plaque_chauffante", {})
            cx, cy = 110, 380 
            pygame.draw.rect(screen, ORANGE if plaque_data.get("etat") == "occupe" else (RED if plaque_data.get("etat") == "en_panne" else BLUE), (cx, cy, 80, 60), border_radius=10)
            screen.blit(font_s.render("Plaque", True, WHITE), (cx+15, cy+20))
            if plaque_data.get("contenu"): pygame.draw.circle(screen, GREEN, (cx+40, cy+30), 10)
            if plaque_data.get("etat") == "en_panne": screen.blit(font_s.render("APPELLE J1!", True, RED), (cx, cy-25))

            reelles = state.get("mini_jeu_dressage", {}).get("reelles", [])
            for item in reelles:
                r, c = item["pos"]
                dx, dy = station_dressage.x + 15 + (c * 20), station_dressage.y + 20 + (r * 20)
                pygame.draw.circle(screen, GREEN, (dx, dy), 10)
                screen.blit(font_s.render(item["ing"][:2], True, BLACK), (dx-7, dy-8))

            chef.draw(screen)

            if state.get("j2_en_main"):
                pygame.draw.circle(screen, RED, (chef.x+20, chef.y-20), 10)
                screen.blit(font_s.render(state.get("j2_en_main")[:3], True, WHITE), (chef.x+10, chef.y-28))

            if station_cible and not popup_dressage_ouvert:
                txt = "PRENDRE DE LA PASSE" if station_cible=="PASSE" else ("UTILISER LA PLAQUE" if station_cible=="CUISSON" else ("DRESSER (OUVRIR)" if station_cible=="DRESSAGE" else ("STATION RÉPARATION" if station_cible=="REPARATION" else "JETER INGRÉDIENT")))
                txt_s = font_s.render(f"[ESPACE] {txt}", True, BLACK)
                br = txt_s.get_rect(center=(chef.x, chef.y - 45)).inflate(20,10)
                pygame.draw.rect(screen, WHITE, br, border_radius=10)
                screen.blit(txt_s, txt_s.get_rect(center=(chef.x, chef.y - 45)))

            centri_data = state.get("ustensiles", {}).get("centrifugeuse", {})
            if station_cible == "REPARATION" and centri_data.get("etat") == "en_panne" and not popup_dressage_ouvert:
                qte_seq, qte_idx = centri_data.get("qte_seq", []), centri_data.get("qte_index", 0)
                pygame.draw.rect(screen, BLACK, (WIDTH//2 - 150, HEIGHT//2 - 100, 300, 60), border_radius=10)
                symb = {"UP": "⬆", "DOWN": "⬇", "LEFT": "⬅", "RIGHT": "➡"}
                for i, d in enumerate(qte_seq):
                    couleur = GREEN if i < qte_idx else WHITE
                    draw_qte_arrow(screen, couleur, (WIDTH//2 - 100 + i*50, HEIGHT//2 - 70), d)

            # ── POPUP DRESSAGE SOURIS 5x5 ──
            if popup_dressage_ouvert:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                
                pygame.draw.rect(screen, WHITE, rect_grille_popup)
                for r in range(5):
                    for c in range(5):
                        cell_rect = pygame.Rect(rect_grille_popup.x + c*80, rect_grille_popup.y + r*80, 80, 80)
                        pygame.draw.rect(screen, BLACK, cell_rect, 2)
                        
                for item in reelles:
                    r, c = item["pos"]
                    pygame.draw.circle(screen, GREEN, (rect_grille_popup.x + c*80 + 40, rect_grille_popup.y + r*80 + 40), 20)
                    titre_ing = font_s.render(item["ing"], True, BLACK)
                    screen.blit(titre_ing, (rect_grille_popup.x + c*80 + 40 - titre_ing.get_width()//2, rect_grille_popup.y + r*80 + 30))

                main_actuelle = state.get('j2_en_main')
                texte_titre = f"Cliquer pour Placer/Reprendre : {main_actuelle}" if main_actuelle else "Cliquez sur un ingrédient pour le reprendre"
                titre = police.render(texte_titre, True, WHITE)
                screen.blit(titre, (WIDTH//2 - titre.get_width()//2, rect_grille_popup.y - 50))
                
                txt2 = font_s.render("Échap/Espace pour fermer", True, GRAY)
                screen.blit(txt2, (WIDTH//2 - txt2.get_width()//2, rect_grille_popup.bottom + 20))

        elif game == "over":
            if get_game_result(state) == "victoire" and bg_victoire:
                screen.blit(bg_victoire, (0, 0))
            elif get_game_result(state) == "defaite" and bg_defaite:
                screen.blit(bg_defaite, (0, 0))
            else:
                screen.blit(map_j2, (0, 0))

            is_victoire = get_game_result(state) == "victoire"
            resultat = "VICTOIRE !" if is_victoire else "DÉFAITE"
            if resultat == "DÉFAITE": 
                screen.fill((255, 255, 255))
                screen.blit(bg_defaite, (0, 0))
                screen.blit(text_def, (170, 50))
                screen.blit(text_merci_def, (60, 150))
                bouton_exit.draw(screen)
            else :                
                screen.fill((255, 255, 255))
                screen.blit(bg_victoire, (0, 0))
                screen.blit(text_vic, (170, 50))
                screen.blit(text_merci, (60, 150))
                bouton_exit.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

def main():
    try: net = Network(server_ip=sys.argv[sys.argv.index("--ip")+1] if "--ip" in sys.argv else None)
    except: sys.exit(1)
    run_game(net)

if __name__ == "__main__": main()