import json
from abc import ABC
from tornado.websocket import WebSocketHandler
from typing import Any, Callable, Protocol
    
from general.singleton import Singleton

class Answer:
    '''Класс для хранения ответа на сообщение'''
    def __init__(self, data: Any, error: str) -> None:
        self.data = data
        self.error = error
    def toJSON(self) -> str:
        return json.dumps(self.__dict__)
    
class Actions(Protocol):
    '''Интерфейс обработки сообщений'''
    def actions_map(self) -> dict[str, Callable[[str], Answer]]:
        '''Метод для контроли и обработки сообщений клиента.'''
        pass
    def verify(self, **kwargs) -> bool:
        '''Метод для верификации клиенита.'''
        pass

class WebsoketClients(Singleton):
    '''Класс для взаимодействия с websocket соединениями из внешних источников'''
    def __init__(self) -> None:
        self.__ws_clients: dict[int, WebSocketHandler] = {}

    def __generatekey__(self) -> int:
        '''Генерирует ключ для словаря.'''
        key = 0
        if key not in self.__ws_clients.keys():
            key += 1
        return key
    
    def add(self, client: WebSocketHandler) -> int:
        '''Добавляет соединение в словарь. `client` - открытое соединение.'''
        key = self.__generatekey__()
        self.__ws_clients[key] = client
        return key 
    
    def __item__(self, key: int): #-> WebSocketHandler | None:
        '''Получить соединение по номеру. `key` - ключ.'''
        if key in self.__ws_clients:
            return self.__ws_clients[key]
    
    def remove(self, key: int) -> bool:
        '''Удалить соединение из списка. `key` - ключ.'''
        if key in self.__ws_clients:
            del self.__ws_clients[key]
            return True
        return False
    
    def send(self, data: str) -> bool:
        '''Отправить сообщение всем соединениям. `data` - данные для отправки.'''
        try: 
            for client in self.__ws_clients.values():
                client.write_message(data)
        except: pass
