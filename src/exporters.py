import pyarrow as pa
import pyarrow.parquet as pq
from datasets import Dataset

# Export CSV
def export_csv(df, output_path):

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
        quoting=1
    )

    print(
        "CSV exported"
    )


# Export Parquet
def export_parquet(df, output_path):

    table = pa.Table.from_pandas(df)

    pq.write_table(
        table,
        output_path
    )

    print(
        "Parquet exported"
    )


# Export Arrow
def export_arrow(df, output_path):

    table = pa.Table.from_pandas(df)

    with pa.OSFile(
        output_path,
        "wb"
    ) as sink:

        with pa.ipc.new_file(
            sink,
            table.schema
        ) as writer:

            writer.write_table(table)

    print(
        "Arrow exported"
    )


# Export Hugging Face dataset
def export_huggingface(
    df,
    output_path
):

    dataset = Dataset.from_pandas(df)

    dataset.save_to_disk(
        output_path
    )

    print(
        "Hugging Face dataset exported"
    )