import re
import unicodedata
import polars as pl

PAGE = re.compile(
    r'\[.*?page.*?\]',
    re.IGNORECASE
)

MULTISPACE = re.compile(r'\s+')

UNWANTED = [
    'copyright',
    'isbn',
    'gretil',
    'disclaimer'
]
def normalize_text(text):
    text = unicodedata.normalize(
        'NFKC',
        str(text)
    )

    text = PAGE.sub(' ', text)
    text = MULTISPACE.sub(
        ' ',
        text
    )
    return text.strip()

def valid_text(text):
    if not text:
        return False
    text = text.strip()
    if len(text) < 3:
        return False
    lower = text.lower()

    for pattern in UNWANTED:
        if pattern in lower:
            return False
    return True

def clean_text_column(df, column):
    return (
        df
        .with_columns(
            pl.col(column)
            .map_elements(normalize_text)
        )
        .filter(
            pl.col(column)
            .map_elements(valid_text)
        )
    )
