import polars as pl
import orjson

from cleaners import (
    normalize_text,
    valid_text
)

from language_detector import (
    detect_language
)


def load_segment_json(path):

    with open(
        path,
        "rb"
    ) as file:

        data = orjson.loads(
            file.read()
        )

    rows = []

    for segment_id, text in data.items():

        rows.append({

            "segment_id":
            segment_id,

            "text":
            text
        })

    return pl.DataFrame(rows)


def process_parallel_table(path):

    df = pl.read_csv(
        path,
        separator="\t"
    )

    required = [

        "src_original",
        "tgt_original"
    ]

    if not all(
        col in df.columns
        for col in required
    ):

        return None

    df = df.rename({

        "src_segmentnr":
        "src_segment_id",

        "tgt_segmentnr":
        "tgt_segment_id",

        "src_original":
        "src_text",

        "tgt_original":
        "tgt_text"
    })

    df = df.with_columns([

        pl.col("src_text")
        .map_elements(
            normalize_text
        ),

        pl.col("tgt_text")
        .map_elements(
            normalize_text
        )
    ])

    df = df.filter(

        pl.col("src_text")
        .map_elements(valid_text)

    ).filter(

        pl.col("tgt_text")
        .map_elements(valid_text)

    )

    if len(df) == 0:
        return None

    src_lang = detect_language(
        df[0, "src_text"]
    )

    tgt_lang = detect_language(
        df[0, "tgt_text"]
    )

    df = df.with_columns([

        pl.lit(src_lang)
        .alias("src_language"),

        pl.lit(tgt_lang)
        .alias("tgt_language"),

        pl.lit("parallel")
        .alias("dataset_type")
    ])

    required_columns = [

        'src_segment_id',

        'tgt_segment_id',

        'src_text',

        'tgt_text',

        'src_language',

        'tgt_language',

        'dataset_type'
    ]

    df = df.select(required_columns)

    return df


def build_parallel_from_segments(
    src_path,
    tgt_path
):

    src_df = load_segment_json(
        src_path
    )

    tgt_df = load_segment_json(
        tgt_path
    )

    src_df = src_df.rename({

        "text":
        "src_text"
    })

    tgt_df = tgt_df.rename({

        "text":
        "tgt_text"
    })

    aligned = src_df.join(

        tgt_df,

        on="segment_id",

        how="inner"
    )

    aligned = aligned.rename({

        "segment_id":
        "src_segment_id"
    })

    aligned = aligned.with_columns(

        pl.col("src_segment_id")
        .alias("tgt_segment_id")
    )

    aligned = aligned.with_columns([

        pl.col("src_text")
        .map_elements(
            normalize_text
        ),

        pl.col("tgt_text")
        .map_elements(
            normalize_text
        )
    ])

    aligned = aligned.filter(

        pl.col("src_text")
        .map_elements(valid_text)

    ).filter(

        pl.col("tgt_text")
        .map_elements(valid_text)

    )

    if len(aligned) == 0:
        return None

    src_lang = detect_language(
        aligned[0, "src_text"]
    )

    tgt_lang = detect_language(
        aligned[0, "tgt_text"]
    )

    aligned = aligned.with_columns([

        pl.lit(src_lang)
        .alias("src_language"),

        pl.lit(tgt_lang)
        .alias("tgt_language"),

        pl.lit("parallel")
        .alias("dataset_type")
    ])

    required_columns = [

        'src_segment_id',

        'tgt_segment_id',

        'src_text',

        'tgt_text',

        'src_language',

        'tgt_language',

        'dataset_type'
    ]

    aligned = aligned.select(
        required_columns
    )

    return aligned