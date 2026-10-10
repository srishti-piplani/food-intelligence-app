"""Verify the real Streamlit shell and every navigation destination."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class HomepageSmokeTest(unittest.TestCase):
    def test_homepage_and_navigation(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.title[0].value, "CeCe — Your Food Bestie")
        self.assertTrue(any("Hungry? Ask CeCe." in block.value for block in app.markdown))
        self.assertEqual(app.radio[0].value, "Home")
        self.assertEqual(app.header[0].value, "Explore with CeCe")

        for section in app.radio[0].options[1:]:
            app.radio[0].set_value(section).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.header[0].value, section)
            if section != "Food Explorer":
                self.assertEqual(app.info[0].value, "Coming Soon")

        app.radio[0].set_value("Food Explorer").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.header[0].value, "Food Explorer")

    def test_search_and_card_navigation(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        app.text_input[0].set_value("tofu")
        next(button for button in app.button if button.label == "Search").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("tofu", app.info[0].value)
        self.assertIn("Coming Soon", app.info[0].value)
        next(button for button in app.button if button.key == "card_pantry").click().run()
        self.assertEqual(app.header[0].value, "Pantry")
        next(button for button in app.button if button.label == "Back to Home →").click().run()
        self.assertEqual(app.radio[0].value, "Home")


if __name__ == "__main__":
    unittest.main()
