
import unittest
from models.ustensile import *
from models.ingredients import *

class TestUstensile(unittest.TestCase):
    def setUp(self):
        self.ustensile = Centrifugeuse()

    def test_etat(self):
        self.ustensile.tomber_en_panne()
        self.assertTrue(self.ustensile.est_en_panne())
        self.ustensile.reparer_panne()
        self.assertFalse(self.ustensile.est_en_panne())

    def test_etat_alliment_panne(self):
        self.ustensile.tomber_en_panne()
        ingredient = Ingredient("nom")
        self.ustensile.cycle_interrompu(ingredient)
        self.assertEqual(ingredient.etat, EtatIngredient.GACHE)
    
    def test_objet(self):
        test = Ustensile("test")
        self.assertEqual(test.nom, "test")


if __name__ == '__main__':
    unittest.main()