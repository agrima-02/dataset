import json
import os

from exceptions import (
    DatasetCheckpointError
)

CHECKPOINT_FILE = (
    "../data/checkpoints/processed_files.json"
)


def load_checkpoint():

    if not os.path.exists(
        CHECKPOINT_FILE
    ):

        return set()

    try:

        with open(
            CHECKPOINT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return set(
                json.load(file)
            )

    except Exception as e:

        raise DatasetCheckpointError(
            f"Failed loading checkpoint: {e}"
        )


def save_checkpoint(
    processed_files
):

    os.makedirs(

        os.path.dirname(
            CHECKPOINT_FILE
        ),

        exist_ok=True
    )

    try:

        with open(

            CHECKPOINT_FILE,

            "w",

            encoding="utf-8"
        ) as file:

            json.dump(

                sorted(
                    list(
                        processed_files
                    )
                ),

                file,

                ensure_ascii=False,

                indent=2
            )

    except Exception as e:

        raise DatasetCheckpointError(
            f"Failed saving checkpoint: {e}"
        )


def mark_processed(
    filename,
    processed_files
):

    processed_files.add(
        filename
    )

    save_checkpoint(
        processed_files
    )