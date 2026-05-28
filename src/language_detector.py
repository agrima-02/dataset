from langdetect import detect
from script_detector import detect_script


def detect_language(text):

    try:

        return detect(text)

    except Exception:

        return detect_script(text)