import json
import logging
from typing import Callable
import tornado
from ORM.database import DatabaseConnection
from ORM.templates import condition_query, sort_query, \
                          insert, update
from remote.tools import Answer
from .auth_controller import Tokens


class UiController:
    def __init__(self, skud_db: DatabaseConnection, logger: logging.Logger = None) -> None:
        '''`skud_db` - соединение с БД СКУДа, `logger` - логгер'''
        self.skud_db = skud_db
        self.skud_db.establish_connection()
        self.logger = logger

        self.tokens = Tokens()

    def table_query(self, table: str, data: str, is_null: False) -> Answer:
        '''Запрос к таблице `table`, `data` - параметры запроса. возвращает ответ Answer, где data - спиоск'''
        try: 
            params = json.loads(data)
            col_names = self.skud_db.table_cols(table)
            interval = (params["start"], 100 + params["start"])
            if is_null:
                table = condition_query(table, col_names, "date_time_end IS NOT NULL")

            sql = sort_query(table, col_names, interval,
                             params["order_column"], params["order_type"])
            
            res = self.skud_db.execute_query(sql)
            return Answer(self.skud_db.rows_to_dicts(col_names, res), "")
        except BaseException as error:
            if self.logger:
                self.logger.warning(f"{error}; In UiController.table_query with table = {table} and data = {data}")
            return Answer([], str(error))
    
    def table_insert(self, table: str, values: str) -> Answer:
        '''Запрос к таблице `table`, `data` - параметры запроса. возвращает ответ Answer, где data - спиоск'''
        try: 
            inserted_vals: dict = json.loads(values)
            col_names = []
            vals = []
            for key, val in inserted_vals:
                col_names.append(key)
                vals.append(val)
            sql = insert(table, col_names)
            res = self.skud_db.execute_query(sql, *vals)
            print(res)
            return Answer("", "")
        except BaseException as error:
            if self.logger:
                self.logger.warning(f"{error}; In UiController.table_query with table = {table} and data = {values}")
            return Answer([], str(error))

    def table_update(self, table: str, data: str) -> Answer:
        '''Запрос к таблице `table`, `data` - параметры запроса. возвращает ответ Answer, где data - спиоск'''
        try: 
            updated: dict = json.loads(data)
            col_names = []
            vals = []
            for key, val in updated["values"]:
                col_names.append(key)
                vals.append(val)
            pk = self.skud_db.table_pk("table")
            key = updated["key"]
            sql = update(table, col_names, f"{pk} = {key}")
            res = self.skud_db.execute_query(sql)
            print(res)  
            return Answer("", "")
        except BaseException as error:
            if self.logger:
                self.logger.warning(f"In UiController.table_query with table = {table} and data = {data}")
            return Answer([], str(error))

    def verify(self, **kwargs) -> bool:
        '''Проверяет '''
        try:
            return self.tokens.check_token(int(kwargs["token"]), int(kwargs["id"]))
        except BaseException as error:
            if self.logger:
                self.logger.warning(f"{error}; In UiController.verify with data = {kwargs}")
            return Answer([], str(error))

class SkudQueryHandler(tornado.web.RequestHandler):
    '''Класс для обработки CRUD запросов к БД СКУДа'''
    def initialize(self, uicontroller: UiController) -> None:
        self.controller = uicontroller

    def check(self, table):
        tables = {"rights", "cards", "rooms", "entities_view", "access_rules_view"}
        return table in tables

    def get(self, table) -> None:
        print("eee")
        if not self.check(table): return
        headers = self.request.headers
        if self.controller.verify(token=headers.get("X-Auth"), id=headers.get("X-Id")):
            data = self.get_body_argument("params")
            is_null = False
            if "NULL" in self.request.body_arguments.keys():
                if self.get_body_argument("params") == "True": 
                    is_null = True
            print(data, is_null)
            answer = self.controller.table_query(table, data, is_null)
            print(answer.toJSON())
            self.write(answer.toJSON())
        
    def post(self, table) -> None:
        headers = self.request.headers
        if self.controller.verify(token=headers.get("X-Auth"), id=headers.get("X-Id")):
            table = self.get_argument()
            data = self.get_body_argument("values")
            answer = self.controller.table_insert(table, data)
            print(answer.toJSON())
            self.write(answer.toJSON())
            
    def put(self, table) -> None:
        headers = self.request.headers
        if self.controller.verify(token=headers.get("X-Auth"), id=headers.get("X-Id")):
            table = self.get_argument()
            data = self.get_body_argument("data")
            answer = self.controller.table_insert(table, data)
            print(answer.toJSON())
            self.write(answer.toJSON())

    def delete(self, table) -> None:
        headers = self.request.headers
        if self.controller.verify(token=headers.get("X-Auth"), id=headers.get("X-Id")):
            answer = self.actions["put"](self.get_body_argument("data"))
            self.set_header("Content-Type", "text/plain")
            self.write(answer.toJSON())


class UiVisitsController(UiController):
    '''Класс для обработки запросов к БД посещений'''
    def actions_map(self) -> dict[str, Callable]:
        actions = {"visits query"         : self.visits_query, 
                   "remote_sessions query": self.remote_sessions_query}
        return actions

    def visits_query(self, data: str) -> Answer:
        return self.table_query("visits_history", data)
        
    def remote_sessions_query(self, data: str) -> Answer:
        return self.table_query("remote_sessions", data)
    

