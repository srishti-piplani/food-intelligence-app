"""Premium comparison acceptance checks, including durable state and rankings."""
import unittest
import pandas as pd
from streamlit.testing.v1 import AppTest
from cece.data_access import DATA_DIR, load_foods
from cece.nutrition import calculate_portion, comparison_insights, protein_per_100_kcal
from cece.explorer_state import clear_search, reset_filters, remove_comparison
from cece.charts import comparison_chart


class ComparisonRedesignTests(unittest.TestCase):
    def test_independent_resets_and_remove(self):
        state = {'compare_foods': ['a', 'b'], 'search_query': 'tofu', 'selected_food': 'a', 'food_type': 'Branded products'}
        clear_search(state)
        self.assertEqual(state['compare_foods'], ['a', 'b'])
        self.assertEqual(state['food_type'], 'Branded products')
        reset_filters(state)
        self.assertEqual(state['search_query'], '')
        self.assertEqual(state['compare_foods'], ['a', 'b'])
        remove_comparison(state, 'a')
        self.assertEqual(state['compare_foods'], ['b'])
        remove_comparison(state)
        self.assertEqual(state['compare_foods'], [])

    def test_insights_ties_unknown_and_zero(self):
        rows = [{'Food': 'A', 'protein_g': 4, 'fiber_g': None, 'calories_kcal': 0, 'protein_density': None},
                {'Food': 'B', 'protein_g': 4, 'fiber_g': 0, 'calories_kcal': 100, 'protein_density': 4},
                {'Food': 'C', 'protein_g': None, 'fiber_g': float('nan'), 'calories_kcal': None, 'protein_density': None}]
        insights = comparison_insights(rows)
        self.assertEqual(insights[0]['foods'], ['A', 'B'])
        self.assertEqual(insights[0]['known_count'], 2)
        self.assertEqual(insights[1]['value'], 0)
        self.assertEqual(insights[2]['foods'], ['A'])
        self.assertEqual(insights[3]['foods'], ['B'])
        self.assertTrue(all(i['value'] is None for i in comparison_insights([{'Food': 'Unknown'}])))

    def test_horizontal_chart_known_values_units(self):
        frame = pd.DataFrame({'Food': ['A', 'B'], 'Protein': [2.52, None], 'Description': ['Full A', 'Full B']})
        fig = comparison_chart(frame, 'Protein', 'Protein per 100 g', 'g', {'A': '#E76F57'})
        self.assertEqual(fig.data[0].orientation, 'h')
        self.assertEqual(list(fig.data[0].x), [2.52])
        self.assertEqual(list(fig.data[0].text), ['2.52 g'])
        self.assertEqual(fig.layout.xaxis.title.text, 'g')
        self.assertEqual(fig.layout.font.family, 'Arial, sans-serif')
        self.assertLess(fig.layout.height, 330)

    def test_complete_three_food_journey_and_view_persistence(self):
        app = AppTest.from_file(str(DATA_DIR.parent / 'app.py')).run()
        for query, food_id in [('tofu', 'usda-172448'), ('cooked lentils', 'usda-172421'), ('oats', 'usda-173904')]:
            app.text_input(key='food_query').set_value(query).run()
            self.assertEqual(len(app.metric), 0)
            app.button(key=f'view_{food_id}').click().run()
            if food_id == 'usda-172448':
                app.number_input(key=f'portion_{food_id}').set_value(150.0).run()
            app.button(key=f'add_compare_{food_id}').click().run()
        self.assertEqual(len(app.session_state['compare_foods']), 3)
        self.assertIn('Compare Foods (3)', app.radio(key='explorer_view').options)
        app.radio(key='explorer_view').set_value('Compare Foods').run()
        self.assertEqual(len(app.get('plotly_chart')), 1)
        self.assertEqual(len(app.metric), 19)
        app.radio(key='comparison_basis').set_value('My portions').run()
        source = load_foods().query('fdc_id == 172448').iloc[0].to_dict()
        self.assertEqual(app.dataframe[0].value.iloc[0]['Calories'], calculate_portion(source, 150)['calories_kcal'])
        app.number_input(key='compare_portion_usda-172448').set_value(175.0).run()
        app.selectbox(key='comparison_nutrient').set_value('Fiber').run()
        app.button(key="nav_Pantry").click().run()
        app.button(key="nav_Food Explorer").click().run()
        self.assertEqual(app.radio(key='explorer_view').value, 'Compare Foods')
        self.assertEqual(app.number_input(key='compare_portion_usda-172448').value, 175)
        self.assertEqual(app.radio(key='comparison_basis').value, 'My portions')
        self.assertEqual(app.selectbox(key='comparison_nutrient').value, 'Fiber')
        app.radio(key='explorer_view').set_value('Explore Foods').run()
        app.button(key='clear_search').click().run()
        self.assertEqual(app.text_input(key='food_query').value, '')
        app.selectbox(key='food_type').set_value('Branded products').run()
        app.button(key='reset_filters').click().run()
        self.assertEqual(app.selectbox(key='food_type').value, 'All foods')
        self.assertEqual(len(app.session_state['compare_foods']), 3)
        app.radio(key='explorer_view').set_value('Compare Foods').run()
        app.button(key='remove_usda-172448').click().run()
        self.assertEqual(len(app.session_state['compare_foods']), 2)
        app.button(key='clear_comparison').click().run()
        self.assertEqual(app.session_state['compare_foods'], [])
        self.assertEqual(len(app.get('plotly_chart')), 0)
        self.assertEqual(len(app.exception), 0)
