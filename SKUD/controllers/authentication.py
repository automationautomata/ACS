import json
from logging import Logger
from random import randint 
from datetime import datetime, timedelta
from typing import Callable
import tornado

from SKUD.ORM.database import DatabaseConnection
from SKUD.ORM.connections import VisitsConnection
from SKUD.ORM.templates import condition_query
from SKUD.general.exception_handler import exception_handler
from SKUD.general.singleton import Singleton
from SKUD.remote.server import Answer


class Tokens(Singleton):
    '''Класс для хранения токенов сессий'''
    def __init__(self) -> None:
        self.__randmax = 2**32
        self.__tokens = {}
        self.duration = timedelta(hours=15)

    def check_token(self, token: int, id: int) -> bool:
        '''Проверяет есть ли токен'''
        now = datetime.now()
        if id in self.__tokens:
            val = self.__tokens[id]
            return val[0] == token and val[1] - now <= self.duration
        return False     
        
    def add(self, id):#: str | int) -> int:
        '''Генерирует новый токен с `id`'''
        token = randint(0, self.__randmax)
        self.__tokens[id] = (token, datetime.now())
        return token
    
    def remove(self, id):#: str | int) -> bool:
        '''Удаление токена'''
        if id in self.__tokens:
            del self.__tokens[id]
            return True
        return False


class AuthenticationController:
    logger: Logger = None    
    def __init__(self, remote_right: int, visits_db: VisitsConnection,
                       skud_db: DatabaseConnection, password: str, 
                       logger: Logger=None, Debug: bool=False) -> None:
        self.visits_db = visits_db
        self.skud_db = skud_db
        self.remote_right = remote_right
        self.tokens = Tokens()
        self.password = password
        
        self.Debug = Debug
        self.skud_db.establish_connection()
        sql = condition_query("access_rules", ["room"], f"right = {self.remote_right}")
        self.remote_rooms = {row[0] for row in self.skud_db.execute_query(sql)}
        AuthenticationController.logger = logger

    @exception_handler(logger, Answer(0, ""))
    def card_authentication(self, data, address) -> Answer:  
        # try:
        msg = json.loads(data)
        if msg['id'] in self.remote_rooms:
            sub_sql = condition_query("cards", ['*'], f"number = {msg['key']}")[0:-1]
            sql = condition_query(f"entities inner join ({sub_sql}) as c on entities.card = c.id", ["c.number"], 
                                    f"right = {self.remote_right}")
            
            card = self.skud_db.execute_query(sql) 

            #### DEBUG ####
            if self.Debug: print("data:", data, "number:", card)
            if self.logger: self.logger.debug(f"data: {data}, card: {card}")

            if len(card) == 1:
                token = self.tokens.add(msg['id'])
                return Answer(token, "")
            return Answer(0, "Invalid card")
        return Answer(0, "Invalid room")
        
        # except BaseException as error:

        #     #### DEBUG ####
        #     if self.Debug: print("ERROR:", str(error))

        #     if self.logger:
        #         self.logger.warning(f"{error}; In AuthenticationController.authentication with data = {data}")
        #     return Answer(0, str(error))
    @exception_handler(logger, Answer(None, ""))
    def password_authentication(self, hash, address):
        if self.password == hash:
            token = self.tokens.add(msg['id'])
        return Answer(None, "")
    

class AuthenticationHandler(tornado.web.RequestHandler):
    '''Класс для аутентификации'''
    def initialize(self, auth: AuthenticationController):
        self.auth = auth

    def get(self) -> None:
        if self.get_body_arguments("auth"): 
            answer = self.auth.card_authentication(self.get_body_argument("auth"), self.request.uri)
        elif self.get_body_arguments("password"): 
            answer = self.auth.password_authentication(self.get_body_argument("password"), self.request.uri)
        else: 
            answer = Answer(None, "INCORRECT BODY")
        self.write(answer.to_json())
        
