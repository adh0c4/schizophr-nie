
from shared.constantes import EtatIngredient
from shared.constantes import StatutCommande
import time

class Ingredient: # Attributs communs à tous les ingrédients
    ph: float = 7.0
    temperature: float = 20.0
    etat: EtatIngredient = EtatIngredient.BRUT
    perissable: bool = False
    timer_degradation: int = 0

    def __init__(self, nom): # Attribut spécifique à chaque ingrédient
        self.nom = nom


# ----- Methétodes changeant l'état de l'ingrédient -----
    def preparer(self) -> None:
        self.etat = EtatIngredient.PREPARE

    def degrader(self) -> None:
        self.etat = EtatIngredient.DEGRADE
        self.timer_degradation += 1

    def est_pret(self) -> bool:
        return self.etat == EtatIngredient.PREPARE
#---------------------------------------------------------


class Perime: # Fonctionnalité perissable pour les ingrédients

    def perissable(self):
        Ingredient.perissable = True

    def demarrer_peremption(self): # Si l'ingredient est périssable, on démarre un timer de dégradation
        if EtatIngredient == EtatIngredient.BRUT and Ingredient.perissable:
            time.sleep(45)
            EtatIngredient = EtatIngredient.GACHE

