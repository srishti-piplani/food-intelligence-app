# Archived engineering history

This file preserves the former milestone-based README for reference. Past UI
instructions, test counts and implementation statuses may be superseded. Use
[the current README](../README.md) for setup and current capabilities.

---

# CeCe — Your Food Bestie

**Hungry? Ask CeCe.**

A friendly food intelligence application with a branded homepage, an offline USDA Food Explorer, portion-aware comparisons, and optional AI explanations through CeCe's Take. Home is the default section; six future modules remain Coming Soon.

## Run locally

From the project root, use the existing virtual environment:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501). Package installation requires internet access initially; the core Food Explorer needs no API key, paid API, or mandatory network request. CeCe's Take optionally uses the paid OpenAI API only when you click Ask CeCe with at least two selected foods. No external fonts, images, or food services are loaded. The existing `.venv`, Git configuration, and `.gitignore` are preserved.

The direct dependencies are pinned to versions validated in the existing Python 3.14.8 environment. Transitive dependencies are not locked yet.

## Verify Milestone 1

```sh
.venv/bin/python -m unittest discover -s tests -v
```

The smoke test runs the actual Streamlit application, checks the brand and tagline, visits every planned module, verifies Coming Soon messages, and returns to Food Explorer without application errors.

For a visual check, open the app and confirm the green/cream styling, readable cards, sidebar navigation, and layout at desktop and narrow browser widths. Food Explorer should explain its upcoming features. Food Explorer now searches verified local USDA records and supports portion nutrition and comparisons. Other modules remain Coming Soon; dietary safety classifications are not implemented.

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

Search accepts text and suggestion buttons, and returns verified USDA records locally. Feature buttons navigate to their respective sections. Native controls preserve labels and keyboard interaction; CSS includes focus outlines and reduced-motion support.

Visual compromises: cropped images retain their original backgrounds; the flattened reference has no transparent mascot assets. Handwritten typography uses local system font fallbacks rather than downloaded fonts. Streamlit controls, sidebar collapse, and column stacking differ from the exact reference. Visual browser review at desktop and mobile widths remains a manual check.

## Milestone 2 — USDA data foundation

Completed October 10, 2026: 36 verified FoodData Central records (30 SR Legacy, 6 Branded), stored as a reproducible offline snapshot. Milestone 2 preserved the visual UI; Milestone 3 now connects search to this data layer.

`cece/data_access.py` now loads and validates the local schema and dataset checksum. `cece/nutrition.py` now scales per-100-g nutrients to gram portions while preserving missing values. `cece/dietary.py` remains a documented future rules boundary with no invented classifications. `scripts/prepare_dataset.py` rebuilds data and source manifests. `tests/test_data_rules.py` and `tests/test_nutrition.py` cover schema, source values, identifiers, ranges, units, missing values, tampering, reproducibility, and portions. No additional dependencies were added.

See [data/README.md](../data/README.md) for the full schema, record selection, limitations, and exact archive regeneration instructions. Offline regeneration:

```sh
.venv/bin/python scripts/prepare_dataset.py
.venv/bin/python -m unittest discover -s tests -v
```

Week 1 documentation summary: CeCe now has a traceable USDA nutrition foundation with explicit missing-value indicators and original source records. All target nutrients are normalized to kcal/grams per 100 g using USDA nutrient IDs. The dataset includes generic preparation variants and exact branded examples, with SHA-256 integrity checks and reproducible extraction. One branded tofu record lacks fiber; it remains unknown. Dietary safety claims are intentionally absent. The local UI, architecture, and environment are preserved.

## Milestone 3 — Functional Food Explorer

CeCe now provides case-insensitive partial-text search across food descriptions and brands using only the verified 36-record USDA snapshot. Multi-word queries match all terms in any order. Empty searches browse all foods, with optional generic/branded filtering.

Search results open nutrition details with adjustable gram portions, five metric cards, and USDA FDC ID, data type, and source links. Compare up to three foods in interactive Plotly calorie and nutrient charts, using either 100 g or individual portions. Missing nutrients are shown as Unknown and omitted from charts rather than replaced with zero.

### Files changed

- `cece/data_access.py`: pure literal search across descriptions and brands.
- `cece/explorer_ui.py`: cached verified loading, results, selection, portions, attribution, comparison controls and charts.
- `cece/ui.py`: connects existing search, suggestions and navigation to Food Explorer while preserving the mascot and visual layout.
- `tests/test_explorer.py`: data search and full application journeys.
- `tests/test_smoke.py`: retains navigation/branding checks and replaces obsolete search-placeholder assertions with functional result checks.
- `README.md`: current usage and submission documentation.

The existing nutrition calculation module, dataset, manifest, theme, and assets are unchanged. No dependencies or network calls were added. Streamlit caches the validated loader using dataset/manifest modification times so locally regenerated data triggers validation again.

