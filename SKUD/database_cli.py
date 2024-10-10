import json
import os
import click
from tabulate import tabulate

from SKUD.general.pathes import (ENABLED_PATH, GLOBAL_SETTINGS_PATH, 
                                 DB_DIR, BACKUP_DIR)

@click.group(chain=True)
def cli(): pass