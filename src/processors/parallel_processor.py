import polars as pl

from loaders import (
    load_tsv_batches,
    load_json_chunks
)

from cleaners import (
    clean_text_column
)

from language_detector import (
    detect_language
)

from ai_filters import (
    get_embeddings
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)

from exceptions import (
    DatasetSchemaError,
)

import logging

logger = logging.getLogger(__name__)

def process_parallel_table(
    path,
    writer
):

    total_rows = 0

    detected_src_language = None

    detected_tgt_language = None

    for df in load_tsv_batches(path):

        required = [

            "src_original",

            "tgt_original"
        ]

        if not all(
            col in df.columns
            for col in required
        ):

            raise DatasetSchemaError(

                f"Required columns missing in {path}"
            )

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

        df = clean_text_column(
            df,
            "src_text"
        )

        df = clean_text_column(
            df,
            "tgt_text"
        )

        if len(df) == 0:
            continue

        sample_size = min(
            100,
            len(df)
        )

        if sample_size > 0:

            try:

                src_embeddings = get_embeddings(

                    df["src_text"]
                    .head(sample_size)
                    .to_list()
                )

                tgt_embeddings = get_embeddings(

                    df["tgt_text"]
                    .head(sample_size)
                    .to_list()
                )

                similarities = [

                    cosine_similarity(
                        [src_embeddings[i]],
                        [tgt_embeddings[i]]
                    )[0][0]

                    for i in range(sample_size)
                ]

                avg_similarity = (
                    sum(similarities)
                    /
                    len(similarities)
                )

                logger.info(
                    f"LaBSE similarity ({path}): "
                    f"{avg_similarity:.3f}"
                )

            except Exception as e:

                logger.warning(
                    f"LaBSE failed ({path}): {e}"
                )
                
        if detected_src_language is None:

            detected_src_language = detect_language(
                df[0, "src_text"]
            )

        if detected_tgt_language is None:

            detected_tgt_language = detect_language(
                df[0, "tgt_text"]
            )

        df = df.with_columns([

            pl.lit(
                detected_src_language
            ).alias(
                "src_language"
            ),

            pl.lit(
                detected_tgt_language
            ).alias(
                "tgt_language"
            ),

            pl.lit(
                "parallel"
            ).alias(
                "dataset_type"
            )
        ])

        required_columns = [

            "src_segment_id",

            "tgt_segment_id",

            "src_text",

            "tgt_text",

            "src_language",

            "tgt_language",

            "dataset_type"
        ]

        df = df.select(
            required_columns
        )

        writer.write(df)

        total_rows += len(df)

    return total_rows


def build_parallel_from_segments(
    src_path,
    tgt_path,
    writer
):

    src_chunks = load_json_chunks(
        src_path
    )

    tgt_chunks = load_json_chunks(
        tgt_path
    )

    total_rows = 0

    detected_src_language = None

    detected_tgt_language = None

    for src_df, tgt_df in zip(
        src_chunks,
        tgt_chunks
    ):

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
        if len(aligned) == 0:

            logger.warning(
                f"No matching IDs: {src_path} <-> {tgt_path}"
            )

            return 0

        aligned = aligned.rename({

            "segment_id":
            "src_segment_id"
        })

        aligned = aligned.with_columns(

            pl.col(
                "src_segment_id"
            ).alias(
                "tgt_segment_id"
            )
        )

        aligned = clean_text_column(

            aligned,

            "src_text"
        )

        aligned = clean_text_column(

            aligned,

            "tgt_text"
        )

        if len(aligned) == 0:
            continue
        sample_size = min(
            100,
            len(aligned)
        )

        if sample_size > 0:

            try:

                src_embeddings = get_embeddings(

                    aligned["src_text"]
                    .head(sample_size)
                    .to_list()
                )

                tgt_embeddings = get_embeddings(

                    aligned["tgt_text"]
                    .head(sample_size)
                    .to_list()
                )

                similarities = [

                    cosine_similarity(
                        [src_embeddings[i]],
                        [tgt_embeddings[i]]
                    )[0][0]

                    for i in range(sample_size)
                ]

                avg_similarity = (
                    sum(similarities)
                    /
                    len(similarities)
                )

                logger.info(

                    f"LaBSE similarity "

                    f"({src_path} <-> {tgt_path}): "

                    f"{avg_similarity:.3f}"
                )

            except Exception as e:

                logger.warning(

                    f"LaBSE failed "

                    f"({src_path} <-> {tgt_path}): "

                    f"{e}"
                )

        if detected_src_language is None:

            detected_src_language = detect_language(
                aligned[0, "src_text"]
            )

        if detected_tgt_language is None:

            detected_tgt_language = detect_language(

                aligned[0, "tgt_text"]
            )

        aligned = aligned.with_columns([

            pl.lit(
                detected_src_language
            ).alias(
                "src_language"
            ),

            pl.lit(
                detected_tgt_language
            ).alias(
                "tgt_language"
            ),

            pl.lit(
                "parallel"
            ).alias(
                "dataset_type"
            )
        ])

        required_columns = [

            "src_segment_id",

            "tgt_segment_id",

            "src_text",

            "tgt_text",

            "src_language",

            "tgt_language",

            "dataset_type"
        ]

        aligned = aligned.select(
            required_columns
        )

        writer.write(
            aligned
        )

        total_rows += len(
            aligned
        )

    return total_rows