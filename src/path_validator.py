from pathlib import Path


def validate_paths(raw_folder, processed_folder):

    raw = Path(raw_folder)
    processed = Path(processed_folder)

    if not raw.exists():
        raise FileNotFoundError(
            f'Raw folder missing: {raw_folder}'
        )

    processed.mkdir(
        parents=True,
        exist_ok=True
    )
