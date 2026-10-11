"""Rebuild the curated dataset from saved USDA records or exact source archives."""

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from cece.data_access import ALL_NUTRIENTS, normalize_record, validate_foods


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_source(source: dict, archive_dir: Path, raw_dir: Path) -> None:
    archive = archive_dir / Path(urlparse(source["url"]).path).name
    with archive.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != source["archive_sha256"]:
        raise ValueError(f"Archive checksum mismatch: {archive}")
    wanted = set(source["fdc_ids"])
    with zipfile.ZipFile(archive) as zipped:
        filename = next(name for name in zipped.namelist() if name.endswith(".json"))
        with zipped.open(filename) as stream:
            if source["data_type"] == "SR Legacy":
                records = json.load(stream)[source["json_key"]]
            else:
                # USDA branded JSON has one full food object on each line.
                # Stream to avoid loading the multi-gigabyte archive into RAM.
                records = (
                    json.loads(line.decode("utf-8").strip().rstrip(","))
                    for line in stream if line.lstrip().startswith(b'{"foodClass"')
                )
            for record in records:
                if record["fdcId"] not in wanted:
                    continue
                (raw_dir / f"{record['fdcId']}.json").write_text(
                    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                wanted.remove(record["fdcId"])
                if not wanted:
                    break
    if wanted:
        raise ValueError(f"Records absent from archive: {sorted(wanted)}")


def prepare(data_dir: Path, archive_dir: Path | None = None) -> None:
    selection = json.loads((data_dir / "selection.json").read_text())
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    rows = []
    selected_ids = [fdc_id for source in selection["sources"] for fdc_id in source["fdc_ids"]]
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("Duplicate curated FDC IDs")
    for source in selection["sources"]:
        if archive_dir:
            extract_source(source, archive_dir, raw_dir)
        for fdc_id in source["fdc_ids"]:
            path = raw_dir / f"{fdc_id}.json"
            record = json.loads(path.read_text())
            if record["fdcId"] != fdc_id or record["dataType"] != source["data_type"]:
                raise ValueError(f"Selection/source mismatch: {fdc_id}")
            row = normalize_record(record, source["url"])
            row["raw_sha256"] = sha256(path)
            rows.append(row)
    frame = pd.DataFrame(rows).sort_values("fdc_id").reset_index(drop=True)
    validate_foods(frame)
    csv_path = data_dir / "foods.csv"
    frame.to_csv(csv_path, index=False, lineterminator="\n")
    manifest = {
        "schema_version": 2,
        "source": "USDA FoodData Central",
        "retrieval_date": selection["retrieved_on"],
        "record_count": len(frame),
        "data_type_counts": frame.data_type.value_counts().sort_index().to_dict(),
        "sha256": sha256(csv_path),
        "selection_sha256": sha256(data_dir / "selection.json"),
        "basis": "per 100 g; calories in kcal; sodium/cholesterol in mg; other nutrients in g",
        "nutrient_ids": {name: info[0] for name, info in ALL_NUTRIENTS.items()},
        "nutrient_units": {name: info[1] for name, info in ALL_NUTRIENTS.items()},
        "missing_counts": {name: int(frame[f"{name}_missing"].sum()) for name in ALL_NUTRIENTS},
        "sources": selection["sources"],
        "raw_sha256": {str(row["fdc_id"]): row["raw_sha256"] for row in rows},
        "limitations": [
            "SR Legacy is a historical snapshot, not current analytical coverage.",
            "Branded records are label-derived snapshots; values may reflect rounding.",
            "Missing nutrients are unknown, not zero. No dietary safety claims are made.",
            "Gram-unit branded records only; volume-unit products are excluded.",
        ],
    }
    (data_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Prepared {len(frame)} verified records; SHA-256 {manifest['sha256']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--archive-dir", type=Path, help="Optional folder containing exact USDA ZIPs listed in selection.json")
    args = parser.parse_args()
    prepare(args.data_dir, args.archive_dir)
