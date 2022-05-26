from pathlib import Path
from openpecha.core.pecha import OpenPechaFS

def get_base_names(opf_path):
    base_names = []
    for base_path in list((opf_path / "base").iterdir()):
        base_names.append(base_path.stem)
    return base_names

def get_reconstructed_notes(durchen_ann):
    pub_mapping = {
        'peking': '«པེ་»',
        'narthang': '«སྣར་»',
        'derge': '«སྡེ་»',
        'chone': '«ཅོ་»'
    }
    note_options = durchen_ann['options']
    default_note = note_options[durchen_ann['default']]['note']
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
        collated_text += f"{prev_chunk}({note_walker}) {reconstructed_notes}"
        char_walker = durchen_ann['span']['end']
        note_walker += 1
        last_durchen_ann = durchen_ann
    if last_durchen_ann:
        collated_text += base_text[last_durchen_ann['span']['end']:]
    else:
        collated_text = base_text
    return collated_text

def opf_to_txt(opf_path, output_dir):
    pecha = OpenPechaFS(opf_path)
    pecha_meta = pecha.read_meta_file()
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        base_text = pecha.read_base_file(base_name)
        text_id = pecha_meta['source_metadata']['text_id']
        collated_text = serialize_notes(durchen_layer, base_text)
        output_path = output_dir / f"{text_id}_{base_name}.txt"
        output_path.write_text(collated_text, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    opf_path = Path('./data/opfs/derge_opfs/P2F6B8194/P2F6B8194.opf')
    opf_to_txt(opf_path, output_dir=Path('./data/serializer_output/'))