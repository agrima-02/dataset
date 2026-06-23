from functools import lru_cache

from langdetect import detect

from script_detector import detect_script

from exceptions import (
    DatasetLanguageError
)

@lru_cache(maxsize=10000)
def detect_language(text):
    try:

        text = str(text).strip()

        if not text:

            return "unknown"

        return detect(text)

    except ValueError:

        return detect_script(text)

    except Exception as e:

        raise DatasetLanguageError(
            f"Language detection failed: {e}"
        )

def detect_language_batch(texts):

    if not texts:

        return []

    return [
        detect_language(
            str(text)
        )
        for text in texts
    ]