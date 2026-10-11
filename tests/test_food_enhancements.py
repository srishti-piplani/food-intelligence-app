"""Milestone 3.1 labels, source nutrition, licensed images and comparisons."""

import json
import unittest
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from cece.charts import bar_chart
from cece.data_access import DATA_DIR, DETAIL_NUTRIENTS, load_foods, normalize_record, validate_foods
from cece.food_labels import short_name, preparation_state, comparison_labels
from cece.imagery import image_metadata
from cece.nutrition import calculate_portion, protein_per_100_kcal


class LabelTests(unittest.TestCase):
    def test_short_names_keep_variants(self):
        cases = {"Edamame, frozen, prepared": "Edamame", "Quinoa, cooked": "Cooked quinoa", "Cereals, oats, regular and quick, not fortified, dry": "Dry oats", "Tofu, firm, prepared with calcium sulfate": "Firm tofu", "Tofu": "Tofu"}
        for source, expected in cases.items():
            self.assertEqual(short_name(source), expected)

    def test_preparation_is_source_supported(self):
        self.assertEqual(preparation_state("Edamame, frozen, unprepared"), "frozen, unprepared")
        self.assertEqual(preparation_state("Edamame, frozen, prepared"), "frozen, prepared")
        self.assertEqual(preparation_state("Tofu, prepared with calcium sulfate"), "Not specified")
        self.assertEqual(preparation_state("Quinoa, cooked"), "cooked")
        self.assertEqual(preparation_state("Oats"), "Not specified")

    def test_duplicate_names_are_distinguishable(self):
        foods = load_foods().to_dict("records")
        labels = comparison_labels(foods)
        self.assertEqual(len(labels), len(set(labels.values())))
        self.assertNotEqual(labels['usda-168410'], labels['usda-168411'])
        first = {**foods[0], 'food_id': 'a', 'fdc_id': 1, 'description': 'Edamame', 'brand': 'Same brand', 'data_type': 'Branded'}
        second = {**first, 'food_id': 'b', 'fdc_id': 2}
        self.assertNotEqual(comparison_labels([first, second])['a'], comparison_labels([first, second])['b'])


class DetailNutrientTests(unittest.TestCase):
    def test_extract_exact_units_and_missing_added_sugars(self):
        foods = load_foods()
        self.assertTrue(foods.added_sugars_g.isna().all())
        self.assertTrue(foods.added_sugars_g_missing.all())
        for food in foods.to_dict('records'):
            source = json.loads((DATA_DIR / food['raw_record']).read_text())
            for name, (nutrient_id, unit, _) in DETAIL_NUTRIENTS.items():
                matches = [n for n in source['foodNutrients'] if n['nutrient']['id'] == nutrient_id]
                if matches:
                    self.assertEqual(matches[0]['nutrient']['unitName'].casefold(), unit)
                    self.assertEqual(food[name], matches[0]['amount'])
                else:
                    self.assertTrue(pd.isna(food[name]))
                    self.assertTrue(food[name + '_missing'])

    def test_sodium_units_and_portion_scaling(self):
        food = load_foods().query('fdc_id == 172421').iloc[0].to_dict()
        source = json.loads((DATA_DIR / food['raw_record']).read_text())
        portion = calculate_portion(food, 150)
        self.assertAlmostEqual(portion['sodium_mg'], food['sodium_mg'] * 1.5)
        self.assertIsNone(portion['added_sugars_g'])
        for nutrient in source['foodNutrients']:
            if nutrient['nutrient']['id'] == 1093:
                nutrient['nutrient']['unitName'] = 'g'
        with self.assertRaises(ValueError):
            normalize_record(source, food['source_archive'])
        frame = load_foods()
        frame.loc[0, 'sodium_mg'] = -1
        with self.assertRaises(ValueError):
            validate_foods(frame)

    def test_protein_density_undefined_values(self):
        food = load_foods().query('fdc_id == 172421').iloc[0].to_dict()
        self.assertAlmostEqual(protein_per_100_kcal(food), 9.02 / 116 * 100)
        for value in (None, 0, -1, float('nan'), float('inf')):
            self.assertIsNone(protein_per_100_kcal({**food, 'calories_kcal': value}))
        self.assertIsNone(protein_per_100_kcal({**food, 'protein_g': None}))
        self.assertEqual(protein_per_100_kcal({**food, 'protein_g': 0}), 0)

    def test_chart_missing_values_units_and_font(self):
        frame = pd.DataFrame({'Food': ['Known', 'Unknown'], 'Protein': [2.5, None]})
        fig = bar_chart(frame, 'Food', 'Protein', 'Protein per 100 kcal', 'g / 100 kcal', {'Known': '#E76F57', 'Unknown': '#68927A'})
        self.assertEqual(sum(len(trace.y) for trace in fig.data), 1)
        self.assertEqual(fig.layout.font.family, 'Arial, sans-serif')
        self.assertEqual(fig.layout.yaxis.title.text, 'g / 100 kcal')


class ImageTests(unittest.TestCase):
    def test_all_images_local_licensed_and_products_are_placeholders(self):
        for food in load_foods().to_dict('records'):
            metadata = image_metadata(food)
            self.assertTrue(Path(metadata['absolute_path']).is_file())
            self.assertIn(metadata['license'], ['CC0-1.0', 'Pexels License', 'CC BY-SA 3.0', 'CC BY-SA 4.0'])
            self.assertFalse(metadata['product_image'])
            if food['data_type'] == 'Branded':
                self.assertEqual(metadata['key'], 'product-placeholder')
            else:
                self.assertNotEqual(metadata['key'], 'product-placeholder')

    def test_ui_density_and_named_controls(self):
        app = AppTest.from_file(str(DATA_DIR.parent / 'app.py')).run()
        app.button(key='suggest_cooked lentils').click().run()
        self.assertEqual(len(app.metric), 0)
        app.button(key='view_usda-172421').click().run()
        self.assertIn('Cooked lentils', app.number_input(key='portion_usda-172421').label)
        self.assertEqual(len(app.metric), 5)
        self.assertEqual(len(app.table[0].value), 6)
        app.session_state['compare_foods'] = ['usda-173904', 'usda-173905']
        app.run()
        app.radio(key='explorer_view').set_value('Compare Foods').run()
        self.assertTrue(any('different preparation states' in entry.value for entry in app.info))
        app.checkbox(key='protein_density').set_value(True).run()
        self.assertEqual(len(app.get('plotly_chart')), 1)
        app.radio(key='comparison_basis').set_value('My portions').run()
        self.assertIn('Dry oats', app.number_input(key='compare_portion_usda-173904').label)
        self.assertEqual(len(app.exception), 0)
