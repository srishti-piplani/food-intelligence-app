# USDA nutrition foundation — Milestone 2

Retrieved October 10, 2026 from public USDA FoodData Central archives. The curated sample has **36 exact records: 30 SR Legacy and 6 Branded**. This is a historical reproducible sample, not comprehensive or current product coverage.

## Files and lineage

- `foods.csv`: normalized records sorted by FDC ID; blank nutrient cells mean missing.
- `selection.json`: fixed FDC IDs, exact source archive URLs and checksums, and acquisition date. This is the curation specification.
- `manifest.json`: dataset SHA-256, count, data types, source archive hashes, selection hash, raw record hashes, and missing counts.
- `raw/<fdc_id>.json`: full original selected USDA objects, including nutrient IDs, units, derivation/source details, ingredients and portions where supplied. JSON formatting is standardized; original field values are retained.
- `README.md`: schema, selection approach, limitations, and regeneration instructions.

## Schema and normalization

`food_id` is `usda-<fdc_id>`. `description` retains the original USDA name. `brand` uses USDA brandName, then brandOwner, otherwise blank. `fdc_id` and `data_type` identify the exact source record.

`calories_kcal`, `protein_g`, `carbohydrates_g`, `fat_g`, and `fiber_g` are **per 100 g**. Each has a Boolean `<column>_missing` indicator. `basis_g` is always 100. `source_url` identifies the USDA detail page; `source_archive` identifies the archive; `raw_record` and `raw_sha256` locate and verify the original saved object.

The mapping uses USDA nutrient IDs 1008 (kcal energy), 1003 (protein), 1005 (carbohydrate by difference), 1004 (total lipid), and 1079 (total dietary fiber). No calories are inferred from macros, and kJ values are not confused with kcal. We use USDA's standardized foodNutrients, not per-serving labelNutrients. Branded records must have gram serving units; volume-based products are excluded rather than assuming density.

Validation rejects duplicate IDs, missing provenance, wrong units or bases, nonnumeric values, inconsistent missing flags, and out-of-range nutrients. Bounds are broad physical plausibility checks (0–1000 kcal and 0–100 g per target nutrient), not dietary judgments. Portion calculations accept finite nonnegative grams and preserve unknown values even at zero grams.

## Curation and limitations

The generic sample includes firm/soft tofu, prepared/unprepared edamame, cooked lentils, cooked/canned chickpeas, cooked white/brown rice, oats/oatmeal, plain/Greek yogurt, quinoa, black beans, produce, egg, milk, and olive oil. Selection deliberately preserves preparation variants rather than merging foods with different water content.

The six exact branded examples are chickpea/lentil pasta (349454), Kibun surimi seafood with tofu and edamame (398589), Natco chickpeas (542499), Quaker granola bar (578760), Pacific Nutritional Foods nigari tofu (1118973), and Chobani Greek oats yogurt (1851216). These were selected from inspected archive records with gram serving units. Product descriptions stay intact; keyword matches do not imply ingredient-only records or dietary compatibility. A manufacturer's brandOwner is not always the consumer-facing brand.

Only fiber for FDC 1118973 is missing among the five target nutrients. It remains blank with `fiber_g_missing=True`; no zero or estimate is substituted. USDA label-derived branded values can reflect rounding and older product versions. SR Legacy is a historical data type. The archive filename release date can differ from a record's publication date; originals retain both available record metadata and lineage.

No vegan, vegetarian, gluten-free, or allergen-safe classifications are supplied. `dietary_evidence.csv` is not created: it would hold cited food-specific evidence. `cece/dietary.py` remains the documented rules boundary for interpreting future evidence as confirmed compatibility, known conflict, or unknown.

## Regenerate offline

From the project root:

```sh
.venv/bin/python scripts/prepare_dataset.py
.venv/bin/python -m unittest discover -s tests -v
```

This uses bundled raw records and performs no network requests. The retrieval date describes the original acquisition, not each rebuild. Unchanged inputs reproduce byte-identical CSV and manifest.

## Re-extract from USDA archives

Download the exact ZIPs to a directory outside the repository (roughly 208 MB total compressed):

```sh
mkdir -p /tmp/cece-usda
curl -fL -o /tmp/cece-usda/FoodData_Central_sr_legacy_food_json_2018-04.zip https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip
curl -fL -o /tmp/cece-usda/FoodData_Central_branded_food_json_2026-04-30.zip https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_branded_food_json_2026-04-30.zip
.venv/bin/python scripts/prepare_dataset.py --archive-dir /tmp/cece-usda
```

The script checks archive hashes before extracting the fixed selected IDs. Branded extraction streams one record at a time to avoid loading gigabytes into memory. Missing files, hash mismatches, or absent selected records produce an explicit error. Nothing downloads automatically. To update sources intentionally, review new records and revise selection metadata; do not silently replace snapshot inputs.

Sources: [USDA downloads](https://fdc.nal.usda.gov/download-datasets/) and [Branded documentation](https://fdc.nal.usda.gov/GBFPD_Documentation/).
