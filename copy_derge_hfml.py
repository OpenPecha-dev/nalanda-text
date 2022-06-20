from pathlib import Path


def copy_derge_hfml(philo_dir, philo_text_list):
    for text_id in philo_text_list:
        if "D" in text_id:
            try:
                derge_hfml = Path(f'./data/derge_res/hfmls/{text_id}.txt').read_text(encoding="utf-8") 
                (philo_dir / f"derge_hfmls/{text_id}.txt").write_text(derge_hfml, encoding='utf-8')
            except:
                print('text not found')

if __name__ =="__main__":
    philo_l = ["01-Nagarjuna","03-BUddhapalita", "06-Shantideva"]
    philo_dir_paths = list(Path('./data/nalanda_works').iterdir())
    for philo_dir_path in philo_dir_paths:
        philo_text_list = (philo_dir_path / f"{philo_dir_path.stem}_text_list.txt").read_text(encoding='utf-8').splitlines()
        if philo_dir_path.stem in philo_l:
            continue
        copy_derge_hfml(philo_dir_path, philo_text_list)

