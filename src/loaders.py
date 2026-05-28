import polars as pl
import orjson
from selectolax.parser import HTMLParser

def load_txt_stream(path):
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                yield {'text': line}

def load_json(path):
    with open(path, 'rb') as file:
        data = orjson.loads(file.read())
    rows = []
    if isinstance(data, dict):
        for k, v in data.items():
            rows.append({
                'segment_id': k,
                'text': v
            })

    elif isinstance(data, list):
        rows = data
    return pl.DataFrame(rows)

def load_html(path):
    rows = []
    with open(path, 'r', encoding='utf-8') as file:
        tree = HTMLParser(file.read())
    text = tree.body.text()
    for line in text.split('\n'):
        line = line.strip()
        if line:
            rows.append({'text': line})
    return pl.DataFrame(rows)

def load_csv(path):
    return pl.read_csv(path)
    
def load_tsv(path):
    return pl.read_csv(
        path,
        separator="\t"
    )
