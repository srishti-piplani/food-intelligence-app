# Preparation scripts

Run these commands from the repository root using the installed project environment.
They operate on local files and do not automatically download data or photographs.

## Rebuild the USDA catalog

```sh
.venv/bin/python scripts/prepare_dataset.py
```

`prepare_dataset.py` reads `data/selection.json` and the bundled original records,
then writes `data/foods.csv` and `data/manifest.json`. It validates identity, data
type, expected units, the nutrient basis, missing indicators and plausible ranges.
The manifest preserves acquisition metadata, source references and checksums.

To re-extract the same selected records from downloaded source ZIPs:

```sh
.venv/bin/python scripts/prepare_dataset.py --archive-dir ../cece-usda-archives
```

The directory must contain the exact archives listed in the selection. Hashes
are verified before extraction; no USDA API key is required. See
[dataset documentation](../data/README.md) for download commands and limitations.
An optional `--data-dir` chooses a different directory containing the selection
and raw records, so preparation can be performed on a separate copy.

## Rebuild reviewed food photographs

```sh
.venv/bin/python scripts/prepare_photos.py --source-dir ../cece-photo-sources
```

Supply the eight approved source JPEGs as `<photo-key>.jpg`, using the entries in
[photo metadata](../assets/foods/photos/metadata.json). The script checks that all
required files exist, corrects orientation, applies crops, writes optimized
720 × 480 WebP images and 240 × 160 thumbnails, and updates image hashes.
It does not approve or discover new photos. Original JPEGs are not bundled;
normal application use relies on the included derivatives and needs no rebuild.
Preserve the [photo credits and license conditions](../assets/foods/photos/CREDITS.md).

## Check the results

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Tests cover source correspondence, schema, calculations and deterministic dataset
regeneration. API tests use mocked responses and make no paid calls.
