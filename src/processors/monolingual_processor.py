import polars as pl

from loaders import (
    load_txt_chunks,
    load_csv_batches,
    load_html_chunks,
    load_json_chunks
)

from cleaners import (
    clean_text_column
)

from language_detector import (
    detect_language
)

from exceptions import (
    DatasetSchemaError
)

def process_monolingual_file(
    path,
    writer
):

    if path.endswith(".txt"):

        chunk_iterator = load_txt_chunks(path)

    elif path.endswith(".csv"):

        chunk_iterator = load_csv_batches(path)

    elif (

        path.endswith(".html")

        or

        path.endswith(".htm")

    ):

        chunk_iterator = load_html_chunks(path)


    elif path.endswith(".json"):

        chunk_iterator = load_json_chunks(path)

    else:

        return 0

    total_rows = 0

    detected_language = None

    for df in chunk_iterator:

        if "text" not in df.columns:
            raise DatasetSchemaError(
                f"'text' column missing in {path}"
            )


        if detected_language is None:

            sample = (

                df[0, "text"]

                if len(df) > 0

                else ""
            )

            detected_language = detect_language(
                sample
            )

        if "segment_id" not in df.columns:

            df = df.with_columns(

                pl.lit("")
                .alias(
                    "segment_id"
                )
            )

        df = df.with_columns([

            pl.lit(
                detected_language
            )

            .alias(
                "language"
            ),

            pl.lit(
                "monolingual"
            )

            .alias(
                "dataset_type"
            )
        ])

        df = clean_text_column(

            df,

            "text"
        )

        required_columns = [

            "segment_id",

            "text",

            "language",

            "dataset_type"
        ]

        df = df.select(
            required_columns
        )

        writer.write(df)

        total_rows += len(df)

    return total_rows