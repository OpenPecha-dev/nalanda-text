import csv
import logging
import yaml
from pathlib import Path

# logging.basicConfig(filename="cross_vol_list.log", level=logging.INFO, filemode="w")
logging.basicConfig(filename="missing_text.log", level=logging.INFO, filemode="w")

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys=False, allow_unicode=True,)

# def _mkdir(path):
#     if path.is_dir():
#         return path
#     path.mkdir(exist_ok=True, parents=True)
#     return path


def get_collated_text(text_id):
    collated_text = {}
    collated_text_paths = list(Path('./data/normalized_collated_text').iterdir())
    collated_text_paths.sort()
    for collated_text_path in collated_text_paths:
        collated_text_id = collated_text_path.stem[:-5]
        vol_id = collated_text_path.stem[-4:]
        if collated_text_id == text_id:
            collated_text[vol_id] = collated_text_path.read_text(encoding='utf-8')
    return collated_text


def get_pandita_text(nalanda_pandita_work_info, nazom_text_list):
    text_id = nalanda_pandita_work_info[0]
    text_code = nalanda_pandita_work_info[1]
    text_title = nalanda_pandita_work_info[2]
    if text_id:
        # if is_cross_vol_text(text_id):
        #     logging.info(f"{text_id}")
        collated_text = get_collated_text(text_id)
        if collated_text:
            for vol_id, text in collated_text.items():
                Path(f'./nalanda_works/{text_code}{text_id}.txt').write_text(text, encoding='utf-8')
        else:
            if text_id not in nazom_text_list:
                logging.info(f'{text_id} missing..')

    
def is_cross_vol_text(text_id):
    collated_text_paths = list(Path('./collated_text').iterdir())
    collated_text_paths.sort()
    for collated_text_path in collated_text_paths:
        collated_text_id = collated_text_path.stem[:-5]
        if f"{text_id}x" == collated_text_id or f"{text_id}y" == collated_text_id:
            return True
    return False

def get_text_list(list_path):
    text_list = list_path.read_text(encoding='utf-8').splitlines()
    text_list = list(set(text_list))
    text_list.sort()
    return text_list

if __name__ == "__main__":
    nazom_text_list = get_text_list(Path('./nazom_text_list.txt'))
    karchak_file = open("nalanda_text_karchak.csv")

    karchak_csvreader = csv.reader(karchak_file)

    karchak = {}
    rows = []
    for row in karchak_csvreader:
        rows.append(row)
    
    for text_info in rows[1:]:
        get_pandita_text(text_info, nazom_text_list)
