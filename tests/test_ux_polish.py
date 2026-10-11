"""Milestone 3.4 visual semantics and active-basis regression coverage."""
import json
import unittest

from streamlit.testing.v1 import AppTest

from cece.data_access import DATA_DIR, load_foods
from cece.explorer_state import add_comparison, remove_comparison
from cece.food_labels import comparison_labels, preparation_state
from cece.nutrition import comparison_snapshot, comparison_insights
from cece.presentation import nutrient_text
from cece.ui import SECTIONS

APP = str(DATA_DIR.parent / 'app.py')


class PolishTests(unittest.TestCase):
    def test_numeric_formatting_only_rounds_display(self):
        self.assertEqual(nutrient_text(78, 'kcal'), '78 kcal')
        self.assertEqual(nutrient_text(78.25, 'kcal'), '78.2 kcal')
        self.assertEqual(nutrient_text(3.66666667, 'g'), '3.67 g')
        self.assertEqual(nutrient_text(4, 'g'), '4.0 g')
        self.assertEqual(nutrient_text(3.66666667, 'g / 100 kcal'), '3.67 g / 100 kcal')
        self.assertEqual(nutrient_text(0, 'g'), '0.0 g')
        for missing in (None, float('nan'), float('inf'), True):
            self.assertEqual(nutrient_text(missing, 'g'), 'Unknown')

    def test_duplicate_and_limit_transitions(self):
        state = {}
        for food_id in ('a', 'a', 'b', 'c', 'd'):
            add_comparison(state, food_id)
        self.assertEqual(state['compare_foods'], ['a', 'b', 'c'])
        self.assertIn('three foods', state['comparison_notice'])
        remove_comparison(state, 'b')
        add_comparison(state, 'd')
        self.assertEqual(state['compare_foods'], ['a', 'c', 'd'])
        self.assertNotIn('comparison_notice', state)

    def test_preparation_subtitles_and_duplicate_unknown_names(self):
        app = AppTest.from_file(APP).run()
        app.button(key='nav_Food Explorer').click().run()
        self.assertFalse(any('Not specified' in c.value for c in app.caption))
        self.assertTrue(any('cooked' in c.value for c in app.caption))
        app.text_input(key='food_query').set_value('olive').run()
        app.button(key='view_usda-171413').click().run()
        self.assertFalse(any('Not specified' in c.value for c in app.caption))
        food = load_foods().query('fdc_id == 171413').iloc[0].to_dict()
        self.assertEqual(preparation_state(food['description']), 'Not specified')
        labels = comparison_labels([food, {**food, 'food_id': 'duplicate', 'fdc_id': 999}])
        self.assertEqual(len(set(labels.values())), 2)
        self.assertFalse(any('Not specified' in label for label in labels.values()))

    def test_added_button_remove_and_manage_full_comparison_in_explore(self):
        app = AppTest.from_file(APP).run()
        for query, food_id in [('tofu', 'usda-172448'), ('lentils', 'usda-172421'), ('oats', 'usda-173904')]:
            app.text_input(key='food_query').set_value(query).run()
            app.button(key=f'view_{food_id}').click().run()
            app.button(key=f'add_compare_{food_id}').click().run()
            button = app.button(key=f'add_compare_{food_id}')
            self.assertEqual(button.label, 'Added to comparison ✓')
            self.assertTrue(button.disabled)
        app.text_input(key='food_query').set_value('olive').run()
        app.button(key='view_usda-171413').click().run()
        app.button(key='add_compare_usda-171413').click().run()
        self.assertEqual(len(app.session_state['compare_foods']), 3)
        self.assertTrue(any('three foods' in w.value for w in app.warning))
        app.button(key='manage_remove_usda-172421').click().run()
        app.button(key='add_compare_usda-171413').click().run()
        self.assertIn('Compare Foods (3)', app.radio(key='explorer_view').options)
        app.button(key='explore_remove_usda-171413').click().run()
        self.assertEqual(app.button(key='add_compare_usda-171413').label, 'Add to comparison')
        self.assertIn('Compare Foods (2)', app.radio(key='explorer_view').options)
        self.assertEqual(len(app.exception), 0)

    def test_shared_snapshot_basis_missing_ties_and_ratio(self):
        foods = load_foods().query('fdc_id in [172448, 172421]').to_dict('records')
        labels = comparison_labels(foods)
        portions = {food['food_id']: (50 if food['fdc_id'] == 172448 else 200) for food in foods}
        per100 = comparison_snapshot(foods, portions, 'Per 100 g')
        custom = comparison_snapshot(foods, portions, 'My portions')
        for row, other in zip(per100, custom):
            self.assertEqual(row['portion_g'], 100)
            self.assertEqual(other['portion_g'], portions[row['food_id']])
            self.assertEqual(row['protein_density'], other['protein_density'])
        winner = lambda rows: comparison_insights([{**r, 'Food': labels[r['food_id']]} for r in rows])[0]['foods']
        self.assertEqual(winner(per100), ['Firm tofu'])
        self.assertEqual(winner(custom), ['Cooked lentils'])
        missing = load_foods().query('fdc_id == 1118973').iloc[0].to_dict()
        self.assertIsNone(comparison_snapshot([missing], {missing['food_id']: 0}, 'My portions')[0]['fiber_g'])
        portions = {f['food_id']: 100 / f['protein_g'] for f in foods}
        self.assertEqual(len(winner(comparison_snapshot(foods, portions, 'My portions'))), 2)
        with self.assertRaises(ValueError):
            comparison_snapshot(foods, portions, 'Other')

    def test_cards_chart_table_insight_basis_agree_after_portion_edit(self):
        app = AppTest.from_file(APP).run()
        app.session_state['compare_foods'] = ['usda-172448', 'usda-172421']
        app.button(key='nav_Food Explorer').click().run()
        app.radio(key='explorer_view').set_value('Compare Foods').run()
        app.selectbox(key='comparison_nutrient').set_value('Protein').run()
        app.number_input(key='compare_portion_usda-172448').set_value(50.0).run()
        app.number_input(key='compare_portion_usda-172421').set_value(200.0).run()

        def check(values, winner):
            table = app.dataframe[0].value
            for actual, expected in zip(table['Protein'], values):
                self.assertAlmostEqual(actual, expected)
            self.assertEqual([m.value for m in app.metric if m.label == 'Protein'], [nutrient_text(v, 'g') for v in values])
            chart = json.loads(app.get('plotly_chart')[0].proto.spec)
            self.assertEqual([trace['text'][0] for trace in chart['data']], [nutrient_text(v, 'g') for v in values])
            # The winner name is in its insight card, following the insight title.
            title_index = next(i for i, m in enumerate(app.markdown) if 'Highest protein**' in m.value)
            self.assertEqual(app.markdown[title_index + 1].value, f'**{winner}**')
            metrics = [m for m in app.metric if m.label in ('Per 100 g', 'My portions')]
            self.assertEqual(metrics[0].value, nutrient_text(max(values), 'g'))

        check([9.04, 9.02], 'Firm tofu')
        app.radio(key='comparison_basis').set_value('My portions').run()
        check([4.52, 18.04], 'Cooked lentils')
        app.number_input(key='compare_portion_usda-172448').set_value(300.0).run()
        check([27.12, 18.04], 'Firm tofu')
        app.radio(key='comparison_basis').set_value('Per 100 g').run()
        check([9.04, 9.02], 'Firm tofu')
        self.assertEqual(len(app.exception), 0)

    def test_sidebar_buttons_icons_and_active_state(self):
        app = AppTest.from_file(APP).run()
        self.assertFalse(any(r.key == 'section' for r in app.radio))
        for section in SECTIONS:
            button = app.button(key=f'nav_{section}')
            self.assertEqual(button.label, section)
            self.assertTrue(button.proto.icon.startswith(":material/"))
            button.click().run()
            self.assertEqual(app.session_state['section'], section)
            self.assertEqual(app.button(key=f'nav_{section}').proto.type, 'primary')
            self.assertEqual(len(app.exception), 0)
