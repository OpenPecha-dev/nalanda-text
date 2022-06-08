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
    philo = "ludup"
    collated_text = Path(f'./data/{philo}_text/{philo}_text_list.txt').read_text(encoding='utf-8')
    collated_text_list = list(Path('./data/collated_text').iterdir())
    # collated_text_list.sort()
    # collated_text_list = [text_id.stem[:-5] for text_id in collated_text_list]
    collated_text_ids = collated_text.splitlines()
    collated_text_ids = list(set(collated_text_ids))
    collated_text_ids.sort()
    # for collated_text_path in collated_text_list:
    #     text_id = collated_text_path.stem[:-5]
    for collated_text_id in collated_text_ids:
        # if text_id in collated_text_ids:
        #     collated_text = collated_text_path.read_text(encoding='utf-8')
        #     new_collated_text = get_normalized_notes_text(collated_text)
        #     Path(f'./data/ludup_text/collated_text/{collated_text_path.stem}.txt').write_text(new_collated_text, encoding='utf-8')
        #     print(text_id)
        collated_text = get_collated_text(collated_text_id)
        while not collated_text:
            collated_text = get_collated_text(collated_text_id)
        for vol_id, text in collated_text.items():
            if has_batch_note(text):
                reformated_collated_text = reformat_batch_notes(text)
                Path(f'./data/{philo}_text/collated_text/{collated_text_id}_{vol_id}.txt').write_text(reformated_collated_text, encoding='utf-8')
            else:
                Path(f'./data/{philo}_text/collated_text/{collated_text_id}_{vol_id}.txt').write_text(text, encoding='utf-8')
        print(f'{collated_text_id} completed..')
    # collated_text_paths = list(Path('./data/collated_text').iterdir())
    # for collated_text_path in collated_text_paths:
    #     text_id = collated_text_path.stem[:-5]
    #     collated_text = collated_text_path.read_text(encoding='utf-8')
    #     if has_batch_note(collated_text):
    #         logging.info(f"{text_id} has batch note") 

        # clean_collated_text(collated_text_path)
