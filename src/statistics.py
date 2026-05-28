import json


def save_stats(
    row_count,
    output_path
):

    stats = {
        'rows': row_count
    }

    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=4)
