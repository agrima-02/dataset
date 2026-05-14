def validate_dataframe(df):

    if df.empty:

        raise ValueError(
            "Dataset is empty"
        )

    # Count null rows
    null_rows = df.isnull().sum().sum()

    print(
        f"Null values: {null_rows}"
    )

    print(
        "Validation successful"
    )