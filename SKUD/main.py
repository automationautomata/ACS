import json
import os
import click

from SKUD.general.config import (ENABLED_PATH, GLOBAL_SETTINGS_PATH, 
                                 DB_DIR, BACKUP_DIR, SETTINGS_KEYS)

@click.group(chain=True)
def cli(): pass


@cli.command(name="clear")
@click.argument("name", type=str)
@click.option("-b", "--backup", type=bool,
    help="Удалить вместе с бекапами.",
    is_flag=True, flag_value=True
    
)
def clear_place(name, backup): 
    '''Удаляет БД места с названием name'''
    try:
        click.echo("Are you sure ? (Yes/No)", end=" ")

        if input().replace(" ", "") != "Yes":
            with open(GLOBAL_SETTINGS_PATH, "r+", encoding="utf8") as file:
                raw = file.read()
                if raw != "":
                    globals_settings = json.loads(raw)
                else: globals_settings = {}
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
@click.option("-r", "--running", type=bool,
    help="Вывод работающих на данный момент.",
    is_flag=True, flag_value=True
)
@click.option("-i", "--info", type=bool,
    help="Вывод вместе с настройками.",
    is_flag=True, flag_value=True
)
def show_place(running, info):
    '''Выводит спосок мест'''
    try:
        backups = os.listdir(BACKUP_DIR)
            
        path = ENABLED_PATH if running else GLOBAL_SETTINGS_PATH
        with open(path, "r+") as file:
            if running: 
                places = file.read().split('\n')
                if len(places) == 0 and places[-1] == '':
                    places = places[0:-1]
            else: places = json.loads(file.read())
            if not info:
                showed = map(lambda p: p if p in backups else f"\033[4m{p}\033[0m", places)
                click.echo(' '.join(showed))
            else:
                if running:
                    with open(GLOBAL_SETTINGS_PATH, "r+") as file2:
                        settings = json.loads(file2.read())
                        places = {p:s for p, s in settings if p in places}
                fmt = lambda p: fmt if p in backups else f"\033[4m{p}\033[0m"
                showed = map(lambda p: f"{fmt(p)}: \n\t ROOM_PORT_MAP: {places[p]['ROOM_PORT_MAP']} \n\t PORT: {places[p]['PORT']}", places)
                click.echo('\n'.join(showed))
            click.echo()
            click.echo("Places without backup was underlined")
    except BaseException as error:
        click.echo(f"\nERROR: {error}\n")

    
@cli.command(name="create")
@click.argument("name", nargs=1, type=str)
@click.argument("settings_path", nargs=1,
    type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option("--debug", "-d", type=bool,
    help="Вывод дополнительной инфоррмации на экран.",
    is_flag=True, flag_value=True
)
def create(name, settings_path, debug):
    '''Создать СКУД с для места name или создать с его, если он не существует 
    
    settings_path - путь к файлу с настройками СКУДа,
    debug - Вывод дополнительной инфоррмации на экран.

    
    Пример содержания файла с настройками:\n\r
    { \n\r
        "ROOM_PORT_MAP": {"0": "/dev/ttyACM0"},\n\r
        "PORT": 9092\n\r
    }'''    
    if not settings_path: return
 
    try:
        with open(settings_path, mode="r+", encoding="utf8") as file:
            settings: dict = json.loads(file.read())
        if settings.keys() != SETTINGS_KEYS:
            click.echo("Settings error")
            click.echo("Settings contains incorrect keys")
            click.echo("The system has not been created")
            return
        with open(GLOBAL_SETTINGS_PATH, "r+", encoding="utf8") as file:
            raw = file.read()
            if raw != "":
                globals_settings = json.loads(raw)
            else: globals_settings = {}
            globals_settings[name] = settings
            file.seek(0)
            file.write(json.dumps(globals_settings)+'\n')
            file.truncate()
    except BaseException as error:
        click.echo("Settings error")
        click.echo(error)
        click.echo("The system has not been created")

    

@cli.command(name="start")
@click.argument("names", nargs=-1, required=False, type=str)
@click.option("--all", type=bool, help="Для всех пользователей.",
    is_flag=True, flag_value=True
)
@click.option("--service", type=bool, help="Запустить сервис.",
    is_flag=True, flag_value=True
)
def start(names, all, service):
    try:
        if all and len(names) == 0:
            with open(GLOBAL_SETTINGS_PATH, "w+") as file:
                globals_settings: dict = json.loads(file.read())
                names = globals_settings.keys()
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


def clear_all():
    os.remove(DB_DIR)
    os.remove(BACKUP_DIR)

##### Wiegand ######

# if __name__ == '__main__':
#     cli()
