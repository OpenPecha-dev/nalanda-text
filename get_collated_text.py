from pathlib import Path
import re
import logging

from pedurma.preview import get_reconstructed_text
from pedurma.reconstruction import get_normalized_notes_text
from reformating_batch_note import reformat_batch_notes


logging.basicConfig(filename="./data/batch_note_text.log", level=logging.INFO, filemode="w" )

def get_collated_text(text_id):
    try:
        collated_text, _ = get_reconstructed_text(text_id, bdrc_img=False)
    except:
        collated_text = {}
    return collated_text

def clean_collated_text(collated_text_path):
    collated_text = collated_text_path.read_text(encoding='utf-8')
    collated_text = collated_text.replace("།་","༎")
    collated_text = collated_text.replace("། ་", "་")
    collated_text_path.write_text(collated_text, encoding="utf-8")

def has_batch_note(collated_text):
    if re.search("\)>", collated_text):
        return True
    else:
        return False
    

if __name__ == "__main__":
    philo = "09-Asanga"
    collated_text = Path(f'./data/nalanda_works/{philo}/{philo}_text_list.txt').read_text(encoding='utf-8')
    collated_text_ids = collated_text.splitlines()
    collated_text_ids = list(set(collated_text_ids))
    collated_text_ids.sort()
    for collated_text_id in collated_text_ids:
        collated_text = get_collated_text(collated_text_id)
        while not collated_text:
            collated_text = get_collated_text(collated_text_id)
        for vol_id, text in collated_text.items():
            if has_batch_note(text):
                reformated_collated_text = reformat_batch_notes(text)
                Path(f'./data/nalanda_works/{philo}/collated_text/{collated_text_id}_{vol_id}.txt').write_text(reformated_collated_text, encoding='utf-8')
            else:
                Path(f'./data/nalanda_works/{philo}/collated_text/{collated_text_id}_{vol_id}.txt').write_text(text, encoding='utf-8')
        print(f'{collated_text_id} completed..')
