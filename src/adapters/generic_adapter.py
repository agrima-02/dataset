def is_supported(file):

    extensions = [
        '.txt',
        '.json',
        '.html',
        '.htm'
    ]

    return any(
        file.endswith(ext)
        for ext in extensions
    )
