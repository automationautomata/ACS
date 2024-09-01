#!/usr/bin/python3

import json
import os
import click

from general.config import (ENABLED_PATH, GLOBAL_SETTINGS_PATH, 
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
def show_place(running):
    '''Выводит спосок мест'''
    try:
        backups = os.listdir(BACKUP_DIR)
         
        path = ENABLED_PATH if running else GLOBAL_SETTINGS_PATH
        with open(path, "r+") as file:
            if running: 
                places = file.read().split('\n')
            else: places = json.loads(file.read()).keys()
        
        click.echo(' '.join(place if place in backups else "\033[4m" + place + "\033[0m" for place in places))
        click.echo()
        click.echo("places without backup was underlined")
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
    '''Запустить СКУД с названием name или создать с его, если он не существует \n
        settings_path - путь к файлу с настройками СКУДа, \n
        debug - Вывод дополнительной инфоррмации на экран.'''
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
            file.write(json.dumps(globals_settings))
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
def start(names, all=False):
    try:
        if all and len(names) == 0:
            with open(GLOBAL_SETTINGS_PATH, "w+") as file:
                globals_settings: dict = json.loads(file.read())
            enabled = globals_settings.keys()
        elif names == "": 
            click.echo("Empty list of places.")
            return
        else:
            enabled = names

        click.echo(enabled)
        with open(ENABLED_PATH, "w+") as file:
            file.seek(0)
            file.write('\n'.join(names))
            file.truncate()

        try: from systemd_service import Service
        except: from general.sysd import Service
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

if __name__ == '__main__':
    cli()