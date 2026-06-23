import polars as pl
import unicodedata


UNWANTED = [

    "copyright",

    "isbn",

    "gretil",

    "disclaimer"
]


def normalize_unicode(text):

    if text is None:

        return ""

    return unicodedata.normalize(
        "NFKC",
        str(text)
    )


def clean_text_column(
    df,
    column
):

    # Unicode normalization
    # (still requires Python)

    df = df.with_columns(

        pl.col(column)

        .map_elements(
            normalize_unicode,
            return_dtype=pl.Utf8
        )
    )

    # Everything below stays inside Polars/Rust

    df = df.with_columns(

        pl.col(column)

        .str.replace_all(
            r"\[.*?page.*?\]",
            ""
        )

        .str.replace_all(
            r"\s+",
            " "
        )

        .str.strip_chars()
    )

    # Remove empty text

    df = df.filter(

        pl.col(column)

        .str.len_chars()

        >= 3
    )

    # Remove unwanted metadata rows

    for pattern in UNWANTED:

        df = df.filter(

            ~pl.col(column)

            .str.to_lowercase()

            .str.contains(pattern)
        )

    return df