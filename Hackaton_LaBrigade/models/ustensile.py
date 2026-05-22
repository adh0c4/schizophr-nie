from typing import TYPE_CHECKING
from shared.constantes import EtatIngredient
from shared.constantes import EtatUstensile

# Permet, lors de du lancement du code, de vérifier si le module "poste" est importé
# pour éviter les problèmes de dépendances circulaires.
if TYPE_CHECKING:
    from models.poste import Poste
# Nous a permit de regler des problèmes d'importation circulaire entre "poste" et "ustensile"

from models.ingredients import Ingredient
import time

class Ustensile:
    def __init__(self, nom: str):
        self.nom: str = nom
        self.etat: EtatIngredient = EtatIngredient.BRUT
        self.timer_cycle: int = 0
        self.temps_cycle_total: int = 0
        # Timestamp de création/installation de l'ustensile
        self.installed_at: float = time.time()
        # Flag indiquant si l'ustensile est en panne (réparé via séquence existante)
        self.panne: bool = False

    def demarrer_cycle(self) -> None:
        self.timer_cycle = 0
        self.etat = EtatIngredient.PREPARE

    def arreter_cycle(self) -> None:
        self.etat = EtatIngredient.BRUT

    def tomber_en_panne(self) -> None:
        self.etat = EtatIngredient.GACHE

    def reparer(self) -> None:
        self.etat = EtatIngredient.BRUT
        self.timer_cycle = 0

# la classe Centrifugeuse hérite de la classe Ustensile, elle a des méthodes spécifiques pour gérer son cycle de transformation et les pannes éventuelles.
class Centrifugeuse(Ustensile):
    def __init__(self):
        super().__init__("centrifugeuse") # appelle le constructeur de la classe parente 
        # pour initialiser le nom de l'ustensile

    def temps_de_cycle(self) -> int:
        return 10 # temps de cycle de 10 secondes

# La centrifugeuse peut tomber en panne pendant un cycle, ce qui interrompt le cycle et gâche l'ingrédient 
# en cours de transformation, mais cela prend du temps et empêche son utilisation pendant la réparation.

    def tomber_en_panne(self) -> None:
        self.etat = EtatUstensile.EN_PANNE
        self.panne = True

    def est_en_panne(self) -> bool:
        if self.panne == True:
            return True
        return False
# Si elle tombe en panne pendant un cycle, le cycle est interrompu et l'ingrédient en cours de transformation est gâché.

    def cycle_interrompu(self, ingredient: Ingredient) -> None:
        ingredient.etat = EtatIngredient.GACHE
        
    def reparer_panne(self):
        self.panne = False
        self.timer_cycle = 0

# le principe de fonctionnement de la centrifugeuse est le suivant :
# - lorsqu'on l'utilise, elle prend un ingrédient disponible sur le poste si il y en a un elle démarre un cycle de transformation,  si il y en a pas, elle ne fait rien
# - pendant le cycle, la centrifugeuse est occupée et ne peut pas être utilisée à nouveau
# - si le cycle arrive à son terme, l'ingrédient est transformé (état préparé)
# - si le cycle est interrompu avant son terme, l'ingrédient est gâché (état gâché)

    def utiliser(self, poste: "Poste") -> None:
        if len(poste.ingredients_disponibles) == 0 or self.etat == EtatUstensile.EN_PANNE:
            return  # si la centrifugeuse est en panne ou pas utilisé, elle ne fait rien
        
        else:
            ingredient = poste.ingredients_disponibles[0]  # prend le premier ingrédient
            poste.envoyer_passage(ingredient)
            self.demarrer_cycle()
            self.etat = EtatUstensile.EN_CYCLE
            self.timer_cycle = 0
            self.temps_cycle_total = self.temps_de_cycle()
            
            if self.timer_cycle == self.temps_de_cycle():
                ingredient.preparer()  # transforme l'ingrédient en jus
                poste.ingredients_disponibles.remove(ingredient)  # retire l'ingrédient du poste
                ingredient.etat = EtatIngredient.PREPARE
                poste.ingredients_disponibles.append(ingredient)  # ajoute l'ingrédient transformé au poste
                self.arreter_cycle()  # arrête le cycle de la centrifugeuse
            elif self.timer_cycle > self.temps_de_cycle():
                self.cycle_interrompu(ingredient)  # cycle interrompu, ingrédient gâché
                self.arreter_cycle()  # arrête le cycle de la centrifugeuse


class PlaqueCuisson(Ustensile):
    def __init__(self):
        super().__init__("Plaque de cuisson")

    def temps_de_cycle(self) -> int:
        return 90

    def tomber_en_panne(self) -> None:
        self.etat = EtatUstensile.EN_PANNE
        self.panne = True

    def est_en_panne(self) -> bool:
        if self.panne == True:
            return True
        return False

    def cycle_interrompu(self, ingredient: Ingredient) -> None:
        ingredient.etat = EtatIngredient.GACHE
        
    def reparer_panne(self):
        self.panne = False
        self.timer_cycle = 0

    def utiliser(self, poste: "Poste") -> None:
        if len(poste.ingredients_disponibles) == 0 or self.etat == EtatUstensile.EN_PANNE:
            return  
        else:
            ingredient = poste.ingredients_disponibles[0] 
            poste.envoyer_passage(ingredient)
            self.demarrer_cycle()
            self.etat = EtatUstensile.EN_CYCLE
            self.timer_cycle = 0
            self.temps_cycle_total = self.temps_de_cycle()
            if self.timer_cycle == self.temps_de_cycle():
                ingredient.preparer() 
                poste.ingredients_disponibles.remove(ingredient) 
                ingredient.etat = EtatIngredient.PREPARE
                poste.ingredients_disponibles.append(ingredient)  
                self.arreter_cycle()  
            elif self.timer_cycle > self.temps_de_cycle():
                self.cycle_interrompu(ingredient)  
                self.arreter_cycle() 
                self.etat = EtatIngredient.DEGRADE
