import pyarrow.parquet as pq

from threading import Lock

from exceptions import (
    DatasetWriteError
)

class StreamingParquetWriter:

    def __init__(
        self,
        output_path
    ):

        self.output_path = output_path

        self.writer = None

        self.lock = Lock()


    def __enter__(self):

        return self


    def __exit__(

        self,

        exc_type,

        exc_val,

        exc_tb
    ):

        self.close()


    def write(
        self,
        df
    ):

        if len(df) == 0:
            return

        table = df.to_arrow()

        with self.lock:

            if self.writer is None:

                self.writer = pq.ParquetWriter(

                    self.output_path,

                    table.schema,

                    compression="zstd"
                )

            try:

                self.writer.write_table(
                    table
                )

            except Exception as e:

                raise DatasetWriteError(
                    f"Failed writing parquet: {e}"
               )


    def close(self):

        with self.lock:

            if self.writer:

                try:

                    self.writer.close()

                except Exception as e:

                    raise DatasetWriteError(
                        f"Failed closing parquet writer: {e}"
                    )

                finally:

                    self.writer = None