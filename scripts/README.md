# Dataset preparation

`prepare_dataset.py` builds `data/foods.csv` and `data/manifest.json` from the fixed selection and original USDA records. It verifies identity, type, units, basis, missing indicators and plausible nutrient ranges before writing outputs. Optional `--archive-dir` re-extracts the same records from checksum-verified USDA ZIPs; it never requires an API key or downloads automatically. See `data/README.md` for exact commands and source limitations.
