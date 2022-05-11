
import logging
import re
from pathlib import Path

from pedurma.utils import from_yaml
from transfer_pedurma_notes import get_derge_text_with_pedurma_notes
from normalize_note import get_normalized_text
from opf_formatter import create_opf

PEDURMA_OUTLINE = from_yaml(Path('./data/pedurma_outline.yml'))
OPF_PATH = Path('./data/opfs')

logging.basicConfig(filename="./data/collated_opfs.log", level=logging.INFO, )#filemode="w"

def rm_text_ann(text):
    """Cleans text annotation

    Args:
        text (str): collated text string having text annotation like {D1118}

    Returns:
        str: clean collated text without text annotation
    """
    clean_text = re.sub("\{[A-Z]\d+\}", "", text)
    return clean_text


def get_clean_base_with_notes(collated_text, text_id, text_fn):
    
    try:
        derge_text = Path(f'./data/derge_res/hfmls/{text_id}.txt').read_text(encoding='utf-8')
        derge_text = rm_text_ann(derge_text)
    except:
        return collated_text
    clean_base_with_notes = get_derge_text_with_pedurma_notes(PEDURMA_OUTLINE, collated_text, derge_text, text_id)
    clean_base_with_notes = re.sub(":་", "་:", clean_base_with_notes)
    clean_base_with_notes = re.sub("(\d+-\d+)\n\n\n\d+-\d+", "\g<1>", clean_base_with_notes)
    clean_base_with_notes = clean_base_with_notes.replace("\n", "")
    clean_base_with_notes = re.sub("\d+-\d+", "\n", clean_base_with_notes)
    Path(f'./data/clean_base_collated_text/{text_fn}.txt').write_text(clean_base_with_notes, encoding='utf-8')
    return clean_base_with_notes


def pipeline(collated_text_path):
    text_fn = collated_text_path.stem
    text_id = collated_text_path.stem[:-5]
    collated_text = collated_text_path.read_text(encoding='utf-8')
    collated_text = rm_text_ann(collated_text)
    clean_base_with_notes = get_clean_base_with_notes(collated_text, text_id, text_fn)
    
    # print("INFO: Pedurma notes are transfer to clean base text.")
    # normalized_note_text = get_normalized_text(clean_base_with_notes)
    # Path(f'./data/normalized_collated_text/{text_fn}.txt').write_text(normalized_note_text, encoding='utf-8')
    # print("INFO: Note payload readiablity improved.")
    # print(f"{text_id} completed")
    # text_opf = create_opf(text_id, normalized_note_text, OPF_PATH)
    # logging.info(f"{text_id} completed with opf {text_opf.pecha_id}")
    # print("INFO: OPF created")
    # text_opf.publish()
    # print("INFO: Pecha published.")

if __name__ == "__main__":
    normalized_collated_text_paths = list(Path('./data/collated_text').iterdir())
    normalized_collated_text_paths.sort()
    # normalized_collated_text_paths = [Path('./data/collated_text/D1784_v015.txt')]
    # normalized_collated_text_paths = [Path('./data/collated_text/D4274_v108.txt'), Path('./data/collated_text/D3871_v061.txt') ]
    for normalized_collated_text_path in normalized_collated_text_paths:
        pipeline(normalized_collated_text_path)



    


