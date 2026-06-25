# Buddhist Dataset Processing Pipeline

A Python pipeline for cleaning, validating, and processing Buddhist text datasets into machine learning-ready formats.

The project supports multiple input formats, performs text cleaning and validation, detects languages, removes invalid entries, and exports the processed data into efficient formats for training NLP models.

---

## Features

- Supports multiple dataset formats
  - TXT
  - TSV
  - CSV
  - JSON
  - HTML

- Cleans and normalizes text
- Removes empty and duplicate entries
- Detects languages automatically
- Processes both monolingual and parallel datasets
- Generates dataset statistics
- Exports datasets to:
  - Apache Arrow
  - Parquet

---

## Project Structure

```
dataset/
│
├── data/
│   ├── raw/               # Input datasets
│   └── processed/         # Output datasets
│
├── src/
│   ├── cleaners.py
│   ├── exporters.py
│   ├── loaders.py
│   ├── validators.py
│   ├── statistics.py
│   ├── logger.py
│   └── main.py
│
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```
git clone https://github.com/agrima-02/dataset.git
cd dataset
```

### 2. Install all dependencies

```
pip install -r requirements.txt
```

If pip is not up to date:

```
python -m pip install --upgrade pip
```

---

### 3. Running the Project

Place all your input files inside:

```
data/raw/
```

Then run:

```
python src/main.py
```

or  (in the terminal)

```
py -3.11 main.py
```
or (depending on your system)

```
python3 src/main.py
```

The processed datasets will be saved in:

```
data/processed/
```

---

## Output

The pipeline generates:

- Cleaned datasets
- Validated datasets
- Apache Arrow files
- Parquet files
- Dataset statistics
- Processing logs

---

## Requirements

- Python 3.10 or newer
- pip

All required Python libraries are listed in:

```
requirements.txt
```

Install them using:

```
pip install -r requirements.txt
```

---

## Technologies Used

- Python
- Polars
- Pandas
- PyArrow
- ORJSON
- Selectolax
- ftlangdetect
- Sentence Transformers
- Hugging Face Datasets

---
