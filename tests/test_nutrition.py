"""Portion behavior verified against a saved USDA cooked lentil record."""

import unittest

from cece.data_access import NUTRIENTS, load_foods
from cece.nutrition import calculate_portion


class PortionTests(unittest.TestCase):
    def setUp(self):
        self.food = load_foods().query("fdc_id == 172421").iloc[0].to_dict()

    def test_known_lentil_values_and_scaling(self):
        # USDA SR Legacy 172421: 116 kcal and 9.02 g protein per 100 g.
        portion = calculate_portion(self.food, 150)
        self.assertAlmostEqual(portion["calories_kcal"], 174)
        self.assertAlmostEqual(portion["protein_g"], 13.53)
        self.assertEqual(calculate_portion(self.food, 100)["fiber_g"], self.food["fiber_g"])
        self.assertEqual(calculate_portion(self.food, 0)["calories_kcal"], 0)

    def test_missing_stays_missing_even_at_zero_portion(self):
        for missing in (None, float("nan")):
            self.food["fiber_g"] = missing
            for grams in (0, 150):
                result = calculate_portion(self.food, grams)
                self.assertIsNone(result["fiber_g"])
                self.assertTrue(result["fiber_g_missing"])

    def test_invalid_portions(self):
        for grams in (-1, float("inf"), float("nan"), "100", True):
            with self.assertRaises(ValueError):
                calculate_portion(self.food, grams)
        self.food["basis_g"] = 1
        with self.assertRaises(ValueError):
            calculate_portion(self.food, 100)
