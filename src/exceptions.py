class DatasetError(Exception):
    """
    Base dataset exception.
    """
    pass


class DatasetLoadError(
    DatasetError
):
    """
    Failed to load file.
    """
    pass


class DatasetSchemaError(
    DatasetError
):
    """
    Missing columns or invalid schema.
    """
    pass


class DatasetAlignmentError(
    DatasetError
):
    """
    Parallel alignment failure.
    """
    pass


class DatasetValidationError(
    DatasetError
):
    """
    Invalid dataset.
    """
    pass


class DatasetWriteError(
    DatasetError
):
    """
    Export failure.
    """
    pass


class DatasetCheckpointError(
    DatasetError
):
    """
    Checkpoint failure.
    """
    pass


class DatasetLanguageError(
    DatasetError
):
    """
    Language detection failure.
    """
    pass