import logging
import re

from pathlib import Path

logging.basicConfig(filename="./data/note_sanity_test.log", level=logging.INFO, filemode="w")

def has_noise(note_text):
    noises = ['〈', '〉', '《', '》']
    for noise in noises:
        if noise in note_text:
            return True
    return False

def is_proper_note(note_text):
    if has_noise(note_text):
        return False
    elif re.search('«པེ་»སྣར་»', note_text):
        return False
    elif re.search('«པེ་»«སྣར་».+', note_text):
        return True
    elif re.search("«པེ་».+", note_text):
        return True
    elif re.search("«སྣར་».+", note_text):
        return True
    else:
        return False

def note_sanity_test(collated_text, text_id):
    notes = re.findall(r"\(\d+\) <.+?>", collated_text)
    for note in notes:
        if is_proper_note(note):
            continue
        else:
            logging.info(f"{text_id} {note}")

if __name__ == "__main__":
    normalized_collated_text_paths = list(Path('./data/normalized_collated_text').iterdir())
    for normalized_collated_text_path in normalized_collated_text_paths:
        text_id = normalized_collated_text_path.stem
        note_sanity_test(normalized_collated_text_path, text_id)
    