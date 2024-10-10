from abc import ABC, abstractmethod
import logging
import sqlite3
import os
import threading
from typing import Callable, Self


class DatabaseConnection:
    def __init__(self, scriptpath: str, name: str, dirpath: str, backup_path: str, after_creation: Callable[[Self]] = None) -> None:
        '''`scriptpath` - путь к скрипту, создающему бд,
        `name` - название БД, `dirpath` - папка с БД, `backup_path` - путь к бекапу БД.'''
        self.__scriptpath = scriptpath
        self.path = os.path.join(dirpath, name)
        self._connections_ = {} #: dict[int, sqlite3.Connection] = {}
        self.after_creation = after_creation

        self.backup = logging.getLogger(f"{name}-backup")
        self.backup.setLevel(logging.INFO)
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        fh = logging.FileHandler(os.path.join(backup_path, f"{name}-backup.log"))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.backup.addHandler(fh)

    def threadsafe_connect(self) -> sqlite3.Connection:
        thread_id = threading.get_native_id()
        if thread_id not in self._connections_.keys():
            #print(self.path)
            self._connections_[thread_id] = sqlite3.connect(self.path)        
        try: 
            self._connections_[thread_id].cursor()
        except: 
            self._connections_[thread_id] = sqlite3.connect(self.path)
        return self._connections_[thread_id]
    
    def exists(self):
        return os.path.isfile(self.path)
            
    def establish_connection(self) -> None:
        '''Устанавливает соединение c базой и, если БД отсутствует,
        то пересоздает ее на основе указанного скрипта.'''
        dir = os.path.dirname(self.path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        if not os.path.exists(self.path):           
            self._createdatabase_()
        else: 
            self.threadsafe_connect()

    def _createdatabase_(self) -> None:
        '''Создает базу данных на основе скрипта.'''
        conn = self.threadsafe_connect()
        cursor = conn.cursor()

        with open(self.__scriptpath, mode="r+", encoding="utf8") as scriptfile:
            script = scriptfile.read()
            cursor.executescript(script)
            conn.commit()
        if self.after_creation is not None: 
            self.after_creation(self)

    def execute_query(self, command: str, *params) -> list[tuple]: 
        '''Выполняет указанную команду command с параметрами params (см. документацию SQLite).'''
        conn = self.threadsafe_connect()
        cursor = conn.cursor()
        result = cursor.execute(command, params).fetchall()
        conn.commit()
        return result
    
    def execute(self, command: str, *params) -> list[tuple]: 
        '''Выполняет указанную команду command с параметрами params (см. документацию SQLite).'''
        conn = self.threadsafe_connect()
        cursor = conn.cursor()
        result = cursor.execute(command, params)
        conn.commit()
        if result:
            self.backup.info('{'+f"\"SQL\": {command}; \"VALUES\": {params}"+'}')
        return result
        
    def table_cols(self, table: str):
        sql = f"SELECT c.name FROM pragma_table_info('{table}') as c;"
        return list(map(lambda row: row[0], self.execute_query(sql)))
    
    def table_pk(self, table: str):
        sql = f"select info.name from pragma_table_info('{table}') as info WHERE info.pk = 1"
        return self.execute_query(sql)[0]

    def rows_to_dicts(self, col_names: list[str], rows: list[tuple]) -> list[dict]:
        data = []
        for row in rows:
            dict_row = {col: val for val, col in zip(row, col_names)}
            data.append(dict_row)
            print("rw", dict_row)
        return data

    def closeall(self) -> None:
        '''Закрывает соединение с БД'''
        for key in self._connections_.keys():
            self._connections_[key].close()
            del self._connections_[key]

    def close(self, key) -> bool:
        if key in self._connections_:
            try:
                self._connections_[key].close()
                del self._connections_[key]
                return True
            except:
                return False 
        return True
    
    