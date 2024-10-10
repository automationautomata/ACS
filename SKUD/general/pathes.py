# Глобальные константы для СКУДа

from os.path import join, dirname
from platform import system

SKUD_DIR = dirname(dirname(__file__))
'''Корневая папка проекта.'''

if system() == "Windows":
    DATA_DIR = join(SKUD_DIR, "skud")
    '''Корневая папка для дирктории с данными для СКУДа.'''

    SETTINGS_DIR = join(SKUD_DIR, "skud")
    '''Корневая папка для дирктории с данными для СКУДа.'''

elif system() == "Linux":
    DATA_DIR = "/var/lib/skud"
    '''Корневая папка для дирктории с данными для СКУДа.'''

    SETTINGS_DIR = "/etc/skud"
    '''Корневая папка для дирктории с данными для СКУДа.'''
    
else:
    raise NameError("Invalid platform")

LOG_DIR = join(DATA_DIR, "log")
'''Путь к папке для логов.'''

DB_DIR = join(DATA_DIR, "DB")
'''Путь к папке с БД.'''

BACKUP_DIR = join(DATA_DIR, "backups")
'''Путь к папке с бекапами БД.'''

SKUD_DB_NAME = "SKUD.db"
'''Название базы данных СКУДа.'''

VISITS_DB_NAME = "visits.db"
'''Название базы данных СКУДа.'''

SKUD_SCRIPT_PATH = join(SKUD_DIR, "dbscripts", "skud_script.sql")
'''Путь к скрипту, создающему базу данных СКУДа.'''

VISITS_SCRIPT_PATH = join(SKUD_DIR, "dbscripts", "visits_script.sql")
'''Путь к скрипту, создающему базу данных посещений.'''

GLOBAL_SETTINGS_PATH = join(SETTINGS_DIR, "global-settings.json")
'''Путь к файлу с настройками для всех мест.'''

ENABLED_PATH = join(SETTINGS_DIR, "enabled")
'''Список мест действующих на данный момент.'''