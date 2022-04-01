import yaml
from pathlib import Path

from pedurma.preview import get_reconstructed_text

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys=False, allow_unicode=True,)

def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


def get_collated_text(text_id):
    collated_text = {}
    collated_text_paths = list(Path('./collated_text').iterdir())
    collated_text_paths.sort()
    for collated_text_path in collated_text_paths:
        collated_text_id = collated_text_path.stem[:-5]
        vol_id = collated_text_path.stem[-4:]
        if collated_text_id == text_id:
            collated_text[vol_id] = collated_text_path.read_text(encoding='utf-8')
    return collated_text


def get_pandita_text(nalanda_pandita_work_info):
    text_id = nalanda_pandita_work_info[0]
    text_code = nalanda_pandita_work_info[1]
    text_title = nalanda_pandita_work_info[3]
    if text_id:
        collated_text = get_collated_text(text_id)
        for vol_id, text in collated_text.items():
            Path(f'./nalanda_works/{text_code}_{vol_id}.txt').write_text(text, encoding='utf-8')
        print(f'{text_id} completed..')

if __name__ == "__main__":
    nalanda_pandita_works = Path('./nalanda_karchak.txt').read_text(encoding='utf-8')
    nalanda_pandita_works = nalanda_pandita_works.splitlines()[1:]
    for nalanda_pandita_work in nalanda_pandita_works:
        nalanda_pandita_work_info = nalanda_pandita_work.split(',')
        get_pandita_text(nalanda_pandita_work_info)
    
