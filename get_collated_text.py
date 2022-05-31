from pathlib import Path
import re
import logging

from pedurma.preview import get_reconstructed_text


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
    collated_text = Path('./data/shanti_deva_text_list.txt').read_text(encoding='utf-8')
    collated_text_list = list(Path('./data/collated_text').iterdir())
    collated_text_list.sort()
    collated_text_list = [text_id.stem[:-5] for text_id in collated_text_list]
    collated_text_ids = collated_text.splitlines()
    collated_text_ids = ["D4383"]
    for collated_text_id in collated_text_ids:
        # if "D" in collated_text_id or "N" in collated_text_id:
        #     continue
        # if collated_text_id in collated_text_list:
        #     continue
        collated_text = get_collated_text(collated_text_id)
        while not collated_text:
            collated_text = get_collated_text(collated_text_id)
        for vol_id, text in collated_text.items():
            Path(f'./data/collated_text/{collated_text_id}_{vol_id}.txt').write_text(text, encoding='utf-8')
        print(f'{collated_text_id} completed..')
    # collated_text_paths = list(Path('./data/collated_text').iterdir())
    # for collated_text_path in collated_text_paths:
    #     text_id = collated_text_path.stem[:-5]
    #     collated_text = collated_text_path.read_text(encoding='utf-8')
    #     if has_batch_note(collated_text):
    #         logging.info(f"{text_id} has batch note")

        # clean_collated_text(collated_text_path)
