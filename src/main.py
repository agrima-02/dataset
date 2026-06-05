import os
import torch

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from logger import setup_logger
from config import CONFIG
from path_validator import validate_paths

from exporters import (
    StreamingParquetWriter
)

from statistics import (
    save_stats
)

from versioning import (
    save_metadata
)

from checkpoint import (
    load_checkpoint,
    mark_processed
)

from processors.monolingual_processor import (
    process_monolingual_file
)

from processors.parallel_processor import (
    process_parallel_table,
    build_parallel_from_segments
)

from exceptions import (

    DatasetLoadError,

    DatasetSchemaError,

    DatasetAlignmentError,

    DatasetValidationError,

    DatasetWriteError,

    DatasetCheckpointError,

    DatasetLanguageError
)

logger = setup_logger()

logger.info(

    f"GPU Available: "

    f"{torch.cuda.is_available()}"
)

if torch.cuda.is_available():

    logger.info(

        f"GPU: "

        f"{torch.cuda.get_device_name(0)}"
    )
    
RAW_FOLDER = CONFIG["raw_folder"]

OUTPUT_FOLDER = CONFIG["processed_folder"]

MAX_WORKERS = min(
    os.cpu_count() or 4,
    8
)


def find_segment_pairs(files):

    pairs = []

    for file in files:

        if "_root-" not in file:
            continue

        prefix = file.split(
            "_root-"
        )[0]

        for other in files:

            if (

                other.startswith(prefix)

                and

                "_translation-" in other

            ):

                pairs.append(
                    (file, other)
                )

                break

    return pairs


