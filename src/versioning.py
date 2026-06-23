import json
from datetime import datetime


def save_metadata(
    output_path,
    dataset_type,
    row_count
):

    metadata = {
        'dataset_type': dataset_type,
        'row_count': row_count,
        'created_at': datetime.utcnow().isoformat()
    }

    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=4)
