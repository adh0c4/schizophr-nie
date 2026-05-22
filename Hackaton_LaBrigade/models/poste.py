from typing import List, Optional

from models.ustensile import Ustensile
from models.ingredients import Ingredient

class Poste: # Chef Chaud et Chef Froid 
    def __init__(self, nom: str):
        self.nom: str = nom
        self.ustensiles: List[Ustensile] = []
        self.ingredients_disponibles: List[Ingredient] = []
        self.joueur_assigne: Optional[str] = None

    def recevoir_ingredient(self, ingredient: Ingredient) -> None:
        self.ingredients_disponibles.append(ingredient)

    def envoyer_passage(self, ingredient: Ingredient) -> None: # Envoie l'ingrédient préparé au poste 
        # suivant
        if ingredient in self.ingredients_disponibles:
            self.ingredients_disponibles.remove(ingredient)

    def get_ustensile(self, nom: str) -> Optional[Ustensile]:
        return next((u for u in self.ustensiles if u.nom == nom), None)
