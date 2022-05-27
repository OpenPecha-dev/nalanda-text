import re
from pathlib import Path
from openpecha.core.pecha import OpenPechaFS

def get_base_names(opf_path):
    base_names = []
    for base_path in list((opf_path / "base").iterdir()):
        base_names.append(base_path.stem)
    return base_names

def reformat_addition_notes(note_options, default_note):
    if not default_note:
        for pub, note_option in note_options.items():
            if note_option['note']:
                note_options[pub]['note'] = f"+{note_option['note']}"
    return note_options

def reformat_omission_notes(note_options, default_note):
    for pub, note_option in note_options.items():
        if not note_option['note'] and note_option['note'] != default_note:
            note_options[pub]['note'] = f"-{default_note}"
    return note_options


def get_reconstructed_notes(durchen_ann):
    pub_mapping = {
        'peking': '«པེ་»',
        'narthang': '«སྣར་»',
        'derge': '«སྡེ་»',
        'chone': '«ཅོ་»'
    }
    note_options = durchen_ann['options']
    default_note = note_options[durchen_ann['default']]['note']
    note_options = reformat_addition_notes(note_options, default_note)
    note_options = reformat_omission_notes(note_options, default_note)
    reconstructed_notes = "<"
    if note_options['peking']['note'] == note_options['narthang']['note'] and note_options['peking']['note'] != default_note:
        if note_options['chone']['note'] == default_note:
            reconstructed_notes = f"<«པེ་»«སྣར་»{note_options['peking']['note']}>"
        elif note_options['narthang']['note'] != note_options['chone']['note']:
            reconstructed_notes = f"<«པེ་»«སྣར་»{note_options['peking']['note']}«ཅོ་»{note_options['chone']['note']}>"
        return reconstructed_notes
    for pub, note_option in note_options.items():
        if note_option['note'] != default_note:
            reconstructed_notes += f"{pub_mapping[pub]}{note_option['note']}"
    reconstructed_notes += ">"
    return reconstructed_notes

def serialize_notes(durchen_layer, base_text):
    collated_text = ""
    char_walker = 0
    note_walker = 1
    last_durchen_ann = {}
    for uuid, durchen_ann in durchen_layer['annotations'].items():
        reconstructed_notes = get_reconstructed_notes(durchen_ann)
        prev_chunk = base_text[char_walker:durchen_ann['span']['end']]
        if reconstructed_notes != "<>":
            collated_text += f"{prev_chunk}({note_walker}) {reconstructed_notes}"
            note_walker += 1
        else:
            collated_text += prev_chunk
        char_walker = durchen_ann['span']['end']
        last_durchen_ann = durchen_ann
    if last_durchen_ann:
        collated_text += base_text[last_durchen_ann['span']['end']:]
    else:
        collated_text = base_text
    return collated_text

def opf_to_txt(opf_path):
    pecha = OpenPechaFS(path=opf_path)
    pecha_meta = pecha.read_meta_file()
    base_names = get_base_names(opf_path)
    collated_text = ""
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        base_text = pecha.read_base_file(base_name)
        text_id = pecha_meta['source_metadata']['text_id']
        collated_text += serialize_notes(durchen_layer, base_text)
        collated_text = re.sub(":་", "་:", collated_text)
        collated_text = collated_text.replace("།།།།", "།། །།")
    return collated_text


if __name__ == "__main__":
    opf_path = Path('./data/opfs/derge_opfs/OB74A874C/OB74A874C.opf')
    collated_text = opf_to_txt(opf_path)
    Path('./data/serializer_output/test.txt').write_text(collated_text, encoding='utf-8')