import pandas as pd
import json
from bs4 import BeautifulSoup


# Load CSV files
def load_csv(path):

    return pd.read_csv(
        path,
        encoding="utf-8"
    )


# Load TSV files
def load_tsv(path):

    return pd.read_csv(
        path,
        sep="\t",
        encoding="utf-8"
    )


# Load TXT files
def load_txt(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    # Split into lines
    lines = text.split("\n")

    # Remove empty lines
    lines = [
        line.strip()
        for line in lines
        if line.strip()
    ]

    df = pd.DataFrame({
        "text": lines
    })

    return df


# Load HTML / HTM files
def load_html(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        soup = BeautifulSoup(
            file,
            "lxml"
        )

    # Extract readable text
    text = soup.get_text(
        separator="\n"
    )

    # Split into lines
    lines = text.split("\n")

    # Remove empty lines
    lines = [
        line.strip()
        for line in lines
        if line.strip()
    ]

    df = pd.DataFrame({
        "text": lines
    })

    return df


# Load JSON files
# Load JSON files
def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # CASE 1:
    # List of dictionaries
    if isinstance(data, list):

        df = pd.DataFrame(data)

    # CASE 2:
    # Dictionary JSON
    elif isinstance(data, dict):

        # If values are strings
        if all(
            isinstance(v, str)
            for v in data.values()
        ):

            rows = []

            for key, value in data.items():

                rows.append({
                    "segment_id": key,
                    "text": value
                })

            df = pd.DataFrame(rows)

        else:

            df = pd.json_normalize(data)

    else:

        raise ValueError(
            "Unsupported JSON structure"
        )

    return df