import json
from datetime import datetime


def save_stats(
    row_count,
    output_path,
    extra_stats=None
):

    stats = {

        "rows": row_count,

        "generated_at": datetime.utcnow().isoformat(),

        "pipeline_version": "v4"
    }

    if extra_stats:

        stats.update(
            extra_stats
        )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(

            stats,

            f,

            ensure_ascii=False,

            indent=4
        )