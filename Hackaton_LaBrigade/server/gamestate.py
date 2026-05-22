import os
import sys
import time
import random
from typing import Dict, List

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_PATH not in sys.path: sys.path.insert(0, ROOT_PATH)

from models.ingredients import Ingredient
from models.poste import Poste
from models.ustensile import Centrifugeuse, PlaqueCuisson
from shared.constantes import (
    SATISFACTION_VICTOIRE_MIN,
    SATISFACTION_VICTOIRE_MAX,
    SATISFACTION_VICTOIRE_DURATION_SEC,
    SATISFACTION_DEFAITE_SEUIL_6MIN,
    SATISFACTION_DEFAITE_SEUIL_20SEC,
    SATISFACTION_DEFAITE_20SEC_DURATION_SEC,
    SATISFACTION_DECAY_INTERVAL_SEC,
    SATISFACTION_DECAY_PERCENT,
)

class GameState:
    def __init__(self):
        self.start_time = time.time()  
        self.satisfaction: float = 100.0 
        self.liste_postes: List[Poste] = []
        self._numero_recette = 0
        
        # ── VARIABLES POUR SERVER.PY ──
        self.game_won: bool = False
        self.game_lost: bool = False
        self.qualite_recette_globale: int = 100
        self.commandes_actives = [] 
        
        poste_froid = Poste("froid")
        poste_froid.ustensiles.append(Centrifugeuse())
        poste_chaud = Poste("chaud")
        poste_chaud.ustensiles.append(PlaqueCuisson())
        self.liste_postes.extend([poste_froid, poste_chaud])
        
        self.j1_en_main = None
        self.j2_en_main = None

        # Timer interne pour suivre si la satisfaction reste dans la fenêtre de victoire
        self._satisfaction_victoire_since = None
        # Timer interne pour suivre si la satisfaction est < 20% de façon continue
        self._satisfaction_below_20_since = None
        # Timer pour la dernière décroissance périodique
        self._last_satisfaction_decay = time.time()

        # ── DRESSAGE 5x5 / RECETTE ──
        self.mini_jeu_dressage = self.generer_nouvelle_recette()
        self.mini_jeu_dressage["reelles"] = []

    def generer_nom_recette(self, ingredients):
        self._numero_recette += 1
        return f"Recette {self._numero_recette}"

    def generer_instructions_recette(self, ingredients):
        instructions = []
        for ing in ingredients:
            if "Jus" in ing:
                base = ing.replace("Jus de ", "")
                instructions.append(f"Tirer le jus de {base}")
            elif "Cuite" in ing:
                instructions.append(f"Cuire la {ing.replace(' Cuite', '').lower()}")
            else:
                instructions.append(f"Ajouter {ing.lower()}")
        return instructions

    def generer_nouvelle_recette(self):
        """Génère 2 ou 3 ingrédients à placer aléatoirement sur une grille 5x5"""
        ingredients_possibles = ["Jus de Tomate", "Jus de Salade", "Viande Cuite", "Tomate Cuite", "Salade"]
        nb_ing = random.randint(2, 3)
        selection = random.sample(ingredients_possibles, nb_ing)
        
        cibles = []
        coords_utilisees = []
        for ing in selection:
            while True:
                pt = [random.randint(0, 4), random.randint(0, 4)]
                if pt not in coords_utilisees:
                    cibles.append({"ing": ing, "pos": pt})
                    coords_utilisees.append(pt)
                    break
        return {
            "nom_recette": self.generer_nom_recette(selection),
            "cibles": cibles,
            "instructions": self.generer_instructions_recette(selection),
        }

    def evaluer_assiette(self):
        cibles = self.mini_jeu_dressage["cibles"].copy()
        reelles = self.mini_jeu_dressage["reelles"]
        
        distances = 0
        cibles_non_trouvees = cibles[:]
        
        for r in reelles:
            # Cherche si l'ingrédient posé correspond à une demande
            match = next((c for c in cibles_non_trouvees if c["ing"] == r["ing"]), None)
            if match:
                # Calcul de la distance de Manhattan
                dist = abs(r["pos"][0] - match["pos"][0]) + abs(r["pos"][1] - match["pos"][1])
                distances += dist
                cibles_non_trouvees.remove(match)
            else:
                distances += 10 # Mauvais ingrédient
                
        distances += len(cibles_non_trouvees) * 10 # Ingrédients manquants
        
        score_plat = max(0, 100 - (distances * 10))
        
        # Ajustement de la satisfaction
        if score_plat >= 50:
            self.satisfaction = min(100.0, self.satisfaction + 20)
        # Si le plat est mal fait (score < 50), la satisfaction ne change pas

        print(f"[SERVEUR] Plat servi ! Score: {score_plat}. Sat: {self.satisfaction}")
        nouvelle = self.generer_nouvelle_recette()
        self.mini_jeu_dressage["cibles"] = nouvelle["cibles"]
        self.mini_jeu_dressage["nom_recette"] = nouvelle["nom_recette"]
        self.mini_jeu_dressage["reelles"] = []

    def apply_action(self, player_id, action):
        if not action or action.get("action") == "get":
            return self.get_snapshot()

        act = action.get("action")
        poste_froid = next((p for p in self.liste_postes if p.nom == "froid"), None)
        poste_chaud = next((p for p in self.liste_postes if p.nom == "chaud"), None)

        # ── POUBELLE (BI-LATÉRALE) ──
        if act == "JETER_POUBELLE":
            joueur = action.get("joueur")
            if joueur == "J1" and self.j1_en_main: self.j1_en_main = None
            elif joueur == "J2" and self.j2_en_main: self.j2_en_main = None

        # ── ACTIONS CHEF FROID (J1) ──
        elif act == "PRENDRE_INGREDIENT" and poste_froid:
            if self.j1_en_main is None:
                self.j1_en_main = action.get("ingredient", "Tomate")
                
        elif act == "ENVOYER_PASSE" and poste_froid and poste_chaud:
            if self.j1_en_main is not None:
                ing = Ingredient(self.j1_en_main)
                poste_chaud.recevoir_ingredient(ing)
                self.j1_en_main = None

        elif act == "INTERACT_CENTRIFUGEUSE" and poste_froid:
            centri = poste_froid.ustensiles[0] if poste_froid.ustensiles else None
            if centri and not getattr(centri, "panne", False):
                etat_actuel = getattr(centri, "etat_simplifie", "libre")
                cycle_en_cours = getattr(centri, "cycle_end", 0) > time.time()
                if etat_actuel == "libre" and self.j1_en_main is not None:
                    centri.etat_simplifie = "occupe"
                    centri.contenu = self.j1_en_main
                    self.j1_en_main = None
                    centri.cycle_end = time.time() + getattr(centri, "temps_de_cycle", lambda: 0)()
                elif etat_actuel == "occupe":
                    if not cycle_en_cours and getattr(centri, "contenu", None) is not None and self.j1_en_main is None:
                        base = centri.contenu
                        self.j1_en_main = base if isinstance(base, str) and base.startswith("Jus") else f"Jus de {base}"
                        centri.etat_simplifie = "libre"
                        centri.contenu = None
                        centri.cycle_end = 0

        elif act == "DECLENCHER_PANNE_DEBUG_FROID":
            centri = poste_froid.ustensiles[0] if poste_froid and poste_froid.ustensiles else None
            if centri:
                centri.panne = True
                centri.qte_seq = [random.choice(["UP", "DOWN", "LEFT", "RIGHT"]) for _ in range(5)]
                centri.qte_index = 0

        elif act == "QTE_INPUT_J1":
            plaque = poste_chaud.ustensiles[0] if poste_chaud and poste_chaud.ustensiles else None
            if plaque and getattr(plaque, "panne", False):
                if action.get("touche") == getattr(plaque, "qte_seq", [])[getattr(plaque, "qte_index", 0)]:
                    plaque.qte_index += 1
                    if plaque.qte_index >= len(plaque.qte_seq):
                        plaque.panne = False
                        plaque.qte_seq = []
                        plaque.qte_index = 0
                        plaque.etat_simplifie = "libre"
                        plaque.installed_at = time.time()
                else: plaque.qte_index = 0
        
        # ── ACTIONS CHEF CHAUD (J2) ──
        elif act == "PRENDRE_PASSE" and poste_chaud:
            if len(poste_chaud.ingredients_disponibles) > 0 and self.j2_en_main is None:
                self.j2_en_main = poste_chaud.ingredients_disponibles.pop(0).nom
                
        elif act == "INTERACTION_PLAQUE" and poste_chaud:
            plaque = poste_chaud.ustensiles[0] if poste_chaud.ustensiles else None
            if plaque and not getattr(plaque, "panne", False):
                etat_actuel = getattr(plaque, "etat_simplifie", "libre")
                if etat_actuel == "libre" and self.j2_en_main is not None:
                    plaque.etat_simplifie = "occupe"
                    plaque.contenu = self.j2_en_main
                    plaque.started_cooking_at = time.time()
                    self.j2_en_main = None
                elif etat_actuel == "occupe":
                    base = getattr(plaque, "contenu", "Truc")
                    started = getattr(plaque, "started_cooking_at", None)
                    elapsed = time.time() - started if started is not None else 0
                    if elapsed <= 10:
                        self.j2_en_main = base
                    elif elapsed > 20:
                        self.j2_en_main = f"{base} Brule"
                    else:
                        self.j2_en_main = base if base.endswith("Cuite") else f"{base} Cuite"
                    plaque.etat_simplifie = "libre"
                    plaque.contenu = None
                    plaque.started_cooking_at = None

        elif act == "DECLENCHER_PANNE_DEBUG_CHAUD":
            plaque = poste_chaud.ustensiles[0] if poste_chaud and poste_chaud.ustensiles else None
            if plaque:
                plaque.panne = True
                plaque.qte_seq = [random.choice(["UP", "DOWN", "LEFT", "RIGHT"]) for _ in range(5)]
                plaque.qte_index = 0

        elif act == "QTE_INPUT_J2":
            centri = poste_froid.ustensiles[0] if poste_froid and poste_froid.ustensiles else None
            if centri and getattr(centri, "panne", False):
                if action.get("touche") == getattr(centri, "qte_seq", [])[getattr(centri, "qte_index", 0)]:
                    centri.qte_index += 1
                    if centri.qte_index >= len(centri.qte_seq):
                        centri.panne = False
                        centri.qte_seq = []
                        centri.qte_index = 0
                        centri.etat_simplifie = "libre"
                        centri.installed_at = time.time()
                else: centri.qte_index = 0

        # ── DRESSAGE INTERACTIF SOURIS ──
        elif act == "DRESSAGE_PLACEMENT_SOURIS":
            pos = action.get("position")
            reelles = self.mini_jeu_dressage["reelles"]
            item_here = next((item for item in reelles if item["pos"] == pos), None)

            if self.j2_en_main and not item_here:
                reelles.append({"pos": pos, "ing": self.j2_en_main})
                self.j2_en_main = None
            elif not self.j2_en_main and item_here:
                self.j2_en_main = item_here["ing"]
                reelles.remove(item_here)

            if len(reelles) == len(self.mini_jeu_dressage["cibles"]):
                self.evaluer_assiette()

        return self.get_snapshot()

    def serialiser_pour_client(self) -> Dict[str, object]:
        poste_froid = next((p for p in self.liste_postes if p.nom == "froid"), None)
        poste_chaud = next((p for p in self.liste_postes if p.nom == "chaud"), None)
        centri = poste_froid.ustensiles[0] if poste_froid else None
        plaque = poste_chaud.ustensiles[0] if poste_chaud else None
        
        return {
            "timer_global": int(time.time() - self.start_time),
            "satisfaction": self.satisfaction,
            "j1_en_main": self.j1_en_main,
            "j2_en_main": self.j2_en_main,
            "mini_jeu_dressage": self.mini_jeu_dressage,
            "ustensiles": {
                "centrifugeuse": {
                    "etat": "en_panne" if getattr(centri, "panne", False) else getattr(centri, "etat_simplifie", "libre"),
                    "qte_seq": getattr(centri, "qte_seq", []), "qte_index": getattr(centri, "qte_index", 0), "contenu": getattr(centri, "contenu", None)
                },
                "plaque_chauffante": {
                    "etat": "en_panne" if getattr(plaque, "panne", False) else getattr(plaque, "etat_simplifie", "libre"),
                    "qte_seq": getattr(plaque, "qte_seq", []), "qte_index": getattr(plaque, "qte_index", 0), "contenu": getattr(plaque, "contenu", None)
                }
            },
            "liste_postes": [{"nom": p.nom, "ingredients": [i.nom for i in p.ingredients_disponibles]} for p in self.liste_postes]
        }

    def get_snapshot(self) -> Dict[str, object]:
        snap = self.serialiser_pour_client()
        snap["game_won"] = self.game_won
        snap["game_lost"] = self.game_lost
        return snap

    # ── MÉTHODES ATTENDUES PAR LE SERVER.PY ──
    def update(self) -> None:
        # Applique la décroissance périodique de la satisfaction, puis vérifie
        # si la satisfaction reste continuellement dans l'intervalle requis
        now = time.time()

        # Décroissance périodique
        if now - self._last_satisfaction_decay >= SATISFACTION_DECAY_INTERVAL_SEC:
            old = self.satisfaction
            self.satisfaction = max(0.0, self.satisfaction * (1.0 - SATISFACTION_DECAY_PERCENT / 100.0))
            self._last_satisfaction_decay = now
            print(f"[SERVEUR] Satisfaction decayed from {old:.1f}% to {self.satisfaction:.1f}%")
            

        # Défaite si la satisfaction reste inférieure à 20% pendant 20 secondes
        if self.satisfaction < SATISFACTION_DEFAITE_SEUIL_20SEC:
            if self._satisfaction_below_20_since is None:
                self._satisfaction_below_20_since = now
            elif now - self._satisfaction_below_20_since >= SATISFACTION_DEFAITE_20SEC_DURATION_SEC:
                self.game_lost = True
                print(f"[SERVEUR] Défaite: satisfaction < {SATISFACTION_DEFAITE_SEUIL_20SEC}% pendant {SATISFACTION_DEFAITE_20SEC_DURATION_SEC}s")
                return 
        else:
            self._satisfaction_below_20_since = None

        # Défaite si, au bout de 6 minutes, la satisfaction est en dessous de 60%
        if now - self.start_time >= SATISFACTION_VICTOIRE_DURATION_SEC:
            if self.satisfaction < SATISFACTION_DEFAITE_SEUIL_6MIN:
                self.game_lost = True
                print(f"[SERVEUR] Défaite: au bout de 6 minutes, satisfaction {self.satisfaction:.1f}% < {SATISFACTION_DEFAITE_SEUIL_6MIN}%")
                return

        if SATISFACTION_VICTOIRE_MIN <= self.satisfaction <= SATISFACTION_VICTOIRE_MAX:
            if self._satisfaction_victoire_since is None:
                self._satisfaction_victoire_since = now
            else:
                elapsed = now - self._satisfaction_victoire_since
                if elapsed >= SATISFACTION_VICTOIRE_DURATION_SEC:
                    self.game_won = True
                    print(f"[SERVEUR] Victoire: satisfaction maintenue {elapsed:.0f}s (>= {SATISFACTION_VICTOIRE_DURATION_SEC}s)")
        else:
            # Si la satisfaction sort de la fenêtre, on réinitialise le compteur
            if self._satisfaction_victoire_since is not None:
                self._satisfaction_victoire_since = None

        # ── USURE AUTOMATIQUE DES USTENSILES (après 60s ils peuvent tomber en panne)
        try:
            poste_froid = next((p for p in self.liste_postes if p.nom == "froid"), None)
            poste_chaud = next((p for p in self.liste_postes if p.nom == "chaud"), None)
            centri = poste_froid.ustensiles[0] if poste_froid and poste_froid.ustensiles else None
            plaque = poste_chaud.ustensiles[0] if poste_chaud and poste_chaud.ustensiles else None
            for ust in (centri, plaque):
                if ust and not getattr(ust, "panne", False):
                    # usure automatique après 60 secondes d'installation
                    if time.time() - getattr(ust, "installed_at", 0) >= 60:
                        ust.panne = True
                        # génère une séquence de réparation compatible avec l'UI existante
                        ust.qte_seq = [random.choice(["UP", "DOWN", "LEFT", "RIGHT"]) for _ in range(4)]
                        ust.qte_index = 0
                        ust.etat_simplifie = "en_panne"
                        print(f"[SERVEUR] Ustensile '{ust.nom}' est tombé en panne (usure automatique).")
        except Exception:
            pass