import json
import os
import click
from tabulate import tabulate
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import hashlib

from SKUD.general.pathes import (ENABLED_PATH, GLOBAL_SETTINGS_PATH, 
                                 DB_DIR, BACKUP_DIR)

type GlobalSettings = dict[str, dict[str, str] | int]

SETTINGS_VALIDATION = {
        "type": "object",
        "properties": {
            "PORT": {"type": "number"},
            "PASSWORD": {"type": "string"},
            "ROOM_PORT_MAP": {"type" : "object"},
            "ADMIN": {
                "type": "object", 
                "properties": {
                        "SID": {"type" : "number"},
                        "CARDS": {"type" : "number"},
                    },
                "required": ["SID", "CARDS"]   
                }       
            },
        "required": ["ROOM_PORT_MAP", "PORT"]
    }
'''Ключи, которые должны быть в файле с настройками.'''

DEAFULT_PASSWORD = "BluePa$$word"
'''Пароль по умолчанию.'''


@click.group(chain=True)
def cli(): pass


@cli.command(name="clear")
@click.argument("name", type=str)
@click.option("-b", "--backup", type=bool, is_flag=True, flag_value=True,
    help="Удалить вместе с бекапами.",
)
def clear_place(name, backup): 
    '''Удаляет БД места с названием name'''
    try:
        click.echo("Are you sure ? (Yes/No)", end=" ")

        if input().replace(" ", "") != "Yes":
            with open(GLOBAL_SETTINGS_PATH, "r+", encoding="utf8") as file:
                raw = file.read()
                globals_settings: GlobalSettings = json.loads(raw) if raw else {}
                del globals_settings[name]
                file.seek(0)
                file.write(json.dumps(globals_settings))
                file.truncate()
            os.remove(os.path.join(DB_DIR, name))
            if backup:
                os.remove(os.path.join(BACKUP_DIR, name))

        click.echo("Done")
    except BaseException as error:
        click.echo(f"\nERROR: {error}\n")



@cli.command(name="show-places")
@click.option("-r", "--running", type=bool, is_flag=True, flag_value=True,
    help="Вывод работающих на данный момент."
)
@click.option("-i", "--info", type=bool, is_flag=True, flag_value=True,
    help="Вывод вместе с настройками."
)
@click.option("-t", "--table", type=bool, is_flag=True, flag_value=True,
    help="Вывод в виде таблицы."
)
def show_place(running, info, table):
    '''Выводит спосок мест'''
    try:
        backups = os.listdir(BACKUP_DIR)
        underline = lambda p: f"\033[4m{p}\033[0m" if p not in backups else p

        with open(ENABLED_PATH if running else GLOBAL_SETTINGS_PATH, "r+") as file:
            if running: 
                places = file.read().split('\n')
                if len(places) == 0 and not places[-1]:
                    places = places[0:-1]
            else: 
                places: GlobalSettings = json.loads(file.read())
        
        if not info:
            underlined = map(underline, places)
            if not table:
                click.echo(' '.join(underlined))
            else: 
                click.echo(tabulate(underlined))
        else:
            if running:
                with open(GLOBAL_SETTINGS_PATH, "r+") as file2:
                    settings = json.loads(file2.read())
                    places = {p:s for p, s in settings if p in places}

            if not table:
                to_str = lambda p: f"{underline(p)}: \n\t ROOM_PORT_MAP: {places[p]['ROOM_PORT_MAP']} \n\t PORT: {places[p]['PORT']}"
                click.echo('\n'.join(map(to_str, places)))
            else: 
                format_settings = lambda x: tabulate(x.items(), tablefmt="plane") if type(x) is dict else x
                setings_keys = list(SETTINGS_VALIDATION["properties"])
                
                table = ([i, underline(item[0])] + [format_settings(item[1][key]) for key in setings_keys] 
                        for i, item in enumerate(places.items()))
                click.echo(tabulate(table, ["Name"]+setings_keys, "rounded_grid"))
        click.echo()
        click.echo("Places without backup was underlined")

    except BaseException as error:
        click.echo(f"\nERROR: {error}\n")

    
@cli.command(name="create")
@click.argument("name", nargs=1, type=str)
@click.argument("settings_path", nargs=1,
    type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option("--debug", "-d", type=bool, is_flag=True, flag_value=True,
    help="Вывод дополнительной инфоррмации на экран."
)
def create(name, settings_path, debug):
    '''Запустить СКУД с названием name или создать его, если он не существует 
    
    settings_path - путь к файлу с настройками СКУДа,
    debug - Вывод дополнительной инфоррмации на экран.

    
    Пример содержания файла с настройками:\n\r
    { \n\r
        "ROOM_PORT_MAP": {"0": "/dev/ttyACM0"},\n\r
        "PORT": 9092\n\r
    }'''    
    if not settings_path: return

    with open(settings_path, mode="r+", encoding="utf8") as file:
        try:
            settings: dict = json.loads(file.read())
            validate(instance=settings, schema=SETTINGS_VALIDATION)
        except (json.decoder.JSONDecodeError, ValidationError) as ex:
            click.echo("Settings error")
            if ex[0] is not None:
                click.echo("Settings have incorrect format")
            else:
                click.echo(f"Settings don't matches schema\n{ex.message}")
            click.echo("The system has not been created")
            return

    with open(GLOBAL_SETTINGS_PATH, "r+", encoding="utf8") as file:
        raw = file.read()
        try:
            globals_settings: GlobalSettings = json.loads(raw) if raw else {}
        except json.decoder.JSONDecodeError as ex:
            click.echo(f"\nSettings error\n{ex}\nThe system has not been created")
            return  
        globals_settings[name] = settings

        if "PASSWORD" in settings:
            password = DEAFULT_PASSWORD
        else: 
            password = settings["PASSWORD"]
        globals_settings[name]["PASSWORD"] = hashlib.sha256(password.encode()).hexdigest()
        
        file.seek(0)
        file.write(json.dumps(globals_settings)+'\n')
        file.truncate()
    

@cli.command(name="start")
@click.argument("names", nargs=-1, required=False, type=str)
@click.option("--all", type=bool, is_flag=True, flag_value=True,
    help="Для всех пользователей."
)
@click.option("--service", type=bool, is_flag=True, flag_value=True,
    help="Запустить сервис."
)
def start(names, all, service):
    try:
        if all and len(names) == 0:
            with open(GLOBAL_SETTINGS_PATH, "w+") as file:
                globals_settings: GlobalSettings = json.loads(file.read())
                names = []
                for name, settings in globals_settings.items():
                    if "PASSWORD" in settings:
                        names.append(f"{name} {settings["PASSWORD"]}")
                    else: 
                        names.append(f"{name}")
        elif len(names) == 0: 
            click.echo("Empty list of places.")
            return
        
        with open(ENABLED_PATH, "w+") as file:
            file.seek(0)
            file.write('\n'.join(names)+'\n')
            file.truncate()

        if service:
            try: from systemd_service import Service
            except: from SKUD.general.sysd import Service
            daemon = Service("skud-service")
            try: daemon.enable()
            except: pass
            daemon.restart()
    except BaseException as error:
        click.echo("Start error")
        click.echo(error)
        click.echo("The system has not been started")



@cli.command(name="database")
@click.argument("query", type=str)
def database(query): 
    pass


def clear_all():
    os.remove(DB_DIR)
    os.remove(BACKUP_DIR)

##### Wiegand ######

# if __name__ == '__main__':
#     cli()
