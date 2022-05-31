import re

from pathlib import Path

def reformat_batch_note(note_text):
    reformated_note_text = note_text
    batch_note_info = re.search("\(.+\)", note_text)[0]
    reformated_batch_note_info = batch_note_info
    reformated_batch_note_info = reformated_batch_note_info.replace("«", "༺")
    reformated_batch_note_info = reformated_batch_note_info.replace("»", "༻")
    reformated_batch_note_info = reformated_batch_note_info.replace("(", "༼")
    reformated_batch_note_info = reformated_batch_note_info.replace(")", "༽")
    reformated_note_text = reformated_note_text.replace(batch_note_info, reformated_batch_note_info)
    return reformated_note_text

def is_batch_note(note_text):
    if ")>" in note_text:
        return True
    return False

def reformat_batch_notes(collated_text):
    notes = re.findall("<.+?>", collated_text)
    reformated_collated_text = collated_text

    for note in notes:
        if is_batch_note(note):
            reformated_batch_note = reformat_batch_note(note)
            reformated_collated_text = reformated_collated_text.replace(note, reformated_batch_note)
    
    return reformated_collated_text


if __name__ == "__main__":
    batch_note_text_ids = Path('./data/shanti_deva_text_list.txt').read_text(encoding='utf-8').splitlines()
    collated_text_paths = list(Path('./data/collated_text').iterdir())
    for collated_text_path in collated_text_paths:
        text_id = collated_text_path.stem[:-5]
        if text_id in batch_note_text_ids:
            collated_text = collated_text_path.read_text(encoding='utf-8')
            reformated_collated_text = reformat_batch_notes(collated_text)
            collated_text_path.write_text(reformated_collated_text, encoding='utf-8')