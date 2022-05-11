import re
from pathlib import Path
from opf_formatter import create_opf, get_durchen_layer
from openpecha.utils import dump_yaml



def test_opf_formatter():
    text_id = "D1133"
    collated_text = Path('./tests/data/D1133_v001.txt').read_text(encoding='utf-8')
    durchen = get_durchen_layer(collated_text, default_pub="derge")
    dump_yaml(durchen, Path('./tests/data/durchen.yml'))


if __name__ == "__main__":
    # test_opf_formatter()
    collated_text = Path('./tests/data/D1133_v001.txt').read_text(encoding='utf-8')
    create_opf(text_id="D1133", collated_text=collated_text, opf_path=Path('./tests/data/'))