if __name__ == "__main__":

    validate_paths(

        RAW_FOLDER,

        OUTPUT_FOLDER
    )

    files = os.listdir(
        RAW_FOLDER
    )

    processed_files = (
        load_checkpoint()
    )

    mono_files = []

    parallel_tsv_files = []

    for file in files:

        if file.endswith(".tsv"):

            parallel_tsv_files.append(
                file
            )

        elif (

            "_root-" not in file

            and

            "_translation-" not in file

        ):

            mono_files.append(
                file
            )

    segment_pairs = find_segment_pairs(
        files
    )

    total_mono_rows = 0

    total_parallel_rows = 0

    with StreamingParquetWriter(

        f"{OUTPUT_FOLDER}/mono.parquet"

    ) as mono_writer, StreamingParquetWriter(

        f"{OUTPUT_FOLDER}/parallel.parquet"

    ) as parallel_writer:

        # ====================
        # MONOLINGUAL FILES
        # ====================

        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor:

            future_to_file = {

                executor.submit(

                    process_monolingual_file,

                    os.path.join(
                        RAW_FOLDER,
                        file
                    ),

                    mono_writer

                ): file

                for file in mono_files

                if file not in processed_files
            }

            for future in as_completed(
                future_to_file
            ):

                file = future_to_file[
                    future
                ]

                try:

                    rows = future.result()

                    total_mono_rows += rows

                    mark_processed(

                        file,

                        processed_files
                    )

                    logger.info(

                        f"Completed mono: {file}"
                    )

                except DatasetLoadError:

                    logger.exception(
                        f"Load failed: {file}"
                    )

                except DatasetSchemaError:

                    logger.exception(
                        f"Schema failed: {file}"
                    )

                except DatasetValidationError:

                    logger.exception(
                        f"Validation failed: {file}"
                    )

                except Exception:

                    logger.exception(
                        f"Unexpected error: {file}"
                    )
                except DatasetWriteError:

                    logger.exception(
                        f"Write failed: {file}"
                    )

                except DatasetCheckpointError:

                    logger.exception(
                        f"Checkpoint failed: {file}"
                    )

                except DatasetLanguageError:

                    logger.exception(
                        f"Language detection failed: {file}"
                    )

        # ====================
        # PARALLEL TSV FILES
        # ====================

        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor:

            future_to_file = {

                executor.submit(

                    process_parallel_table,

                    os.path.join(
                        RAW_FOLDER,
                        file
                    ),

                    parallel_writer

                ): file

                for file in parallel_tsv_files

                if file not in processed_files
            }

            for future in as_completed(
                future_to_file
            ):

                file = future_to_file[
                    future
                ]

                try:

                    rows = future.result()

                    total_parallel_rows += rows

                    mark_processed(

                        file,

                        processed_files
                    )

                    logger.info(

                        f"Completed parallel TSV: {file}"
                    )

                except DatasetLoadError:

                    logger.exception(
                        f"Load failed: {file}"
                    )

                except DatasetSchemaError:

                    logger.exception(
                        f"Schema failed: {file}"
                    )

                except DatasetValidationError:

                    logger.exception(
                        f"Validation failed: {file}"
                    )

                except DatasetWriteError:

                    logger.exception(
                        f"Write failed: {file}"
                    )

                except DatasetCheckpointError:

                    logger.exception(
                        f"Checkpoint failed: {file}"
                    )

                except DatasetLanguageError:

                    logger.exception(
                        f"Language detection failed: {file}"
                    )

                except Exception:

                    logger.exception(
                        f"Unexpected error: {file}"
                    )
        # ====================
        # SEGMENT ALIGNMENT
        # ====================

        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor:

            future_to_pair = {

                executor.submit(

                    build_parallel_from_segments,

                    os.path.join(
                        RAW_FOLDER,
                        src_file
                    ),

                    os.path.join(
                        RAW_FOLDER,
                        tgt_file
                    ),

                    parallel_writer

                ): (src_file, tgt_file)

                for src_file, tgt_file in segment_pairs

                if not (

                    src_file in processed_files

                    and

                    tgt_file in processed_files
                )
            }

            for future in as_completed(
                future_to_pair
            ):

                src_file, tgt_file = (

                    future_to_pair[
                        future
                    ]
                )

                try:

                    rows = future.result()

                    total_parallel_rows += rows

                    mark_processed(
                        src_file,
                        processed_files
                    )

                    mark_processed(
                        tgt_file,
                        processed_files
                    )

                    logger.info(

                        f"Completed segment pair: "

                        f"{src_file} <-> {tgt_file}"
                    )

                except DatasetLoadError:

                    logger.exception(

                        f"Load failed: "

                        f"{src_file} <-> {tgt_file}"
                    )

                except DatasetSchemaError:

                    logger.exception(

                        f"Schema failed: "

                        f"{src_file} <-> {tgt_file}"
                    )

                except DatasetAlignmentError:

                    logger.exception(

                        f"Alignment failed: "

                        f"{src_file} <-> {tgt_file}"
                    )

                except DatasetValidationError:

                    logger.exception(

                        f"Validation failed: "

                        f"{src_file} <-> {tgt_file}"
                    )

                except DatasetWriteError:

                    logger.exception(

                        f"Write failed: "

                        f"{src_file} <-> {tgt_file}"
                    )

                except DatasetCheckpointError:

                    logger.exception(

                        f"Checkpoint failed: "

                        f"{src_file} <-> {tgt_file}"
                    )

                except DatasetLanguageError:

                    logger.exception(

                        f"Language detection failed: "

                        f"{src_file} <-> {tgt_file}"
                    )

                except Exception:

                    logger.exception(

                        f"Unexpected error: "

                        f"{src_file} <-> {tgt_file}"
                    )

    try:

        save_metadata(

            f"{OUTPUT_FOLDER}/mono_metadata.json",

            "monolingual",

            total_mono_rows
        )

        save_metadata(

            f"{OUTPUT_FOLDER}/parallel_metadata.json",

            "parallel",

            total_parallel_rows
        )

        save_stats(

            total_mono_rows,

            f"{OUTPUT_FOLDER}/mono_stats.json"
        )

        save_stats(

            total_parallel_rows,

            f"{OUTPUT_FOLDER}/parallel_stats.json"
        )

    except Exception:

        logger.exception(
            "Failed saving metadata/stats"
        )