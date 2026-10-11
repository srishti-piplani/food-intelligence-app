"""Validate authentic records, reject malformed input, and check reproducibility."""

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from cece.data_access import DATA_DIR, ALL_NUTRIENTS, load_foods, normalize_record, validate_foods
from scripts.prepare_dataset import prepare


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.foods = load_foods()

    def test_actual_dataset_and_source_values(self):
        self.assertEqual(len(self.foods), 36)
        self.assertEqual(self.foods.data_type.value_counts().to_dict(), {"SR Legacy": 30, "Branded": 6})
        for row in self.foods.to_dict("records"):
            raw_path = DATA_DIR / row["raw_record"]
            self.assertEqual(hashlib.sha256(raw_path.read_bytes()).hexdigest(), row["raw_sha256"])
            original = normalize_record(json.loads(raw_path.read_text()), row["source_archive"])
            for name in ALL_NUTRIENTS:
                if original[name] is None:
                    self.assertTrue(pd.isna(row[name]))
                else:
                    self.assertAlmostEqual(row[name], original[name])
            self.assertEqual(original["description"], row["description"])

    def test_required_schema(self):
        with self.assertRaises(ValueError):
            validate_foods(self.foods.drop(columns=["source_url"]))

    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):
            validate_foods(pd.concat([self.foods, self.foods.iloc[:1]]))
        for field in ("food_id", "fdc_id"):
            frame = self.foods.copy()
            frame.loc[1, field] = frame.loc[0, field]
            with self.assertRaises(ValueError):
                validate_foods(frame)

    def test_nutrient_ranges_and_non_numeric_values(self):
        for value in (-1, 1001, float("inf")):
            frame = self.foods.copy()
            frame.loc[0, "calories_kcal"] = value
            with self.assertRaises(ValueError):
                validate_foods(frame)
        frame = self.foods.copy()
        frame["protein_g"] = frame.protein_g.astype(object)
        frame.loc[0, "protein_g"] = "not supplied"
        with self.assertRaises(ValueError):
            validate_foods(frame)

    def test_missing_and_zero_are_distinct(self):
        frame = self.foods.copy()
        frame.loc[0, "fiber_g"] = float("nan")
        frame.loc[0, "fiber_g_missing"] = True
        validate_foods(frame)
        frame.loc[0, "fiber_g_missing"] = False
        with self.assertRaises(ValueError):
            validate_foods(frame)
        frame.loc[0, "fiber_g"] = 0
        validate_foods(frame)

    def test_units_and_basis_rejected(self):
        record = json.loads((DATA_DIR / "raw/172421.json").read_text())
        for nutrient in record["foodNutrients"]:
            if nutrient["nutrient"]["id"] == 1003:
                nutrient["nutrient"]["unitName"] = "mg"
        with self.assertRaises(ValueError):
            normalize_record(record, "test-source")
        branded = json.loads((DATA_DIR / "raw/578760.json").read_text())
        branded["servingSizeUnit"] = "ml"
        with self.assertRaises(ValueError):
            normalize_record(branded, "test-source")
        frame = self.foods.copy()
        frame.loc[0, "basis_g"] = 1
        with self.assertRaises(ValueError):
            validate_foods(frame)

    def test_checksum_tampering_and_offline_regeneration(self):
        with tempfile.TemporaryDirectory() as folder:
            copied = Path(folder) / "data"
            shutil.copytree(DATA_DIR, copied)
            prepare(copied)
            self.assertEqual((copied / "foods.csv").read_bytes(), (DATA_DIR / "foods.csv").read_bytes())
            self.assertEqual((copied / "manifest.json").read_bytes(), (DATA_DIR / "manifest.json").read_bytes())
            with (copied / "foods.csv").open("a") as stream:
                stream.write("\n")
            with self.assertRaisesRegex(ValueError, "checksum"):
                load_foods(copied)
