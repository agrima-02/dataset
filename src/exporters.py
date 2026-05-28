import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path

class StreamingParquetWriter:
    def __init__(self, output_path):
        self.output_path = output_path
        self.writer = None
    def write(self, df):
        table = df.to_arrow()
        if self.writer is None:
            self.writer = pq.ParquetWriter(
                self.output_path,
                table.schema,
                compression='zstd'
            )
        self.writer.write_table(table)
    def close(self):
        if self.writer:
            self.writer.close()
