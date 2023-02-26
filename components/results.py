from os.path import join, exists
from os import getcwd, makedirs
from json import dump


def create_results_folder(name: str) -> None:
    directory = join(getcwd(), 'results', name)
    if not exists(directory):
        makedirs(directory)
    return directory


def dump_results(results: dict, file_name: str, folder_name: str) -> None:
    folder_path = create_results_folder(folder_name)
    file_path = join(folder_path, file_name+'.json')
    with open(file_path, 'w', encoding ='utf8') as json_file:
        dump(results, json_file, allow_nan=True, indent=4)