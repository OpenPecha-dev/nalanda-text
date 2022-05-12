import re

from antx import transfer
from pathlib import Path
from pydantic import BaseModel


from openpecha.core.annotations import Pagination, Durchen, Span
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData
from openpecha.core.pecha import OpenPechaFS


class DurchenOption(BaseModel):
    note: str
    probability: float = None
    features: list = None

def get_base_text(collated_text):
    base_text = re.sub(r"\d+-\d+", "", collated_text)
    base_text = re.sub(r"\(\d+\) <.+?>", "", base_text)
    base_text = base_text.replace(":","")
    return base_text


def get_pages(collated_text):
    chunks = re.split(r"(\d+-\d+)", collated_text)
    pages = {}
    cur_page = ""
    for chunk in chunks:
        if re.search(r"\d+-\d+", chunk):
            pg_num = re.search(r"\d+-(\d+)", chunk).group(1)
            pages[pg_num] = cur_page
            cur_page = ""
        else:
            cur_page = chunk
        
    return pages 


def get_pagination_layer(collated_text):
    pagination_layer = Layer(annotation_type=LayerEnum.pagination)
    collated_text = re.sub(r"\(\d+\) <.+?>", "", collated_text)
    pages = get_pages(collated_text)
    char_walker = 0
    for pg_no, page in pages.items():
        span = Span(start=char_walker, end=char_walker + len(page))
        pagination_layer.set_annotation(Pagination(span=span, imgnum=int(pg_no)))
        char_walker += len(page) + 1
    
    return pagination_layer


def normalized_note_text_space(note_text_options, default_option):
    patterns = [['space', "( )"]]
    for pub, note_text in note_text_options.items():
        if note_text != default_option and " " in default_option and "།" in note_text:
            normalized_note_text = transfer(default_option, patterns, note_text)
            note_text_options[pub] = normalized_note_text
    return note_text_options


def get_note_text_options(default_option, note_chunk):
    default_option = default_option.replace(":", "")
    note_chunk = re.sub('\(\d+\)', '', note_chunk)
    if "+" in note_chunk:
        default_option = ""
    note_chunk = re.sub("\+", "", note_chunk)
    pub_mapping = {
        '«པེ་»': 'peking',
        '«པེ»': 'peking',
        '«སྣར་»': 'narthang',
        '«སྣར»': 'narthang',
        '«སྡེ་»': 'derge',
        '«སྡེ»': 'derge',
        '«ཅོ་»': 'chone',
        '«ཅོ»': 'chone'
    }
    note_text_options = {
        'peking': '',
        'narthang': '',
        'derge': '',
        'chone': ''
    }
    note_parts = re.split('(«པེ་»|«སྣར་»|«སྡེ་»|«ཅོ་»|«པེ»|«སྣར»|«སྡེ»|«ཅོ»)', note_chunk)
    pubs = note_parts[1::2]
    notes = note_parts[2::2]
    for walker, (pub, note_part) in enumerate(zip(pubs, notes)):
        if note_part:
            note_text_options[pub_mapping[pub]] = note_part.replace('>', '')
        else:
            if notes[walker+1]:
                note_text_options[pub_mapping[pub]] = notes[walker+1].replace('>', '')
            else:
                note_text_options[pub_mapping[pub]] = notes[walker+2].replace('>', '')
    for pub, note in note_text_options.items():
        if "-" in note:
            note_text_options[pub] = ""
        if not note:
            note_text_options[pub] = default_option
    note_text_options = normalized_note_text_space(note_text_options, default_option)
    return note_text_options


def get_note_options(note_text_options):
    note_options = {
        'peking': None,
        'narthang': None,
        'derge': None,
        'chone': None
    }
    for pub, note_text in note_text_options.items():
        note_options[pub] = DurchenOption(note=note_text)
    return note_options


def get_syls(text):
    chunks = re.split('(་|།།|།)',text)
    syls = []
    cur_syl = ''
    for chunk in chunks:
        if re.search('་|།།|།',chunk):
            cur_syl += chunk
            syls.append(cur_syl)
            cur_syl = ''
        else:
            cur_syl += chunk
    if cur_syl:
        syls.append(cur_syl)
    return syls


def get_default_option(prev_chunk):
    default_option = ''
    if ':' in prev_chunk:
        default_option = re.search(':.*', prev_chunk)[0]
    else:
        syls = get_syls(prev_chunk)
        if syls:
            default_option = syls[-1]
    default_option = default_option.replace("#", "")
    return default_option


def get_durchen_annotation(prev_chunk, note_chunk, char_walker, default_pub):
    default_option = get_default_option(prev_chunk)
    ann_start = char_walker - len(default_option)
    ann_end = char_walker
    note_text_options = get_note_text_options(default_option, note_chunk)
    note_options = get_note_options(note_text_options)
    span = Span(start=ann_start, end=ann_end)
    durchen_ann = Durchen(span=span, default=default_pub, options=note_options)
    return durchen_ann


def get_durchen_layer(collated_text, default_pub):
    durchen_layer = Layer(annotation_type=LayerEnum.durchen)
    char_walker = 0
    collated_text = re.sub(r"\d+-\d+", "", collated_text)
    collated_text = collated_text.replace("\n", "#")
    chunks = re.split('(\(\d+\) <.+?>)', collated_text)
    prev_chunk = chunks[0]
    for chunk in chunks:
        if re.search('\(\d+\) <.+?>', chunk):
            durchen_layer.set_annotation(get_durchen_annotation(prev_chunk, chunk, char_walker, default_pub))
        else:
            clean_chunk = chunk.replace(":", "")
            char_walker += len(clean_chunk)
        prev_chunk = chunk
    
    return durchen_layer
    

def get_default_pub(text_id):
    if "D" in text_id:
        return "derge"
    elif "N" in text_id:
        return "narthang"
    elif "Q" in text_id:
        return "peking"
    else:
        return "chone"


def create_opf(text_id, collated_text, opf_path):
    metadata = PechaMetaData(initial_creation_type=InitialCreationEnum.input)
    pecha = OpenPechaFS(meta=metadata)
    default_pub = get_default_pub(text_id)
    base_text = get_base_text(collated_text)
    # pagination_layer = get_pagination_layer(collated_text)
    durchen_layer = get_durchen_layer(collated_text, default_pub)
    base_name = pecha.set_base(base_text)
    # pecha.set_layer(base_name, pagination_layer)
    pecha.set_layer(base_name, durchen_layer)
    pecha._meta.source_metadata = {
        "text_id": text_id
    }
    pecha.save(output_path = opf_path)
    return pecha


if __name__ == "__main__":
    text_id = "D1133"
    collated_text = Path('./data/normalized_collated_text/D1133_v001.txt').read_text(encoding='utf-8')
    create_opf(text_id, collated_text, opf_path=Path('./data/opfs'))