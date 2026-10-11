"""Milestone 3.2 explicit-selection, photo, and comparison acceptance checks."""

import hashlib
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest

from cece.data_access import load_foods
from cece.explorer_state import submit_search, select_food, clear_selection
from cece.imagery import image_metadata, PHOTOS, ROOT

APP = ROOT / 'app.py'


class SelectionTests(unittest.TestCase):
    def test_state_transitions_preserve_comparisons(self):
        state = {'compare_foods': ['usda-172421']}
        select_food(state, 'usda-170894')
        submit_search(state, ' tofu ')
        self.assertNotIn('selected_food', state)
        self.assertEqual(state['search_query'], 'tofu')
        self.assertEqual(state['compare_foods'], ['usda-172421'])
        select_food(state, 'usda-172448')
        clear_selection(state)
        self.assertNotIn('selected_food', state)

    def test_greek_yogurt_journey_close_switch_and_clear(self):
        app = AppTest.from_file(str(APP)).run()
        self.assertEqual(len(app.metric), 0)
        app.button(key='suggest_Greek yogurt').click().run()
        self.assertEqual(len(app.metric), 0)
        self.assertTrue(any('Choose a food' in block.value for block in app.markdown))
        app.button(key='view_usda-170894').click().run()
        self.assertEqual(app.session_state['selected_food'], 'usda-170894')
        self.assertEqual(app.button(key='view_usda-170894').label, 'Selected ✓')
        self.assertTrue(any(block.value == 'Nutrition Breakdown' for block in app.subheader))
        app.number_input(key='portion_usda-170894').set_value(150.0).run()
        source = load_foods().query('fdc_id == 170894').iloc[0]
        self.assertEqual(app.metric[0].value, f'{source.calories_kcal * 1.5:,.1f} kcal')
        self.assertTrue(any('170894' in block.value and 'Original record' in block.value for block in app.markdown))
        app.button(key='close_nutrition').click().run()
        self.assertEqual(len(app.metric), 0)
        app.button(key='view_usda-171304').click().run()
        self.assertEqual(app.session_state['selected_food'], 'usda-171304')
        app.text_input(key='food_query').set_value('chickpeas').run()
        self.assertEqual(len(app.metric), 0)
        app.button(key='view_usda-173757').click().run()
        next(button for button in app.button if button.label == 'Search').click().run()
        self.assertEqual(len(app.metric), 0)
        self.assertEqual(len(app.exception), 0)

    def test_filter_clears_hidden_selection_and_query_survives_navigation(self):
        app = AppTest.from_file(str(APP)).run()
        app.button(key='suggest_tofu').click().run()
        app.button(key='view_usda-172448').click().run()
        app.selectbox(key='food_type').set_value('Branded products').run()
        self.assertEqual(len(app.metric), 0)
        app.button(key="nav_Pantry").click().run()
        app.button(key="nav_Food Explorer").click().run()
        self.assertEqual(app.text_input(key='food_query').value, 'tofu')
        self.assertEqual(len(app.exception), 0)

    def test_comparison_requires_two_and_supports_add_remove(self):
        app = AppTest.from_file(str(APP)).run()
        app.button(key='suggest_cooked lentils').click().run()
        app.session_state['compare_foods'] = ['usda-172421']
        app.run()
        app.radio(key='explorer_view').set_value('Compare Foods').run()
        self.assertEqual(len(app.get('plotly_chart')), 0)
        app.radio(key='explorer_view').set_value('Explore Foods').run()
        app.button(key='view_usda-172421').click().run()
        self.assertEqual(app.button(key='add_compare_usda-172421').label, 'Added to comparison ✓')
        self.assertTrue(app.button(key='add_compare_usda-172421').disabled)
        self.assertEqual(len(app.session_state['compare_foods']), 1)
        app.text_input(key='food_query').set_value('tofu').run()
        app.button(key='view_usda-1118973').click().run()
        self.assertEqual(app.metric[4].value, 'Unknown')
        app.button(key='add_compare_usda-1118973').click().run()
        app.radio(key='explorer_view').set_value('Compare Foods').run()
        self.assertEqual(len(app.get('plotly_chart')), 1)
        app.radio(key='comparison_basis').set_value('My portions').run()
        app.number_input(key='compare_portion_usda-172421').set_value(150.0).run()
        self.assertEqual(app.dataframe[0].value.iloc[0]['Calories'], 174)
        app.session_state['compare_foods'] = ['usda-172421']
        app.run()
        app.radio(key='explorer_view').set_value('Compare Foods').run()
        self.assertEqual(len(app.get('plotly_chart')), 0)
        self.assertEqual(len(app.exception), 0)


class PhotoTests(unittest.TestCase):
    def test_reviewed_photos_checksums_dimensions_and_mappings(self):
        self.assertEqual(len(PHOTOS['photos']), 8)
        ids = set(load_foods().food_id)
        for food_id, photo_key in PHOTOS['food_mappings'].items():
            self.assertIn(food_id, ids)
            self.assertIn(photo_key, PHOTOS['photos'])
        for photo in PHOTOS['photos'].values():
            for field in ('creator', 'source', 'attribution_url', 'license', 'license_url', 'review_note', 'changes'):
                self.assertTrue(photo[field])
            self.assertFalse(photo['product_image'])
            for field, checksum, size in [('path', 'sha256', (720,480)), ('thumbnail_path', 'thumbnail_sha256', (240,160))]:
                path = ROOT / photo[field]
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), photo[checksum])
                with Image.open(path) as image:
                    self.assertEqual(image.size, size)
                    self.assertEqual(image.format, 'WEBP')

    def test_missing_file_unknown_mapping_and_branded_fallback(self):
        food = load_foods().query('fdc_id == 170894').iloc[0].to_dict()
        self.assertEqual(image_metadata(food)['kind'], 'photograph')
        catalog = {'food_mappings': {food['food_id']: 'missing'}, 'photos': {'missing': {'path': 'assets/nonexistent.webp'}}}
        with patch('cece.imagery.PHOTOS', catalog):
            self.assertEqual(image_metadata(food)['kind'], 'illustration')
        with patch('cece.imagery.PHOTOS', {'food_mappings': {}, 'photos': {}}):
            self.assertEqual(image_metadata(food)['kind'], 'illustration')
        branded = load_foods().query('fdc_id == 1851216').iloc[0].to_dict()
        self.assertEqual(image_metadata(branded)['key'], 'product-placeholder')
