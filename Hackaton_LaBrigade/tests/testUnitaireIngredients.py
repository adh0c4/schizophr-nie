
import unittest
from models.ingredients import *

class TestIngredients(unittest.TestCase):

    def test_etat(self):
        #Brut
        test = Ingredient
        self.assertEqual(test.etat, EtatIngredient.BRUT)

    def test_etat_prepare(self):
        #Prepare
        test = Ingredient.preparer(self)
        self.assertEqual(self.etat, EtatIngredient.PREPARE)

    def test_perissable(self):
        test = Perime()
        test.perissable()
        self.assertTrue(Ingredient.perissable)


if __name__ == '__main__':
    unittest.main()