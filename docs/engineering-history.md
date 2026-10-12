# Engineering notes

This document describes current engineering decisions and safeguards. The existing
filename is retained so incoming links continue to resolve. For the product
introduction and setup, use the [main README](../README.md).

## Application boundaries

CeCe is a single Streamlit application with modular Python components. The UI
calls local data access and deterministic nutrition functions. The optional AI
request is isolated from food search and calculation logic. There is no database,
autonomous agent, live USDA integration, RAG pipeline or background request loop.

The [developer walkthrough](developer-walkthrough.md) lists actual functions,
module responsibilities and user workflows. The [dataset documentation](../data/README.md)
explains schema, source lineage and reproducible preparation.

## Data integrity

The bundled catalog contains 36 selected USDA records. Schema validation checks
identifiers, nutrient bases, provenance fields, missing indicators and plausible
ranges. The loader checks the CSV checksum and manifest count. Preparation and
tests check source correspondence; runtime search does not reopen every raw file.

All eleven nutrients retain their source units and missing status. Display
rounding does not alter calculations or rankings. Missing values remain Unknown,
even at zero grams. Comparisons identify preparation differences and report ties
and known-value coverage without declaring a food universally healthier.

The small per-record JSON collection is an audit fixture. Larger catalogs would
need batched source storage and indexed lookup rather than millions of small files
or a full in-memory pandas scan. Those storage changes are not implemented.

## AI grounding and state

CeCe's Take receives the same calculated snapshot displayed in Compare Foods.
Its context contains five main nutrients, known preparation states, source IDs
and links, selected and compared portions, missing flags, protein density and
computed observations. The model is instructed to interpret supplied facts and
separate general meal ideas from verified nutrition claims.

Requests use the official Responses API with a strict JSON response schema,
a 400-token output cap, 20-second timeout and zero retries. Only an explicit Ask
click makes a request. Authentication, access, quota, network, timeout and invalid
response failures produce safe messages rather than a fabricated fallback.

Generated text, original context, model and context fingerprint are stored in the
server-side Streamlit session. Changed foods, goals, basis or portions mark a
response outdated; changing a chart or ordinary navigation does not regenerate
it. Session state is not durable account or database storage.

Structured output validates the shape of the answer, not every factual statement.
There is no independent semantic fact checker. `store=False` is a request setting,
not a claim that all provider data retention is disabled. See
[OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data).

## Security and reproducibility

Credentials are read from environment variables or local Streamlit secrets. They
are not included in recommendation context or saved recommendation state. Ignore
rules exclude `.env`, `.env.*` and `.streamlit/secrets.toml`; `.env.example` contains
placeholders. Do not commit real credentials or screenshots showing them.

Direct dependencies are pinned; transitive dependencies are not fully locked.
Dataset regeneration is tested for byte-identical output in the validated
environment, not guaranteed across every Python version and platform. Automated
API tests use mocks. Browser layout and live model quality require manual checks.

## Visual implementation

The supplied design reference guides the cream, coral, green and pastel palette.
The application uses real Streamlit controls and local artwork rather than a full
screenshot background. Sidebar navigation uses native icon buttons and separate
Soon badges; unfinished destinations remain clearly marked.

Native Streamlit styling and narrow-screen column behavior can differ from the
reference. Recheck keyboard focus, sidebar alignment, chart labels and overflow
when changing Streamlit versions. The [homepage screenshot](../assets/screenshots/cece-homepage.png)
shows the running application, not the original design reference.

## Artwork and licensing

- Generic photographs have creator, source, license, modification and checksum
  metadata. [Photo credits](../assets/foods/photos/CREDITS.md) retain the Pexels and
  Wikimedia attribution and respective licenses.
- Original food fallback SVGs have a [CC0 dedication](../assets/foods/LICENSE.txt).
  That dedication applies only to the specified illustrations, not photographs
  or the mascot.
- CeCe mascot and homepage artwork were cropped from the supplied
  [design reference](../assets/cece-design-reference.png). Creator/distribution
  rights are not documented in this repository; do not assume the SVG dedication
  covers them.
- There is no root software license. Individual asset licenses do not establish
  a license for the entire project.
