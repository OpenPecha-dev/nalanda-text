import re
import logging
import shutil
from antx import transfer
from collections import defaultdict
from pathlib import Path

from opf_formatter import create_open_opf
from openpecha.blupdate import PechaBaseUpdate
from openpecha.core.ids import get_open_pecha_id
from openpecha.core.metadata import OpenPechaMetadata, InitialCreationType
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import dump_yaml, load_yaml

from opf_serializer import get_base_names, opf_to_txt

logging.basicConfig(filename="./data/transfer_issue_text.log", level=logging.INFO, filemode="w" )

def find_title(hfml):
    title = ""
    if re.search("བོད་སྐད་དུ། .+?།", hfml):
        title = "༄༅། །"
        title += re.search("བོད་སྐད་དུ། (.+?།)", hfml).group(1)
    return title


def has_title(hfml):
    if re.search("\{D.+?\}༄༅། །རྒྱ་གར་", hfml) or re.search("\{D.+?\}༄༅༅། །རྒྱ་གར་", hfml):
        return False
    else:
        return True


def get_text_title(pedurma_outline, text_id, hfml):
    title = ""
    if has_title(hfml):
        return ""
    # title = find_title(hfml)
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

def get_derge_text_with_pedurma_line_break(collated_text, derge_text):
    collated_text = re.sub("\(\d+\) <.+?>", "", collated_text)
    patterns = [["line_break", "(\n)"], ['double_tesg', "(:)"]]
    derge_text_with_pedurma_line_break = transfer(collated_text, patterns, derge_text)
    return derge_text_with_pedurma_line_break

def create_derge_opf(text_id, derge_text, opf_path):
    metadata = OpenPechaMetadata(initial_creation_type=InitialCreationType.input)
    derge_pecha = OpenPechaFS(metadata=metadata, base={}, layers=defaultdict(dict))
    derge_pecha.set_base(derge_text)
    derge_pecha._meta.source_metadata = {
        "text_id": text_id
    }
    derge_pecha.save(output_path = opf_path)
    return derge_pecha


def has_transfer_issue(derge_durchen_layer, text_id):
    if "fail" in str(derge_durchen_layer):
        return True
    return False
        
    
    

def get_derge_text_with_notes(text_id, collated_text, pedurma_outline):
    collated_opf = create_open_opf(text_id, collated_text, opf_path=Path('./data/opfs/collated_opfs'))
    collated_opf_path = collated_opf.opf_path
    derge_text = get_derge_text(pedurma_outline, text_id)
    derge_text_with_pedurma_line_break = get_derge_text_with_pedurma_line_break(collated_text, derge_text)
    derge_opf = create_derge_opf(text_id, derge_text_with_pedurma_line_break, opf_path=Path('./data/opfs/derge_opfs'))
    derge_opf_path = derge_opf.opf_path
    collated_base_names = get_base_names(collated_opf_path)
    derge_base_names = get_base_names(derge_opf_path)
    for derge_base_name,collated_base_name in zip(derge_base_names, collated_base_names):
        collated_durchen_layer = collated_opf.read_layers_file(collated_base_name, "Durchen")
        (derge_opf_path / f"layers/").mkdir()
        (derge_opf_path / f"layers/{derge_base_name}").mkdir()
        dump_yaml(collated_durchen_layer, (derge_opf_path / f"layers/{derge_base_name}/Durchen.yml"))
        transfer_durchen_layer(collated_opf_path, derge_opf_path, collated_base_name, derge_base_name)
        derge_durchen_layer = derge_opf.read_layers_file(derge_base_name, "Durchen")
        if has_transfer_issue(derge_durchen_layer, text_id):
            logging.info(f"{text_id} transfer issue")
            return collated_text
    derge_text_with_notes = opf_to_txt(derge_opf_path)
    shutil.rmtree(str(collated_opf_path.parent))
    # shutil.rmtree(str(derge_opf_path.parent))
    return derge_text_with_notes



def transfer_durchen_layer(src_opf, trg_opf, src_base_name, trg_base_name):
    pecha_updater = PechaBaseUpdate(src_opf, trg_opf)
    pecha_updater.update_vol(src_base_name, trg_base_name)

if __name__ == "__main__":
    pedurma_outline = load_yaml(Path('./data/pedurma_outline.yml'))
    collated_text = Path('./data/collated_text/D4274_v108.txt').read_text(encoding='utf-8')
    text_id = "D4274"
    texts = get_derge_text_with_notes(text_id, collated_text, pedurma_outline)
    for base_name, text in texts.items():
        Path(f"./data/serializer_output/{base_name}.txt").write_text(text, encoding='utf-8')
