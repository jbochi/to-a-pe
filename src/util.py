from datetime import timedelta
import re

def slugify(text):
    text = text.replace("'", "")
    text = re.subn(r'(\s|\.|\(|\)|\/|\\)', ' ', text)[0]
    text = text.strip().lower()
    text = re.subn(r'(-|\s)+', '-', text)[0]
    return text

def format_timedelta_seconds(timedelta_seconds):
    return str(timedelta(seconds=timedelta_seconds))[:-3]
