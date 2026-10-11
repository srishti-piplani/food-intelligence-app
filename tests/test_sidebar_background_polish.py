"""Milestone 3.5 sidebar and consumer protein-density presentation checks."""
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from cece.data_access import DATA_DIR, load_foods
from cece.nutrition import protein_per_100_kcal, comparison_insights
from cece.ui import SECTIONS, NAV_ICONS

APP = str(DATA_DIR.parent / 'app.py')


class SidebarInsightPolishTests(unittest.TestCase):
    def test_icons_share_native_navigation_buttons(self):
        app = AppTest.from_file(APP).run()
        for name in SECTIONS:
            button = app.button(key=f'nav_{name}')
            self.assertEqual(button.label, name)
            self.assertEqual(button.proto.icon, f':material/{NAV_ICONS[name]}:')
        self.assertFalse(any('cece-nav-icon' in node.value for node in app.sidebar.markdown))

    def test_sidebar_has_inline_soon_without_separate_captions(self):
        app = AppTest.from_file(APP).run()
        self.assertFalse(any(c.value == 'Coming Soon' for c in app.sidebar.caption))
        badges = [node.proto.body for node in app.sidebar.get('html')]
        self.assertEqual(sum('nav-soon' in body and 'nav-soon-empty' not in body and '>Soon<' in body for body in badges), 6)
        self.assertEqual(sum('nav-soon-empty' in body for body in badges), 2)
        app.button(key='nav_Pantry').click().run()
        self.assertEqual(app.button(key='nav_Pantry').proto.type, 'primary')
        app.button(key='nav_Food Explorer').click().run()
        self.assertEqual(app.session_state['section'], 'Food Explorer')
        self.assertEqual(len(app.exception), 0)

    def test_consumer_density_wording_precision_and_portion_independence(self):
        app = AppTest.from_file(APP).run()
        app.session_state['compare_foods'] = ['usda-172448', 'usda-172421']
        app.button(key='nav_Food Explorer').click().run()
        app.radio(key='explorer_view').set_value('Compare Foods').run()
        self.assertTrue(any('Most protein for your calories' in m.value for m in app.markdown))
        self.assertFalse(any('Source ratio' in m.label for m in app.metric))
        value = next(m.value for m in app.metric if m.label == 'g protein per 100 kcal')
        food = load_foods().query('fdc_id == 172448').iloc[0].to_dict()
        self.assertEqual(value, f'{protein_per_100_kcal(food):,.2f}')
        app.radio(key='comparison_basis').set_value('My portions').run()
        app.number_input(key='compare_portion_usda-172448').set_value(0.0).run()
        self.assertEqual(next(m.value for m in app.metric if m.label == 'g protein per 100 kcal'), value)
        self.assertEqual(len(app.exception), 0)

    def test_density_missing_positive_calories_and_ties(self):
        food = load_foods().query('fdc_id == 172448').iloc[0].to_dict()
        for field, value in [('protein_g', None), ('protein_g', float('nan')), ('calories_kcal', None), ('calories_kcal', 0), ('calories_kcal', -1)]:
            self.assertIsNone(protein_per_100_kcal({**food, field: value}))
        density = protein_per_100_kcal(food)
        insight = comparison_insights([{'Food': 'A', 'protein_density': density}, {'Food': 'B', 'protein_density': density}, {'Food': 'Unknown', 'protein_density': None}])[3]
        self.assertEqual(insight['foods'], ['A', 'B'])
        self.assertEqual(insight['known_count'], 2)
        self.assertEqual(insight['total_count'], 3)

    def test_unknown_density_insight_has_no_fabricated_zero(self):
        foods = load_foods().copy()
        foods.loc[foods.fdc_id.isin([172448, 172421]), 'protein_g'] = float('nan')
        with patch('cece.explorer_ui._cached_foods', return_value=foods):
            app = AppTest.from_file(APP).run()
            app.session_state['compare_foods'] = ['usda-172448', 'usda-172421']
            app.button(key='nav_Food Explorer').click().run()
            app.radio(key='explorer_view').set_value('Compare Foods').run()
            self.assertTrue(any('Most protein for your calories' in m.value for m in app.markdown))
            self.assertTrue(any('Unknown for all selected foods' in m.value for m in app.markdown))
            self.assertFalse(any(m.label == 'g protein per 100 kcal' for m in app.metric))
            self.assertEqual(len(app.exception), 0)
