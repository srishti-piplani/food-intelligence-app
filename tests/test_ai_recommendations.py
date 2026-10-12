"""CeCe's Take grounding, API boundary and real UI journeys; no paid calls."""

import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import openai
from streamlit.testing.v1 import AppTest

from cece.ai_recommendations import (
    DEFAULT_MODEL, GOALS, MAX_OUTPUT_TOKENS, RecommendationError,
    build_context, configuration, context_fingerprint, generate_take,
)
from cece.data_access import DATA_DIR, load_foods
from cece.nutrition import calculate_portion, comparison_snapshot

APP = str(DATA_DIR.parent / 'app.py')
RICE_IDS = ['usda-168878', 'usda-169704', 'usda-168917']
ANSWER = "For more protein, cooked quinoa leads these selected foods on the per-100-g basis: its USDA record supplies 4.4 g protein, compared with 2.74 g for brown rice and 2.69 g for white rice. That makes it a practical choice for your stated goal, although this comparison alone cannot tell us everything about a complete meal. Each food can still contribute to your plate; the best fit also depends on the portion you actually eat and what you serve alongside it. General meal idea: pair your chosen grain with vegetables and a protein source you enjoy. That pairing is a suggestion, not an additional USDA nutrition calculation."


def selected(ids=RICE_IDS):
    indexed = {r['food_id']: r for r in load_foods().to_dict('records')}
    return [indexed[i] for i in ids]


def context(mode='Per 100 g', goal='More protein', ids=RICE_IDS, grams=100):
    foods = selected(ids)
    portions = {f['food_id']: float(grams) for f in foods}
    return build_context(foods, comparison_snapshot(foods, portions, mode), portions, mode, goal)


def comparison_app(ids=RICE_IDS):
    app = AppTest.from_file(APP).run()
    app.session_state['compare_foods'] = list(ids)
    app.button(key='nav_Food Explorer').click().run()
    app.radio(key='explorer_view').set_value('Compare Foods').run()
    return app


class GroundingTests(unittest.TestCase):
    def test_exact_goals_ids_source_units_and_preparation(self):
        self.assertEqual(GOALS, ('A balanced meal', 'More protein', 'More fiber', 'Fewer calories'))
        payload = context()
        self.assertEqual(payload['goal'], 'More protein')
        self.assertEqual([f['fdc_id'] for f in payload['foods']], [168878, 169704, 168917])
        self.assertEqual(payload['nutrient_units']['calories_kcal'], 'kcal')
        self.assertEqual(payload['nutrient_units']['protein_g'], 'g')
        for record, food in zip(payload['foods'], selected()):
            self.assertEqual(record['source_url'], food['source_url'])
            self.assertEqual(record['data_type'], food['data_type'])
            self.assertIn('cooked', record['preparation_state'])
            self.assertEqual(record['nutrients']['protein_g'], food['protein_g'])
        self.assertEqual(payload['computed_observations'][0]['foods'], ['Cooked quinoa'])

    def test_portions_basis_missing_and_density_are_grounded(self):
        ids = ['usda-172421', 'usda-1118973']
        payload = context('My portions', ids=ids, grams=150)
        per100 = context('Per 100 g', ids=ids, grams=150)
        for record, food in zip(payload['foods'], selected(ids)):
            expected = calculate_portion(food, 150)
            self.assertEqual(record['nutrients']['calories_kcal'], expected['calories_kcal'])
            self.assertEqual(record['selected_portion_g'], 150)
            self.assertEqual(record['compared_portion_g'], 150)
        self.assertIsNone(payload['foods'][1]['nutrients']['fiber_g'])
        self.assertTrue(payload['foods'][1]['missing_nutrients']['fiber_g'])
        self.assertEqual(per100['comparison_basis'], 'Per 100 g')
        self.assertEqual(per100['foods'][0]['selected_portion_g'], 150)
        self.assertEqual(per100['foods'][0]['compared_portion_g'], 100)
        self.assertEqual(payload['foods'][0]['protein_g_per_100_kcal'], per100['foods'][0]['protein_g_per_100_kcal'])
        self.assertNotIn('NaN', json.dumps(payload, allow_nan=False))

    def test_fingerprint_tracks_all_inputs_even_saved_100g_portions(self):
        initial = context_fingerprint(context())
        variants = [context(goal='More fiber'), context(mode='My portions'),
                    context(grams=150), context(ids=RICE_IDS[:2])]
        self.assertTrue(all(context_fingerprint(v) != initial for v in variants))
        self.assertEqual(context_fingerprint(context()), initial)
        with self.assertRaises(ValueError):
            context(goal='Unsupported')


