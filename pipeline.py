
import logging
import re
from pathlib import Path

from pedurma.utils import from_yaml
from transfer_notes import get_derge_text_with_notes
# from transfer_pedurma_notes import get_derge_text_with_pedurma_notes
from normalize_note import get_normalized_text
from opf_formatter import create_open_opf

PEDURMA_OUTLINE = from_yaml(Path('./data/pedurma_outline.yml'))

logging.basicConfig(filename="./data/collated_opfs.log", level=logging.INFO, filemode="w" )#filemode="w"

def rm_text_ann(text):
    """Cleans text annotation

    Args:
        text (str): collated text string having text annotation like {D1118}

    Returns:
        str: clean collated text without text annotation
    """
    clean_text = re.sub("\{[A-Z]\d+\}", "", text)
    return clean_text

def get_pages(text):
    pages = []
    chunks = re.split("(\d+-\d+)", text)
    for chunk in chunks:
        if re.search("\d+-\d+", chunk):
            continue
        else:
            pages.append(chunk)
    return pages

def reformat_collated_text(text):
    reformated_text =""
    pages = get_pages(text)
    for page in pages:
        reformated_page = page.replace("\n","")
        if reformated_page:
            reformated_text += f'{reformated_page}\n'
    return reformated_text


def pipeline(philo, collated_text_path, pedurma_outline):
    text_fn = collated_text_path.stem
    text_id = collated_text_path.stem[:-5]
    collated_text = collated_text_path.read_text(encoding='utf-8')
    collated_text = reformat_collated_text(collated_text)
    if "D" in text_id:
        clean_text_with_pedurma_notes = get_derge_text_with_notes(philo, text_id, collated_text, pedurma_outline,)
    else:
        clean_text_with_pedurma_notes = rm_text_ann(collated_text)
    Path(f'./data/{philo}_text/clean_base_collated_text/{text_fn}.txt').write_text(clean_text_with_pedurma_notes, encoding='utf-8')
    
    print("INFO: Pedurma notes are transfer to clean base text.")
    # clean_text_with_pedurma_notes = Path(f'./data/{philo}_text/clean_base_collated_text/{text_fn}.txt').read_text(encoding='utf-8')
    clean_text_with_pedurma_notes = clean_text_with_pedurma_notes.replace("\n", "")
    normalized_note_text = get_normalized_text(clean_text_with_pedurma_notes)
    Path(f'./data/{philo}_text/normalized_collated_text/{text_fn}.txt').write_text(normalized_note_text, encoding='utf-8')
    print("INFO: Note payload readiablity improved.")
    opf_path = Path(f'./data/{philo}_text/opfs')
    text_opf = create_open_opf(text_id, normalized_note_text, opf_path)
    logging.info(f"{text_id} completed with opf {text_opf.pecha_id}")
    print("INFO: OPF created")
    # text_opf.publish()
    # print("INFO: Pecha published.")

if __name__ == "__main__":
    philo = "shanti_deva"
    philo_text = Path(f'./data/{philo}_text/{philo}_text_list.txt').read_text(encoding='utf-8').splitlines()
    collated_text_paths = list(Path(f'./data/{philo}_text/collated_text').iterdir())
    collated_text_paths.sort()
    #collated_text_paths = [Path('./data/collated_text/D1784_v015.txt'), ]#Path('./data/collated_text/D3871_v061.txt')]
    collated_text_paths = [Path('./data/shanti_deva_text/collated_text/D3871_v061.txt')]
    pedurma_outline = from_yaml(Path('./data/pedurma_outline.yml'))
    for collated_text_path in collated_text_paths:
        text_id = collated_text_path.stem[:-5]
        if text_id in philo_text:
            pipeline(philo, collated_text_path, pedurma_outline)



    