### Test the user journey

```sh
.venv/bin/python -m streamlit run app.py
.venv/bin/python -m unittest discover -s tests -v
```

1. On Home, click **cooked lentils**, or type `LENTILS` and press Enter. Food Explorer opens with results and no automatic selection. The Search button opens Food Explorer; opening Food Explorer with empty input browses all foods.
2. Click **View nutrition** for cooked lentils. Set the portion to 150 g: calories should show 174.0 kcal and protein 13.5 g (display rounded). Check the USDA source link and FDC ID 172421.
3. Search `Quaker` and select the branded granola bar. It is identified as a branded product, not generic oats.
4. Search `tofu` and select FDC 1118973: fiber should display **Unknown**.
5. Choose up to three foods in comparison. Hover chart bars and use the legend to identify foods. Switch to **My portions** and adjust individual gram amounts; charts and the table update. Missing fiber stays blank in the table and has no chart bar.
6. Search an unavailable name to see the no-match state; clear the field in Food Explorer to browse again. Visit Pantry or another future module to confirm its Coming Soon state.

### Limitations

The sample covers only 36 records and is a historical snapshot. Search matches text, not synonyms, recipe meaning, dietary compatibility, or nutritional goals. Portions use grams only and are bounded to 0–10,000 g in the UI. Branded values may reflect label rounding. No AI chat, dietary safety classification, or external search is provided. Automated tests check functional rendering and charts; browser appearance remains a manual review.

### Week 1 submission summary

Milestone 3 turns CeCe's branded Streamlit shell into an interactive food analysis application. Users search a verified offline USDA dataset, distinguish generic and branded foods, scale five nutrients to gram portions, inspect original source attribution, and compare up to three foods through interactive Plotly visualizations. Missing nutrients stay unknown. UI, data access, and nutrition calculations remain separate, with cached data loading and automated search-to-comparison tests.

## Milestone 3.1 — Clearer comparisons and richer nutrition

Food Explorer now uses short display names such as **Cooked quinoa**, **Dry oats**, and **Edamame**, while keeping complete USDA descriptions and FDC IDs in expandable source details. Preparation labels come only from explicit words in USDA descriptions. Duplicate comparison labels are disambiguated using preparation and, only if still necessary, record identity. Portion controls use food names.

Comparison charts use Arial typography matching the app's interface, CeCe coral/green/lavender colors, compact sizing, clear units/bases, readable labels, and interactive tooltips. Foods retain the same colors across charts. A preparation-state notice helps distinguish raw, dry, cooked, frozen and canned records. An optional **Show protein per 100 kcal** chart uses protein × 100 / calories from the source basis. Missing protein or nonpositive/missing calories are excluded; it does not rate overall food quality.

The main five metric cards remain first. **Detailed nutrition** adds total sugars, added sugars, saturated fat, trans fat, sodium, and cholesterol for the selected portion. Sodium/cholesterol are in mg; sugar/fat values are in g. All values come from original USDA records. Added sugars are unknown in every selected record; other detailed nutrients can also be missing. Zero is displayed only when supplied by USDA.

### Food thumbnails and rights

Milestone 3.1 introduced original, locally authored representative SVG illustrations under **CC0 1.0**; Milestone 3.2 now prefers reviewed photographs where mapped and uses these illustrations as fallbacks. These are illustrations, not photos of the exact food or preparation. Branded products have polished placeholders labeled **Product image unavailable**; no unverified packaging imagery is used. `assets/foods/metadata.json` records creator, local path, source, license and representation status, with attribution visible in source details. `assets/foods/LICENSE.txt` applies only to these new illustrations, not the mascot or supplied reference artwork. No external image host, paid API, font download, or new package is required.

### Changed files

- `cece/food_labels.py`: source-derived short names, preparation states and collision-safe comparison labels.
- `cece/charts.py`: reusable Plotly styling, units and missing-value omission.
- `cece/imagery.py` and `assets/foods/`: representative artwork, attribution and placeholder selection.
- `cece/explorer_ui.py`: named controls, thumbnails, detailed nutrition/source expanders and protein-density comparison.
- `cece/styles.css`: interface typography aligned with chart typography; expressive hero lettering retained.
- `cece/data_access.py`, `cece/nutrition.py`, `scripts/prepare_dataset.py`: eleven-nutrient schema, unit validation, portion scaling and density calculation.
- `data/foods.csv`, `data/manifest.json`, `data/README.md`: regenerated schema version 2 and documentation.
- `tests/test_data_rules.py`, `tests/test_food_enhancements.py`: source-value coverage for all nutrients, labels, preparation, missing data, density, chart styling and image metadata.

### Manual verification

