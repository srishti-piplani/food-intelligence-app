# CeCe — Your Food Bestie

**Hungry? Ask CeCe.**

CeCe is a friendly food companion that helps you explore nutrition, compare foods,
and decide what fits your next meal. It brings trustworthy food information and
practical explanations together in one bright, approachable experience.

![CeCe homepage with mascot, food search, navigation, and feature cards](assets/screenshots/cece-homepage.png)

*The current homepage. Food Explorer is available; planned modules are marked Soon.*

## Why CeCe?

“What should I eat?” can turn into a lot of searching, label reading, and guesswork.
CeCe makes it easier to understand your options, adjust portions, and see the
trade-offs—without losing sight of the enjoyment of food.

The vision is a complete food companion: discover ingredients and products,
understand meals, find places to eat, make use of your pantry, and explore food
traditions with support for your preferences and needs.

## What you can do today

- **Explore foods:** search a local catalog of **36 curated USDA records**, including
  generic foods and branded products. Filter by food type and try search suggestions.
- **Understand nutrition:** select a food, adjust its portion in grams, and view
  calories, protein, carbohydrates, fat, fiber, and additional nutrient details.
- **Compare your options:** compare up to three foods per 100 g or by your selected
  portions, with interactive charts and clear, factual insights.
- **Hear CeCe's Take ✨:** choose A balanced meal, More protein, More fiber, or Fewer
  calories and ask for a friendly explanation grounded in your selected foods.
- **Check the source:** open original USDA descriptions, FoodData Central IDs,
  record links, and image attribution.

## CeCe's Take ✨

Not sure what to choose? Ask your food bestie!

The card sits at the top of Compare Foods. Add at least two foods, choose your goal,
and click **Ask CeCe ✨**. The OpenAI-powered explanation uses the same USDA
nutrition values and portions shown in the comparison, with source links beneath
its answer. Meal pairings are general suggestions, not extra verified nutrition facts.

Recommendations are generated only when you ask. Changing foods, portions, or your
goal marks the previous take outdated so you can request a fresh explanation.
Food search and nutrition comparisons work without an OpenAI API key.

## The food companion we're building

| Module | Vision | Status |
| --- | --- | --- |
| Food Explorer | Discover ingredients and products, understand nutrition, and compare options. | Available with a small catalog; broader coverage planned |
| Personal Food Profile | Bring together preferences, dietary needs, goals, and favorite cuisines. | Planned |
| Meal Builder | Customize meals and portions around your goals. | Planned |
| Restaurant Finder | Discover places and menu options that suit your preferences. | Planned |
| Pantry | Find meal ideas using ingredients you have. | Planned |
| Festival Foods | Explore traditional dishes and suitable adaptations. | Planned |
| AI Food Assistant | Get broader conversational support for food decisions. | Planned |

CeCe's Take is available today; the broader AI Food Assistant and other planned
modules are not yet functional.

## Built with

**Python · Streamlit · pandas · Plotly · OpenAI Responses API**

Food data and images are stored locally. OpenAI is used only for optional
recommendation requests. See the [developer walkthrough](docs/developer-walkthrough.md)
for the architecture and code flow.

## Try CeCe locally

The project was tested with Python 3.14.8. On macOS/Linux:

```sh
git clone https://github.com/srishti-piplani/food-intelligence-app.git
cd food-intelligence-app
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Reuse an existing `.venv` if you already have one. On Windows, create it with
`py -3.14 -m venv .venv` and use `.venv\Scripts\python.exe` for Python commands.
Open the local address printed by Streamlit, normally `http://localhost:8501`.
Package installation needs internet access; browsing the bundled catalog does not.

## Optional: enable CeCe's Take

You need your own **OpenAI API key and API billing/quota**. A ChatGPT subscription
is not the application's API credential. Create `.streamlit/secrets.toml` locally:

```toml
OPENAI_API_KEY = "your-key-here"
OPENAI_MODEL = "gpt-4.1-mini"
```

Alternatively, set `OPENAI_API_KEY` and optionally `OPENAI_MODEL` as environment
variables before starting the app. Environment values take precedence.
Restart Streamlit after configuring the key.

Keep keys private: `.env` and `.streamlit/secrets.toml` are ignored by Git.
`.env.example` contains placeholders; copying it does not automatically load
`.env`. Each Ask click may incur charges—check [OpenAI model pricing](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
and your API project limits.

## Try these journeys

**Explore:** search `Greek yogurt`, select the nonfat record, and change the
portion to 150 g. Open Detailed Nutrition and USDA Source Details.

**Compare:** add cooked white rice, brown rice, and quinoa. Open Compare Foods,
choose More protein, and click Ask CeCe. Try different portions and see how the
comparison changes.

## Sources, care, and credits

Nutrition comes from [USDA FoodData Central](https://fdc.nal.usda.gov/). The current
catalog is a static sample of **30 SR Legacy and 6 Branded records**, retrieved
October 10, 2026—not live USDA search or comprehensive product coverage.
Missing nutrients remain **Unknown**, never assumed to be zero.

CeCe does not classify foods as allergy-safe, gluten-free, vegan, or medically
suitable. AI explanations can be wrong and are not personalized medical advice;
check important claims against the displayed sources.

Food photos are representative, not exact preparation or branded product images.
See [photo credits and licenses](assets/foods/photos/CREDITS.md),
[food illustration licensing](assets/foods/LICENSE.txt), and
[artwork and engineering notes](docs/engineering-history.md#artwork-and-licensing).

## For developers

- [Code walkthrough and architecture](docs/developer-walkthrough.md)
- [USDA schema, sources, and regeneration](data/README.md)
- [Preparation script usage](scripts/README.md)
- [Engineering notes and safeguards](docs/engineering-history.md)

Run the automated checks:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

API tests use mocked responses and make no paid requests. Browser appearance and
live recommendation quality still need manual review.
