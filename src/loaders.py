import polars as pl
import ijson
import re

from exceptions import (
    DatasetLoadError
)

DEFAULT_BATCH_SIZE = 100000


def load_txt_chunks(
    path,
    chunk_size=DEFAULT_BATCH_SIZE
):

    try:

        batch = []

        with open(
            path,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                batch.append({
                    "text": line
                })

                if len(batch) >= chunk_size:

                    yield pl.DataFrame(batch)

                    batch = []

        if batch:

            yield pl.DataFrame(batch)

    except FileNotFoundError:

        raise DatasetLoadError(
            f"File not found: {path}"
        )

    except PermissionError:

        raise DatasetLoadError(
            f"Permission denied: {path}"
        )

    except Exception as e:

        raise DatasetLoadError(
            f"TXT loader failed for {path}: {e}"
        )


def load_csv_batches(
    path,
    batch_size=DEFAULT_BATCH_SIZE
):

    try:

        reader = pl.read_csv_batched(
            path,
            batch_size=batch_size
        )

        while True:

            batches = reader.next_batches(1)

            if not batches:
                break

            yield batches[0]

    except Exception as e:

        raise DatasetLoadError(
            f"CSV loader failed for {path}: {e}"
        )


def load_tsv_batches(
    path,
    batch_size=DEFAULT_BATCH_SIZE
):

    try:

        reader = pl.read_csv_batched(
            path,
            separator="\t",
            batch_size=batch_size
        )

        while True:

            batches = reader.next_batches(1)

            if not batches:
                break

            yield batches[0]

    except Exception as e:

        raise DatasetLoadError(
            f"TSV loader failed for {path}: {e}"
        )


HTML_TAG_PATTERN = re.compile(
    r"<[^>]+>"
)


def load_html_chunks(
    path,
    chunk_size=DEFAULT_BATCH_SIZE
):

    try:

        batch = []

        with open(
            path,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as file:

            for line in file:

                line = HTML_TAG_PATTERN.sub(
                    " ",
                    line
                )

                line = line.strip()

                if not line:
                    continue

                batch.append({
                    "text": line
                })

                if len(batch) >= chunk_size:

                    yield pl.DataFrame(batch)

                    batch = []

        if batch:

            yield pl.DataFrame(batch)

    except Exception as e:

        raise DatasetLoadError(
            f"HTML loader failed for {path}: {e}"
        )


def load_json_chunks(
    path,
    chunk_size=DEFAULT_BATCH_SIZE
):

    try:

        batch = []

        with open(
            path,
            "rb"
        ) as file:

            parser = ijson.kvitems(
                file,
                ""
            )

            for key, value in parser:

                batch.append({

                    "segment_id": str(key),

                    "text": str(value)
                })

                if len(batch) >= chunk_size:

                    yield pl.DataFrame(batch)

                    batch = []

        if batch:

            yield pl.DataFrame(batch)

    except Exception as e:

        raise DatasetLoadError(
            f"JSON loader failed for {path}: {e}"
        )