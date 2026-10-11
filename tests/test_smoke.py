"""Verify the real Streamlit shell and every navigation destination."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest
from cece.ui import SECTIONS


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class HomepageSmokeTest(unittest.TestCase):
    def test_homepage_and_navigation(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.title[0].value, "CeCe — Your Food Bestie")
        self.assertTrue(any("Hungry? Ask CeCe." in block.value for block in app.markdown))
        self.assertEqual(app.session_state["section"], "Home")
        self.assertEqual(app.header[0].value, "Explore with CeCe")

        for section in SECTIONS[1:]:
            app.button(key=f"nav_{section}").click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.header[0].value, section)
            if section != "Food Explorer":
                self.assertEqual(app.info[0].value, "Coming Soon")

        app.button(key="nav_Food Explorer").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.header[0].value, "Food Explorer")

    def test_search_and_card_navigation(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        app.text_input[0].set_value("tofu")
        next(button for button in app.button if button.label == "Search").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("tofu" in text.value.casefold() for text in app.markdown))
        self.assertEqual(len(app.metric), 0)
        app.button(key="view_usda-172448").click().run()
        self.assertEqual(len(app.metric), 5)
        app.button(key="nav_Home").click().run()
        next(button for button in app.button if button.key == "card_pantry").click().run()
        self.assertEqual(app.header[0].value, "Pantry")
        next(button for button in app.button if button.label == "Back to Home →").click().run()
        self.assertEqual(app.session_state["section"], "Home")


if __name__ == "__main__":
    unittest.main()