Search `edamame` and confirm prepared/unprepared frozen records remain distinguishable. Compare **Dry oats** and **Cooked oatmeal** and look for the preparation-state notice. Switch between 100 g and custom portions; confirm controls use names. Enable protein-per-100-kcal comparison. Expand Detailed nutrition to confirm mg/g units and Unknown added sugars. Expand Source details for the complete original description and image attribution. Generic foods show representative thumbnails; branded products show placeholders.

```sh
.venv/bin/python scripts/prepare_dataset.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m streamlit run app.py
```

Known limits: representative illustrations do not distinguish every preparation or brand. Preparation remains Not specified where source text does not establish it. Short names simplify descriptions; original variants remain available in source details. The dataset is still a historical 36-record snapshot with incomplete detailed nutrients. Chart legibility on very narrow screens still needs manual browser review. No dietary safety classifications or AI functionality were added.

**Week 1 submission summary:** Milestone 3.1 improves CeCe's food analysis experience with readable names, preparation-aware comparisons, locally licensed thumbnails, compact branded charts and optional protein-density analysis. The verified USDA pipeline now retains eleven nutrients with correct units, explicit missing values, original provenance and deterministic regeneration. Existing search, portions, navigation and comparison behavior remain covered by automated tests.

## Milestone 3.2 — Food Explorer UX and photography

Home retains CeCe's two-ponytail mascot and reference-based design, with a more prominent **Hungry? Ask CeCe.** tagline and a bright search container. Search/Enter and suggestions open a compact Food Explorer with a single shared input. The explorer uses discovery cards on the left and **Nutrition Breakdown** on the right. Native Streamlit columns stack on mobile, and stable container keys scope CSS; no generated class names are targeted.

No food is selected automatically. A new search (including submitting the same query again) clears details; filtering clears a selected food if it disappears from results. Clicking View nutrition explicitly selects and highlights the correct card. Close restores the friendly empty panel. Search text survives navigation through Coming Soon modules. Comparison selections survive new searches.

Calories have the strongest nutrition emphasis, with four readable macro/fiber metrics, adjacent gram controls, expandable Detailed Nutrition and USDA Source Details. The verified eleven-nutrient dataset, provenance, preparation script and calculations are unchanged. Comparison charts appear only for two or three foods, use compact Calories/Nutrients tabs, and preserve 100-g/custom-portion and optional protein-density views. Add to comparison and removable selection chips support the workflow.

### Photography and rights

**8 distinct real food photos** are mapped to **15 generic USDA records**, stored locally as 720 × 480 WebP images and 240 × 160 thumbnails (about 467 KB for all sixteen files). Six photos are from Pexels under the Pexels License; quinoa and lentils are from Wikimedia Commons under CC BY-SA 3.0 and 4.0 respectively. No generic photo is used for branded products. Unmapped generic records and missing photo files use original illustrations; branded products retain labeled placeholders.

