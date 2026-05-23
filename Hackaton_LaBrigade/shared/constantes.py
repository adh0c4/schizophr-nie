from enum import Enum

class EtatIngredient(Enum):
    BRUT = "Brut"
    PREPARE = "Prepare"
    DEGRADE = "Degrade"
    GACHE = "Gache"


class StatutCommande(Enum):
    EN_ATTENTE = "En attente"
    EN_COURS = "En cours"
    PRETE = "Prete"
    REFUSEE = "Refusee"

class EtatUstensile(Enum):
    EN_CYCLE = "En cycle"
    EN_PANNE = "En panne"
    LIBRE = "Libre"
    OCCUPE = "Occupe"

    CATALOGUE_MOTIFS = [
    # Motif 1 : En diagonale
    {
        "tomate": (0, 0),
        "gel_citron": (1, 1),
        "emulsion": (2, 2),
        "sphère_algue": (3, 3),
        "fleur_comestible": (4, 4)
    },
    # Motif 2 : En croix / constellation centrée
    {
        "tomate": (2, 0),
        "gel_citron": (0, 2),
        "emulsion": (2, 2),
        "sphère_algue": (4, 2),
        "fleur_comestible": (2, 4)
    },
    # Motif 3 : En cercle / carré périphérique
    {
        "tomate": (1, 1),
        "gel_citron": (3, 1),
        "emulsion": (2, 2),
        "sphère_algue": (1, 3),
        "fleur_comestible": (3, 3)
    }
]
    
# Étape à partir de laquelle une panne peut se déclencher
ETAPE_DECLENCHEMENT_PANNE = 4

# Liste des actions possibles pour la séquence de réparation
ACTIONS_REPARATION = ["HAUT", "BAS", "GAUCHE", "DROITE"]

# Longueur de la séquence de touches requise pour réparer
LONGUEUR_SEQUENCE_REPARATION = 4

# Durabilité maximale d'un ustensile neuf
DURABILITE_MAX = 100.0

# Vitesse d'usure (combien de durabilité on perd par tick serveur quand la machine tourne)
USURE_PAR_TICK_CENTRIFUGEUSE = 0.5  # S'use lentement mais fait des longs cycles
USURE_PAR_TICK_PLAQUE = 1.0         # S'use plus vite quand on l'allume

# Conditions de victoire basées sur la satisfaction
SATISFACTION_VICTOIRE_MIN = 60.0
SATISFACTION_VICTOIRE_MAX = 100.0
SATISFACTION_VICTOIRE_DURATION_SEC = 6 * 60  # 6 minutes

# Conditions de défaite basées sur la satisfaction
SATISFACTION_DEFAITE_SEUIL_6MIN = 60.0
SATISFACTION_DEFAITE_SEUIL_20SEC = 20.0
SATISFACTION_DEFAITE_20SEC_DURATION_SEC = 20

# Décroissance périodique de la satisfaction
SATISFACTION_DECAY_INTERVAL_SEC = 20  # toutes les 20 secondes
SATISFACTION_DECAY_PERCENT = 10.0     # baisse de 10% à chaque intervalle