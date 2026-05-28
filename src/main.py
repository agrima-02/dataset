import os
import polars as pl

from logger import setup_logger
from config import CONFIG
from path_validator import validate_paths

from loaders import (
    load_txt_stream,
    load_json,
    load_html,
    load_csv,
    load_tsv
)

from cleaners import (
    clean_text_column
)

from exporters import (
    StreamingParquetWriter
)

from language_detector import (
    detect_language
)

from statistics import (
    save_stats
)

from versioning import (
    save_metadata
)

from parallel_builder import (

    process_parallel_table,

    build_parallel_from_segments
)


logger = setup_logger()
RAW_FOLDER = CONFIG['raw_folder']
OUTPUT_FOLDER = CONFIG['processed_folder']

def process_monolingual(path):
    try:
        # TXT
        if path.endswith('.txt'):
            rows = list(
                load_txt_stream(path)
            )
            df = pl.DataFrame(rows)
        # JSON
        elif path.endswith('.json'):
            df = load_json(path)
        # HTML
        elif (
            path.endswith('.html')
            or path.endswith('.htm')
        ):
            df = load_html(path)
        # CSV
        elif path.endswith('.csv'):
            df = load_csv(path)

        else:
            return None

        if 'text' not in df.columns:
            return None

        sample = (
            df[0, 'text']
            if len(df) > 0
            else ''
        )
        language = detect_language(
            sample
        )
        required_columns = [
            'segment_id',
            'text',
            'language',
            'dataset_type'
        ]

        if 'segment_id' not in df.columns:
            df = df.with_columns(
                pl.lit("")
                .cast(pl.Utf8)
                .alias('segment_id')
            )

        else:
            df = df.with_columns(
                pl.col('segment_id')
                .cast(pl.Utf8)
            )
        df = df.with_columns([
            pl.lit(language)
            .alias('language'),
            pl.lit('monolingual')
            .alias('dataset_type')
        ])

        df = df.select(
            required_columns
        )

        df = df.with_columns([
            pl.col('segment_id')
            .cast(pl.Utf8),
            pl.col('text')
            .cast(pl.Utf8),
            pl.col('language')
            .cast(pl.Utf8),
            pl.col('dataset_type')
            .cast(pl.Utf8)
        ])

        df = clean_text_column(
            df,
            'text'
        )
        return df

    except FileNotFoundError as e:
        logger.error(e)

    except PermissionError as e:
        logger.error(e)

    except UnicodeDecodeError as e:
        logger.error(e)

    except ValueError as e:
        logger.error(e)

    except Exception as e:
        logger.exception(e)

    return None

if __name__ == '__main__':
    validate_paths(
        RAW_FOLDER,
        OUTPUT_FOLDER
    )
    mono_writer = StreamingParquetWriter(
        f'{OUTPUT_FOLDER}/mono.parquet'
    )

    parallel_writer = StreamingParquetWriter(
        f'{OUTPUT_FOLDER}/parallel.parquet'
    )

    total_mono_rows = 0
    total_parallel_rows = 0

    files = os.listdir(
        RAW_FOLDER
    )

    processed_segment_pairs = set()
    for file in files:
        path = os.path.join(
            RAW_FOLDER,
            file
        )
        # =========================
        # TSV PARALLEL TABLES
        # =========================

        if file.endswith(".tsv"):
            df = process_parallel_table(
                path
            )
            if df is not None:
                parallel_writer.write(df)
                total_parallel_rows += len(df)
                logger.info(
                    f'Processed parallel TSV: {file}'
                )
            continue
        # =========================
        # GENERIC SEGMENT JSON PAIRS
        # =========================

        if "_root-" in file:
            prefix = file.split("_root-")[0]
            translation_file = None
            for other in files:
                if (
                    other.startswith(prefix)
                    and "_translation-" in other
                ):
                    translation_file = other
                    break
            
            if translation_file is None:
                continue

            pair_key = (
                file,
                translation_file
            )

            if pair_key in processed_segment_pairs:
                continue

            aligned = build_parallel_from_segments(
                os.path.join(
                    RAW_FOLDER,
                    file
                ),

                os.path.join(
                    RAW_FOLDER,
                    translation_file
                )
            )

            if aligned is not None:
                parallel_writer.write(
                    aligned
                )
                total_parallel_rows += len(
                    aligned
                )
                logger.info(
                    f'Processed segment pair: '
                    f'{file} <-> {translation_file}'
                )
            processed_segment_pairs.add(
                pair_key
            )

            continue
        # =========================
        # MONOLINGUAL
        # =========================

        df = process_monolingual(
            path
        )
        if df is None:
            continue

        mono_writer.write(df)
        total_mono_rows += len(df)

        logger.info(
            f'Processed mono: {file}'
        )

    mono_writer.close()
    parallel_writer.close()
    save_metadata(
        f'{OUTPUT_FOLDER}/mono_metadata.json',
        'monolingual',
        total_mono_rows
    )

    save_metadata(
        f'{OUTPUT_FOLDER}/parallel_metadata.json',
        'parallel',
        total_parallel_rows
    )

    save_stats(
        total_mono_rows,
        f'{OUTPUT_FOLDER}/mono_stats.json'
    )

    save_stats(
        total_parallel_rows,
        f'{OUTPUT_FOLDER}/parallel_stats.json'
    )

    logger.info(
        'Pipeline completed'
    )
