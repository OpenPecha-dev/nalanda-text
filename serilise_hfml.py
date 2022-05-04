import yaml
from pathlib import Path
from openpecha.serializers import HFMLSerializer

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))

def serialize_hfml(opf_path, text_id):
    serializer = HFMLSerializer(opf_path,text_id=text_id, layers=["Pagination"])
    serializer.apply_layers()
    results = serializer.get_result()
    return results


if __name__ == "__main__":
    opf_path = Path('./derge_res/P000002/P000002.opf')
    text_ids = Path('./collated_text_list.txt').read_text(encoding='utf-8').splitlines()
    for text_id in text_ids:
        if "D" in text_id and "x" not in text_id:
            text_id = text_id.replace("x", "")
            hfmls = serialize_hfml(opf_path, text_id)
            for vol_walker, (vol_id, hfml) in enumerate(hfmls.items()):
                if len(hfmls)>2 and vol_walker == 0:
                    Path(f'./derge_res/hfmls/{text_id}x.txt').write_text(hfml, encoding='utf-8')
                elif len(hfmls)>2 and vol_walker == 1:
                    Path(f'./derge_res/hfmls/{text_id}y.txt').write_text(hfml, encoding='utf-8')
                else:
                    Path(f'./derge_res/hfmls/{text_id}.txt').write_text(hfml, encoding='utf-8')
            
