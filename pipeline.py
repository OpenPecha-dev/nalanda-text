import re
from pathlib import Path

from pedurma.utils import from_yaml
from transfer_pedurma_notes import get_derge_text_with_pedurma_notes
from normalize_note import get_normalized_text
from opf_formatter import create_opf

PEDURMA_OUTLINE = from_yaml(Path('./data/pedurma_outline.yml'))
OPF_PATH = Path('./data/opfs')


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
    Path(f'./data/clean_base_collated_text/{text_fn}.txt').write_text(clean_base_with_notes, encoding='utf-8')
    return clean_base_with_notes


def pipeline(collated_text_path):
    text_fn = collated_text_path.stem
    text_id = collated_text_path.stem[:-5]
    collated_text = collated_text_path.read_text(encoding='utf-8')
    collated_text = rm_text_ann(collated_text)
    
    clean_base_with_notes = get_clean_base_with_notes(collated_text, text_id, text_fn)
    print("INFO: Pedurma notes are transfer to clean base text.")
    normalized_note_text = get_normalized_text(clean_base_with_notes)
    print("INFO: Note payload readiablity improved.")
    text_opf = create_opf(text_id, normalized_note_text, OPF_PATH)
    print("INFO: OPF created")
    text_opf.publish()
    print("INFO: Pecha published.")

if __name__ == "__main__":
    collated_text_path = Path('./data/collated_text/D2945_v038.txt')
    pipeline(collated_text_path)



    


