import logging
from os import path
from components.prefabcad import load_elements, get_accessories, update_steel_acc_amount


def sync_steel_acc(directory: str):
    production_dir = path.join(directory, "Do produkcji")
    drawings_dir = path.join(directory, "Rysunki", "Bloki")

    elements = load_elements(production_dir)
    accessories = get_accessories(elements)
    steel_accessories = [x for x in accessories if '_AK_' in x.index]
    for i in steel_accessories:
        acc_path = path.join(drawings_dir, f'{i.index}.txt')
        print(acc_path)
        if path.isfile(acc_path):
            update_steel_acc_amount(acc_path, i.index, i.amount)
            logging.debug(f'Accessory {i.index} updated')
        else:
            logging.error(f"File {i.index}.txt doesn't exists")
            # raise FileExistsError("File doesn't exists")