import json
import os
import logging
import time
import psutil
from multiprocessing import Process
# from threading import Thread
# from pydbus import SessionBus
from SKUD.general.exeption_handler import ExceptionHandler
from SKUD.controllers.auth_controller import AuthenticationController
from SKUD.controllers.access_controller import AccessController
from SKUD.controllers.ui_controller import SkudQueryHandler, UiController

from SKUD.remote.server import create_tornado_server
from SKUD.ORM.database import DatabaseConnection
from SKUD.ORM.loggers import VisitLogger

from SKUD.general.config import (LOG_DIR, SKUD_DIR, DB_DIR, BACKUP_DIR, ENABLED_PATH, GLOBAL_SETTINGS_PATH,
                                 SKUD_SCRIPT_PATH, SKUD_DB_NAME, VISITS_SCRIPT_PATH, VISITS_DB_NAME)


# bus = SessionBus()
# # notifications = bus.get("org.freedesktop.# notifications", # Bus name
#     "/org/freedesktop/# notifications" # Object path)
# )


def start(settings, name):
    # Запуск и настройка работы ардуино
    print(settings, name)

     
    logger = logging.getLogger("skud-service-backup")

    logger.setLevel(logging.INFO)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    fh = logging.FileHandler(os.path.join(LOG_DIR, "skud-service-backup.log"))

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ex_handler = ExceptionHandler(logger)
    skud_db = DatabaseConnection(name=f"{name}-{SKUD_DB_NAME}", dirpath=os.path.join(DB_DIR, name), 
                                 exception_handler=ex_handler,
                                 scriptpath=SKUD_SCRIPT_PATH, backup_path=os.path.join(BACKUP_DIR, name))

    visits_db = VisitLogger(name=f"{name}-{VISITS_DB_NAME}", dirpath=os.path.join(DB_DIR, name), 
                            exception_handler=ex_handler,
                            scriptpath=VISITS_SCRIPT_PATH, backup_path=os.path.join(BACKUP_DIR, name))

    ac = AccessController(skud=skud_db, ports=settings["ROOM_PORT_MAP"].values(),
                          exception_handler=ex_handler,
                          visits_db=visits_db, isdaemon=False)

    ac.start(settings["ROOM_PORT_MAP"])
    time.sleep(2)


    # if True:
    #     click.echo('\n'.join(visits_db.execute_query("SELECT * FROM sqlite_temp_master;")))
    #     click.echo('\n'.join(visits_db.execute_query("SELECT * FROM visits_history;")))

    # Запуск и нстройка работы сервера

    ui_controller = UiController(skud_db=skud_db)
    auth_constroller = AuthenticationController(0, visits_db, skud_db)

    router = [(r"/ui/(.*)", SkudQueryHandler, dict(uicontroller=ui_controller))]
    # def wl(): 
    #     for i in range(2):
    #         time.sleep(1)            
    #         # notifications.Notify('test', 0, 'dialog-information', "wlll" , "PLACE", [], {}, 5000)
    #         backup.info("wll")
    #     print("end")
    #     backup.info(os.getpid())
        #print(processes[0].pid in psutil.pids())

    #t = Thread(target=wl, daemon=False)
    t, _ = create_tornado_server(settings["PORT"], router, auth=auth_constroller.authenticatior, isdaemon=False)
    t.start()

processes: list[Process] = []
try:
    with open(GLOBAL_SETTINGS_PATH, mode="r+", encoding="utf8") as file:
        global_settings = json.loads(file.read())
        backup.info(str((str(global_settings) , "global_settings")))

    with open(ENABLED_PATH, mode="r+", encoding="utf8") as file:
        enabled = set(file.read().split('\n'))
        backup.info(str((str(enabled) , "ENABLED")))


    for place in global_settings:
        settings = global_settings[place]
        if place in enabled:
            backup.info(str((place , "PLACE")))

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
if len(processes):
    print( processes[0].pid in psutil.pids())
print([(p.name, p.pid) for p in processes])
# notifications.Notify('test', 0, 'dialog-information', str([p.name for p in processes]) , "PROC", [], {}, 5000)
# notifications.Notify('test', 0, 'dialog-information', str([p.pid for p in processes]) , "PROC2", [], {}, 5000)
