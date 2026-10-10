# CeCe — Your Food Bestie

**Hungry? Ask CeCe.**

A friendly food intelligence application. Milestone 1 provides a branded Streamlit homepage, Home as the default section and Food Explorer as the main food destination, and working navigation to six Coming Soon modules.

## Run locally

From the project root, use the existing virtual environment:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501). Package installation requires internet access initially; the application itself needs no API key, paid API, or mandatory network request. No external fonts, images, or food services are loaded. The existing `.venv`, Git configuration, and `.gitignore` are preserved.

The direct dependencies are pinned to versions validated in the existing Python 3.14.8 environment. Transitive dependencies are not locked yet.

## Verify Milestone 1

```sh
.venv/bin/python -m unittest discover -s tests -v
```

The smoke test runs the actual Streamlit application, checks the brand and tagline, visits every planned module, verifies Coming Soon messages, and returns to Food Explorer without application errors.

For a visual check, open the app and confirm the green/cream styling, readable cards, sidebar navigation, and layout at desktop and narrow browser widths. Food Explorer should explain its upcoming features. The search field and suggestion buttons accept input and show a truthful Coming Soon response. Nutrition calculations, data records, and dietary classifications are not implemented.

## File guide

| File | Purpose |
| --- | --- |
| `app.py` | Thin Streamlit entry point. |
| `.streamlit/config.toml` | Consistent light theme and disabled usage telemetry. Contains no secrets. |
| `cece/__init__.py` | Makes `cece` an importable Python package. |
| `cece/ui.py` | Homepage components, functional search preview, navigation callbacks, cards, and Coming Soon states. |
| `cece/styles.css` | Warm cream/coral styling, typography, spacing, hover/focus states, and responsive adjustments. |
| `assets/cece-design-reference.png` | Original supplied visual reference. |
| `assets/cece-portrait.png`, `assets/cece-hero.png` | Cropped original CeCe artwork for consistent mascot identity. |
| `assets/food-explorer.png`, `assets/meal-builder.png`, `assets/restaurant-finder.png`, `assets/pantry.png`, `assets/festival-foods.png` | Cropped feature imagery from the reference. |
| `cece/data_access.py` | Documented placeholder for local food loading, validation, and search. |
| `cece/nutrition.py` | Documented placeholder for calculations independent of Streamlit. |
| `cece/dietary.py` | Documented placeholder for evidence-based dietary evaluation. |
| `data/README.md` | Defines future verified datasets, provenance, and dietary evidence contracts. |
| `scripts/README.md` | Reserves a separate home for future dataset preparation tools. |
| `requirements.txt` | Validated runtime dependency versions: Streamlit, pandas, Plotly. Only Streamlit is used in this milestone. |
| `tests/test_smoke.py` | Application and navigation smoke test using Streamlit AppTest and standard-library unittest. |
| `README.md` | Setup, verification, scope, architecture, and file guide. |

## Evidence versus rules

`data/dietary_evidence.csv` will store **food-specific evidence**. `cece/dietary.py` will contain **rules that interpret it**. The CSV is not created yet, and the Python module currently contains only its contract. Separating these allows evidence updates without rewriting program logic and allows the same logic to be reused by a future API.

Compatibility must have three explicit outcomes: confirmed compatibility, known conflict, and unknown. Every confirmation needs supporting evidence for the specific criterion. Missing information stays unknown; it must not be advertised as allergen or gluten safety.

## Engineering choices

- Separate presentation, data access, calculations, and dietary rules by responsibility.
- Keep the entry point thin and future calculation/rule functions independent of Streamlit.
- Use a local data boundary so runtime remains reproducible and offline-capable.
- Preserve source IDs, data types, units, and evidence instead of inventing missing values.
- Test observable behavior: branding, navigation, and absence of runtime errors.
- Use one small package; defer databases, service frameworks, agents, and additional abstractions until needed.
- Preserve existing repository settings and keep secrets out of version control using the existing ignore rules.

Later milestones will add verified generic and branded USDA records, food search, portion controls, and interactive nutrition comparisons. No AI, database, or restaurant integration is implemented yet.

## Reference-based visual redesign

The UI recreates the supplied reference with real Streamlit controls and local CSS. The entire screenshot is never used as a background. Artwork is cropped from the original; no replacement mascot or nutrition data is generated. Home and Food Explorer share the discovery layout. All other destinations have Coming Soon states.

Search is an interactive preview: it accepts text, supports Enter/submit and suggestion buttons, and explains that results are not available. Feature buttons navigate to their respective sections. Native controls preserve labels and keyboard interaction; CSS includes focus outlines and reduced-motion support.

Visual compromises: cropped images retain their original backgrounds; the flattened reference has no transparent mascot assets. Handwritten typography uses local system font fallbacks rather than downloaded fonts. Streamlit controls, sidebar collapse, and column stacking differ from the exact reference. Visual browser review at desktop and mobile widths remains a manual check.

## Milestone 2 — USDA data foundation

Completed October 10, 2026: 36 verified FoodData Central records (30 SR Legacy, 6 Branded), stored as a reproducible offline snapshot. The visual UI is unchanged; search still shows its preview response until the next milestone connects it to the data layer.

`cece/data_access.py` now loads and validates the local schema and dataset checksum. `cece/nutrition.py` now scales per-100-g nutrients to gram portions while preserving missing values. `cece/dietary.py` remains a documented future rules boundary with no invented classifications. `scripts/prepare_dataset.py` rebuilds data and source manifests. `tests/test_data_rules.py` and `tests/test_nutrition.py` cover schema, source values, identifiers, ranges, units, missing values, tampering, reproducibility, and portions. No additional dependencies were added.

See [data/README.md](data/README.md) for the full schema, record selection, limitations, and exact archive regeneration instructions. Offline regeneration:

```sh
.venv/bin/python scripts/prepare_dataset.py
.venv/bin/python -m unittest discover -s tests -v
```

Week 1 documentation summary: CeCe now has a traceable USDA nutrition foundation with explicit missing-value indicators and original source records. All target nutrients are normalized to kcal/grams per 100 g using USDA nutrient IDs. The dataset includes generic preparation variants and exact branded examples, with SHA-256 integrity checks and reproducible extraction. One branded tofu record lacks fiber; it remains unknown. Dietary safety claims are intentionally absent. The local UI, architecture, and environment are preserved.
