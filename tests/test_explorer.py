"""Search contracts and actual Streamlit search-to-comparison journeys."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from cece.data_access import load_foods, search_foods

APP = Path(__file__).resolve().parents[1] / "app.py"


class SearchTests(unittest.TestCase):
    def test_literal_partial_case_insensitive_and_multiword(self):
        foods = load_foods()
        self.assertEqual(set(search_foods(foods, "TOF").fdc_id), set(search_foods(foods, "tof").fdc_id))
        self.assertIn(172421, search_foods(foods, "cooked lentils").fdc_id.tolist())
        self.assertIn(578760, search_foods(foods, "qUaKeR").fdc_id.tolist())
        self.assertEqual(len(search_foods(foods, "  ")), len(foods))
        self.assertTrue(search_foods(foods, "[.*]").empty)
        self.assertTrue(search_foods(foods, "unavailable-food").empty)


class ExplorerJourneyTests(unittest.TestCase):
    def test_suggestions_selection_portion_and_comparison(self):
        app = AppTest.from_file(str(APP)).run()
        app.button(key="suggest_cooked lentils").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.text_input(key="food_query").value, "cooked lentils")
        self.assertEqual(len(app.metric), 0)
        app.button(key="view_usda-172421").click().run()
        self.assertEqual(app.metric[0].value, "116.0 kcal")
        app.number_input(key="portion_usda-172421").set_value(150.0).run()
        self.assertEqual(app.metric[0].value, "174.0 kcal")
        app.text_input(key="food_query").set_value("tofu").run()
        app.button(key="view_usda-1118973").click().run()
        self.assertEqual(app.metric[4].value, "Unknown")
        self.assertTrue(any("1118973" in block.value and "Original record" in block.value for block in app.markdown))
        app.session_state['compare_foods'] = ["usda-172421", "usda-1118973", "usda-578760"]
        app.run()
        app.radio(key='explorer_view').set_value('Compare Foods').run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.get("plotly_chart")), 1)
        self.assertEqual(len(app.session_state["compare_foods"]), 3)
        app.radio(key="comparison_basis").set_value("My portions").run()
        app.number_input(key="compare_portion_usda-172421").set_value(150.0).run()
        table = app.dataframe[0].value
        self.assertAlmostEqual(table.iloc[0]["Calories"], 174)
        self.assertTrue(table.iloc[1]["Fiber"] != table.iloc[1]["Fiber"])
        self.assertEqual(len(app.exception), 0)

    def test_empty_no_match_and_filter(self):
        app = AppTest.from_file(str(APP)).run()
        app.button(key="nav_Food Explorer").click().run()
        self.assertEqual(len([b for b in app.button if str(b.key).startswith("view_")]), 36)
        app.selectbox(key="food_type").set_value("Branded products").run()
        self.assertEqual(len([b for b in app.button if str(b.key).startswith("view_")]), 6)
        app.text_input(key="food_query").set_value("unavailable-food").run()
        self.assertIn("No matching foods", app.info[0].value)
        self.assertEqual(len(app.metric), 0)
        self.assertEqual(len(app.exception), 0)