| Photo | Creator | Source / applicable license |
| --- | --- | --- |
| Tofu | Polina Tankilevitch | [Pexels](https://www.pexels.com/photo/photo-of-tofu-on-white-plate-against-white-background-4518584/) / Pexels License |
| Edamame | Valeria Boltneva | [Pexels](https://www.pexels.com/photo/green-bean-1860193/) / Pexels License |
| Plain yogurt | elif tekkaya | [Pexels](https://www.pexels.com/photo/white-ceramic-bowl-filled-with-yogurt-10809258/) / Pexels License |
| Dry oats | Eva Bronzini | [Pexels](https://www.pexels.com/photo/top-view-of-oat-flakes-5988273/) / Pexels License |
| Chickpeas | Paula Berken | [Pexels](https://www.pexels.com/photo/close-up-of-a-bowl-of-chickpeas-7090131/) / Pexels License |
| Cooked white rice | Robert Moutongoh | [Pexels](https://www.pexels.com/photo/a-bowl-of-cooked-rice-8923092/) / Pexels License |
| Cooked quinoa | ProjectManhattan | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Quinoa_2.jpg) / CC BY-SA 3.0 |
| Cooked lentils | Liat Portal / HaJunkiyada | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Liat_Portal_for_Foodie_Disorder_-_Cooked_Lentils_with_Caramelized_Onions.jpg) / CC BY-SA 4.0 |

[Pexels license](https://www.pexels.com/license/) allows application use and modification subject to its restrictions. The Wikimedia crops retain their respective share-alike image licenses. Credit, source and license links, modification notices, and representative-image caveats are visible in USDA Source Details and recorded in [photo credits](../assets/foods/photos/CREDITS.md). The parent folder's CC0 SVG license does not apply to these photographs or the CeCe mascot.

`assets/foods/photos/metadata.json` stores reviewed stable food-ID mappings, source/creator/license URLs, preparation caveats, image dimensions, and source/derived SHA-256 checksums. Images are representative: yogurt fat level is not visually verified; edamame shows pods/seasoning; lentils show onions. Pictured additions do not change the USDA values, and this is stated in the nutrition panel. No remote photo, image search or API call happens at runtime.

To rebuild optimized photo files, download the eight reviewed `download_url` entries to a directory as `<photo-key>.jpg`, then run:

```sh
.venv/bin/python scripts/prepare_photos.py --source-dir /path/to/reviewed-source-jpegs
```

This offline script uses Pillow already installed through Streamlit. It performs reviewed crops and compression, updates checksums, and never discovers, approves or downloads new photos automatically. New photographs must have reviewed subject matches and license metadata before mapping.

### Files changed

- `cece/ui.py`, `cece/styles.css`: prominent shared search, compact explorer route, hero tagline, typography, selected-card and calorie styling.
- `cece/explorer_state.py`: explicit selection, clear and shared-search transitions.
- `cece/explorer_ui.py`: two-column discovery/details, empty/close states, photo display/attribution, and minimum-two-food comparisons.
- `cece/imagery.py`, `assets/foods/photos/`: reviewed photo mappings, optimized assets, credits and missing-file fallbacks.
- `scripts/prepare_photos.py`: offline photo optimization.
- `tests/test_explorer_ux.py` and existing UI tests: explicit selection, stale-state clearing, correct yogurt portions, missing nutrients, photo rights/checksums/fallbacks, comparisons and source attribution.
- `README.md`: acceptance workflow, limitations, image credits and submission summary.

### Acceptance workflow

```sh
.venv/bin/python -m streamlit run app.py
.venv/bin/python -m unittest discover -s tests -v
```

1. Open Home and confirm the prominent tagline and unchanged CeCe mascot.
2. Click Greek yogurt. Food Explorer opens with photographs and no nutrition selected.
3. Select nonfat Greek yogurt (FDC 170894): Nutrition Breakdown shows 59.0 kcal per 100 g. Set 150 g: 88.5 kcal.
4. Open Detailed Nutrition and USDA Source Details for units, Unknown added sugars, original USDA link and image credit.
5. Click Close; select another food; submit a new search and confirm the panel clears.
6. Add one food to comparison: charts stay hidden. Add a second: Calories/Nutrients tabs appear. Choose a third, change portions, enable protein density and remove items using ×.
7. Search tofu and select FDC 1118973 to verify Unknown fiber. Test an unavailable query and generic/branded filtering.
8. At desktop width confirm discovery/details sit side by side; at mobile width confirm vertical stacking and readable cards.

**Validation:** 30 automated tests pass, including the yogurt acceptance journey, data reproducibility and existing calculations. All eight photo crops were visually reviewed. No browser automation was available in this environment, so desktop/mobile browser appearance still requires manual review; AppTest verifies component behavior, not CSS rendering.

**Known limits:** photography covers 15 of 30 generic records; remaining records use illustrations, and all six branded records use placeholders. Photos represent categories, not exact preparations or nutrition portions. Native Streamlit columns and internal list scrolling differ from a fully custom front end. All data remains the historical 36-record snapshot; no dietary safety classification or AI response is added.

**Week 1 submission summary:** Milestone 3.2 brings an explicit search–select–explore workflow to CeCe, with a responsive discovery/detail layout, prominent calories, preparation-aware nutrition and compact comparisons requiring two foods. Eight licensed real food photographs are mapped to verified generic USDA records with local optimized assets, attribution and fallbacks. Source-backed calculations, missing-value integrity, the mascot and offline runtime are preserved.

## Milestone 3.3 — Explore and compare with clarity

Food Explorer now has exactly two views immediately beneath its heading:
**Explore Foods** and **Compare Foods (N)**. Explore integrates search,
clickable suggestions, collapsible food-type filters, photo result cards and
an explicit-selection nutrition panel. Clear Search and Reset Filters act
independently and preserve comparison selections. A new search closes stale
nutrition details; no food is automatically selected.

Compare supports up to three foods, photographed summary cards, named gram
controls, individual removal and Clear Comparison. One compact horizontal
chart compares Calories, Protein, Carbs, Fat or Fiber, with per-100-g and
selected-portion bases. The optional protein-per-100-kcal mode uses source
values and is independent of portion size. Bar labels round only for display; the expandable table retains calculated numeric values.
Unknown measurements receive no bars and never become zero. Deterministic
insights show highest protein, highest fiber, lowest calories and highest
protein density, including ties and the number of foods with known values.
No overall health ranking is implied. Preparation differences remain visible.

### Implementation responsibilities

- `cece/ui.py`: shared native search controls and preserved homepage shell.
- `cece/explorer_ui.py`: the two views, result/detail components, comparison
  cards, actions and display of source and image attribution.
- `cece/explorer_state.py`: independent search/filter resets and selection,
  view and comparison transitions. Durable state is separate from disposable
  widget keys, so selections and edited portions survive navigation.
- `cece/nutrition.py`: existing 11-nutrient scaling and protein density, plus
  pure deterministic comparison insights. Rankings use known finite values
  only, with a 1e-9 floating-point tolerance for ties.
- `cece/charts.py`: reusable Arial-styled Plotly charts with short labels,
  explicit units, source descriptions in tooltips and proportional height.
- `cece/styles.css`: readable type scale, cream/coral/green cards and responsive
  styles scoped to authored component keys and semantic Streamlit attributes.
- `tests/test_comparison_redesign.py`: reset, tie, missing-value, chart and
  complete three-food acceptance tests. Existing interaction tests follow the
  dedicated comparison view; data, provenance and photo checks remain intact.

The verified 36-record USDA snapshot, all 11 nutrient fields, offline pipeline,
licensed photos, mascot, Git configuration, `.gitignore` and virtual environment
are preserved. This milestone adds no dependencies or external requests.

### Run and verify

```bash
.venv/bin/streamlit run app.py
.venv/bin/python -m unittest discover -s tests -v
```

1. On Home, confirm **Hungry? Ask CeCe.**, search tofu, and confirm Explore
   shows results with a friendly empty nutrition panel.
2. Select Firm tofu (FDC 172448), set 150 g, inspect Detailed Nutrition and
   USDA Source Details, then Add to comparison.
3. Search cooked lentils and oats, select each and add them. Confirm the view
   label reads Compare Foods (3) and new searches clear detail selection only.
4. Open Compare. Check the three summary cards, switch Per 100 g / My portions,
   edit grams, and change the nutrient selector. Compare bar values against
   the expandable detailed table; test the protein-density option too.
5. Review the stated insight basis and preparation warning. Switch views and
   sidebar destinations and verify selections, controls and grams persist.
6. Remove one food, then Clear Comparison; fewer than two foods gives guidance.
7. In Explore, test Clear Search and Reset Filters separately while foods are
   in comparison. Try an unmatched query and a branded food with missing fiber.
8. In a browser, check approximately 1440-pixel desktop and 390-pixel mobile
   widths: readable text, native keyboard controls, stacked columns, chart
   resizing and absence of horizontal overflow.

**Validation:** 34 automated tests pass. AppTest verifies interactions and
rendering errors, not pixel fidelity. Desktop/mobile appearance needs manual
browser verification. Native Streamlit radio controls provide accessible
view navigation rather than custom tabs; mobile columns stack and may require
scrolling. The expandable native table may scroll horizontally. Representative
photos are not exact preparation images; branded products retain approved
placeholders. Source omissions remain Unknown.

**Week 1 submission summary:** Refined CeCe's offline USDA Food Explorer into
separate discovery and comparison experiences with explicit nutrition selection,
persistent three-food comparisons, portion-aware horizontal charts and factual
nutrition insights. Preserved all verified nutrient values, provenance, licensed
imagery and the existing visual identity, with automated acceptance coverage.

## Milestone 3.4 — Visual system and comparison polish

CeCe now uses a consolidated warm cream-to-peach design system, white cards,
16 px functional body text, readable secondary labels, semibold nutrient
labels, prominent metric values and restrained shadows. CSS tokens define
colors, 16 px card radii and spacing in multiples of 8 px. The original
mascot, homepage art, licensed photographs and prominent tagline remain.

The sidebar uses native Streamlit buttons with Material icons, coral-tinted
active rows and visible Coming Soon captions. It has no radio circles to hide;
keyboard activation, focus styles and the native collapsible sidebar remain.
Food result, detail and comparison cards omit unavailable preparation
subtitles. Original descriptions and the internal preparation metadata remain
available; this omission does not assert any preparation or dietary status.

Explore's comparison action changes to **Added to comparison ✓** when selected,
with a separate **Remove from comparison** action. Duplicates are prevented
by the state helper and the disabled Added button. When all three slots are
occupied, a Manage comparison expander lets users remove an existing food
without leaving Explore. The count updates on the next native button rerun.

Comparison cards, charts, the table and factual insight rankings now use a
single `comparison_snapshot` computed with the active **Per 100 g** or
**My portions** mode. Stored gram edits are retained, but only My portions
applies them. Each card states its displayed basis. Protein per 100 kcal
remains a source ratio independent of portions, including when a portion
is zero. Missing values remain Unknown, and ties use unrounded measurements.

Insight cards show recognizable food names and large values with coral,
green and pastel accents. Calories display up to one decimal, gram nutrients
one or two decimals, and protein density two decimals. Charts use the same
formatting for direct labels and tooltips. Rounding affects presentation only;
chart bar lengths, table values and rankings retain full calculation precision.
Missing-value coverage text appears only when values are excluded.

### Files and responsibilities

- `.streamlit/config.toml`: local Arial with sans-serif fallback for native
  widgets and tables, matching CSS and Plotly without downloading fonts.
- `cece/styles.css`: consolidated design tokens, surfaces, typography,
  selected/hover/focus styles and narrow-screen rules.
- `cece/ui.py`: native icon sidebar navigation and persistent section state.
- `cece/explorer_ui.py`: conditional preparation subtitles, Added/removal/full
  comparison controls, shared comparison snapshot and insight cards.
- `cece/explorer_state.py`: testable duplicate prevention and three-food limit.
- `cece/nutrition.py`: shared active-basis snapshot using existing portion and
  density calculations; existing nutrient calculations are unchanged.
- `cece/presentation.py` (new): display-only formatting with honest Unknown
  handling. This module has no food classifications or nutrition calculations.
- `cece/charts.py`: readable matching chart colors, labels and tooltips.
- `cece/food_labels.py`: unknown preparation omitted from collision labels,
  with source record IDs still disambiguating identical names.
- Existing navigation/interaction tests follow native sidebar buttons; new
  `tests/test_ux_polish.py` tests formatting, preparation display, button states,
  duplicates, limits, removal, shared basis, ranking reversals and navigation.

### Verification and limitations

Run the app and full suite with the existing virtual environment:

```bash
.venv/bin/streamlit run app.py
.venv/bin/python -m unittest discover -s tests -v
```

**Automated validation:** 41 tests pass. The offline preparation check reproduces
the unchanged 36-record USDA dataset checksum:
`cb44d2b2e1b112c2caf01a399f30b953dacc5562de0c8f7d48804103baef11f2`.
All 11 nutrients, source links, missing-value handling and licensed assets remain.
No dependencies or external requests were added; Git configuration, `.gitignore`
and the virtual environment are preserved.

Manual browser checklist:

1. Review Home's mascot and tagline, the icon sidebar's active row, Coming Soon
   indicators, keyboard focus and all navigation destinations.
2. Search olive oil: verify no “Not specified” subtitle appears. Search cooked
   lentils: verify the supported preparation subtitle remains.
3. Select Firm tofu (FDC 172448). Check metric typography, change its portion,
   open Detailed Nutrition and USDA Source Details, and verify image credits.
4. Add it to comparison: verify Added, removal and count. Add lentils and oats;
   select a fourth food, try adding it, and use Manage comparison to free a slot.
5. Compare Firm tofu and cooked lentils. Set tofu to 50 g and lentils to 200 g.
   Per 100 g should show 9.04 g and 9.02 g protein, with tofu highest. My portions
   should show 4.52 g and 18.04 g, with lentils highest. Cards, the Protein chart,
   insight and detailed table must agree. Increase tofu to 300 g: 27.12 g makes
   tofu highest again. Switching back restores the per-100-g comparison.
6. Toggle protein density; confirm the ratio and its winner remain independent
   of portion edits. Check missing branded fiber displays Unknown, not zero.
7. Switch views and sidebar pages: confirm selections, basis and gram edits
   survive. Test individual removal, Clear Comparison and independent search
   and filter resets.
8. Review at approximately 1440 px and 390 px widths. Confirm readable cards,
   stacked columns, collapsible sidebar, chart resizing and no page overflow.

Browser automation is unavailable here: AppTest verifies functionality and
render errors, but desktop/mobile CSS appearance still needs manual review.
Native Streamlit button navigation has primary/secondary styling rather than
custom ARIA navigation links. Material icon rendering depends on Streamlit's
font assets; text labels remain functional if icons fail to load. Columns stack
on narrow screens, and the detailed table can scroll horizontally. Very long
product labels may wrap or require extra chart space. Photos remain
representative, and exact branded product images remain unavailable.

**Week 1 submission summary:** Polished CeCe's consumer visual design and
sidebar, clarified comparison selection/removal, and unified cards, charts and
insights around one active comparison basis. Added display-only number
formatting and regression tests while preserving offline USDA provenance,
all nutrient fields and honest Unknown handling.

## Milestone 3.5 — Compact sidebar and background polish

Sidebar navigation now uses compact icon/button rows with a small **Soon**
badge beside unfinished features. Separate Coming Soon captions were removed
from the sidebar; destination pages still show their Coming Soon states.
Coral-tinted active rows, native keyboard buttons, visible focus, the mascot,
branding, motivational card and collapsible sidebar are preserved.

The page has a brighter cream-to-peach gradient with an original reusable
`assets/food-pattern.svg` (about 1.3 KB). Tomato, leaf, carrot, lemon and utensil
line art uses 5.5% opacity. The SVG is embedded as a local CSS data URL, so no
network request or static-file server is needed. A translucent content surface
softens the pattern behind text, and white cards shield nutrition and charts.

The fourth insight reads **Most protein for your calories**, with the winning
food, a value rounded to two decimals and the label **g protein per 100 kcal**.
“Source ratio” is no longer displayed. The calculation and source data are
unchanged: known protein divided by known positive calories times 100. Ties
and Unknown handling remain, and the ratio is independent of portion size.

Files changed: `cece/ui.py`, `cece/styles.css`, `cece/explorer_ui.py`, this README.
Added `assets/food-pattern.svg` and
`tests/test_sidebar_background_polish.py`.

**Validation:** All 45 tests pass, including inline sidebar badges and active
navigation, density wording/precision, missing values, ties and independence
from portions. Compilation and whitespace checks pass. The verified USDA
snapshot checksum remains unchanged; no dependencies were added.

For manual verification, run `.venv/bin/streamlit run app.py`. At desktop and
approximately 390 px widths, confirm Soon stays beside each navigation label,
active rows update, keyboard focus is visible, the sidebar collapses, and the
background remains subtle around readable white cards. Compare tofu and lentils
and check the fourth insight's two-decimal value and full unit label, then change
portions to verify that ratio stays constant.

Browser CSS review remains manual because browser automation is unavailable.
The sidebar uses native Streamlit columns with narrowly scoped semantic CSS to
keep badges on the same row; unusually narrow resized sidebars may wrap long
navigation names. Streamlit may change semantic DOM attributes in future
versions, so recheck styling after upgrades. Badge text itself is decorative;
button help also identifies unfinished destinations as Coming Soon.

## Milestone 4 — CeCe's Take ✨

CeCe's Take is an optional, click-only AI explanation at the **very top of
Compare Foods**, directly beneath the view navigation and above amount controls,
food cards, charts and deterministic insights. Its goal selector and Ask button
are always visible. Zero or one selected food shows “Add at least two foods to
hear CeCe's take!” and disables the button. Two or three foods enable it.

Choose exactly one goal: **A balanced meal**, **More protein**, **More fiber**,
or **Fewer calories**. Ask CeCe requests an approximately 80–120 word explanation
of goal-specific choices, trade-offs and, where appropriate, a general meal idea.
USDA links are displayed directly under the generated response. The prompt
separates verified facts from general pairing suggestions and prohibits invented
values, dietary safety inferences, medical advice, universal health rankings and
claims that an ingredient alone is a complete meal.

### Local OpenAI configuration

The official SDK is installed in the existing virtual environment and pinned
in `requirements.txt`. To reproduce the environment:

```sh
.venv/bin/python -m pip install -r requirements.txt
```

Create an API key in your OpenAI API account and ensure that project has API
billing/quota and access to the configured model. **Do not paste the key into
source code, screenshots, README, commits or chat.** Choose one local method:

**Option A: Streamlit secrets (recommended for this local demo).** Create or edit
`.streamlit/secrets.toml` locally in your editor, with these top-level entries:

```toml
OPENAI_API_KEY = "replace-with-your-real-key-locally"
OPENAI_MODEL = "gpt-4.1-mini"
```

**Option B: Environment variables.** In the same terminal used to launch CeCe:

```sh
export OPENAI_API_KEY="replace-with-your-real-key-locally"
export OPENAI_MODEL="gpt-4.1-mini"
```

Environment values take precedence over Streamlit secrets. `OPENAI_MODEL` is
optional and defaults to `gpt-4.1-mini`. `.env.example` contains placeholders
only. Streamlit does **not** automatically load `.env`; use Option A or B rather
than assuming copying `.env.example` enables the feature. Existing `.gitignore`
entries already ignore `.env`, `.env.*` and `.streamlit/secrets.toml`, while
allowing `.env.example` to be committed. No credential files were created by
this milestone, and no key is hardcoded, printed or stored in recommendation
session state.

Restart Streamlit after setting credentials:

```sh
.venv/bin/python -m streamlit run app.py
```

Without a key, the app remains usable offline; clicking Ask CeCe shows friendly
configuration guidance. The feature requires internet access only for that click.

### Rice and quinoa demonstration

1. Search **white rice** in Explore. Select cooked white rice, FDC **168878**, and
   Add to comparison.
2. Search **brown rice**. Add cooked brown rice, FDC **169704**.
3. Search **quinoa**. Add cooked quinoa, FDC **168917**.
4. Open **Compare Foods (3)**. CeCe's Take should be the first card. Select
   **More protein**, leave **Per 100 g**, and click **Ask CeCe ✨** once.
5. Check the explanation against the verified protein values: white rice
   **2.69 g**, brown rice **2.74 g**, and quinoa **4.40 g per 100 g**. Quinoa has
   the most protein among these three records on this basis.
6. Select **My portions** and change grams. The old response should be clearly
   marked **outdated**, without a new API request. Clicking Ask again uses the
   displayed portion-adjusted values. Editing grams while Per 100 g is active
   also marks the response outdated, but nutrients still use the 100-g basis.
7. Try **A balanced meal**. The response should describe contributions and
   complementary foods, rather than declaring one grain a complete meal.
8. Change the chart nutrient or switch views and return: the recommendation
   remains visible, with no automatic API call. Change goal/basis/foods/portions:
   it is marked outdated. With fewer than two foods, the card remains discoverable
   and Ask is disabled; any previous take remains explicitly marked outdated.

### Grounding, state and API boundary

- `cece/ai_recommendations.py` (new) builds a JSON context from the exact
  `comparison_snapshot` used by the cards. It includes source IDs/types/URLs,
  recognizable names, known preparation states, selected and compared grams,
  active basis, five nutrient values and missing flags, Python-computed protein
  density and deterministic observations. Null means Unknown, never zero.
- The prompt asks the model to **interpret**, rather than compute, those facts.
  Saved portions are explicitly separated from the grams used by Per 100 g.
- The official OpenAI SDK uses `client.responses.create()` with a strict
  one-field JSON schema, `store=False`, a **400-token output cap**, a **20-second
  timeout** and **zero retries**. There is one application request per explicit
  Ask click. No tools, search, RAG, agents or background requests are enabled.
- `cece/ai_ui.py` (new) owns the compact card, credential resolution, loading
  state, safe errors, and response display. The server-side session stores
  the text, model, full input context and its SHA-256 fingerprint. Input changes
  mark the prior response outdated; they never regenerate it automatically.
  Sources beneath an outdated response refer to its original input records.
- `cece/explorer_ui.py` creates the top-of-page slot and fills it with the current
  snapshot after portion widgets have yielded their values, before the empty
  comparison return. Existing calculations, charts and discovery are preserved.
- `cece/styles.css` adds only styles scoped to the new recommendation card.
  `cece/ui.py` updates the data-promise caption to acknowledge optional AI help;
  the sidebar and homepage layout are unchanged.
- `requirements.txt` adds `openai==2.54.0`; `.env.example` supplies placeholders.
  `tests/test_ai_recommendations.py` (new) covers grounding, API behavior and
  full Streamlit interactions with mocked responses.

### Costs and limitations

Default model: **gpt-4.1-mini**, a non-reasoning model supporting Responses and
structured output. Current official pricing is **$0.40 per million input tokens**
and **$1.60 per million output tokens**. For example, 1,500 input and 200 output
tokens cost approximately **$0.00092** per successful request (about one-tenth
of a US cent). Actual cost varies with prompt/response length and model choice;
additional clicks incur additional charges. Confirm current pricing and project
limits before a larger demonstration. [Official model details and pricing](https://developers.openai.com/api/docs/models/gpt-4.1-mini).
[Official Python SDK](https://developers.openai.com/api/reference/python) and
[Responses API reference](https://developers.openai.com/api/reference/python/resources/responses/methods/create)
document the integration used here.

This is a grounded generative explanation, not a medical advisor or a
programmatic fact checker. Prompt rules and verified inputs reduce errors but
cannot guarantee every model statement. Review claims against displayed USDA
facts; recommendation length is requested, not rigidly enforced. API keys,
billing, model access, connectivity and provider limits can prevent generation.
The model name is configurable, but replacement models must support Responses
and strict JSON structured output and work within the chosen output cap.
Malformed, empty, refused or incomplete responses produce a friendly error;
no invented fallback recommendation is displayed. API error bodies and keys
are never shown to users.

No live paid call was made: no local key was configured during implementation.
The SDK/API boundary was verified with mocked responses. Browser appearance and
live response quality require manual verification after local credential setup.
The original 36-food historical snapshot and incomplete nutrient coverage still
limit the comparison; general pairing ideas have no verified numerical nutrition
claims beyond the selected records.

### Validation and Week 1 submission summary

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
```

**58 tests pass**, including the existing 46 tests. Added coverage verifies
always-visible top placement, exact goals, disabled/enabled states, one click/one
request, IDs and source references, per-100-g and portion grounding, missing
nutrients, credential configuration, safe auth/quota/network/timeout errors,
malformed responses, rerun/navigation persistence, and stale handling for every
input change. Automated tests make no paid API requests. Dependency, compilation
and whitespace checks pass. The USDA dataset checksum remains
`cb44d2b2e1b112c2caf01a399f30b953dacc5562de0c8f7d48804103baef11f2`.

**Week 1 summary:** Added CeCe's Take, a compact goal-based comparison explanation
using the OpenAI Responses API. Verified USDA nutrition values, preparation,
portions, missing indicators and sources ground the model's input. Explicit
click-only generation, bounded output, safe credential handling and stale-response
labels keep the feature inexpensive and transparent, while the food explorer
remains fully usable offline.
