import os
import pandas as pd

from loaders import (
    load_csv,
    load_tsv,
    load_json,
    load_txt,
    load_html
)

from cleaners import (
    clean_dataframe
)

from validators import (
    validate_dataframe
)

from exporters import (
    export_csv,
    export_parquet,
    export_arrow,
    export_huggingface
)


RAW_FOLDER = "../data/raw"

PROCESSED_FOLDER = "../data/processed"

all_dfs = []


for file in os.listdir(RAW_FOLDER):

    path = os.path.join(
        RAW_FOLDER,
        file
    )

    try:

        # CSV
        if file.endswith(".csv"):

            df = load_csv(path)

        # TSV
        elif file.endswith(".tsv"):

            df = load_tsv(path)

        # JSON
        elif file.endswith(".json"):

            df = load_json(path)

        # TXT
        elif file.endswith(".txt"):

            df = load_txt(path)

        # HTML / HTM
        elif (
            file.endswith(".html")
            or file.endswith(".htm")
        ):

            df = load_html(path)

        else:

            print(
                f"Skipping unsupported file: {file}"
            )

            continue

        # Detect parallel corpus
        if (
            "src_original" in df.columns
            and "tgt_original" in df.columns
        ):

            df["dataset_type"] = "parallel"

            df["src_language"] = (
                "Sanskrit"
            )

            df["tgt_language"] = (
                "Tibetan"
            )

        else:

            df["dataset_type"] = (
                "monolingual"
            )

        # Monolingual fallback
        if (
            "text" not in df.columns
            and "src_original" not in df.columns
        ):

            first_column = (
                df.columns[0]
            )

            df = df.rename(
                columns={
                    first_column: "text"
                }
            )

        # Add metadata
        df["source_file"] = file

        # Language tagging
        if "pali" in file.lower():

            df["language"] = "Pali"

        elif "sanskrit" in file.lower():

            df["language"] = "Sanskrit"

        elif "tibetan" in file.lower():

            df["language"] = "Tibetan"

        elif "chinese" in file.lower():

            df["language"] = "Chinese"

        else:

            df["language"] = "Unknown"

        # Clean dataset
        df = clean_dataframe(df)

        # Validate dataset
        validate_dataframe(df)

        # Store dataframe
        all_dfs.append(df)

        print(
            f"Processed: {file}"
        )

    except Exception as e:

        print(
            f"Error processing {file}: {e}"
        )


# Merge all datasets
final_df = pd.concat(
    all_dfs,
    ignore_index=True
)

# Export CSV
export_csv(
    final_df,
    f"{PROCESSED_FOLDER}/final_dataset.csv"
)

# Export Parquet
export_parquet(
    final_df,
    f"{PROCESSED_FOLDER}/final_dataset.parquet"
)

# Export Arrow
export_arrow(
    final_df,
    f"{PROCESSED_FOLDER}/final_dataset.arrow"
)

# Export Hugging Face dataset
export_huggingface(
    final_df,
    f"{PROCESSED_FOLDER}/hf_dataset"
)

print(
    "Pipeline completed successfully"
)