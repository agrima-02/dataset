def validate_dataframe(df):

    if df.empty:
        raise ValueError(
            "Dataset is empty"
        )

    print(
        f"Rows: {len(df)}"
    )

    print(
        "Validation successful"
    )
