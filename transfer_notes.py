import re
from antx import transfer
from pathlib import Path

from opf_formatter import create_opf

from openpecha.blupdate import PechaBaseUpdate
from openpecha.utils import dump_yaml, load_yaml


def find_title(hfml):
    title = ""
    if re.search("བོད་སྐད་དུ། .+?།", hfml):
        title = "༄༅། །"
        title += re.search("བོད་སྐད་དུ། (.+?།)", hfml).group(1)
    return title


def has_title(hfml):
    if re.search("\{D.+?\}༄༅༅། །རྒྱ་གར་སྐད་དུ།", hfml):
        return False
    else:
        return True


def get_text_title(pedurma_outline, text_id, hfml):
    if has_title(hfml):
        return ""
    title = find_title(hfml)
    if not title:
        for _, outline_info in pedurma_outline.items():
                if outline_info['rkts_id'] == text_id:
                    title = outline_info['text_title']
                    return f'༄༅། །{title}'
    return title

def get_derge_text(pedurma_outline, text_id):
    derge_text = Path(f'./data/derge_res/hfmls/{text_id}.txt').read_text(encoding='utf-8')
    derge_text = f'{get_text_title(pedurma_outline, text_id, derge_text)}\n{derge_text}'
    if derge_text[-1] == "༄":
        derge_text = derge_text[:-1]
    derge_text = re.sub("〔.+?〕", "", derge_text)
    derge_text = re.sub("{.+\}", "", derge_text)
    derge_text = derge_text.replace("\n", "")
    return derge_text

def get_derge_text_with_pedurma_line_break(collated_opf, derge_text):
    collated_text = collated_opf.read_base_file("00001")
    patterns = [["line_break", "(\n)"]]
    derge_text_with_pedurma_line_break = transfer(collated_text, patterns, derge_text)
    return derge_text_with_pedurma_line_break
    

def get_derge_text_with_notes(collated_text_path, pedurma_outline):
    text_id = collated_text_path.stem[:5]
    collated_text = collated_text_path.read_text(encoding="utf-8")
    collated_opf = create_opf(text_id, collated_text, opf_path=Path('./data/opfs/collated_opfs'))
    collated_opf_path = collated_opf.opf_path
    derge_text = get_derge_text(pedurma_outline, text_id)
    derge_text_with_pedurma_line_break = get_derge_text_with_pedurma_line_break(collated_opf, derge_text)
    derge_opf = create_opf(text_id, derge_text_with_pedurma_line_break, opf_path=Path('./data/opfs/derge_opfs'))
    derge_opf_path = derge_opf.opf_path
    collated_durchen_layer = collated_opf.read_layers_file("00001", "Durchen")
    dump_yaml(collated_durchen_layer, (derge_opf_path / "layers/00001/Durchen.yml"))
    transfer_durchen_layer(collated_opf_path, derge_opf_path)



def transfer_durchen_layer(src_opf, trg_opf):
    pecha_updater = PechaBaseUpdate(src_opf, trg_opf)
    pecha_updater.update_vol("00001")

if __name__ == "__main__":
    # src_opf = Path('./data/opfs/collated_opfs/PD01B8805/PD01B8805.opf')
    # trg_opf = Path('./data/opfs/derge_opfs/PD01B8804/PD01B8804.opf')
    # transfer_durchen_layer(src_opf, trg_opf)
    pedurma_outline = load_yaml(Path('./data/pedurma_outline.yml'))
    collated_text_path = Path('./data/collated_text/D4274_v108.txt')
    get_derge_text_with_notes(collated_text_path, pedurma_outline)
