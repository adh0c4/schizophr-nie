from typing import List
from models.ingredients import Ingredient

class Recette:
    def __init__(self):
        self.etapes: List[str] = []
        self.etape_courante: int = 0
        self.ordre_aleatoire: bool = False
        self.score_qualite: int = 0

    def etape_suivante(self) -> None:
        if self.etape_courante < len(self.etapes) - 1:
            self.etape_courante += 1

    def valider_passage(self, ingredient: Ingredient) -> None:
        if ingredient.est_pret():
            self.score_qualite += 10

    def calculer_score(self) -> int:
        return self.score_qualite

###########