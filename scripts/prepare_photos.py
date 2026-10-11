"""Offline optimization of the reviewed photo library from source JPEGs.

Download each approved metadata download_url to <source-dir>/<photo-key>.jpg.
This script adds no network access and does not discover or approve new photos.
"""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def prepare_photos(source_dir: Path) -> None:
    photo_dir = ROOT / 'assets/foods/photos'
    catalog_path = photo_dir / 'metadata.json'
    catalog = json.loads(catalog_path.read_text())
    for key in catalog['photos']:
        if not (source_dir / f'{key}.jpg').is_file():
            raise FileNotFoundError(f'Missing reviewed source photograph: {key}.jpg')
    for key, metadata in catalog['photos'].items():
        source = source_dir / f'{key}.jpg'
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original).convert('RGB')
        if key == 'tofu':
            width, height = image.size
            image = image.crop((int(width*.2), int(height*.15), int(width*.8), int(height*.85)))
        for field, checksum, size in [('path', 'sha256', (720, 480)), ('thumbnail_path', 'thumbnail_sha256', (240, 160))]:
            target = ROOT / metadata[field]
            ImageOps.fit(image, size, method=Image.Resampling.LANCZOS).save(target, quality=82, method=6)
            metadata[checksum] = hashlib.sha256(target.read_bytes()).hexdigest()
        metadata['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    catalog_path.write_text(json.dumps(catalog, indent=2) + '\n')
    print(f"Optimized {len(catalog['photos'])} approved photographs and thumbnails.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    prepare_photos(parser.parse_args().source_dir)
