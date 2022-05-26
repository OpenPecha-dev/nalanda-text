from __future__ import annotations
import re
from pathlib import Path
from antx.core import transfer
from pedurma.utils import from_yaml

from utils import reformat_line_break



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


def transfer_line_break(normalized_text, pedurma_text):
    normalized_text  = normalized_text.replace("\n", "")
    patterns = [["pedurma_page", r"(\d+-\d+)"], ["line_break", "(\n)"]]
    new_pedurma_text = transfer(pedurma_text, patterns, normalized_text)
    return new_pedurma_text


def get_combined_text(hfmls):
    whole_text = ''
    for vol_id, vol_text in hfmls.items():
        whole_text += f'{vol_text}\n'
    return whole_text

def transfer_pedurma_notes(pedurma_text, derge_text):
    derge_text_with_notes = ''
    derge_text = re.sub("〔.+?〕", "", derge_text)
    derge_text = derge_text.replace("\n", "")
    if derge_text[-1] == "༄":
        derge_text = derge_text[:-1]
    patterns = [["pedurma_notes", r"(\(\d+\) <.*?>)"], ["double_tseg", "(:)"]]
    pedurma_text = pedurma_text.replace("\n" ,"")
    derge_text_with_notes = transfer(pedurma_text, patterns, derge_text, output="txt")
    return derge_text_with_notes


def reformat_text(text):
    reformated_text = ""
    text = re.sub("\n", "", text)
    text_parts = re.split("(། །)", text)
    sentence_walker = 0
    for text_part in text_parts:
        if text_part == "། །":
            if sentence_walker == 100:
                reformated_text += f"{text_part}\n"
                sentence_walker = 0
            else:
                reformated_text += text_part
                sentence_walker += 1
        else:
            reformated_text += text_part
    reformated_text = reformated_text.replace("##", "\n")
    return reformated_text

def get_derge_text_with_pedurma_notes(pedurma_outline, pedurma_text, derge_text, text_id):
    derge_text = f'{get_text_title(pedurma_outline, text_id, derge_text)}\n{derge_text}'
    derge_text_with_pedurma_notes = transfer_pedurma_notes(pedurma_text, derge_text)
    # derge_text_with_pedurma_notes = reformat_line_break(derge_text_with_pedurma_notes)
    pedurma_with_derge_text = transfer_line_break(derge_text_with_pedurma_notes, pedurma_text)
    return pedurma_with_derge_text


if __name__ == "__main__":
    # pedurma_outline = from_yaml(Path('./data/pedurma_outline.yml'))
    # text_paths = list(Path('./data/collated_text').iterdir())
    # text_paths.sort()
    # for text_path in text_paths:
    #     text_fn = text_path.stem
    #     text_id = text_path.stem[:-5]
    #     try:
    #         derge_text = Path(f'./data/derge_res/hfmls/{text_id}.txt').read_text(encoding='utf-8')
    #     except:
    #         derge_text = ""
    #     if derge_text:
    #         pedurma_text = text_path.read_text(encoding='utf-8')
    #         derge_with_notes = get_derge_text_with_pedurma_notes(pedurma_outline, pedurma_text, derge_text, text_id)
    #         Path(f'./data/clean_base_collated_text/{text_fn}.txt').write_text(derge_with_notes, encoding='utf-8')
    src = Path('./data/opfs/collated_opfs/PD01B8805/PD01B8805.opf/base/00001.txt').read_text(encoding='utf-8')
    trg = Path('./data/opfs/derge_opfs/PD01B8804/PD01B8804.opf/base/00001.txt').read_text(encoding='utf-8')
    trg = trg.replace("\n", "")
    annotations = [["linebreak", "(\n)"]]
    new_trg = transfer(src, annotations, trg)
    Path('./base.txt').write_text(new_trg, encoding='utf-8')


    
    
