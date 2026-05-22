
from typing import Optional
from models.ingredients import Ingredient
from shared.constantes import EtatIngredient, StatutCommande # importe les class d'enumeration pour les etats et status

class Commande:
    def __init__(self, numero_table: int, plat_attendu: str):
        self.numero_table: int = numero_table
        self.plat_attendu: str = plat_attendu
        # Défini le statut de la commande par rapport a une class d'enumeration 
        self.statut: StatutCommande = StatutCommande.EN_ATTENTE 
        self.timer_service: int = 0

    def accepter(self) -> None: # accepte la commande et change son statut pour dire que la commande est en cours
        self.statut = StatutCommande.EN_COURS

    def refuser(self) -> None: # refuse la commande et change son statut
        self.statut = StatutCommande.REFUSEE

    def calculer_retard(self) -> int:
        return max(0, self.timer_service - 10) # Donne-moi le temps de retard, mais si le résultat est négatif, donne-moi 0
        # Si le temps de service est de 15, le retard sera de 5
