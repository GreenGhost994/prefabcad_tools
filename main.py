from components.prefabcad import *
from components.steel_acc_sync import *
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

if path.exists(directory):
    sync_steel_acc(directory)
else:
    raise FileNotFoundError('No such directory')
