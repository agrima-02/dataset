import re

TIBETAN = re.compile(r'[\u0F00-\u0FFF]')
CHINESE = re.compile(r'[\u4E00-\u9FFF]')
DEVANAGARI = re.compile(r'[\u0900-\u097F]')


def detect_script(text):

    if TIBETAN.search(text):
        return 'tibetan'

    if CHINESE.search(text):
        return 'chinese'

    if DEVANAGARI.search(text):
        return 'sanskrit'

    return 'latin'
