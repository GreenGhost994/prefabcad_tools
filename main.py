from components.prefabcad import *
from components.steel_acc_sync import *
from components.element_stats import analyze_project_stats
from components.results import dump_results
from os import path, environ

import logging
import logging.handlers
 

handler = logging.handlers.WatchedFileHandler(
    environ.get("LOGFILE", "root.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(environ.get("LOGLEVEL", "DEBUG"))
root.addHandler(handler)


directory = input('Enter project folder path: ')
mode = input('1: element stats, 2: steel accessory sync')

if not path.exists(directory):
    raise FileNotFoundError('No such directory')
if int(mode) not in [1, 2]:
    raise ValueError('Mode not avaible')

if int(mode) == 1:
    project_name = input('Enter project INDEX: ')
    results = analyze_project_stats(directory)
    dump_results(results, project_name, 'element_stats')

elif int(mode) == 2:
    sync_steel_acc(directory)
