from datasets import load_dataset
from config import CONFIG


def load_monolingual_dataset():

    return load_dataset(
        "parquet",
        data_files=f"{CONFIG['processed_folder']}/mono.parquet"
    )


def load_parallel_dataset():

    return load_dataset(
        "parquet",
        data_files=f"{CONFIG['processed_folder']}/parallel.parquet"
    )

if __name__ == "__main__":

    mono = load_monolingual_dataset()

    parallel = load_parallel_dataset()

    print(mono)
    print(parallel)