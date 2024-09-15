import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))


import json
import os
import logging
import time
import psutil
from multiprocessing import Process
# from threading import Thread
# from pydbus import SessionBus
from SKUD.controllers.auth_controller import AuthenticationController
from SKUD.controllers.access_controller import AccessController
from SKUD.controllers.ui_controller import SkudQueryHandler, UiController

from SKUD.remote.server import create_tornado_server
from SKUD.ORM.database import DatabaseConnection
from SKUD.ORM.loggers import VisitLogger

from SKUD.general.config import (ENABLED_PATH, GLOBAL_SETTINGS_PATH, LOG_DIR, SKUD_DIR, 
                                 DB_DIR, BACKUP_DIR, SKUD_SCRIPT_PATH, 
                                 SKUD_DB_NAME, VISITS_SCRIPT_PATH, VISITS_DB_NAME)

# bus = SessionBus()
# # notifications = bus.get("org.freedesktop.# notifications", # Bus name
#     "/org/freedesktop/# notifications" # Object path)
# )
def createlogger(name: str) -> logging.Logger: 
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    fh = logging.FileHandler(os.path.join(LOG_DIR, f"{name}.log"))

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def start(settings, name):
    # Запуск и настройка работы ардуино
    print(settings, name)

     
    controllers_logger = createlogger("skud-service-backup")

    skud_db = DatabaseConnection(name=f"{name}-{SKUD_DB_NAME}", dirpath=os.path.join(DB_DIR, name), 
                                 scriptpath=SKUD_SCRIPT_PATH, backup_path=os.path.join(BACKUP_DIR, name))

    visits_db = VisitLogger(name=f"{name}-{VISITS_DB_NAME}", dirpath=os.path.join(DB_DIR, name), 
                            scriptpath=VISITS_SCRIPT_PATH, backup_path=os.path.join(BACKUP_DIR, name))

    print(settings)
    try:
        ports = settings["ROOM_PORT_MAP"].values()
        ac = AccessController(skud=skud_db, ports=ports,
                            logger=controllers_logger,
                            visits_db=visits_db, isdaemon=True, 
                            arduino_loggers={p:createlogger("arduino") for p in ports})

        ac.start(ports)
    except BaseException as error:
        print(f"SKUD ACCESS CONTROLLER ERROR: {error}")

    time.sleep(2)

    ui_controller = UiController(skud_db=skud_db, logger=controllers_logger)
    auth_constroller = AuthenticationController(0, visits_db, skud_db, logger=controllers_logger)

    router = [(r"/ui/(.*)", SkudQueryHandler, dict(uicontroller=ui_controller))]
    try:
        t, _ = create_tornado_server(settings["PORT"], router, auth=auth_constroller.authenticatior, isdaemon=True)
        t.start()    
    except BaseException as error:
        print(f"SKUD SERVER ERROR: {error}")

    time.sleep(10)
    print("dd")

processes: list[Process] = []
try: 
    with open(GLOBAL_SETTINGS_PATH, mode="r+", encoding="utf8") as file:
        global_settings = json.loads(file.read())
    #global_settings = {"skud-test": global_settings}
    with open(ENABLED_PATH, mode="r+", encoding="utf8") as file:
        enabled = set(file.read().split('\n'))
    #enabled = global_settings.keys()
    for place in global_settings & enabled:
        settings = global_settings[place]
        p = Process(target=start, args=(settings, place,), name=f"skud-{place}", daemon=False)
        p.start()
        processes.append(p)
    
    print("END")
except BaseException as error:
    # notifications.Notify('test', 0, 'dialog-information', str(error) , "Err", [], {}, 5000)

    print(f"SKUD SERVICE ERROR: {error}")
def find_process_id(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return proc.info['pid']
    return None

print(find_process_id("skud-a"))
print("; ".join(f"{p.name}, {p.pid}" for p in processes))

sys.path.remove(SKUD_DIR)

# # notifications.Notify('test', 0, 'dialog-information', str([p.name for p in processes]) , "PROC", [], {}, 5000)
# # notifications.Notify('test', 0, 'dialog-information', str([p.pid for p in processes]) , "PROC2", [], {}, 5000)