class APIBoundaryTests(unittest.TestCase):
    def test_config_environment_secrets_and_placeholders(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(configuration(), ('', DEFAULT_MODEL))
            self.assertEqual(configuration({'OPENAI_API_KEY': 'fake-test-key', 'OPENAI_MODEL': 'test-model'}), ('fake-test-key', 'test-model'))
            self.assertEqual(configuration({'OPENAI_API_KEY': 'replace-me'})[0], '')
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-test-key', 'OPENAI_MODEL': 'env-model'}):
            self.assertEqual(configuration({'OPENAI_API_KEY': 'secret-test-key'}), ('env-test-key', 'env-model'))

    def test_one_responses_call_structured_output_and_bounded_cost(self):
        with patch('openai.OpenAI') as constructor:
            client = constructor.return_value.__enter__.return_value
            client.responses.create.return_value = SimpleNamespace(status='completed', output_text=json.dumps({'recommendation': ANSWER}))
            payload = context(goal='More fiber', mode='My portions', grams=150)
            self.assertEqual(generate_take(payload, 'fake-test-key', 'configured-model'), ANSWER)
            constructor.assert_called_once_with(api_key='fake-test-key', timeout=20.0, max_retries=0)
            client.responses.create.assert_called_once()
            request = client.responses.create.call_args.kwargs
            self.assertEqual(json.loads(request['input']), payload)
            self.assertEqual(request['model'], 'configured-model')
            self.assertFalse(request['store'])
            self.assertEqual(request['max_output_tokens'], MAX_OUTPUT_TOKENS)
            self.assertTrue(request['text']['format']['strict'])
            self.assertNotIn('tools', request)

    def test_missing_key_and_too_few_foods_make_no_request(self):
        with patch('openai.OpenAI') as constructor:
            with self.assertRaisesRegex(RecommendationError, 'API key'):
                generate_take(context(), '')
            with self.assertRaisesRegex(RecommendationError, 'at least two'):
                generate_take(context(ids=RICE_IDS[:1]), 'fake-test-key')
            constructor.assert_not_called()

    def test_auth_quota_network_timeout_and_status_failures_are_safe(self):
        request = httpx.Request('POST', 'https://api.openai.com/v1/responses')
        errors = [
            openai.AuthenticationError('sensitive-test-text', response=httpx.Response(401, request=request), body=None),
            openai.PermissionDeniedError('sensitive-test-text', response=httpx.Response(403, request=request), body=None),
            openai.RateLimitError('sensitive-test-text', response=httpx.Response(429, request=request), body=None),
            openai.APIConnectionError(message='sensitive-test-text', request=request),
            openai.APITimeoutError(request=request),
            openai.BadRequestError('sensitive-test-text', response=httpx.Response(400, request=request), body=None),
        ]
        for error in errors:
            with self.subTest(error=type(error).__name__), patch('openai.OpenAI') as constructor:
                client = constructor.return_value.__enter__.return_value
                client.responses.create.side_effect = error
                with self.assertRaises(RecommendationError) as caught:
                    generate_take(context(), 'fake-test-key')
                self.assertNotIn('sensitive-test-text', str(caught.exception))
                self.assertNotIn('fake-test-key', str(caught.exception))
                client.responses.create.assert_called_once()

    def test_incomplete_refused_or_malformed_responses(self):
        responses = [SimpleNamespace(status='incomplete', output_text='{}'),
                     SimpleNamespace(status='completed', output_text=''),
                     SimpleNamespace(status='completed', output_text='not-json'),
                     SimpleNamespace(status='completed', output_text='{"recommendation": null}'),
                     SimpleNamespace(status='completed', output_text='{}'), None]
        for response in responses:
            with self.subTest(response=response), patch('openai.OpenAI') as constructor:
                constructor.return_value.__enter__.return_value.responses.create.return_value = response
                with self.assertRaisesRegex(RecommendationError, 'complete recommendation'):
                    generate_take(context(), 'fake-test-key')


class AIJourneyTests(unittest.TestCase):
    def test_card_always_first_visible_and_disabled_under_two(self):
        with patch('cece.ai_ui.generate_take') as generate:
            for count in (0, 1, 2, 3):
                app = comparison_app(RICE_IDS[:count])
                self.assertEqual(app.subheader[0].value, "CeCe's Take ✨")
                radio_keys = [r.key for r in app.radio]
                self.assertLess(radio_keys.index('cece_goal'), radio_keys.index('comparison_basis'))
                self.assertEqual(app.radio(key='cece_goal').options, list(GOALS))
                self.assertEqual(app.button(key='ask_cece').disabled, count < 2)
                if count < 2:
                    self.assertTrue(any('Add at least two foods to hear' in c.value for c in app.caption))
                app.run()
                self.assertEqual(len(app.exception), 0)
            generate.assert_not_called()

    def test_click_once_goal_portions_match_cards_and_reruns_preserve_response(self):
        with patch('cece.ai_ui._configuration', return_value=('fake-test-key', DEFAULT_MODEL)), patch('cece.ai_ui.generate_take', return_value=ANSWER) as generate:
            app = comparison_app()
            app.radio(key='comparison_basis').set_value('My portions').run()
            app.number_input(key='compare_portion_usda-168878').set_value(150.0).run()
            app.radio(key='cece_goal').set_value('More protein').run()
            generate.assert_not_called()
            app.button(key='ask_cece').click().run()
            generate.assert_called_once()
            payload = generate.call_args.args[0]
            self.assertEqual(payload['goal'], 'More protein')
            self.assertEqual(payload['comparison_basis'], 'My portions')
            self.assertEqual(payload['foods'][0]['nutrients']['calories_kcal'], app.dataframe[0].value.iloc[0]['Calories'])
            self.assertEqual(payload['foods'][0]['compared_portion_g'], 150)
            self.assertTrue(any(ANSWER in m.value for m in app.markdown))
            self.assertTrue(any('FDC 168878' in m.value for m in app.markdown))
            app.run()
            app.selectbox(key='comparison_nutrient').set_value('Fiber').run()
            app.radio(key='explorer_view').set_value('Explore Foods').run()
            app.radio(key='explorer_view').set_value('Compare Foods').run()
            self.assertTrue(any(ANSWER in m.value for m in app.markdown))
            self.assertFalse(any('outdated' in w.value for w in app.warning))
            self.assertEqual(generate.call_count, 1)
            self.assertEqual(len(app.exception), 0)

    def test_every_changed_input_marks_previous_take_outdated_without_calls(self):
        with patch('cece.ai_ui._configuration', return_value=('fake-test-key', DEFAULT_MODEL)), patch('cece.ai_ui.generate_take', return_value=ANSWER) as generate:
            for change in ('goal', 'basis', 'portion', 'food'):
                with self.subTest(change=change):
                    app = comparison_app()
                    app.button(key='ask_cece').click().run()
                    calls = generate.call_count
                    if change == 'goal':
                        app.radio(key='cece_goal').set_value('More fiber').run()
                    elif change == 'basis':
                        app.radio(key='comparison_basis').set_value('My portions').run()
                    elif change == 'portion':
                        app.number_input(key='compare_portion_usda-168878').set_value(200.0).run()
                    else:
                        app.button(key='remove_usda-168878').click().run()
                    self.assertTrue(any('outdated' in w.value for w in app.warning))
                    self.assertEqual(generate.call_count, calls)
                    app.button(key='ask_cece').click().run()
                    self.assertEqual(generate.call_count, calls + 1)
                    self.assertFalse(any('outdated' in w.value for w in app.warning))
                    self.assertEqual(len(app.exception), 0)

    def test_missing_key_and_failure_are_friendly_and_do_not_crash(self):
        with patch('cece.ai_ui._configuration', return_value=('', DEFAULT_MODEL)), patch('openai.OpenAI') as constructor:
            app = comparison_app()
            app.button(key='ask_cece').click().run()
            self.assertTrue(any('API key' in i.value for i in app.info))
            constructor.assert_not_called()
            self.assertEqual(len(app.exception), 0)
        with patch('cece.ai_ui._configuration', return_value=('fake-test-key', DEFAULT_MODEL)), patch('cece.ai_ui.generate_take', side_effect=RecommendationError('CeCe could not connect.')) as generate:
            app = comparison_app()
            app.button(key='ask_cece').click().run()
            self.assertTrue(any('could not connect' in i.value for i in app.info))
            app.run()
            self.assertEqual(generate.call_count, 1)
            self.assertEqual(len(app.exception), 0)
