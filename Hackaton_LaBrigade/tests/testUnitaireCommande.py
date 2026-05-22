
import unittest
from models.commande import *

class TestCommandes(unittest.TestCase):
    
    def setUp(self):
        self.test = Commande(numero_table=1, plat_attendu="plat1")

    def test_statut(self):
        self.assertEqual(self.test.statut, StatutCommande.EN_ATTENTE)
    
    def test_statut_accept(self):
        self.test.accepter()
        self.assertEqual(self.test.statut, StatutCommande.EN_COURS)
        self.test.refuser()
        self.assertEqual(self.test.statut, StatutCommande.REFUSEE)

    def test_calculer_retard(self):
        #En retard
        self.test.timer_service = 12
        self.assertEqual(self.test.calculer_retard(), 2)
        #Dans les temps
        self.test.timer_service = 9
        self.assertEqual(self.test.calculer_retard(), 0)

    def test_objet(self):
        self.assertEqual(self.test.numero_table, 1)
        self.assertEqual(self.test.plat_attendu, "plat1")


if __name__ == '__main__':
    unittest.main()